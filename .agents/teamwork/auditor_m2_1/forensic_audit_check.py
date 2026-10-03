import os
import sys
import json
import time
from datetime import datetime, timezone

# Ensure utf-8 output
sys.stdout.reconfigure(encoding='utf-8')

# Resolve Scripting Module
sys.path.append(r'C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules')
import DaVinciResolveScript as dvr

EXPECTED_HIGHLIGHTS = {
    "Highlight_Gaming_REPO_Jumpscare": {
        "id": "H1",
        "category": "Gaming",
        "source_file": "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4",
        "start_sec": 6720.0,
        "end_sec": 6785.0,
        "duration_sec": 65.0,
        "start_frame": 403200,
        "end_frame": 407100,
        "duration_frames": 3900
    },
    "Highlight_Gaming_Climbing_Clutch": {
        "id": "H2",
        "category": "Gaming",
        "source_file": "ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4",
        "start_sec": 5855.0,
        "end_sec": 5915.0,
        "duration_sec": 60.0,
        "start_frame": 351300,
        "end_frame": 354900,
        "duration_frames": 3600
    },
    "Highlight_Gaming_Ib_Horror": {
        "id": "H3",
        "category": "Gaming",
        "source_file": "IB - สำรวจโลกภาพวาด P1.mp4",
        "start_sec": 4475.0,
        "end_sec": 4530.0,
        "duration_sec": 55.0,
        "start_frame": 268500,
        "end_frame": 271800,
        "duration_frames": 3300
    },
    "Highlight_Fun_DnD_Bard": {
        "id": "H4",
        "category": "Fun",
        "source_file": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4",
        "start_sec": 980.0,
        "end_sec": 1035.0,
        "duration_sec": 55.0,
        "start_frame": 58800,
        "end_frame": 62100,
        "duration_frames": 3300
    },
    "Highlight_Meme_GarticPhone_Art": {
        "id": "H5",
        "category": "Meme",
        "source_file": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4",
        "start_sec": 2510.0,
        "end_sec": 2575.0,
        "duration_sec": 65.0,
        "start_frame": 150600,
        "end_frame": 154500,
        "duration_frames": 3900
    },
    "Highlight_Meme_FreeTalk_Tiger": {
        "id": "H6",
        "category": "Meme",
        "source_file": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4",
        "start_sec": 2235.0,
        "end_sec": 2295.0,
        "duration_sec": 60.0,
        "start_frame": 134100,
        "end_frame": 137700,
        "duration_frames": 3600
    },
    "Highlight_Fun_Overcooked_KitchenFire": {
        "id": "H7",
        "category": "Fun/Gaming",
        "source_file": "เมื่อไทกะคือความชิบหายในครัว!.mp4",
        "start_sec": 7640.0,
        "end_sec": 7705.0,
        "duration_sec": 65.0,
        "start_frame": 458400,
        "end_frame": 462300,
        "duration_frames": 3900
    }
}

def run_forensic_audit():
    audit = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "resolve_connectivity": {},
        "database_info": {},
        "project_info": {},
        "timeline_audits": [],
        "source_media_integrity": {},
        "violations": []
    }

    print("=== FORENSIC AUDIT: LIVE RESOLVE & MEDIA VERIFICATION ===")

    # 1. Connect to Resolve
    resolve = dvr.scriptapp('Resolve')
    if not resolve:
        err = "FATAL: Could not connect to DaVinci Resolve scripting app"
        audit["violations"].append(err)
        print(err)
        return audit

    version_info = resolve.GetVersion()
    audit["resolve_connectivity"] = {
        "product": resolve.GetProductName(),
        "version": version_info
    }
    print(f"Resolve Product: {resolve.GetProductName()}, Version: {version_info}")

    # 2. Database & Project Info
    pm = resolve.GetProjectManager()
    curr_db = pm.GetCurrentDatabase()
    audit["database_info"] = curr_db
    print(f"Current Database: {curr_db}")

    if curr_db.get("DbName") != "google drive" or curr_db.get("DbType") != "Disk":
        audit["violations"].append(f"Unexpected DB: {curr_db}, expected Disk 'google drive'")

    proj = pm.GetCurrentProject()
    if not proj:
        err = "FATAL: No project currently open in DaVinci Resolve"
        audit["violations"].append(err)
        print(err)
        return audit

    proj_name = proj.GetName()
    proj_id = proj.GetUniqueId()
    tl_count = proj.GetTimelineCount()
    fps_setting = proj.GetSetting('timelineFrameRate')
    playback_fps = proj.GetSetting('timelinePlaybackFrameRate')

    audit["project_info"] = {
        "name": proj_name,
        "id": proj_id,
        "timeline_count": tl_count,
        "timeline_fps": fps_setting,
        "timeline_playback_fps": playback_fps
    }
    print(f"Project Name: {proj_name}")
    print(f"Project ID: {proj_id}")
    print(f"Timeline Count: {tl_count}")
    print(f"Timeline FPS: {fps_setting}")

    if proj_name != "tygarina_2026-09-30":
        audit["violations"].append(f"Unexpected project name: {proj_name}")
    if tl_count != 7:
        audit["violations"].append(f"Expected 7 timelines, found {tl_count}")

    # 3. Timeline inspection
    tl_map = {}
    for idx in range(1, tl_count + 1):
        tl = proj.GetTimelineByIndex(idx)
        tl_map[tl.GetName()] = tl

    for exp_name, exp in EXPECTED_HIGHLIGHTS.items():
        print(f"\n--- Checking Timeline: {exp_name} ({exp['id']}) ---")
        if exp_name not in tl_map:
            err = f"Timeline {exp_name} missing from project"
            audit["violations"].append(err)
            print(f"FAIL: {err}")
            continue

        tl = tl_map[exp_name]
        start_f = tl.GetStartFrame()
        end_f = tl.GetEndFrame()
        duration_f = end_f - start_f
        duration_s = duration_f / 60.0

        v_tracks = tl.GetTrackCount("video")
        a_tracks = tl.GetTrackCount("audio")
        v_items = tl.GetItemListInTrack("video", 1) or []
        a_items = tl.GetItemListInTrack("audio", 1) or []

        v_item = v_items[0] if v_items else None
        a_item = a_items[0] if a_items else None

        v_name = v_item.GetName() if v_item else None
        v_dur = v_item.GetDuration() if v_item else None
        v_src_start = v_item.GetSourceStartFrame() if v_item else None
        v_src_end = v_item.GetSourceEndFrame() if v_item else None
        v_mp_item = v_item.GetMediaPoolItem() if v_item else None
        v_mp_path = v_mp_item.GetClipProperty("File Path") if v_mp_item else None

        a_name = a_item.GetName() if a_item else None
        a_src_start = a_item.GetSourceStartFrame() if a_item else None
        a_src_end = a_item.GetSourceEndFrame() if a_item else None

        # Checks
        chk_dur_match = (duration_f == exp["duration_frames"])
        chk_window = (30.0 <= duration_s <= 180.0)
        chk_v_name = (v_name == exp["source_file"])
        chk_v_src_start = (v_src_start == exp["start_frame"])
        chk_v_src_end = (v_src_end == exp["end_frame"])
        chk_v_tracks = (v_tracks >= 1)
        chk_a_tracks = (a_tracks >= 1)

        tl_record = {
            "name": exp_name,
            "id": tl.GetUniqueId(),
            "start_frame": start_f,
            "end_frame": end_f,
            "duration_frames": duration_f,
            "duration_sec": duration_s,
            "video_tracks": v_tracks,
            "audio_tracks": a_tracks,
            "video_item_name": v_name,
            "video_item_duration": v_dur,
            "video_source_start": v_src_start,
            "video_source_end": v_src_end,
            "video_file_path": v_mp_path,
            "audio_item_name": a_name,
            "audio_source_start": a_src_start,
            "audio_source_end": a_src_end,
            "checks": {
                "duration_exact_match": chk_dur_match,
                "duration_within_30s_180s": chk_window,
                "source_file_match": chk_v_name,
                "source_start_match": chk_v_src_start,
                "source_end_match": chk_v_src_end,
                "has_video_track": chk_v_tracks,
                "has_audio_track": chk_a_tracks
            }
        }
        audit["timeline_audits"].append(tl_record)

        print(f"  Duration: {duration_f}f ({duration_s}s) [Expected {exp['duration_frames']}f / {exp['duration_sec']}s] -> {'PASS' if chk_dur_match else 'FAIL'}")
        print(f"  Window (30s-180s): {'PASS' if chk_window else 'FAIL'}")
        print(f"  Source Clip: '{v_name}' -> {'PASS' if chk_v_name else 'FAIL'}")
        print(f"  Source Frames: {v_src_start} to {v_src_end} -> {'PASS' if (chk_v_src_start and chk_v_src_end) else 'FAIL'}")
        print(f"  Media Path: {v_mp_path}")

        if not chk_dur_match:
            audit["violations"].append(f"{exp_name}: duration mismatch {duration_f} != {exp['duration_frames']}")
        if not chk_window:
            audit["violations"].append(f"{exp_name}: duration {duration_s}s outside [30s, 180s]")
        if not chk_v_name:
            audit["violations"].append(f"{exp_name}: clip name mismatch '{v_name}' != '{exp['source_file']}'")
        if not (chk_v_src_start and chk_v_src_end):
            audit["violations"].append(f"{exp_name}: source frame mismatch [{v_src_start}, {v_src_end}] != [{exp['start_frame']}, {exp['end_frame']}]")

    # 4. Source Media Directory Forensic Audit
    media_dir = r"C:\Users\warit\SynologyDrive\Tygarina\2026-09-30"
    print(f"\n=== FORENSIC CHECK: SOURCE MEDIA IN {media_dir} ===")
    if not os.path.exists(media_dir):
        err = f"FATAL: Source media dir does not exist: {media_dir}"
        audit["violations"].append(err)
        print(err)
        return audit

    entries = os.listdir(media_dir)
    mp4_files = [f for f in entries if f.endswith(".mp4")]
    non_mp4_files = [f for f in entries if not f.endswith(".mp4")]

    print(f"Total entries: {len(entries)}")
    print(f"Total .mp4 files: {len(mp4_files)}")
    print(f"Non-mp4 files: {non_mp4_files}")

    total_bytes = 0
    file_details = []
    # Worker 1 was launched around 02:21Z and completed around 02:41Z on 2026-10-02
    # Check if ANY file was modified today or during worker execution
    modified_during_run = []
    
    for f in mp4_files:
        p = os.path.join(media_dir, f)
        st = os.stat(p)
        total_bytes += st.st_size
        mtime = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc)
        file_details.append({
            "name": f,
            "size": st.st_size,
            "mtime_utc": mtime.isoformat()
        })
        # Check if modified after the workflow started (2026-10-02T02:21:27Z)
        workflow_start_ts = datetime.fromisoformat("2026-10-02T02:21:27+00:00").timestamp()
        if st.st_mtime > workflow_start_ts:
            modified_during_run.append((f, mtime.isoformat()))

    audit["source_media_integrity"] = {
        "directory": media_dir,
        "total_files": len(mp4_files),
        "total_bytes": total_bytes,
        "total_gib": round(total_bytes / (1024 ** 3), 4),
        "non_mp4_files": non_mp4_files,
        "modified_recently": modified_during_run
    }

    print(f"Total Bytes: {total_bytes} ({total_bytes / (1024**3):.4f} GiB)")
    print(f"Recently modified files count: {len(modified_during_run)}")

    if len(mp4_files) != 32:
        audit["violations"].append(f"Expected 32 source video files, found {len(mp4_files)}")
    if non_mp4_files:
        audit["violations"].append(f"Unexpected files in source media dir: {non_mp4_files}")
    if modified_during_run:
        audit["violations"].append(f"Source media files modified recently: {modified_during_run}")

    # 5. On-Disk Database check
    print("\n=== CHECKING RESOLVE DISK DATABASE ON STORAGE ===")
    # Look for database directory for 'google drive'
    # Default locations or Google Drive locations
    gdrive_candidates = [
        r"G:\My Drive\Resolve Project Database",
        r"G:\My Drive\Resolve",
        r"G:\My Drive\DaVinci Resolve",
        r"C:\Users\warit\AppData\Roaming\Blackmagic Design\DaVinci Resolve\Support\Resolve Project Library"
    ]
    found_db_paths = []
    for cand in gdrive_candidates:
        if os.path.exists(cand):
            found_db_paths.append(cand)
            print(f"Found DB candidate: {cand}")

    audit["database_paths_found"] = found_db_paths

    audit["clean"] = (len(audit["violations"]) == 0)
    print(f"\n==========================================")
    print(f"AUDIT RESULT: {'CLEAN' if audit['clean'] else 'INTEGRITY VIOLATION'}")
    if audit["violations"]:
        print("VIOLATIONS DETECTED:")
        for v in audit["violations"]:
            print(f"  - {v}")
    print(f"==========================================")

    out_file = r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\auditor_m2_1\audit_raw_results.json"
    with open(out_file, "w", encoding="utf-8") as fp:
        json.dump(audit, fp, ensure_ascii=False, indent=2)
    print(f"Saved audit output to {out_file}")

    return audit

if __name__ == "__main__":
    res = run_forensic_audit()
    sys.exit(0 if res["clean"] else 1)
