"""
Independent Verification and Adversarial Stress-Test Script
Reviewer 1: reviewer_m2_1
Target: Milestone M2 - DaVinci Resolve Highlight Timeline Construction
"""
import sys
import os
import json
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules')
import DaVinciResolveScript as dvr

EXPECTED_SPEC = [
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

def run_independent_review():
    review_output = {
        "timestamp": datetime.now().isoformat(),
        "resolve_connection": {},
        "project_audit": {},
        "timeline_audits": [],
        "media_integrity_audit": {},
        "adversarial_checks": {},
        "verdict": "UNKNOWN"
    }

    print("======================================================================")
    print("REVIEWER 1 INDEPENDENT AUDIT & ADVERSARIAL VERIFICATION")
    print("======================================================================")

    # 1. Connect to DaVinci Resolve
    resolve = dvr.scriptapp('Resolve')
    if not resolve:
        print("[FAIL] Could not connect to DaVinci Resolve Scripting API")
        sys.exit(1)

    version_str = resolve.GetVersionString()
    product_name = resolve.GetProductName()
    print(f"[OK] Connected to {product_name} v{version_str}")

    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    if not proj:
        print("[FAIL] No active project in Resolve")
        sys.exit(1)

    proj_name = proj.GetName()
    proj_fps = proj.GetSetting('timelineFrameRate')
    proj_playback_fps = proj.GetSetting('timelinePlaybackFrameRate')
    proj_width = proj.GetSetting('timelineResolutionWidth')
    proj_height = proj.GetSetting('timelineResolutionHeight')
    total_timelines = proj.GetTimelineCount()

    print(f"[AUDIT] Active Project Name: {proj_name}")
    print(f"[AUDIT] Project Timeline Count: {total_timelines}")
    print(f"[AUDIT] Project Timeline FPS: {proj_fps}")
    print(f"[AUDIT] Project Playback FPS: {proj_playback_fps}")
    print(f"[AUDIT] Project Resolution: {proj_width}x{proj_height}")

    review_output["resolve_connection"] = {
        "product": product_name,
        "version": version_str
    }
    review_output["project_audit"] = {
        "name": proj_name,
        "timeline_count": total_timelines,
        "timeline_fps": proj_fps,
        "playback_fps": proj_playback_fps,
        "resolution": f"{proj_width}x{proj_height}"
    }

    # Verify project invariants
    assert proj_name == "tygarina_2026-09-30", f"Unexpected project: {proj_name}"
    assert total_timelines == 7, f"Expected exactly 7 timelines, found {total_timelines}"
    assert float(proj_fps) == 60.0, f"Expected timelineFrameRate 60.0, found {proj_fps}"

    # Map timelines
    timelines_by_name = {}
    for i in range(1, total_timelines + 1):
        tl = proj.GetTimelineByIndex(i)
        timelines_by_name[tl.GetName()] = tl

    all_timelines_valid = True
    print("\n----------------------------------------------------------------------")
    print("TIMELINE INDIVIDUAL AUDIT")
    print("----------------------------------------------------------------------")

    for spec in EXPECTED_SPEC:
        tname = spec["name"]
        print(f"\nAuditing [{spec['id']}] '{tname}':")
        if tname not in timelines_by_name:
            print(f"  [CRITICAL FAIL] Timeline '{tname}' does not exist in Resolve project!")
            all_timelines_valid = False
            continue

        tl = timelines_by_name[tname]
        start_frame = tl.GetStartFrame()
        end_frame = tl.GetEndFrame()
        duration_frames = end_frame - start_frame
        duration_sec = duration_frames / 60.0

        v_tracks = tl.GetTrackCount("video")
        a_tracks = tl.GetTrackCount("audio")
        sub_tracks = tl.GetTrackCount("subtitle")

        v_items = tl.GetItemListInTrack("video", 1) or []
        a_items = tl.GetItemListInTrack("audio", 1) or []

        v_clip = v_items[0] if v_items else None
        a_clip = a_items[0] if a_items else None

        v_name = v_clip.GetName() if v_clip else None
        v_dur = v_clip.GetDuration() if v_clip else None
        v_src_start = v_clip.GetSourceStartFrame() if v_clip else None
        v_src_end = v_clip.GetSourceEndFrame() if v_clip else None
        v_rec_start = v_clip.GetStart() if v_clip else None
        v_rec_end = v_clip.GetEnd() if v_clip else None

        a_name = a_clip.GetName() if a_clip else None
        a_dur = a_clip.GetDuration() if a_clip else None
        a_src_start = a_clip.GetSourceStartFrame() if a_clip else None
        a_src_end = a_clip.GetSourceEndFrame() if a_clip else None
        a_rec_start = a_clip.GetStart() if a_clip else None
        a_rec_end = a_clip.GetEnd() if a_clip else None

        # Check conditions
        check_name_ok = (tname == spec["name"])
        check_duration_exact = (duration_frames == spec["duration_frames"])
        check_duration_window = (30.0 <= duration_sec <= 180.0)
        check_v_clip_count = (len(v_items) == 1)
        check_v_clip_source = (v_name == spec["source_file"])
        check_v_src_start = (v_src_start == spec["start_frame"])
        check_v_src_end = (v_src_end == spec["end_frame"])
        check_v_dur = (v_dur == spec["duration_frames"])

        check_a_clip_count = (len(a_items) == 1)
        check_a_clip_source = (a_name == spec["source_file"])
        check_a_src_start = (a_src_start == spec["start_frame"])
        check_a_src_end = (a_src_end == spec["end_frame"])
        check_a_dur = (a_dur == spec["duration_frames"])

        # Audio-video sync check
        check_av_sync = (v_src_start == a_src_start and v_src_end == a_src_end and v_rec_start == a_rec_start and v_rec_end == a_rec_end)

        tl_pass = all([
            check_name_ok,
            check_duration_exact,
            check_duration_window,
            check_v_clip_count,
            check_v_clip_source,
            check_v_src_start,
            check_v_src_end,
            check_v_dur,
            check_a_clip_count,
            check_a_clip_source,
            check_a_src_start,
            check_a_src_end,
            check_a_dur,
            check_av_sync
        ])

        print(f"  Duration: {duration_frames} frames ({duration_sec:.2f}s) [Expected: {spec['duration_frames']} frames, {spec['duration_sec']}s] -> {'PASS' if check_duration_exact else 'FAIL'}")
        print(f"  Within 30s-180s constraint: {duration_sec:.2f}s -> {'PASS' if check_duration_window else 'FAIL'}")
        print(f"  Video Clip: '{v_name}' (expected '{spec['source_file']}') -> {'PASS' if check_v_clip_source else 'FAIL'}")
        print(f"  Video Source Start: {v_src_start} (expected {spec['start_frame']}) -> {'PASS' if check_v_src_start else 'FAIL'}")
        print(f"  Video Source End: {v_src_end} (expected {spec['end_frame']}) -> {'PASS' if check_v_src_end else 'FAIL'}")
        print(f"  Audio Track Clip: '{a_name}' -> {'PASS' if check_a_clip_source else 'FAIL'}")
        print(f"  Audio Source In/Out: [{a_src_start}, {a_src_end}] -> {'PASS' if (check_a_src_start and check_a_src_end) else 'FAIL'}")
        print(f"  Audio/Video Sync Invariant: Record=[{v_rec_start}..{v_rec_end}] vs [{a_rec_start}..{a_rec_end}] -> {'PASS' if check_av_sync else 'FAIL'}")

        if not tl_pass:
            all_timelines_valid = False

        review_output["timeline_audits"].append({
            "id": spec["id"],
            "name": tname,
            "category": spec["category"],
            "start_frame": start_frame,
            "end_frame": end_frame,
            "duration_frames": duration_frames,
            "duration_seconds": duration_sec,
            "video_tracks": v_tracks,
            "audio_tracks": a_tracks,
            "subtitle_tracks": sub_tracks,
            "video_clip": {
                "name": v_name,
                "duration": v_dur,
                "source_start": v_src_start,
                "source_end": v_src_end,
                "record_start": v_rec_start,
                "record_end": v_rec_end
            },
            "audio_clip": {
                "name": a_name,
                "duration": a_dur,
                "source_start": a_src_start,
                "source_end": a_src_end,
                "record_start": a_rec_start,
                "record_end": a_rec_end
            },
            "checks": {
                "name_ok": check_name_ok,
                "duration_exact": check_duration_exact,
                "duration_in_window": check_duration_window,
                "v_clip_count_1": check_v_clip_count,
                "v_clip_source_ok": check_v_clip_source,
                "v_src_start_ok": check_v_src_start,
                "v_src_end_ok": check_v_src_end,
                "v_dur_ok": check_v_dur,
                "a_clip_count_1": check_a_clip_count,
                "a_clip_source_ok": check_a_clip_source,
                "a_src_start_ok": check_a_src_start,
                "a_src_end_ok": check_a_src_end,
                "a_dur_ok": check_a_dur,
                "av_sync_ok": check_av_sync
            },
            "pass": tl_pass
        })

    # 2. Source Media Directory Forensic Audit
    print("\n----------------------------------------------------------------------")
    print("SOURCE MEDIA NON-DESTRUCTIVE FORENSIC AUDIT")
    print("----------------------------------------------------------------------")
    media_dir = r"C:\Users\warit\SynologyDrive\Tygarina\2026-09-30"
    all_entries = os.listdir(media_dir)
    mp4_files = [f for f in all_entries if f.endswith(".mp4")]
    other_entries = [f for f in all_entries if not f.endswith(".mp4")]

    print(f"Total directory entries: {len(all_entries)}")
    print(f"Total .mp4 files: {len(mp4_files)} (Expected: 32)")
    print(f"Non-.mp4 files/directories: {other_entries} (Expected: None)")

    file_stats = []
    total_bytes = 0
    for f in mp4_files:
        full_path = os.path.join(media_dir, f)
        st = os.stat(full_path)
        total_bytes += st.st_size
        mtime = datetime.fromtimestamp(st.st_mtime).isoformat()
        file_stats.append({
            "name": f,
            "size": st.st_size,
            "modified": mtime,
            "modified_ts": st.st_mtime
        })

    total_gib = total_bytes / (1024 ** 3)
    print(f"Total Source Footage Size: {total_bytes} bytes ({total_gib:.4f} GiB)")

    # All files should have mtime prior to task start (2026-10-02 09:00:00 local time)
    task_start_timestamp = datetime(2026, 10, 2, 9, 0, 0).timestamp()
    files_unmodified = all(st["modified_ts"] < task_start_timestamp for st in file_stats)

    media_intact = (len(mp4_files) == 32 and len(other_entries) == 0 and total_bytes == 74624842819 and files_unmodified)
    print(f"Source Media Non-Destructive Invariant: {'PASS' if media_intact else 'FAIL'}")

    review_output["media_integrity_audit"] = {
        "media_dir": media_dir,
        "entry_count": len(all_entries),
        "mp4_file_count": len(mp4_files),
        "non_mp4_entries": other_entries,
        "total_bytes": total_bytes,
        "total_gib": round(total_gib, 4),
        "expected_bytes": 74624842819,
        "files_unmodified_before_task": files_unmodified,
        "intact": media_intact,
        "file_stats": file_stats
    }

    # 3. Adversarial Integrity Checks
    print("\n----------------------------------------------------------------------")
    print("ADVERSARIAL INTEGRITY AUDIT")
    print("----------------------------------------------------------------------")
    # Check for hardcoded results in worker verification script
    # Check if worker genuinely called Resolve API
    # Check if media offline or broken links exist
    adversarial_findings = []

    # Check 1: Are there any offline clips in any timeline?
    offline_items_found = 0
    for tl_data in review_output["timeline_audits"]:
        tl = timelines_by_name[tl_data["name"]]
        proj.SetCurrentTimeline(tl)
        # Probe media status
        v_items = tl.GetItemListInTrack("video", 1) or []
        for it in v_items:
            # Check media pool item
            mpi = it.GetMediaPoolItem()
            if not mpi:
                adversarial_findings.append(f"Timeline {tl_data['name']} item has no MediaPoolItem!")
                offline_items_found += 1
            else:
                m_path = mpi.GetClipProperty("File Path")
                if not os.path.exists(m_path):
                    adversarial_findings.append(f"Media file missing: {m_path}")
                    offline_items_found += 1

    check_zero_offline = (offline_items_found == 0)
    print(f"Adversarial Check 1 (Zero Offline Media): {'PASS' if check_zero_offline else 'FAIL'}")

    # Check 2: Timeline isolation - do timelines alter each other or share dirty states?
    # Verify each timeline has exactly 1 video track and 1 audio track and no unintended subtitle/generator items
    track_pollution = False
    for tl_data in review_output["timeline_audits"]:
        if tl_data["video_tracks"] != 1 or tl_data["audio_tracks"] != 1 or tl_data["subtitle_tracks"] != 0:
            track_pollution = True
            adversarial_findings.append(f"Timeline {tl_data['name']} has unexpected track counts: V={tl_data['video_tracks']}, A={tl_data['audio_tracks']}, Sub={tl_data['subtitle_tracks']}")
    print(f"Adversarial Check 2 (Track Purity & Isolation): {'PASS' if not track_pollution else 'FAIL'}")

    # Check 3: Frame rate mismatch risks (e.g. 24fps vs 60fps drift)
    # At 60fps, 3900 frames is exactly 65.0s. If it were 24fps, it would be 162.5s.
    # Confirm that GetSetting('timelineFrameRate') is 60.0.
    fps_ok = (float(proj_fps) == 60.0)
    print(f"Adversarial Check 3 (Frame Rate Consistency): {'PASS' if fps_ok else 'FAIL'}")

    review_output["adversarial_checks"] = {
        "zero_offline_media": check_zero_offline,
        "track_purity": not track_pollution,
        "frame_rate_consistency": fps_ok,
        "adversarial_findings": adversarial_findings
    }

    # Final gate determination
    final_pass = (all_timelines_valid and media_intact and check_zero_offline and not track_pollution and fps_ok)
    review_output["verdict"] = "APPROVE" if final_pass else "REQUEST_CHANGES"

    print("\n======================================================================")
    print(f"FINAL AUDIT VERDICT: {review_output['verdict']}")
    print("======================================================================")

    out_file = r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\reviewer_m2_1\audit_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(review_output, f, ensure_ascii=False, indent=2)
    print(f"Audit results written to: {out_file}")

    return final_pass

if __name__ == "__main__":
    success = run_independent_review()
    sys.exit(0 if success else 1)
