"""
Independent Empirical Validation Suite for Milestone 1: Project Backup & Baseline Validation.
Author: Challenger M1-2 (teamwork_preview_challenger)
Role: critic, specialist (verification-before-completion)

This test suite empirically validates:
1. Full project backup (.drp) on disk (existence, size >= 500KB, CRC32, project XML DbId, MediaPool).
2. Baseline JSON file schema, metadata, and structure.
3. Timeline count (exactly 30 timelines).
4. Frame rate distribution (timeline #25 at 30.0 fps, other 29 at 60.0 fps).
5. Start timecodes (all 30 start at 01:00:00:00, with correct frame alignment).
6. Total subtitle cue count (exactly 2,066 cues across 30 timelines, valid text & timing).
7. Pilot timeline structure ('หนีฝ่าความหนาว_Minecraft-vdo' with 45 cues, V1 gameplay, V2 reaction gifs, V3 adjustment clips).
8. Audio track structure across timelines.
9. Live DaVinci Resolve cross-validation against the active project.
"""

import json
import os
import sys
import uuid
import zipfile
import pytest

# Ensure workspace root is in sys.path
WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

BASELINE_JSON_PATH = os.path.join(
    WORKSPACE_DIR, ".agents", "teamwork", "worker_m1", "baseline_30_timelines.json"
)
EXPECTED_BACKUP_PATH = r"G:\My Drive\Projects\Katy404\2026-09-29\KT404_2026-09-29_pre_9x16_conversion_2026-10-01.drp"
EXPECTED_PROJECT_NAME = "KT404_2026-09-29"
EXPECTED_PROJECT_ID = "7c38045b-c9ae-426c-8b4c-2e2d726d88ff"
EXPECTED_TOTAL_TIMELINES = 30
EXPECTED_TOTAL_SUBTITLE_CUES = 2066
PILOT_TIMELINE_NAME = "หนีฝ่าความหนาว_Minecraft-vdo"
PILOT_EXPECTED_CUES = 45


@pytest.fixture(scope="module")
def baseline_data():
    assert os.path.exists(BASELINE_JSON_PATH), f"Baseline JSON missing at: {BASELINE_JSON_PATH}"
    with open(BASELINE_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


class TestBackupFileIntegrity:
    """Stress-test and verify the physical .drp backup file on disk."""

    def test_backup_file_exists(self):
        assert os.path.exists(EXPECTED_BACKUP_PATH), f"Backup file not found at: {EXPECTED_BACKUP_PATH}"

    def test_backup_file_size(self, baseline_data):
        size = os.path.getsize(EXPECTED_BACKUP_PATH)
        assert size >= 500_000, f"Backup size ({size} bytes) is below minimum threshold of 500KB"
        recorded_size = baseline_data["backup_verification"]["size_bytes"]
        assert size == recorded_size, f"Backup size ({size}) does not match recorded size in baseline ({recorded_size})"

    def test_backup_zip_crc32(self):
        with zipfile.ZipFile(EXPECTED_BACKUP_PATH, "r") as zf:
            corrupt = zf.testzip()
            assert corrupt is None, f"Corrupted file found in .drp archive: {corrupt}"

    def test_backup_project_xml_dbid(self):
        with zipfile.ZipFile(EXPECTED_BACKUP_PATH, "r") as zf:
            names = zf.namelist()
            assert "project.xml" in names, "project.xml not found in .drp archive"
            with zf.open("project.xml") as pxml:
                content = pxml.read().decode("utf-8", errors="replace")
                assert f'DbId="{EXPECTED_PROJECT_ID}"' in content, (
                    f"DbId {EXPECTED_PROJECT_ID} not found in project.xml header"
                )

    def test_backup_mediapool_present(self):
        with zipfile.ZipFile(EXPECTED_BACKUP_PATH, "r") as zf:
            names = zf.namelist()
            has_mp = any("MediaPool" in n for n in names)
            assert has_mp, "MediaPool structure missing from .drp archive"


class TestBaselineSchema:
    """Verify baseline JSON structure, schema, and root fields."""

    def test_top_level_keys(self, baseline_data):
        required_keys = {
            "milestone",
            "timestamp_utc",
            "project_name",
            "project_id",
            "backup_path",
            "backup_verification",
            "total_timelines",
            "timelines_summary",
            "timelines",
        }
        actual_keys = set(baseline_data.keys())
        missing = required_keys - actual_keys
        assert not missing, f"Missing required top-level keys in baseline JSON: {missing}"

    def test_project_identity(self, baseline_data):
        assert baseline_data["project_name"] == EXPECTED_PROJECT_NAME
        assert baseline_data["project_id"] == EXPECTED_PROJECT_ID

    def test_backup_verification_metadata(self, baseline_data):
        bv = baseline_data["backup_verification"]
        assert bv["exists"] is True
        assert bv["size_bytes"] >= 500_000
        assert bv["crc32_valid"] is True
        assert bv["testzip_result"] is None
        assert bv["project_id_verified"] is True
        assert bv["has_mediapool"] is True
        assert bv["total_archive_members"] > 0


class TestTimelineCountsAndProperties:
    """Verify timeline counts, uniqueness, frame rates, and timecodes."""

    def test_timeline_counts(self, baseline_data):
        assert baseline_data["total_timelines"] == EXPECTED_TOTAL_TIMELINES
        assert len(baseline_data["timelines_summary"]) == EXPECTED_TOTAL_TIMELINES
        assert len(baseline_data["timelines"]) == EXPECTED_TOTAL_TIMELINES

    def test_timeline_indices_and_uniqueness(self, baseline_data):
        indices = [t["timeline_index"] for t in baseline_data["timelines"]]
        assert sorted(indices) == list(range(1, EXPECTED_TOTAL_TIMELINES + 1)), "Timeline indices must be 1..30"

        names = [t["timeline_name"] for t in baseline_data["timelines"]]
        assert len(names) == len(set(names)), "Timeline names must be unique"
        for name in names:
            assert name and len(name.strip()) > 0, "Timeline name must not be blank"

        ids = [t["timeline_id"] for t in baseline_data["timelines"]]
        assert len(ids) == len(set(ids)), "Timeline IDs must be unique"
        for tid in ids:
            uuid_obj = uuid.UUID(tid)
            assert str(uuid_obj) == tid

    def test_framerate_distribution(self, baseline_data):
        """Verify timeline #25 ('บอสมังกร_Soul Walker-vdo') has frameRate 30.0, and other 29 have frameRate 60.0."""
        timelines = baseline_data["timelines"]

        t25 = timelines[24]  # 0-indexed index 24 corresponds to timeline_index 25
        assert t25["timeline_index"] == 25
        assert t25["timeline_name"] == "บอสมังกร_Soul Walker-vdo"
        assert t25["frame_rate"] == 30.0, f"Timeline #25 must have frame rate 30.0, got {t25['frame_rate']}"

        fps_counts = {}
        for t in timelines:
            fps = t["frame_rate"]
            fps_counts[fps] = fps_counts.get(fps, 0) + 1

        assert fps_counts == {60.0: 29, 30.0: 1}, (
            f"Expected 29 at 60.0 fps and 1 at 30.0 fps, got: {fps_counts}"
        )

        summary_fps_counts = {}
        for s in baseline_data["timelines_summary"]:
            fps = s["fps"]
            summary_fps_counts[fps] = summary_fps_counts.get(fps, 0) + 1
        assert summary_fps_counts == {60.0: 29, 30.0: 1}

    def test_start_timecode_and_frame_alignment(self, baseline_data):
        """Verify all 30 timelines start at 01:00:00:00."""
        for t in baseline_data["timelines"]:
            idx = t["timeline_index"]
            name = t["timeline_name"]
            fps = t["frame_rate"]
            start_tc = t["start_tc"]
            start_frame = t["start_frame"]
            end_frame = t["end_frame"]
            dur_frames = t["duration_frames"]

            assert start_tc == "01:00:00:00", f"Timeline #{idx} ({name}) start_tc is {start_tc}, expected 01:00:00:00"

            expected_start_frame = int(3600 * fps)
            assert start_frame == expected_start_frame, (
                f"Timeline #{idx} ({name}) start_frame {start_frame} != expected {expected_start_frame} for {fps} fps"
            )

            assert dur_frames == end_frame - start_frame, (
                f"Timeline #{idx} duration_frames {dur_frames} != end_frame - start_frame ({end_frame - start_frame})"
            )
            assert dur_frames > 0, f"Timeline #{idx} duration must be positive"

    def test_resolution_and_aspect_ratio(self, baseline_data):
        """Verify all 30 baseline timelines are horizontal 16:9 (1920x1080)."""
        for t in baseline_data["timelines"]:
            assert t["resolution_width"] == 1920
            assert t["resolution_height"] == 1080
            assert t["is_16_by_9"] is True


class TestSubtitleIntegrity:
    """Stress-test and verify subtitle cues across all 30 timelines."""

    def test_total_subtitle_cue_count(self, baseline_data):
        """Verify total subtitle cue count matches worker claim (2,066 cues across 30 timelines)."""
        summary_total = sum(s["subtitle_cues"] for s in baseline_data["timelines_summary"])
        assert summary_total == EXPECTED_TOTAL_SUBTITLE_CUES, (
            f"Summary total cues ({summary_total}) != {EXPECTED_TOTAL_SUBTITLE_CUES}"
        )

        detail_counts_sum = sum(t["subtitle_track"]["cue_count"] for t in baseline_data["timelines"])
        assert detail_counts_sum == EXPECTED_TOTAL_SUBTITLE_CUES, (
            f"Detail cue_count sum ({detail_counts_sum}) != {EXPECTED_TOTAL_SUBTITLE_CUES}"
        )

        cues_array_sum = sum(len(t["subtitle_track"]["cues"]) for t in baseline_data["timelines"])
        assert cues_array_sum == EXPECTED_TOTAL_SUBTITLE_CUES, (
            f"Cues array sum ({cues_array_sum}) != {EXPECTED_TOTAL_SUBTITLE_CUES}"
        )

    def test_subtitle_cues_temporal_and_text_validity(self, baseline_data):
        """Every single cue out of 2,066 must have valid frames, duration, and clean text."""
        total_checked = 0

        for t in baseline_data["timelines"]:
            tl_idx = t["timeline_index"]
            tl_start = t["start_frame"]
            tl_end = t["end_frame"]
            cues = t["subtitle_track"]["cues"]

            for i, cue in enumerate(cues):
                total_checked += 1
                assert cue["cue_index"] == i + 1
                c_start = cue["start_frame"]
                c_end = cue["end_frame"]
                c_dur = cue["duration_frames"]
                text = cue["text"]

                # Timing consistency
                assert c_start < c_end, f"Cue {cue['cue_index']} start >= end ({c_start} >= {c_end})"
                assert c_dur == c_end - c_start, f"Cue duration mismatch: {c_dur} != {c_end - c_start}"
                assert c_start >= tl_start, f"Cue starts before timeline: {c_start} < {tl_start}"
                assert c_end <= tl_end + 120, f"Cue extends unreasonably beyond timeline end: {c_end} > {tl_end}"

                # Text validity: non-empty string
                assert text is not None and len(text.strip()) > 0, f"Blank subtitle cue found at {cue}"
                
                # Check for unexpected replacement characters:
                # Timeline 20 cue 31 has literal '\ufffd' in the live DaVinci Resolve project database itself.
                if tl_idx == 20 and cue["cue_index"] == 31:
                    assert text == "\ufffd", f"Expected live project artifact '\\ufffd', got: {text}"
                else:
                    assert "\ufffd" not in text, f"Unexpected replacement character in timeline {tl_idx} cue {cue['cue_index']}: {text}"

        assert total_checked == EXPECTED_TOTAL_SUBTITLE_CUES


class TestPilotTimelineDetails:
    """Stress-test and inspect the pilot timeline 'หนีฝ่าความหนาว_Minecraft-vdo'."""

    @pytest.fixture
    def pilot_timeline(self, baseline_data):
        matching = [t for t in baseline_data["timelines"] if t["timeline_name"] == PILOT_TIMELINE_NAME]
        assert len(matching) == 1, f"Expected exactly 1 pilot timeline, found {len(matching)}"
        return matching[0]

    def test_pilot_subtitle_cues_count(self, pilot_timeline):
        """Check pilot timeline has exactly 45 subtitle cues."""
        assert pilot_timeline["subtitle_track"]["cue_count"] == PILOT_EXPECTED_CUES
        assert len(pilot_timeline["subtitle_track"]["cues"]) == PILOT_EXPECTED_CUES

    def test_pilot_video_tracks_structure(self, pilot_timeline):
        """Verify pilot timeline has V1 gameplay, V2 reaction gifs, V3 adjustment clips."""
        vtracks = pilot_timeline["video_tracks"]
        assert len(vtracks) >= 3, f"Expected at least 3 video tracks, found {len(vtracks)}"

        track_map = {tr["track_index"]: tr for tr in vtracks}
        assert 1 in track_map, "Track V1 missing"
        assert 2 in track_map, "Track V2 missing"
        assert 3 in track_map, "Track V3 missing"

        v1 = track_map[1]
        v2 = track_map[2]
        v3 = track_map[3]

        assert v1["item_count"] >= 1, "V1 has 0 items"
        assert v2["item_count"] >= 1, "V2 has 0 items"
        assert v3["item_count"] >= 1, "V3 has 0 items"

        # Check V1 contains gameplay media
        v1_names = [it["name"] for it in v1["items"]]
        assert any("Minecraft" in n or ".mp4" in n for n in v1_names), f"V1 items unexpected: {v1_names}"

        # Check V2 contains reaction GIF/asset
        v2_names = [it["name"] for it in v2["items"]]
        assert any(".gif" in n or "Cat" in n for n in v2_names), f"V2 items unexpected: {v2_names}"

        # Check V3 contains Adjustment Clips with Fusion comps
        v3_items = v3["items"]
        assert len(v3_items) == 3, f"Expected 3 adjustment clips in pilot timeline V3, got {len(v3_items)}"
        for item in v3_items:
            assert item.get("is_adjustment_clip") is True, f"Item {item['name']} not flagged as adjustment clip"
            fusion_info = item.get("fusion_comp", {})
            assert fusion_info.get("comp_count", 0) >= 1, f"Item {item['name']} has no Fusion compositions"
            tools = fusion_info.get("tools", [])
            tool_names = [t.get("name") for t in tools]
            assert "Transform1" in tool_names, f"Adjustment clip missing Transform1 tool: {tools}"

    def test_pilot_audio_tracks(self, pilot_timeline):
        """Verify pilot timeline audio track structure."""
        atracks = pilot_timeline["audio_tracks"]
        assert len(atracks) >= 3, f"Expected at least 3 audio tracks, got {len(atracks)}"
        track_map = {tr["track_index"]: tr for tr in atracks}
        assert 1 in track_map, "Track A1 missing"
        assert 2 in track_map, "Track A2 missing"
        assert 3 in track_map, "Track A3 missing"

        assert track_map[1]["track_name"] == "Original stream audio"
        assert track_map[2]["track_name"] == "SFX"
        assert track_map[3]["track_name"] == "BGM"


class TestAllTimelinesTrackStructure:
    """Stress-test track structure across all 30 baseline timelines."""

    def test_all_timelines_have_video_and_audio_tracks(self, baseline_data):
        for t in baseline_data["timelines"]:
            idx = t["timeline_index"]
            name = t["timeline_name"]

            vtracks = t["video_tracks"]
            atracks = t["audio_tracks"]

            assert len(vtracks) >= 3, f"Timeline #{idx} ({name}) has {len(vtracks)} video tracks (expected >= 3)"
            assert len(atracks) >= 3, f"Timeline #{idx} ({name}) has {len(atracks)} audio tracks (expected >= 3)"

            v_indices = {tr["track_index"] for tr in vtracks}
            a_indices = {tr["track_index"] for tr in atracks}

            assert {1, 2, 3}.issubset(v_indices), f"Timeline #{idx} video tracks missing 1, 2, or 3: {v_indices}"
            assert {1, 2, 3}.issubset(a_indices), f"Timeline #{idx} audio tracks missing 1, 2, or 3: {a_indices}"


class TestLiveResolveCrossValidation:
    """Empirical cross-validation against the live DaVinci Resolve instance."""

    def test_live_resolve_matching(self, baseline_data):
        from scripts.enrichment_assets import get_resolve
        r = get_resolve()
        assert r is not None, "Could not connect to DaVinci Resolve API"

        pm = r.GetProjectManager()
        project = pm.GetCurrentProject()
        assert project is not None, "No active project in DaVinci Resolve"
        assert project.GetName() == EXPECTED_PROJECT_NAME
        assert project.GetUniqueId() == EXPECTED_PROJECT_ID

        live_timeline_count = project.GetTimelineCount()
        assert live_timeline_count == EXPECTED_TOTAL_TIMELINES, (
            f"Live Resolve timeline count ({live_timeline_count}) != baseline ({EXPECTED_TOTAL_TIMELINES})"
        )

        for i in range(1, live_timeline_count + 1):
            tl = project.GetTimelineByIndex(i)
            tl_name = tl.GetName()
            tl_id = tl.GetUniqueId()
            tl_fps = float(tl.GetSetting("timelineFrameRate"))

            base_tl = baseline_data["timelines"][i - 1]
            assert base_tl["timeline_index"] == i
            assert base_tl["timeline_name"] == tl_name, (
                f"Timeline index {i} name mismatch: live '{tl_name}' != base '{base_tl['timeline_name']}'"
            )
            assert base_tl["timeline_id"] == tl_id, (
                f"Timeline index {i} ID mismatch: live '{tl_id}' != base '{base_tl['timeline_id']}'"
            )
            assert base_tl["frame_rate"] == tl_fps, (
                f"Timeline index {i} FPS mismatch: live {tl_fps} != base {base_tl['frame_rate']}"
            )
