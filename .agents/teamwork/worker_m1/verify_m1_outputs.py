"""Independent Verification Script for Milestone 1 Deliverables."""

import json
import os
import sys
import zipfile

BACKUP_PATH = r"G:\My Drive\Projects\Katy404\2026-09-29\KT404_2026-09-29_pre_9x16_conversion_2026-10-01.drp"
BASELINE_PATH = r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\worker_m1\baseline_30_timelines.json"
EXPECTED_DBID = "7c38045b-c9ae-426c-8b4c-2e2d726d88ff"

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def verify_backup():
    print("=== 1. Verifying Backup File ===")
    assert os.path.exists(BACKUP_PATH), f"Backup file missing: {BACKUP_PATH}"
    size = os.path.getsize(BACKUP_PATH)
    print(f"File exists: {BACKUP_PATH}")
    print(f"File size: {size:,} bytes")
    assert size > 500_000, f"File size too small: {size}"

    assert zipfile.is_zipfile(BACKUP_PATH), "Not a valid zip archive"
    with zipfile.ZipFile(BACKUP_PATH, "r") as z:
        bad = z.testzip()
        assert bad is None, f"CRC32 error on {bad}"
        print("CRC32 integrity: PASS")

        names = z.namelist()
        assert "project.xml" in names, "Missing project.xml"
        header = z.read("project.xml")[:2000].decode("utf-8", errors="ignore")
        assert EXPECTED_DBID in header, f"DbId mismatch in project.xml: {EXPECTED_DBID}"
        print(f"DbId verified in project.xml: {EXPECTED_DBID}")

        has_mp = any("MediaPool" in n for n in names)
        assert has_mp, "Missing MediaPool in zip"
        print(f"Total archive members: {len(names)}")
    print("Backup verification: PASS")


def verify_baseline():
    print("\n=== 2. Verifying Baseline JSON ===")
    assert os.path.exists(BASELINE_PATH), f"Baseline JSON missing: {BASELINE_PATH}"
    with open(BASELINE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["project_name"] == "KT404_2026-09-29"
    assert data["project_id"] == EXPECTED_DBID
    assert data["total_timelines"] == 30, f"Expected 30 timelines, got {data['total_timelines']}"
    assert len(data["timelines"]) == 30, f"Expected 30 timeline records, got {len(data['timelines'])}"

    fps_counts = {}
    total_cues = 0

    for i, tl in enumerate(data["timelines"]):
        idx = tl["timeline_index"]
        name = tl["timeline_name"]
        fps = tl["frame_rate"]
        fps_counts[fps] = fps_counts.get(fps, 0) + 1
        dur_f = tl["duration_frames"]
        res_w = tl["resolution_width"]
        res_h = tl["resolution_height"]
        is_16_9 = tl["is_16_by_9"]

        assert idx == i + 1, f"Index mismatch at {i}: {idx}"
        assert dur_f > 0, f"Duration 0 in timeline {name}"
        assert res_w == 1920 and res_h == 1080 and is_16_9, f"Timeline {name} is not 1920x1080 16:9"

        # Tracks
        v_count = tl["track_counts"]["video"]
        a_count = tl["track_counts"]["audio"]
        sub_count = tl["track_counts"]["subtitle"]
        assert v_count >= 2, f"Video track count < 2 in {name}"
        assert a_count >= 3, f"Audio track count < 3 in {name}"
        assert sub_count == 1, f"Subtitle track count != 1 in {name}"

        # Subtitles
        sub_cues = tl["subtitle_track"]["cue_count"]
        assert sub_cues > 0, f"0 subtitle cues in {name}"
        assert len(tl["subtitle_track"]["cues"]) == sub_cues
        total_cues += sub_cues

        # Audio
        for a_track in tl["audio_tracks"]:
            assert a_track["track_type"] in ["mono", "stereo"], f"Invalid audio type in {name}"

        # Video
        for v_track in tl["video_tracks"]:
            assert v_track["track_index"] >= 1

    print(f"Total timelines verified: {len(data['timelines'])}")
    print(f"Timeline FPS distribution: {fps_counts} (Expected: {{60.0: 29, 30.0: 1}})")
    assert fps_counts.get(60.0) == 29, "Expected exactly 29 60.0 fps timelines"
    assert fps_counts.get(30.0) == 1, "Expected exactly 1 30.0 fps timeline"
    print(f"Total subtitle cues across 30 timelines: {total_cues}")
    print("Baseline verification: PASS")


if __name__ == "__main__":
    verify_backup()
    verify_baseline()
    print("\nALL MILESTONE 1 DELIVERABLES FULLY VERIFIED!")
