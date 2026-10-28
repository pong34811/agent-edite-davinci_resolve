"""Pure-logic tests for scripts/delete_archived_timelines.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import delete_archived_timelines as d  # noqa: E402


def test_main_name():
    assert d.main_name("ช็อตฮา  โอ้ย-vdo_archived_v01") == "ช็อตฮา  โอ้ย-vdo"
    assert d.main_name("clip_archived_v12") == "clip"
    assert d.main_name("clip") is None
    assert d.main_name("clip_archived") is None


def test_plan_keeps_orphans():
    pairs, orphans = d.plan(["a", "a_archived_v01", "b_archived_v01", "c"])
    assert pairs == [("a_archived_v01", "a")]
    assert orphans == ["b_archived_v01"]
