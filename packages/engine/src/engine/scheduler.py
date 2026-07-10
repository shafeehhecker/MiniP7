"""
CPM Scheduling Engine for Mini-P7.
Forward pass, backward pass, float calculation, and critical path — for all
four relationship types (FS/SS/FF/SF) with lag (ADR-0011).

Semantics (working days; lag may be negative — a *lead*)
--------------------------------------------------------
For a relationship P -> S with lag L, the forward pass enforces:

    FS:  ES(S) >= EF(P) + L      "S starts after P finishes"
    SS:  ES(S) >= ES(P) + L      "S starts after P starts"
    FF:  EF(S) >= EF(P) + L      "S finishes after P finishes"
    SF:  EF(S) >= ES(P) + L      "S finishes after P starts"

and the backward pass enforces the mirror images:

    FS:  LF(P) <= LS(S) - L
    SS:  LS(P) <= LS(S) - L
    FF:  LF(P) <= LF(S) - L
    SF:  LS(P) <= LF(S) - L

ES is clamped at 0 (nothing starts before the project), and LF is capped at
the project finish (nothing may finish after it without delaying the project).
Rationale for both is recorded in ADR-0011.

Activity types (see ADR-0008)
-----------------------------
- ``TASK`` — scheduled normally.
- ``MILESTONE`` — a zero-duration task; falls out of the standard passes.
- ``LEVEL_OF_EFFORT`` — now that typed relationships exist, an LOE with
  predecessors *spans* them: it runs from the earliest ES to the latest EF of
  the activities it supports. It never drives other activities and is never on
  the critical path; an LOE that appears as someone's predecessor is rejected.
  An LOE with no predecessors schedules as an ordinary task.
- ``SUMMARY`` — still scheduled as a task; roll-up awaits the WBS (ADR-0008).
"""
from typing import Dict, List
from collections import deque

from schema import Activity, ActivityType, Relationship, RelationshipType


class SchedulerError(Exception):
    pass


class CPMScheduler:
    """
    Critical Path Method engine.

    Algorithm:
    1. Validate references; separate level-of-effort activities
    2. Topological sort of driving activities (Kahn's algorithm)
    3. Forward pass  → ES / EF under all four relationship constraints
    4. Backward pass → LS / LF under the mirror constraints, capped at finish
    5. Floats: total = LS - ES; free = tightest slack toward any successor
    6. Critical path = driving activities with zero total float
    7. Level-of-effort activities span their predecessors
    """

    def __init__(self, activities: Dict[str, Activity]):
        self.activities = activities  # {id: Activity}
        self._loe_ids = {
            aid for aid, a in activities.items()
            if a.type == ActivityType.LEVEL_OF_EFFORT and a.relationships
        }

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def schedule(self) -> List[Activity]:
        """Run full CPM and return activities with all fields populated."""
        if not self.activities:
            return []

        self._validate()
        order = self._topological_sort()
        self._forward_pass(order)
        self._backward_pass(order)
        self._compute_float()
        self._schedule_level_of_effort()

        return list(self.activities.values())

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate(self):
        for act_id, act in self.activities.items():
            for rel in act.relationships:
                if rel.predecessor_id not in self.activities:
                    raise SchedulerError(
                        f"Activity '{act_id}' references unknown predecessor "
                        f"'{rel.predecessor_id}'"
                    )
                if rel.predecessor_id in self._loe_ids:
                    raise SchedulerError(
                        f"Activity '{act_id}' depends on level-of-effort activity "
                        f"'{rel.predecessor_id}'. A level-of-effort activity spans "
                        "other work and never drives it (ADR-0011)."
                    )

    # ------------------------------------------------------------------
    # Topological sort (Kahn's BFS) over driving activities
    # ------------------------------------------------------------------

    def _driving_ids(self) -> List[str]:
        return [aid for aid in self.activities if aid not in self._loe_ids]

    def _topological_sort(self) -> List[str]:
        driving = self._driving_ids()
        in_degree: Dict[str, int] = {aid: 0 for aid in driving}
        successors: Dict[str, List[str]] = {aid: [] for aid in driving}

        for act_id in driving:
            for rel in self.activities[act_id].relationships:
                successors[rel.predecessor_id].append(act_id)
                in_degree[act_id] += 1

        queue = deque(sorted(aid for aid, deg in in_degree.items() if deg == 0))
        order: List[str] = []

        while queue:
            current = queue.popleft()
            order.append(current)
            for succ in successors[current]:
                in_degree[succ] -= 1
                if in_degree[succ] == 0:
                    queue.append(succ)

        if len(order) != len(driving):
            raise SchedulerError(
                "Circular dependency detected in activity network. "
                "Please check predecessor relationships."
            )

        return order

    # ------------------------------------------------------------------
    # Forward pass: compute ES and EF
    # ------------------------------------------------------------------

    @staticmethod
    def _es_floor(pred: Activity, rel: Relationship, duration: int) -> int:
        """The earliest-start floor a single relationship imposes on its
        successor, expressed as an ES bound (EF bounds are shifted by -duration)."""
        if rel.type == RelationshipType.FS:
            return pred.EF + rel.lag
        if rel.type == RelationshipType.SS:
            return pred.ES + rel.lag
        if rel.type == RelationshipType.FF:
            return pred.EF + rel.lag - duration
        # SF
        return pred.ES + rel.lag - duration

    def _forward_pass(self, order: List[str]):
        for act_id in order:
            act = self.activities[act_id]
            floors = [
                self._es_floor(self.activities[r.predecessor_id], r, act.duration)
                for r in act.relationships
            ]
            act.ES = max([0, *floors])  # nothing starts before day 0
            act.EF = act.ES + act.duration

    # ------------------------------------------------------------------
    # Backward pass: compute LS and LF
    # ------------------------------------------------------------------

    @staticmethod
    def _lf_ceiling(succ: Activity, rel: Relationship, duration: int) -> int:
        """The latest-finish ceiling a single relationship imposes on its
        predecessor (LS bounds are shifted by +duration)."""
        if rel.type == RelationshipType.FS:
            return succ.LS - rel.lag
        if rel.type == RelationshipType.SS:
            return succ.LS - rel.lag + duration
        if rel.type == RelationshipType.FF:
            return succ.LF - rel.lag
        # SF
        return succ.LF - rel.lag + duration

    def _successor_rels(self) -> Dict[str, List[tuple]]:
        """Map each driving activity to [(successor, relationship), ...]."""
        succ: Dict[str, List[tuple]] = {aid: [] for aid in self._driving_ids()}
        for act_id in self._driving_ids():
            act = self.activities[act_id]
            for rel in act.relationships:
                succ[rel.predecessor_id].append((act, rel))
        return succ

    def _backward_pass(self, order: List[str]):
        driving = self._driving_ids()
        project_finish = max(self.activities[a].EF for a in driving)
        succ_rels = self._successor_rels()

        for act_id in reversed(order):
            act = self.activities[act_id]
            ceilings = [
                self._lf_ceiling(succ, rel, act.duration)
                for succ, rel in succ_rels[act_id]
            ]
            # Nothing may finish after the project without delaying it, so the
            # project finish caps every LF — including activities whose only
            # constraints (e.g. an SS successor) would otherwise let them
            # drift past the end (ADR-0011).
            act.LF = min([project_finish, *ceilings])
            act.LS = act.LF - act.duration

    # ------------------------------------------------------------------
    # Float and critical path
    # ------------------------------------------------------------------

    @staticmethod
    def _relationship_slack(pred: Activity, succ: Activity, rel: Relationship) -> int:
        """How far `pred` can slip before this relationship pushes `succ`."""
        if rel.type == RelationshipType.FS:
            return succ.ES - (pred.EF + rel.lag)
        if rel.type == RelationshipType.SS:
            return succ.ES - (pred.ES + rel.lag)
        if rel.type == RelationshipType.FF:
            return succ.EF - (pred.EF + rel.lag)
        # SF
        return succ.EF - (pred.ES + rel.lag)

    def _compute_float(self):
        """
        Total Float = LS - ES  (slack without delaying project end)
        Free Float  = tightest relationship slack toward any successor, and —
                      for every activity, not just terminals — the slack to the
                      project finish itself. The finish term is what keeps
                      FF <= TF in the presence of negative lag: a lead can
                      leave a successor's ES clamped at day 0 (so the
                      relationship shows slack) while the predecessor's own
                      finish is the project finish (so it has none). Found by
                      the Hypothesis property suite; recorded in ADR-0011.
        """
        driving = self._driving_ids()
        project_finish = max(self.activities[a].EF for a in driving)
        succ_rels = self._successor_rels()

        for act_id in driving:
            act = self.activities[act_id]
            act.total_float = act.LS - act.ES
            act.is_critical = act.total_float == 0

            slacks = [
                self._relationship_slack(act, succ, rel)
                for succ, rel in succ_rels[act_id]
            ]
            act.free_float = min([project_finish - act.EF, *slacks])

    # ------------------------------------------------------------------
    # Level of effort (ADR-0008, unlocked by ADR-0011)
    # ------------------------------------------------------------------

    def _schedule_level_of_effort(self):
        """An LOE with predecessors spans them: earliest ES to latest EF of the
        activities it supports. It has no float of its own (it stretches and
        shrinks with the work) and is never on the critical path."""
        for aid in self._loe_ids:
            act = self.activities[aid]
            preds = [self.activities[r.predecessor_id] for r in act.relationships]
            act.ES = min(p.ES for p in preds)
            act.EF = max(p.EF for p in preds)
            act.LS, act.LF = act.ES, act.EF
            act.total_float = 0
            act.free_float = 0
            act.is_critical = False

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------

    def get_critical_path(self) -> List[str]:
        """Return IDs of critical activities in order."""
        return [
            act_id
            for act_id, act in self.activities.items()
            if act.is_critical
        ]

    def get_milestones(self) -> List[str]:
        """Return IDs of milestone activities (zero-duration markers)."""
        return [
            act_id
            for act_id, act in self.activities.items()
            if act.type == ActivityType.MILESTONE
        ]

    def project_duration(self) -> int:
        if not self.activities:
            return 0
        return max(act.EF for act in self.activities.values())
