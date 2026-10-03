"""
Comprehensive Empirical Verification & Forensic Stress Harness for Milestone M2.
Challenger 1 (challenger_m2_1)
"""
import sys
import os
import json
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules')
import DaVinciResolveScript as dvr

EXPECTED_CANDIDATES = [
    {
        "id": "H1",
        "category": "Gaming",
        "name": "Highlight_Gaming_REPO_Jumpscare",
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
        "name": "Highlight_Gaming_Climbing_Clutch",
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
        "name": "Highlight_Gaming_Ib_Horror",
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
        "name": "Highlight_Fun_DnD_Bard",
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
        "name": "Highlight_Meme_GarticPhone_Art",
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
        "name": "Highlight_Meme_FreeTalk_Tiger",
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
        "name": "Highlight_Fun_Overcooked_KitchenFire",
        "source_file": "เมื่อไทกะคือความชิบหายในครัว!.mp4",
        "start_sec": 7640.0,
        "end_sec": 7705.0,
        "duration_sec": 65.0,
        "start_frame": 458400,
        "end_frame": 462300,
        "duration_frames": 3900
    }
]

def run_stress_verification():
    report = {
        "timestamp": datetime.now().isoformat(),
        "challenger": "challenger_m2_1",
        "project": {},
        "timelines": [],
        "source_storage": {},
        "summary": {}
    }

    resolve = dvr.scriptapp('Resolve')
    if not resolve:
        raise RuntimeError("Failed to attach to DaVinci Resolve")

    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    if not proj:
        raise RuntimeError("No current project open")

    proj_name = proj.GetName()
    tl_count = proj.GetTimelineCount()
    tl_fps = float(proj.GetSetting("timelineFrameRate"))

    report["project"] = {
        "name": proj_name,
        "timeline_count": tl_count,
        "timeline_fps": tl_fps,
        "resolution": f"{proj.GetSetting('timelineResolutionWidth')}x{proj.GetSetting('timelineResolutionHeight')}"
    }

    assert proj_name == "tygarina_2026-09-30", f"Project mismatch: {proj_name}"
    assert tl_count == 7, f"Timeline count mismatch: {tl_count}"
    assert tl_fps == 60.0, f"Timeline FPS mismatch: {tl_fps}"

    # Map existing timelines
    timelines_by_name = {}
    for idx in range(1, tl_count + 1):
        tl = proj.GetTimelineByIndex(idx)
        timelines_by_name[tl.GetName()] = tl

    all_passed = True
    tl_details = []

    for cand in EXPECTED_CANDIDATES:
        c_id = cand["id"]
        c_name = cand["name"]
        
        assert c_name in timelines_by_name, f"Missing timeline: {c_name}"
        tl = timelines_by_name[c_name]

        start_f = tl.GetStartFrame()
        end_f = tl.GetEndFrame()
        duration_f = end_f - start_f
        duration_s = duration_f / 60.0

        v_tracks = tl.GetTrackCount("video")
        a_tracks = tl.GetTrackCount("audio")
        sub_tracks = tl.GetTrackCount("subtitle")

        v_items = tl.GetItemListInTrack("video", 1)
        a_items = tl.GetItemListInTrack("audio", 1)

        assert len(v_items) == 1, f"[{c_id}] Expected 1 video item, found {len(v_items)}"
        assert len(a_items) == 1, f"[{c_id}] Expected 1 audio item, found {len(a_items)}"

        v0 = v_items[0]
        a0 = a_items[0]

        v_mpi = v0.GetMediaPoolItem()
        a_mpi = a0.GetMediaPoolItem()

        assert v_mpi is not None, f"[{c_id}] Missing Video MediaPoolItem"
        assert a_mpi is not None, f"[{c_id}] Missing Audio MediaPoolItem"

        v_props = v_mpi.GetClipProperty()
        total_media_frames = int(v_props.get("Frames", 0))

        v_src_start = v0.GetSourceStartFrame()
        v_src_end = v0.GetSourceEndFrame()
        v_left_offset = v0.GetLeftOffset()
        v_right_offset = v0.GetRightOffset()
        v_duration = v0.GetDuration()

        # Empirical checks
        c_exact_duration = (duration_f == cand["duration_frames"])
        c_bounds_duration = (30.0 <= duration_s <= 180.0)
        c_frame_bounds = (1800 <= duration_f <= 10800)
        c_src_start = (v_src_start == cand["start_frame"])
        c_src_end = (v_src_end == cand["end_frame"])
        c_offsets_no_negative = (v_left_offset >= 0 and v_right_offset >= 0)
        c_offset_sum = (v_src_start + v_duration + v_right_offset == total_media_frames)
        c_av_sync = (v_src_start == a0.GetSourceStartFrame() and v_src_end == a0.GetSourceEndFrame() and v_duration == a0.GetDuration())
        c_zero_markers = (len(tl.GetMarkers()) == 0 and len(v0.GetMarkers()) == 0)
        c_zero_fusion = (v0.GetFusionCompCount() == 0)
        c_file_exists = os.path.isfile(v_props.get("File Path", ""))

        tl_pass = all([
            c_exact_duration,
            c_bounds_duration,
            c_frame_bounds,
            c_src_start,
            c_src_end,
            c_offsets_no_negative,
            c_offset_sum,
            c_av_sync,
            c_zero_markers,
            c_zero_fusion,
            c_file_exists
        ])

        if not tl_pass:
            all_passed = False

        detail = {
            "id": c_id,
            "name": c_name,
            "category": cand["category"],
            "source_file": cand["source_file"],
            "metrics": {
                "start_frame": start_f,
                "end_frame": end_f,
                "duration_frames": duration_f,
                "duration_seconds": round(duration_s, 2),
                "source_start_frame": v_src_start,
                "source_end_frame": v_src_end,
                "left_offset": v_left_offset,
                "right_offset": v_right_offset,
                "total_media_frames": total_media_frames,
                "video_tracks": v_tracks,
                "audio_tracks": a_tracks,
                "subtitle_tracks": sub_tracks
            },
            "checks": {
                "exact_duration_match": c_exact_duration,
                "duration_within_30s_180s": c_bounds_duration,
                "frame_count_within_1800_10800": c_frame_bounds,
                "source_start_frame_match": c_src_start,
                "source_end_frame_match": c_src_end,
                "no_negative_offsets": c_offsets_no_negative,
                "frame_offset_sum_equals_total_media_frames": c_offset_sum,
                "audio_video_perfect_sync": c_av_sync,
                "zero_unrequested_markers": c_zero_markers,
                "zero_unrequested_fusion_comps": c_zero_fusion,
                "source_media_file_exists": c_file_exists
            },
            "status": "PASS" if tl_pass else "FAIL"
        }
        tl_details.append(detail)

    report["timelines"] = tl_details

    # Source media integrity
    media_dir = r"C:\Users\warit\SynologyDrive\Tygarina\2026-09-30"
    files = [f for f in os.listdir(media_dir) if f.endswith(".mp4")]
    total_size = sum(os.path.getsize(os.path.join(media_dir, f)) for f in files)
    storage_intact = (len(files) == 32 and total_size == 74624842819)

    report["source_storage"] = {
        "directory": media_dir,
        "file_count": len(files),
        "total_bytes": total_size,
        "total_gib": round(total_size / (1024**3), 2),
        "intact": storage_intact
    }

    report["summary"] = {
        "total_timelines_evaluated": len(EXPECTED_CANDIDATES),
        "timelines_passed": sum(1 for t in tl_details if t["status"] == "PASS"),
        "timelines_failed": sum(1 for t in tl_details if t["status"] == "FAIL"),
        "source_storage_intact": storage_intact,
        "verdict": "APPROVE" if (all_passed and storage_intact) else "REQUEST_CHANGES"
    }

    out_json = r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\scratch\challenger_verification_report.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(json.dumps(report["summary"], indent=2))
    return report

if __name__ == "__main__":
    report = run_stress_verification()
