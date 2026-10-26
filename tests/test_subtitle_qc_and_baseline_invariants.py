"""
Tests for Subtitle Cue Alignment & Protected Baseline Invariants (Lane 3).
Audits Timeline 'FirstPass v2_illustrated' in Project 'ทำไมถึงชื่อ Armigon'.
"""
import json
import os
import sys
from pathlib import Path
import pytest

WORKSPACE_DIR = Path(__file__).resolve().parents[1]
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

BASELINE_PATH = WORKSPACE_DIR / ".agents" / "teamwork" / "explorer_survey_3" / "baseline_inventory.json"
PLACEMENTS_PATH = Path(r"D:\agent-edite-davinci_resolve\.hermes\projects\armigon-name\placements.json")
AUDIT_JSON_PATH = WORKSPACE_DIR / ".agents" / "teamwork" / "subtitle_qc_worker" / "audit_results.json"


@pytest.fixture(scope="module")
def baseline_data():
    assert BASELINE_PATH.exists(), f"Baseline inventory missing: {BASELINE_PATH}"
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def placements_data():
    assert PLACEMENTS_PATH.exists(), f"Placements file missing: {PLACEMENTS_PATH}"
    return json.loads(PLACEMENTS_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def audit_results():
    assert AUDIT_JSON_PATH.exists(), f"Audit results file missing: {AUDIT_JSON_PATH}"
    return json.loads(AUDIT_JSON_PATH.read_text(encoding="utf-8"))


class TestAuditResultsIntegrity:
    """Validate empirical audit results produced by Lane 3 audit script."""

    def test_audit_verdict_approved(self, audit_results):
        verdict = audit_results.get("verdict", {})
        assert verdict.get("final_status") == "APPROVED", f"Audit verdict not approved: {verdict}"
        assert verdict.get("all_protected_tracks_pass") is True
        assert verdict.get("subtitle_zero_overlap") is True
        assert verdict.get("v1_continuous_0_3063") is True
        assert verdict.get("all_10_illustrations_aligned") is True
        assert verdict.get("zero_drift") is True

    def test_protected_track_v1_main_video(self, audit_results, baseline_data):
        v1 = audit_results["protected_tracks"]["video_1_main_video"]
        assert v1["status"] == "PASS"
        assert v1["live_count"] == 10
        assert v1["baseline_count"] == 10
        assert v1["max_drift_frames"] == 0

        # Continuous 0-3063
        items = v1["items"]
        assert items[0]["start_live"] == 0
        assert items[-1]["end_live"] == 3063
        for i in range(len(items) - 1):
            assert items[i]["end_live"] == items[i + 1]["start_live"]

    def test_protected_track_a1_dialogue(self, audit_results):
        a1 = audit_results["protected_tracks"]["audio_1_dialogue"]
        assert a1["status"] == "PASS"
        assert a1["live_count"] == 10
        assert a1["baseline_count"] == 10
        assert a1["max_drift_frames"] == 0

    def test_protected_track_a2_sfx(self, audit_results):
        a2 = audit_results["protected_tracks"]["audio_2_sfx"]
        assert a2["status"] == "PASS"
        assert a2["live_count"] == 11
        assert a2["baseline_count"] == 11
        assert a2["max_drift_frames"] == 0

    def test_subtitle_track_1_invariants(self, audit_results):
        sub = audit_results["protected_tracks"]["subtitle_1"]
        assert sub["status"] == "PASS"
        assert sub["live_count"] == 52
        assert sub["baseline_count"] == 52
        assert sub["max_drift_frames"] == 0

        # Zero overlap
        overlap_check = audit_results["subtitle_overlap_check"]
        assert overlap_check["status"] == "PASS"
        assert overlap_check["overlap_count"] == 0

        # Boundary span: 9 to 3005
        items = sub["items"]
        assert items[0]["start_live"] == 9
        assert items[-1]["end_live"] == 3005

    def test_v2_illustration_alignment(self, audit_results, placements_data):
        alignments = audit_results["subtitle_cue_alignment"]
        assert len(alignments) == 10

        total_illustration_frames = 0
        for i, align in enumerate(alignments):
            assert align["status"] == "PASS", f"Illustration {i} failed alignment: {align}"
            assert align["start_aligned"] is True
            assert align["end_aligned"] is True
            assert align["dialogue_cues_covered"] >= 1
            total_illustration_frames += align["duration"]

        assert total_illustration_frames == 1794, f"Total frames {total_illustration_frames} != 1794"


class TestLiveResolveConnection:
    """Live verification against DaVinci Resolve if currently connected."""

    def test_live_resolve_audit_if_available(self):
        try:
            from scripts.resolve_common import connect_resolve
            resolve = connect_resolve()
            if not resolve:
                pytest.skip("Resolve not running or external scripting disabled")
            pm = resolve.GetProjectManager()
            proj = pm.GetCurrentProject()
            if not proj or proj.GetName() != "ทำไมถึงชื่อ Armigon":
                pytest.skip(f"Current project is '{proj.GetName() if proj else None}', not 'ทำไมถึงชื่อ Armigon'")

            # Execute the audit directly
            from scripts.scratch.audit_subtitle_alignment_and_baseline import run_audit
            res = run_audit()
            assert res["verdict"]["final_status"] == "APPROVED"
        except ImportError:
            pytest.skip("Resolve scripting module not available in test runner")
