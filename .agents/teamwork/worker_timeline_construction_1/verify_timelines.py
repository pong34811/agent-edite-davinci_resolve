"""
Verification script for 7 highlight timelines in DaVinci Resolve and source footage integrity.
Worker 1: worker_timeline_construction_1
"""
import sys
import os
import json
from datetime import datetime

# Blackmagic Design DaVinciResolveScript path
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules')
import DaVinciResolveScript as dvr

EXPECTED_HIGHLIGHTS = [
    {
        "id": "H1",
        "category": "Gaming",
        "timeline_name": "Highlight_Gaming_REPO_Jumpscare",
        "source_file": "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4",
        "start_sec": 6720.0,
        "end_sec": 6785.0,
        "duration_sec": 65.0,
        "start_frame": 403200,
        "end_frame": 407100,
        "duration_frames": 3900
    },
    {
        "id": "H2",
        "category": "Gaming",
        "timeline_name": "Highlight_Gaming_Climbing_Clutch",
        "source_file": "ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4",
        "start_sec": 5855.0,
        "end_sec": 5915.0,
        "duration_sec": 60.0,
        "start_frame": 351300,
        "end_frame": 354900,
        "duration_frames": 3600
    },
    {
        "id": "H3",
        "category": "Gaming",
        "timeline_name": "Highlight_Gaming_Ib_Horror",
        "source_file": "IB - สำรวจโลกภาพวาด P1.mp4",
        "start_sec": 4475.0,
        "end_sec": 4530.0,
        "duration_sec": 55.0,
        "start_frame": 268500,
        "end_frame": 271800,
        "duration_frames": 3300
    },
    {
        "id": "H4",
        "category": "Fun",
        "timeline_name": "Highlight_Fun_DnD_Bard",
        "source_file": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4",
        "start_sec": 980.0,
        "end_sec": 1035.0,
        "duration_sec": 55.0,
        "start_frame": 58800,
        "end_frame": 62100,
        "duration_frames": 3300
    },
    {
        "id": "H5",
        "category": "Meme",
        "timeline_name": "Highlight_Meme_GarticPhone_Art",
        "source_file": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4",
        "start_sec": 2510.0,
        "end_sec": 2575.0,
        "duration_sec": 65.0,
        "start_frame": 150600,
        "end_frame": 154500,
        "duration_frames": 3900
    },
    {
        "id": "H6",
        "category": "Meme",
        "timeline_name": "Highlight_Meme_FreeTalk_Tiger",
        "source_file": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4",
        "start_sec": 2235.0,
        "end_sec": 2295.0,
        "duration_sec": 60.0,
        "start_frame": 134100,
        "end_frame": 137700,
        "duration_frames": 3600
    },
    {
        "id": "H7",
        "category": "Fun/Gaming",
        "timeline_name": "Highlight_Fun_Overcooked_KitchenFire",
        "source_file": "เมื่อไทกะคือความชิบหายในครัว!.mp4",
        "start_sec": 7640.0,
        "end_sec": 7705.0,
        "duration_sec": 65.0,
        "start_frame": 458400,
        "end_frame": 462300,
        "duration_frames": 3900
    }
]

def verify_all():
    results = {
        "timestamp": datetime.now().isoformat(),
        "project": {},
        "timelines": [],
        "source_media_check": {},
        "all_checks_passed": False
    }

    resolve = dvr.scriptapp('Resolve')
    if not resolve:
        raise RuntimeError("Could not connect to DaVinci Resolve instance")

    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    if not proj:
        raise RuntimeError("No current project open")

    proj_name = proj.GetName()
    timeline_count = proj.GetTimelineCount()
    timeline_fps = proj.GetSetting('timelineFrameRate')

    results["project"] = {
        "name": proj_name,
        "timeline_count": timeline_count,
        "timeline_fps": timeline_fps
    }

    print(f"=== Project Verification ===")
    print(f"Active Project: {proj_name}")
    print(f"Timeline Count: {timeline_count}")
    print(f"Timeline FPS: {timeline_fps}")
    assert proj_name == "tygarina_2026-09-30", f"Expected project tygarina_2026-09-30, got {proj_name}"
    assert timeline_count == 7, f"Expected 7 timelines, got {timeline_count}"

    # Map timelines by name
    timeline_map = {}
    for i in range(1, timeline_count + 1):
        tl = proj.GetTimelineByIndex(i)
        timeline_map[tl.GetName()] = tl

    all_tl_passed = True
    print("\n=== Timeline Integrity Verification ===")

    for exp in EXPECTED_HIGHLIGHTS:
        tname = exp["timeline_name"]
        print(f"\nChecking [{exp['id']}] {tname}:")
        if tname not in timeline_map:
            print(f"  FAILED: Timeline {tname} not found in project")
            all_tl_passed = False
            continue

        tl = timeline_map[tname]
        start_f = tl.GetStartFrame()
        end_f = tl.GetEndFrame()
        duration_f = end_f - start_f
        duration_s = duration_f / 60.0

        v_tracks = tl.GetTrackCount("video")
        a_tracks = tl.GetTrackCount("audio")

        v_items = tl.GetItemListInTrack("video", 1)
        a_items = tl.GetItemListInTrack("audio", 1)

        v_item_name = v_items[0].GetName() if v_items else None
        v_item_start = v_items[0].GetStart() if v_items else None
        v_item_end = v_items[0].GetEnd() if v_items else None
        v_item_duration = v_items[0].GetDuration() if v_items else None
        v_source_start = v_items[0].GetSourceStartFrame() if v_items else None
        v_source_end = v_items[0].GetSourceEndFrame() if v_items else None

        a_item_name = a_items[0].GetName() if a_items else None
        a_source_start = a_items[0].GetSourceStartFrame() if a_items else None
        a_source_end = a_items[0].GetSourceEndFrame() if a_items else None

        # Check conditions
        cond_duration_match = (duration_f == exp["duration_frames"])
        cond_duration_window = (30.0 <= duration_s <= 180.0)
        cond_v_track = (v_tracks >= 1)
        cond_v_item_name = (v_item_name == exp["source_file"])
        cond_v_source_start = (v_source_start == exp["start_frame"])
        cond_v_source_end = (v_source_end == exp["end_frame"])

        tl_status = {
            "id": exp["id"],
            "name": tname,
            "category": exp["category"],
            "source_file": exp["source_file"],
            "start_frame": start_f,
            "end_frame": end_f,
            "duration_frames": duration_f,
            "duration_seconds": duration_s,
            "video_tracks": v_tracks,
            "audio_tracks": a_tracks,
            "video_item_name": v_item_name,
            "video_item_duration": v_item_duration,
            "source_start_frame": v_source_start,
            "source_end_frame": v_source_end,
            "audio_item_name": a_item_name,
            "audio_source_start_frame": a_source_start,
            "audio_source_end_frame": a_source_end,
            "checks": {
                "duration_exact_match": cond_duration_match,
                "duration_in_30s_180s_window": cond_duration_window,
                "video_track_count_ok": cond_v_track,
                "video_clip_matches_source": cond_v_item_name,
                "source_start_frame_matches": cond_v_source_start,
                "source_end_frame_matches": cond_v_source_end
            },
            "passed": all([
                cond_duration_match,
                cond_duration_window,
                cond_v_track,
                cond_v_item_name,
                cond_v_source_start,
                cond_v_source_end
            ])
        }

        print(f"  Duration: {duration_f} frames ({duration_s:.1f}s) [Expected: {exp['duration_frames']} frames, {exp['duration_sec']}s] -> {'PASS' if cond_duration_match else 'FAIL'}")
        print(f"  Duration in [30s, 180s]: {duration_s:.1f}s -> {'PASS' if cond_duration_window else 'FAIL'}")
        print(f"  Video Track 1 Clip: {v_item_name} -> {'PASS' if cond_v_item_name else 'FAIL'}")
        print(f"  Source Start Frame: {v_source_start} (Exp: {exp['start_frame']}) -> {'PASS' if cond_v_source_start else 'FAIL'}")
        print(f"  Source End Frame: {v_source_end} (Exp: {exp['end_frame']}) -> {'PASS' if cond_v_source_end else 'FAIL'}")

        if not tl_status["passed"]:
            all_tl_passed = False

        results["timelines"].append(tl_status)

    # Verify source footage files non-destructive invariant
    print("\n=== Non-Destructive Invariant Check on Source Media ===")
    media_dir = r"C:\Users\warit\SynologyDrive\Tygarina\2026-09-30"
    source_files = [f for f in os.listdir(media_dir) if f.endswith(".mp4")]
    print(f"Total .mp4 files in {media_dir}: {len(source_files)} (Expected: 32)")

    total_size = sum(os.path.getsize(os.path.join(media_dir, f)) for f in source_files)
    total_gb = total_size / (1024 ** 3)
    print(f"Total size of source files: {total_gb:.2f} GiB (Expected: ~69.50 GiB)")

    results["source_media_check"] = {
        "file_count": len(source_files),
        "total_bytes": total_size,
        "total_gib": round(total_gb, 2),
        "expected_count": 32,
        "intact": (len(source_files) == 32)
    }

    results["all_checks_passed"] = (all_tl_passed and results["source_media_check"]["intact"])
    print(f"\nOverall Verification Status: {'ALL CHECKS PASSED' if results['all_checks_passed'] else 'VERIFICATION FAILED'}")

    out_path = r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\worker_timeline_construction_1\verification_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Saved verification results to {out_path}")

    return results["all_checks_passed"]

if __name__ == "__main__":
    success = verify_all()
    sys.exit(0 if success else 1)
