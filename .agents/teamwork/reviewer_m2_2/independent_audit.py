"""
Independent Audit & Adversarial Review Script
Reviewer 2: reviewer_m2_2
"""
import sys
import os
import json
import time
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules')

try:
    import DaVinciResolveScript as dvr
except ImportError as e:
    print(f"Error importing DaVinciResolveScript: {e}")
    sys.exit(2)

def run_audit():
    audit_report = {
        "timestamp": datetime.now().isoformat(),
        "resolve_connected": False,
        "active_project": {},
        "timelines_audit": [],
        "media_pool_audit": {},
        "source_files_audit": {},
        "adversarial_findings": [],
        "gate_checks": {}
    }

    print("=== Reviewer 2 Independent Adversarial Audit ===")

    # 1. Connect to Resolve
    resolve = dvr.scriptapp('Resolve')
    if not resolve:
        print("[FAIL] Could not connect to Resolve")
        audit_report["adversarial_findings"].append("Could not connect to DaVinci Resolve")
        return audit_report

    audit_report["resolve_connected"] = True
    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    if not proj:
        print("[FAIL] No active project in Resolve")
        audit_report["adversarial_findings"].append("No active project open in Resolve")
        return audit_report

    proj_name = proj.GetName()
    proj_id = proj.GetUniqueId()
    tl_count = proj.GetTimelineCount()
    tl_fps = proj.GetSetting('timelineFrameRate')
    play_fps = proj.GetSetting('timelinePlaybackFrameRate')

    audit_report["active_project"] = {
        "name": proj_name,
        "unique_id": proj_id,
        "timeline_count": tl_count,
        "timeline_fps": tl_fps,
        "playback_fps": play_fps
    }

    print(f"Connected to Project: '{proj_name}' (ID: {proj_id})")
    print(f"Total Timelines: {tl_count}")
    print(f"Timeline FPS: {tl_fps}, Playback FPS: {play_fps}")

    # Check project name
    if proj_name != "tygarina_2026-09-30":
        audit_report["adversarial_findings"].append(f"Unexpected active project name: {proj_name}")

    # 2. Inspect all timelines in project
    expected_timelines = {
        "Highlight_Gaming_REPO_Jumpscare": {
            "category": "Gaming",
            "source_file": "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4",
            "exp_start_s": 6720.0,
            "exp_end_s": 6785.0,
            "exp_dur_s": 65.0,
            "exp_start_f": 403200,
            "exp_end_f": 407100,
            "exp_dur_f": 3900
        },
        "Highlight_Gaming_Climbing_Clutch": {
            "category": "Gaming",
            "source_file": "ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4",
            "exp_start_s": 5855.0,
            "exp_end_s": 5915.0,
            "exp_dur_s": 60.0,
            "exp_start_f": 351300,
            "exp_end_f": 354900,
            "exp_dur_f": 3600
        },
        "Highlight_Gaming_Ib_Horror": {
            "category": "Gaming",
            "source_file": "IB - สำรวจโลกภาพวาด P1.mp4",
            "exp_start_s": 4475.0,
            "exp_end_s": 4530.0,
            "exp_dur_s": 55.0,
            "exp_start_f": 268500,
            "exp_end_f": 271800,
            "exp_dur_f": 3300
        },
        "Highlight_Fun_DnD_Bard": {
            "category": "Fun",
            "source_file": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4",
            "exp_start_s": 980.0,
            "exp_end_s": 1035.0,
            "exp_dur_s": 55.0,
            "exp_start_f": 58800,
            "exp_end_f": 62100,
            "exp_dur_f": 3300
        },
        "Highlight_Meme_GarticPhone_Art": {
            "category": "Meme",
            "source_file": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4",
            "exp_start_s": 2510.0,
            "exp_end_s": 2575.0,
            "exp_dur_s": 65.0,
            "exp_start_f": 150600,
            "exp_end_f": 154500,
            "exp_dur_f": 3900
        },
        "Highlight_Meme_FreeTalk_Tiger": {
            "category": "Meme",
            "source_file": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4",
            "exp_start_s": 2235.0,
            "exp_end_s": 2295.0,
            "exp_dur_s": 60.0,
            "exp_start_f": 134100,
            "exp_end_f": 137700,
            "exp_dur_f": 3600
        },
        "Highlight_Fun_Overcooked_KitchenFire": {
            "category": "Fun/Gaming",
            "source_file": "เมื่อไทกะคือความชิบหายในครัว!.mp4",
            "exp_start_s": 7640.0,
            "exp_end_s": 7705.0,
            "exp_dur_s": 65.0,
            "exp_start_f": 458400,
            "exp_end_f": 462300,
            "exp_dur_f": 3900
        }
    }

    found_timelines = {}
    for i in range(1, tl_count + 1):
        tl = proj.GetTimelineByIndex(i)
        t_name = tl.GetName()
        t_id = tl.GetUniqueId()
        found_timelines[t_name] = {
            "index": i,
            "timeline_obj": tl,
            "id": t_id
        }

    print(f"\nFound {len(found_timelines)} timelines in project:")
    for name, info in found_timelines.items():
        print(f"  [{info['index']}] {name} (ID: {info['id']})")

    # Audit each expected timeline
    for exp_name, exp_data in expected_timelines.items():
        print(f"\n--- Auditing: {exp_name} ---")
        if exp_name not in found_timelines:
            print(f"[FAIL] Timeline {exp_name} NOT found in Resolve!")
            audit_report["adversarial_findings"].append(f"Missing timeline: {exp_name}")
            continue

        tl_info = found_timelines[exp_name]
        tl = tl_info["timeline_obj"]

        # Set as current timeline to test API response & track data
        proj.SetCurrentTimeline(tl)
        cur_tl = proj.GetCurrentTimeline()
        cur_name = cur_tl.GetName() if cur_tl else None
        print(f"Switched current timeline to: {cur_name}")

        start_f = tl.GetStartFrame()
        end_f = tl.GetEndFrame()
        dur_f = end_f - start_f
        dur_s = dur_f / 60.0

        v_tracks = tl.GetTrackCount("video")
        a_tracks = tl.GetTrackCount("audio")
        sub_tracks = tl.GetTrackCount("subtitle")

        print(f"Timeline Start Frame: {start_f}, End Frame: {end_f}, Duration: {dur_f} frames ({dur_s:.2f}s)")
        print(f"Tracks: Video={v_tracks}, Audio={a_tracks}, Subtitle={sub_tracks}")

        # Check video items
        v_items = tl.GetItemListInTrack("video", 1) or []
        a_items = tl.GetItemListInTrack("audio", 1) or []

        v_audit = []
        for vi in v_items:
            mpi = vi.GetMediaPoolItem()
            mpi_path = mpi.GetClipProperty("File Path") if mpi else None
            vi_data = {
                "name": vi.GetName(),
                "start": vi.GetStart(),
                "end": vi.GetEnd(),
                "duration": vi.GetDuration(),
                "source_start": vi.GetSourceStartFrame(),
                "source_end": vi.GetSourceEndFrame(),
                "has_media_pool_item": (mpi is not None),
                "media_pool_item_path": mpi_path
            }
            v_audit.append(vi_data)

        a_audit = []
        for ai in a_items:
            mpi = ai.GetMediaPoolItem()
            mpi_path = mpi.GetClipProperty("File Path") if mpi else None
            ai_data = {
                "name": ai.GetName(),
                "start": ai.GetStart(),
                "end": ai.GetEnd(),
                "duration": ai.GetDuration(),
                "source_start": ai.GetSourceStartFrame(),
                "source_end": ai.GetSourceEndFrame(),
                "has_media_pool_item": (mpi is not None),
                "media_pool_item_path": mpi_path
            }
            a_audit.append(ai_data)

        # Integrity checks
        checks = {
            "exists": True,
            "duration_exact_frames": (dur_f == exp_data["exp_dur_f"]),
            "duration_in_bounds": (30.0 <= dur_s <= 180.0),
            "video_track_count_ok": (v_tracks >= 1),
            "audio_track_count_ok": (a_tracks >= 1),
            "single_video_item": (len(v_items) == 1),
            "single_audio_item": (len(a_items) == 1),
            "video_item_matches_source": (len(v_items) == 1 and v_items[0].GetName() == exp_data["source_file"]),
            "video_source_start_match": (len(v_items) == 1 and v_items[0].GetSourceStartFrame() == exp_data["exp_start_f"]),
            "video_source_end_match": (len(v_items) == 1 and v_items[0].GetSourceEndFrame() == exp_data["exp_end_f"]),
            "video_record_placement_zero": (len(v_items) == 1 and v_items[0].GetStart() == start_f),
            "media_pool_item_valid": (len(v_items) == 1 and v_items[0].GetMediaPoolItem() is not None)
        }

        for check_name, check_val in checks.items():
            status_str = "PASS" if check_val else "FAIL"
            if not check_val:
                print(f"  [CHECK FAIL] {check_name}: {check_val}")
                audit_report["adversarial_findings"].append(f"{exp_name} failed check: {check_name}")
            else:
                print(f"  [CHECK PASS] {check_name}")

        audit_entry = {
            "name": exp_name,
            "expected": exp_data,
            "actual": {
                "start_frame": start_f,
                "end_frame": end_f,
                "duration_frames": dur_f,
                "duration_seconds": dur_s,
                "video_tracks": v_tracks,
                "audio_tracks": a_tracks,
                "video_items": v_audit,
                "audio_items": a_audit
            },
            "checks": checks,
            "passed": all(checks.values())
        }
        audit_report["timelines_audit"].append(audit_entry)

    # 3. Non-Destructive Invariant Check on Source Media
    print("\n=== Auditing Source Directory: C:\\Users\\warit\\SynologyDrive\\Tygarina\\2026-09-30 ===")
    media_dir = r"C:\Users\warit\SynologyDrive\Tygarina\2026-09-30"
    all_entries = os.listdir(media_dir)
    mp4_files = [f for f in all_entries if f.endswith(".mp4")]
    non_mp4_files = [f for f in all_entries if not f.endswith(".mp4")]

    print(f"Total directory entries: {len(all_entries)}")
    print(f"Total .mp4 video files: {len(mp4_files)} (Expected: 32)")
    print(f"Non-.mp4 files/directories: {non_mp4_files}")

    file_stats = []
    total_bytes = 0
    today_str = datetime.now().strftime("%Y-%m-%d")

    # Check if modified during or after prompt launch (2026-10-02T02:21:27Z / 09:21:27 local)
    prompt_launch_time = datetime(2026, 10, 2, 9, 21, 27)
    modified_during_run = []
    for f in mp4_files:
        fpath = os.path.join(media_dir, f)
        stat = os.stat(fpath)
        mtime = datetime.fromtimestamp(stat.st_mtime)
        ctime = datetime.fromtimestamp(stat.st_ctime)
        size = stat.st_size
        total_bytes += size

        if mtime >= prompt_launch_time:
            modified_during_run.append((f, mtime.isoformat()))

        file_stats.append({
            "name": f,
            "size_bytes": size,
            "mtime": mtime.isoformat(),
            "ctime": ctime.isoformat()
        })

    total_gib = total_bytes / (1024 ** 3)
    print(f"Total Size: {total_bytes} bytes ({total_gib:.4f} GiB)")
    print(f"Files modified after prompt launch (09:21:27): {len(modified_during_run)}")
    if modified_during_run:
        print(f"[ALERT] Files modified during run: {modified_during_run}")
        for mf in modified_during_run:
            audit_report["adversarial_findings"].append(f"Source file modified during run: {mf[0]} at {mf[1]}")

    audit_report["source_files_audit"] = {
        "directory": media_dir,
        "entry_count": len(all_entries),
        "mp4_count": len(mp4_files),
        "non_mp4_entries": non_mp4_files,
        "total_bytes": total_bytes,
        "total_gib": round(total_gib, 4),
        "modified_during_run_count": len(modified_during_run),
        "modified_during_run": modified_during_run,
        "is_intact": (len(mp4_files) == 32 and len(non_mp4_files) == 0 and len(modified_during_run) == 0)
    }

    # 4. Gate Checks Summary
    all_tls_ok = all(t["passed"] for t in audit_report["timelines_audit"]) if audit_report["timelines_audit"] else False
    has_7_timelines = (len(audit_report["timelines_audit"]) == 7 and tl_count == 7)
    source_intact = audit_report["source_files_audit"]["is_intact"]
    categories = set(t["expected"]["category"] for t in audit_report["timelines_audit"])
    has_gaming = any("Gaming" in c for c in categories)
    has_fun = any("Fun" in c for c in categories)
    has_meme = any("Meme" in c for c in categories)
    categories_balanced = (has_gaming and has_fun and has_meme)

    audit_report["gate_checks"] = {
        "resolve_connected": audit_report["resolve_connected"],
        "correct_project": (proj_name == "tygarina_2026-09-30"),
        "timeline_count_is_7": has_7_timelines,
        "all_timelines_conforming": all_tls_ok,
        "durations_within_30s_180s": all(t["checks"]["duration_in_bounds"] for t in audit_report["timelines_audit"]),
        "source_media_non_destructive_preserved": source_intact,
        "categories_covered_gaming_fun_meme": categories_balanced,
        "no_adversarial_findings": (len(audit_report["adversarial_findings"]) == 0)
    }

    print("\n=== Final Gate Evaluation ===")
    for g, val in audit_report["gate_checks"].items():
        print(f"  {g}: {'PASS' if val else 'FAIL'}")

    final_verdict = "APPROVE" if all(audit_report["gate_checks"].values()) else "REQUEST_CHANGES"
    audit_report["final_verdict"] = final_verdict
    print(f"\nFinal Verdict: {final_verdict}")

    # Write audit JSON
    out_file = r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\reviewer_m2_2\audit_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(audit_report, f, ensure_ascii=False, indent=2)
    print(f"Saved independent audit results to {out_file}")

    return audit_report

if __name__ == "__main__":
    run_audit()
