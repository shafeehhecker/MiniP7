"""Hand-worked cases for typed relationships and lag (ADR-0011).

Every expected number here was computed by hand from the semantics table in
the scheduler's docstring, so a failure means the engine disagrees with the
specification — not with itself.
"""
import pytest
from schema import Activity, ActivityType, Relationship, RelationshipType as RT
from engine import CPMScheduler, SchedulerError


def rel(pred, type=RT.FS, lag=0):
    return Relationship(predecessor_id=pred, type=type, lag=lag)


def schedule(acts):
    d = {a.id: a for a in acts}
    CPMScheduler(d).schedule()
    return d


class TestForwardPass:
    def test_fs_with_lag(self):
        d = schedule([
            Activity(id="A", name="a", duration=3),
            Activity(id="B", name="b", duration=2, relationships=[rel("A", RT.FS, 2)]),
        ])
        assert (d["B"].ES, d["B"].EF) == (5, 7)  # starts 2 after A finishes at 3

    def test_fs_negative_lag_is_a_lead(self):
        d = schedule([
            Activity(id="A", name="a", duration=5),
            Activity(id="B", name="b", duration=2, relationships=[rel("A", RT.FS, -2)]),
        ])
        assert d["B"].ES == 3  # overlaps A's last 2 days

    def test_ss(self):
        d = schedule([
            Activity(id="A", name="a", duration=5),
            Activity(id="B", name="b", duration=3, relationships=[rel("A", RT.SS, 2)]),
        ])
        assert (d["B"].ES, d["B"].EF) == (2, 5)

    def test_ff(self):
        d = schedule([
            Activity(id="A", name="a", duration=5),
            Activity(id="B", name="b", duration=2, relationships=[rel("A", RT.FF)]),
        ])
        assert (d["B"].ES, d["B"].EF) == (3, 5)  # must finish with A

    def test_sf(self):
        # B may not finish before A starts + lag
        d = schedule([
            Activity(id="A", name="a", duration=3, relationships=[]),
            Activity(id="B", name="b", duration=2, relationships=[rel("A", RT.SF, 4)]),
        ])
        assert (d["B"].ES, d["B"].EF) == (2, 4)  # EF >= ES_A(0) + 4

    def test_es_clamped_at_zero(self):
        # FF with a short successor would push ES negative without the clamp
        d = schedule([
            Activity(id="A", name="a", duration=1),
            Activity(id="B", name="b", duration=10, relationships=[rel("A", RT.FF)]),
        ])
        assert d["B"].ES == 0 and d["B"].EF == 10

    def test_tightest_of_multiple_constraints_wins(self):
        d = schedule([
            Activity(id="A", name="a", duration=4),
            Activity(id="B", name="b", duration=6),
            Activity(id="C", name="c", duration=2,
                     relationships=[rel("A", RT.FS), rel("B", RT.SS, 1)]),
        ])
        assert d["C"].ES == 4  # FS from A (4) beats SS from B (1)


class TestBackwardPassAndFloat:
    def test_worked_ss_network_floats(self):
        # A(5); B(3) SS+2 after A. Finish = max(5, 5) = 5.
        d = schedule([
            Activity(id="A", name="a", duration=5),
            Activity(id="B", name="b", duration=3, relationships=[rel("A", RT.SS, 2)]),
        ])
        assert d["A"].is_critical and d["B"].is_critical
        assert d["A"].total_float == 0 and d["B"].total_float == 0

    def test_ss_predecessor_of_critical_work_is_start_critical(self):
        # Under SS, A's *start* drives B; A cannot slip its start without
        # pushing B, so A is critical even though its finish constrains nobody.
        d = schedule([
            Activity(id="A", name="a", duration=1),
            Activity(id="B", name="b", duration=10, relationships=[rel("A", RT.SS)]),
        ])
        assert d["A"].is_critical and d["B"].is_critical

    def test_lf_capped_at_project_finish(self):
        # A(10) with a short SS successor: B's LS(9) + A's duration(10) would
        # put A's LF at 19 — past the project finish of 10. The cap keeps every
        # LF inside the project (ADR-0011 records why this is correct).
        d = schedule([
            Activity(id="A", name="a", duration=10),
            Activity(id="B", name="b", duration=1, relationships=[rel("A", RT.SS)]),
        ])
        assert d["A"].LF == 10 and d["A"].is_critical
        assert d["B"].total_float == 9

    def test_fs_chain_all_critical(self):
        d = schedule([
            Activity(id="A", name="a", duration=2),
            Activity(id="B", name="b", duration=3, relationships=[rel("A")]),
            Activity(id="C", name="c", duration=4, relationships=[rel("B")]),
        ])
        assert all(d[x].is_critical for x in "ABC")
        assert d["C"].EF == 9

    def test_free_float_respects_relationship_type(self):
        # A(2) and B(5) both FS into C. A has free float 3; B none.
        d = schedule([
            Activity(id="A", name="a", duration=2),
            Activity(id="B", name="b", duration=5),
            Activity(id="C", name="c", duration=1,
                     relationships=[rel("A"), rel("B")]),
        ])
        assert d["A"].free_float == 3 and d["B"].free_float == 0


class TestLevelOfEffort:
    def test_loe_spans_its_predecessors(self):
        d = schedule([
            Activity(id="A", name="a", duration=2),
            Activity(id="B", name="b", duration=3, relationships=[rel("A")]),
            Activity(id="PM", name="pm", duration=1,
                     type=ActivityType.LEVEL_OF_EFFORT, predecessors=["A", "B"]),
        ])
        assert (d["PM"].ES, d["PM"].EF) == (0, 5)
        assert not d["PM"].is_critical

    def test_loe_never_drives(self):
        acts = {
            "A": Activity(id="A", name="a", duration=2),
            "PM": Activity(id="PM", name="pm", duration=1,
                           type=ActivityType.LEVEL_OF_EFFORT, predecessors=["A"]),
            "B": Activity(id="B", name="b", duration=1, predecessors=["PM"]),
        }
        with pytest.raises(SchedulerError, match="level-of-effort"):
            CPMScheduler(acts).schedule()

    def test_loe_without_links_schedules_as_task(self):
        d = schedule([Activity(id="PM", name="pm", duration=4,
                               type=ActivityType.LEVEL_OF_EFFORT)])
        assert (d["PM"].ES, d["PM"].EF) == (0, 4)


class TestValidation:
    def test_cycle_through_typed_relationships(self):
        acts = {
            "A": Activity(id="A", name="a", duration=1,
                          relationships=[rel("B", RT.SS)]),
            "B": Activity(id="B", name="b", duration=1,
                          relationships=[rel("A", RT.FF)]),
        }
        with pytest.raises(SchedulerError, match="Circular"):
            CPMScheduler(acts).schedule()

    def test_unknown_predecessor_in_relationship(self):
        acts = {"A": Activity(id="A", name="a", duration=1,
                              relationships=[rel("GHOST")])}
        with pytest.raises(SchedulerError, match="unknown predecessor"):
            CPMScheduler(acts).schedule()

    def test_plain_predecessors_still_work(self):
        # Backward compatibility: ids imply FS with zero lag.
        d = schedule([
            Activity(id="A", name="a", duration=2),
            Activity(id="B", name="b", duration=3, predecessors=["A"]),
        ])
        assert d["B"].ES == 2
