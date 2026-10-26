"""
Tests for Audio Headroom & Track Integrity Verification (Lane 4).
Audits Timeline 'FirstPass v2_illustrated' in Project 'ทำไมถึงชื่อ Armigon'.
"""
from __future__ import annotations

import json
from pathlib import Path
import pytest

WORKSPACE_DIR = Path(__file__).resolve().parents[1]
BASELINE_PATH = WORKSPACE_DIR / ".agents" / "teamwork" / "explorer_survey_3" / "baseline_inventory.json"
RESULTS_PATH = WORKSPACE_DIR / ".agents" / "teamwork" / "audio_qc_worker" / "audio_qc_results.json"
NAME_V3_PATH = Path(r"D:\agent-edite-davinci_resolve\.hermes\projects\armigon-name\name_v3.mov")


@pytest.fixture(scope="module")
def audio_results():
    assert RESULTS_PATH.exists(), f"Audio QC results file missing: {RESULTS_PATH}"
    return json.loads(RESULTS_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def baseline_data():
    assert BASELINE_PATH.exists(), f"Baseline inventory file missing: {BASELINE_PATH}"
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))


class TestAudioTracksIntegrity:
    """Validate audio track configuration and clip properties on FirstPass v2_illustrated."""

    def test_project_and_timeline_identity(self, audio_results):
        assert audio_results["project_name"] == "ทำไมถึงชื่อ Armigon"
        assert audio_results["timeline_name"] == "FirstPass v2_illustrated"
        assert audio_results["timeline_id"] == "83e7cd5c-172f-4ce6-9f46-c90e6749263b"

    def test_audio_tracks_summary(self, audio_results):
        tracks = audio_results["audio_tracks_summary"]
        assert len(tracks) == 3, f"Expected 3 audio tracks, found {len(tracks)}"
        
        # Track 1: Dialogue
        t1 = tracks[0]
        assert t1["index"] == 1
        assert t1["name"] == "Dialogue"
        assert t1["enabled"] is True
        assert t1["locked"] is False
        assert t1["sub_type"] == "stereo"
        assert t1["item_count"] == 10

        # Track 2: SFX
        t2 = tracks[1]
        assert t2["index"] == 2
        assert t2["name"] == "SFX"
        assert t2["enabled"] is True
        assert t2["locked"] is False
        assert t2["sub_type"] == "stereo"
        assert t2["item_count"] == 11

        # Track 3: BGM
        t3 = tracks[2]
        assert t3["index"] == 3
        assert t3["name"] == "BGM"
        assert t3["enabled"] is True
        assert t3["locked"] is False
        assert t3["sub_type"] == "stereo"
        assert t3["item_count"] == 0

    def test_dialogue_track_items_and_headroom(self, audio_results, baseline_data):
        d_report = audio_results["track_1_dialogue"]
        assert d_report["item_count"] == 10
        assert d_report["all_online"] is True
        assert d_report["all_baseline_match"] is True
        assert d_report["no_clipping"] is True

        baseline_items = baseline_data["tracks"]["audio"][0]["items"]
        assert len(baseline_items) == 10

        for item, b_item in zip(d_report["items"], baseline_items):
            assert item["file_online"] is True
            assert item["start"] == b_item["start"]
            assert item["end"] == b_item["end"]
            assert item["duration"] == (b_item["end"] - b_item["start"])
            assert item["clipping_detected"] is False
            assert item["effective_true_peak_dbfs"] is not None
            assert item["effective_true_peak_dbfs"] < 0.0, f"Clipping on {item['name']} at frame {item['start']}"
            assert item["headroom_db"] > 0.0

    def test_sfx_track_items_and_headroom(self, audio_results, baseline_data):
        sfx_report = audio_results["track_2_sfx"]
        assert sfx_report["item_count"] == 11
        assert sfx_report["all_online"] is True
        assert sfx_report["all_baseline_match"] is True
        assert sfx_report["no_clipping"] is True

        baseline_items = baseline_data["tracks"]["audio"][1]["items"]
        assert len(baseline_items) == 11

        for item, b_item in zip(sfx_report["items"], baseline_items):
            assert item["file_online"] is True
            assert item["name"] == b_item["name"]
            assert item["start"] == b_item["start"]
            assert item["end"] == b_item["end"]
            assert item["clipping_detected"] is False
            assert item["effective_true_peak_dbfs"] is not None
            assert item["effective_true_peak_dbfs"] < 0.0, f"Clipping on SFX {item['name']}"
            assert item["headroom_db"] > 0.0

    def test_bgm_track_empty(self, audio_results):
        bgm_report = audio_results["track_3_bgm"]
        assert bgm_report["item_count"] == 0
        assert bgm_report["empty_verified"] is True

    def test_name_v3_audio_isolation(self, audio_results):
        v2_audio = audio_results["v2_name_v3_audio_isolation"]
        assert v2_audio["exists"] is True
        assert v2_audio["audio_streams_count"] == 0
        assert v2_audio["pure_video_verified"] is True
        assert len(v2_audio["streams"]) == 1
        assert v2_audio["streams"][0]["codec_type"] == "video"
