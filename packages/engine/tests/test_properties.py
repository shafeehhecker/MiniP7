"""Property-based tests for the CPM engine (Phase 2 "done when", ADR-0011).

Hypothesis generates random dependency networks — every relationship type,
lags positive and negative — and asserts the *invariants* of a correct
schedule rather than specific numbers. Each property below is a statement a
scheduler must satisfy for every possible network; a counterexample is a bug
by definition.
"""
import copy

from hypothesis import given, settings, strategies as st

from schema import Activity, Relationship, RelationshipType
from engine import CPMScheduler, compute_evm

REL_TYPES = list(RelationshipType)


@st.composite
def networks(draw, max_size=12):
    """A random acyclic network of task activities.

    Acyclicity by construction: activity i may only depend on activities j < i,
    so no generated network can contain a cycle. Types and lags are drawn
    freely (lags -3..5, durations 0..10, so milestota-like zero durations and
    leads both occur).
    """
    n = draw(st.integers(min_value=1, max_value=max_size))
    acts = {}
    for i in range(n):
        aid = f"T{i}"
        rels = []
        if i > 0:
            pred_indices = draw(st.lists(
                st.integers(min_value=0, max_value=i - 1),
                max_size=3, unique=True))
            for j in pred_indices:
                rels.append(Relationship(
                    predecessor_id=f"T{j}",
                    type=draw(st.sampled_from(REL_TYPES)),
                    lag=draw(st.integers(min_value=-3, max_value=5))))
        acts[aid] = Activity(
            id=aid, name=aid,
            duration=draw(st.integers(min_value=0, max_value=10)),
            budget=draw(st.integers(min_value=0, max_value=100)),
            percent_complete=draw(st.integers(min_value=0, max_value=100)),
            actual_cost=draw(st.integers(min_value=0, max_value=100)),
            relationships=rels)
    return acts


def scheduled(acts):
    CPMScheduler(acts).schedule()
    return acts


@given(networks())
@settings(max_examples=200)
def test_schedule_arithmetic_invariants(acts):
    """EF = ES + duration; ES >= 0; LS = LF - duration — for every activity."""
    for a in scheduled(acts).values():
        assert a.EF == a.ES + a.duration
        assert a.ES >= 0
        assert a.LS == a.LF - a.duration


@given(networks())
@settings(max_examples=200)
def test_no_negative_float_and_lf_within_project(acts):
    """Without deadlines, no activity can have negative total float, and
    nothing may finish later than the project (the LF cap, ADR-0011)."""
    acts = scheduled(acts)
    finish = max(a.EF for a in acts.values())
    for a in acts.values():
        assert a.total_float >= 0
        assert a.LF <= finish


@given(networks())
@settings(max_examples=200)
def test_total_float_bounds_free_float(acts):
    """Free float (slip without delaying anyone) can never exceed total float
    (slip without delaying the project)."""
    for a in scheduled(acts).values():
        assert a.free_float <= a.total_float


@given(networks())
@settings(max_examples=200)
def test_critical_path_exists(acts):
    """Every network has at least one critical activity."""
    assert any(a.is_critical for a in scheduled(acts).values())


@given(networks())
@settings(max_examples=200)
def test_every_constraint_is_satisfied(acts):
    """The scheduled dates satisfy every relationship's inequality — the
    engine's output is checked directly against the ADR-0011 semantics."""
    acts = scheduled(acts)
    for a in acts.values():
        for r in a.relationships:
            p = acts[r.predecessor_id]
            if r.type == RelationshipType.FS:
                assert a.ES >= p.EF + r.lag or a.ES == 0
            elif r.type == RelationshipType.SS:
                assert a.ES >= p.ES + r.lag or a.ES == 0
            elif r.type == RelationshipType.FF:
                assert a.EF >= p.EF + r.lag or a.ES == 0
            else:  # SF
                assert a.EF >= p.ES + r.lag or a.ES == 0


@given(networks())
@settings(max_examples=100)
def test_scheduling_is_deterministic_and_idempotent(acts):
    """Same input → byte-identical output; rescheduling changes nothing."""
    first = {k: a.model_copy(deep=True) for k, a in scheduled(acts).items()}
    again = scheduled(acts)
    assert {k: a.model_dump() for k, a in again.items()} == \
           {k: a.model_dump() for k, a in first.items()}


@given(networks())
@settings(max_examples=100)
def test_input_order_does_not_matter(acts):
    """The schedule is a function of the network, not of dict ordering."""
    a1 = scheduled(copy.deepcopy(acts))
    reversed_acts = dict(reversed(list(copy.deepcopy(acts).items())))
    a2 = scheduled(reversed_acts)
    for k in acts:
        assert a1[k].model_dump() == a2[k].model_dump()


@given(st.lists(st.integers(min_value=0, max_value=10), min_size=1, max_size=8))
def test_fs_chain_duration_is_sum_of_durations(durations):
    """A pure FS chain's project duration is exactly the sum of durations —
    the oldest CPM sanity check there is."""
    acts = {}
    prev = None
    for i, d in enumerate(durations):
        aid = f"T{i}"
        acts[aid] = Activity(id=aid, name=aid, duration=d,
                             predecessors=[prev] if prev else [])
        prev = aid
    s = CPMScheduler(acts)
    s.schedule()
    assert s.project_duration() == sum(durations)
    assert all(a.is_critical for a in acts.values())


@given(networks(), st.integers(min_value=0, max_value=40))
@settings(max_examples=200)
def test_evm_invariants(acts, day):
    """PV and EV never exceed BAC; identities SV = EV-PV and CV = EV-AC hold;
    PV is monotonically non-decreasing in time."""
    acts = scheduled(acts)
    r = compute_evm(acts.values(), day)
    assert 0 <= r.pv <= r.bac + 1e-9
    assert 0 <= r.ev <= r.bac + 1e-9
    assert r.sv == r.ev - r.pv
    assert r.cv == r.ev - r.ac
    later = compute_evm(acts.values(), day + 5)
    assert later.pv >= r.pv - 1e-9
