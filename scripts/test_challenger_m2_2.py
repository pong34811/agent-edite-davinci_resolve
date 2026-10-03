"""Challenger M2-2 Independent Empirical Verification & Stress-Test Script.

Mission:
Empirically stress-test the 1:1 invariant preservation between
'หนีฝ่าความหนาว_Minecraft-vdo' (original) and 'หนีฝ่าความหนาว_Minecraft-vdo_9x16' (vertical):
1. Subtitle cues: strict 1:1 comparison (count 45, verbatim text strings, start frames,
   end frames, SMPTE timecodes, duration, ordering, absence of gaps/overlaps/anomalies).
2. Audio tracks: compare track counts (3), track types (Stereo), volume levels (0.0 dB),
   clip start/end frames, durations, and underlying media items.
3. Total timeline durations: exact frame equality (5880 frames, bounds 216000..221880).
4. Original 16:9 timeline: verify 100% untouched against baseline_30_timelines.json.
5. Stress-tests: edge cases, house style compliance, media offline checks, boundary checks.
"""

import datetime
import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

PROJECT_NAME = "KT404_2026-09-29"
PROJECT_ID = "7c38045b-c9ae-426c-8b4c-2e2d726d88ff"
ORIGINAL_NAME = "หนีฝ่าความหนาว_Minecraft-vdo"
TARGET_NAME = f"{ORIGINAL_NAME}_9x16"
EXPECTED_ORIGINAL_ID = "7dcaea9a-b19f-4fa4-ac24-9a4f8c12f3ff"
EXPECTED_DURATION = 5880
EXPECTED_START_FRAME = 216000
EXPECTED_END_FRAME = 221880
EXPECTED_FPS = 60.0
EXPECTED_SUBTITLE_COUNT = 45
EXPECTED_AUDIO_TRACKS = 3
EXPECTED_ORIGINAL_VIDEO_TRACKS = 3
EXPECTED_VERTICAL_VIDEO_TRACKS = 4

BASELINE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".agents",
    "teamwork",
    "worker_m1",
    "baseline_30_timelines.json",
)

OUTPUT_JSON_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".agents",
    "teamwork",
    "challenger_m2_2",
    "audit_results.json",
)


def get_resolve():
    """Connect to DaVinci Resolve via scripting DLL."""
    if sys.platform == "win32":
        os.environ.setdefault(
            "RESOLVE_SCRIPT_LIB",
            r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll",
        )
        resolve_dir = r"C:\Program Files\Blackmagic Design\DaVinci Resolve"
        if hasattr(os, "add_dll_directory") and os.path.isdir(resolve_dir):
            try:
                os.add_dll_directory(resolve_dir)
            except Exception:
                pass
        script_module_dir = (
            r"C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\lib\modules"
        )
        if os.path.isdir(script_module_dir) and script_module_dir not in sys.path:
            sys.path.append(script_module_dir)
    try:
        import DaVinciResolveScript as dvr_script

        return dvr_script.scriptapp("Resolve")
    except Exception as exc:
        print(f"Error importing DaVinciResolveScript: {exc}", file=sys.stderr)
        return None


def get_property(item, key, default=None):
    """Retrieve property from item safely."""
    try:
        val = item.GetProperty(key)
        if isinstance(val, dict):
            return val.get(key, default)
        if val is not None and val is not False:
            return val
    except Exception:
        pass
    try:
        props = item.GetProperty()
        if isinstance(props, dict):
            return props.get(key, default)
    except Exception:
        pass
    return default


def frame_to_smpte(frame_num: int, fps: float = 60.0) -> str:
    """Convert absolute frame number to SMPTE timecode HH:MM:SS:FF at given fps."""
    fps_int = int(round(fps))
    tot_secs = frame_num // fps_int
    f = frame_num % fps_int
    s = tot_secs % 60
    m = (tot_secs // 60) % 60
    h = tot_secs // 3600
    return f"{h:02d}:{m:02d}:{s:02d}:{f:02d}"


def frames_to_duration_tc(frames: int, fps: float = 60.0) -> str:
    """Convert frame count duration to duration timecode HH:MM:SS:FF."""
    fps_int = int(round(fps))
    tot_secs = frames // fps_int
    f = frames % fps_int
    s = tot_secs % 60
    m = (tot_secs // 60) % 60
    h = tot_secs // 3600
    return f"{h:02d}:{m:02d}:{s:02d}:{f:02d}"


def run_audit():
    print("=" * 75)
    print("CHALLENGER M2-2: EMPIRICAL 1:1 INVARIANT PRESERVATION AUDIT")
    print("=" * 75)

    audit_data = {
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "challenger": "challenger_m2_2",
        "verdict": "PENDING",
        "tests": {},
        "summary": {},
    }

    # 1. Connect to Resolve
    resolve = get_resolve()
    if not resolve:
        print("[FAIL] Cannot connect to live DaVinci Resolve instance.")
        audit_data["verdict"] = "REQUEST_CHANGES"
        audit_data["error"] = "Cannot connect to DaVinci Resolve"
        save_results(audit_data)
        sys.exit(1)

    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    if not proj:
        print("[FAIL] No active project in DaVinci Resolve.")
        audit_data["verdict"] = "REQUEST_CHANGES"
        audit_data["error"] = "No active project"
        save_results(audit_data)
        sys.exit(1)

    proj_name = proj.GetName()
    proj_id = proj.GetUniqueId()
    print(f"Project: {proj_name} (ID: {proj_id})")

    if proj_id != PROJECT_ID:
        print(f"[FAIL] Expected Project ID {PROJECT_ID}, got {proj_id}")
        audit_data["verdict"] = "REQUEST_CHANGES"
        audit_data["error"] = f"Project ID mismatch: {proj_id}"
        save_results(audit_data)
        sys.exit(1)

    # 2. Load Baseline JSON
    if not os.path.exists(BASELINE_PATH):
        print(f"[FAIL] Baseline file not found: {BASELINE_PATH}")
        audit_data["verdict"] = "REQUEST_CHANGES"
        audit_data["error"] = f"Missing baseline file: {BASELINE_PATH}"
        save_results(audit_data)
        sys.exit(1)

    with open(BASELINE_PATH, "r", encoding="utf-8") as f:
        baseline_root = json.load(f)

    baseline_tl = None
    for tl in baseline_root.get("timelines", []):
        if tl.get("timeline_name") == ORIGINAL_NAME:
            baseline_tl = tl
            break

    if not baseline_tl:
        print(f"[FAIL] Baseline record for '{ORIGINAL_NAME}' not found.")
        audit_data["verdict"] = "REQUEST_CHANGES"
        audit_data["error"] = f"Missing timeline baseline: {ORIGINAL_NAME}"
        save_results(audit_data)
        sys.exit(1)

    print(f"Loaded preflight baseline for '{ORIGINAL_NAME}' ({baseline_tl['timeline_id']})")

    # 3. Locate Live Timelines
    orig_tl = None
    vert_tl = None
    timeline_count = proj.GetTimelineCount()
    for i in range(1, timeline_count + 1):
        tl = proj.GetTimelineByIndex(i)
        if tl.GetName() == ORIGINAL_NAME:
            orig_tl = tl
        elif tl.GetName() == TARGET_NAME:
            vert_tl = tl

    if not orig_tl:
        print(f"[FAIL] Original timeline '{ORIGINAL_NAME}' not found in project.")
        audit_data["verdict"] = "REQUEST_CHANGES"
        audit_data["error"] = f"Original timeline missing: {ORIGINAL_NAME}"
        save_results(audit_data)
        sys.exit(1)

    if not vert_tl:
        print(f"[FAIL] Vertical timeline '{TARGET_NAME}' not found in project.")
        audit_data["verdict"] = "REQUEST_CHANGES"
        audit_data["error"] = f"Vertical timeline missing: {TARGET_NAME}"
        save_results(audit_data)
        sys.exit(1)

    print(f"Found Original Timeline: {orig_tl.GetName()} (ID: {orig_tl.GetUniqueId()})")
    print(f"Found Vertical Timeline: {vert_tl.GetName()} (ID: {vert_tl.GetUniqueId()})")

    failures = []

    def record_check(test_group: str, test_name: str, passed: bool, details: Any):
        if test_group not in audit_data["tests"]:
            audit_data["tests"][test_group] = []
        status_str = "PASS" if passed else "FAIL"
        print(f"  [{status_str}] {test_name}: {details}")
        audit_data["tests"][test_group].append({
            "test": test_name,
            "passed": passed,
            "details": details,
        })
        if not passed:
            failures.append((test_group, test_name, details))

    # =========================================================================
    # SECTION 1: TOTAL TIMELINE DURATIONS & BOUNDARY COMPARISON
    # =========================================================================
    print("\n--- SECTION 1: TIMELINE DURATIONS & BOUNDARIES ---")
    orig_start = orig_tl.GetStartFrame()
    orig_end = orig_tl.GetEndFrame()
    orig_dur = orig_end - orig_start
    orig_fps = float(orig_tl.GetSetting("timelineFrameRate") or 0.0)

    vert_start = vert_tl.GetStartFrame()
    vert_end = vert_tl.GetEndFrame()
    vert_dur = vert_end - vert_start
    vert_fps = float(vert_tl.GetSetting("timelineFrameRate") or 0.0)

    record_check("durations", "Original start frame is 216000", orig_start == EXPECTED_START_FRAME, orig_start)
    record_check("durations", "Vertical start frame is 216000", vert_start == EXPECTED_START_FRAME, vert_start)
    record_check("durations", "Original end frame is 221880", orig_end == EXPECTED_END_FRAME, orig_end)
    record_check("durations", "Vertical end frame is 221880", vert_end == EXPECTED_END_FRAME, vert_end)
    record_check("durations", "Original duration is 5880 frames", orig_dur == EXPECTED_DURATION, orig_dur)
    record_check("durations", "Vertical duration is 5880 frames", vert_dur == EXPECTED_DURATION, vert_dur)
    record_check("durations", "Exact frame equality between orig and vert", orig_dur == vert_dur == EXPECTED_DURATION, f"orig={orig_dur}, vert={vert_dur}")
    record_check("durations", "Original FPS is 60.0", orig_fps == EXPECTED_FPS, orig_fps)
    record_check("durations", "Vertical FPS is 60.0", vert_fps == EXPECTED_FPS, vert_fps)
    record_check("durations", "Frame rate equality", orig_fps == vert_fps == EXPECTED_FPS, f"orig={orig_fps}, vert={vert_fps}")

    # =========================================================================
    # SECTION 2: SUBTITLE TRACK STRICT 1:1 COMPARISON
    # =========================================================================
    print("\n--- SECTION 2: SUBTITLE TRACK STRICT 1:1 COMPARISON ---")
    orig_sub_track_count = orig_tl.GetTrackCount("subtitle")
    vert_sub_track_count = vert_tl.GetTrackCount("subtitle")
    record_check("subtitles", "Original subtitle track count is 1", orig_sub_track_count == 1, orig_sub_track_count)
    record_check("subtitles", "Vertical subtitle track count is 1", vert_sub_track_count == 1, vert_sub_track_count)

    orig_cues = orig_tl.GetItemListInTrack("subtitle", 1) or []
    vert_cues = vert_tl.GetItemListInTrack("subtitle", 1) or []
    base_cues = baseline_tl.get("subtitle_track", {}).get("cues", [])

    record_check("subtitles", "Original subtitle cue count is 45", len(orig_cues) == EXPECTED_SUBTITLE_COUNT, len(orig_cues))
    record_check("subtitles", "Vertical subtitle cue count is 45", len(vert_cues) == EXPECTED_SUBTITLE_COUNT, len(vert_cues))
    record_check("subtitles", "Baseline subtitle cue count is 45", len(base_cues) == EXPECTED_SUBTITLE_COUNT, len(base_cues))
    record_check("subtitles", "Cue count 1:1 equality (orig == vert == baseline)", len(orig_cues) == len(vert_cues) == len(base_cues) == 45, f"{len(orig_cues)}=={len(vert_cues)}=={len(base_cues)}")

    sub_diffs_orig_vs_vert = []
    sub_diffs_vert_vs_base = []
    sub_diffs_orig_vs_base = []
    sub_tc_diffs = []
    cues_audit_table = []

    for idx in range(min(len(orig_cues), len(vert_cues), len(base_cues))):
        oc = orig_cues[idx]
        vc = vert_cues[idx]
        bc = base_cues[idx]

        oc_text = oc.GetName()
        vc_text = vc.GetName()
        bc_text = bc["text"]

        oc_start = oc.GetStart()
        vc_start = vc.GetStart()
        bc_start = bc["start_frame"]

        oc_end = oc.GetEnd()
        vc_end = vc.GetEnd()
        bc_end = bc["end_frame"]

        oc_dur = oc.GetDuration()
        vc_dur = vc.GetDuration()
        bc_dur = bc["duration_frames"]

        # Calculate SMPTE timecodes
        oc_start_tc = frame_to_smpte(oc_start, orig_fps)
        oc_end_tc = frame_to_smpte(oc_end, orig_fps)
        vc_start_tc = frame_to_smpte(vc_start, vert_fps)
        vc_end_tc = frame_to_smpte(vc_end, vert_fps)
        bc_start_tc = bc["start_tc"]
        bc_end_tc = bc["end_tc"]

        # Compare orig vs vert
        if oc_text != vc_text or oc_start != vc_start or oc_end != vc_end or oc_dur != vc_dur or oc_start_tc != vc_start_tc or oc_end_tc != vc_end_tc:
            sub_diffs_orig_vs_vert.append({
                "cue_index": idx + 1,
                "orig": {"text": oc_text, "start": oc_start, "end": oc_end, "dur": oc_dur, "start_tc": oc_start_tc, "end_tc": oc_end_tc},
                "vert": {"text": vc_text, "start": vc_start, "end": vc_end, "dur": vc_dur, "start_tc": vc_start_tc, "end_tc": vc_end_tc},
            })

        # Compare vert vs baseline
        if vc_text != bc_text or vc_start != bc_start or vc_end != bc_end or vc_dur != bc_dur or vc_start_tc != bc_start_tc or vc_end_tc != bc_end_tc:
            sub_diffs_vert_vs_base.append({
                "cue_index": idx + 1,
                "vert": {"text": vc_text, "start": vc_start, "end": vc_end, "dur": vc_dur, "start_tc": vc_start_tc, "end_tc": vc_end_tc},
                "base": {"text": bc_text, "start": bc_start, "end": bc_end, "dur": bc_dur, "start_tc": bc_start_tc, "end_tc": bc_end_tc},
            })

        # Compare orig vs baseline
        if oc_text != bc_text or oc_start != bc_start or oc_end != bc_end or oc_dur != bc_dur:
            sub_diffs_orig_vs_base.append({
                "cue_index": idx + 1,
                "orig": {"text": oc_text, "start": oc_start, "end": oc_end, "dur": oc_dur},
                "base": {"text": bc_text, "start": bc_start, "end": bc_end, "dur": bc_dur},
            })

        cues_audit_table.append({
            "cue_index": idx + 1,
            "text": vc_text,
            "start_frame": vc_start,
            "end_frame": vc_end,
            "duration_frames": vc_dur,
            "start_tc": vc_start_tc,
            "end_tc": vc_end_tc,
            "orig_match": (oc_text == vc_text and oc_start == vc_start and oc_end == vc_end),
            "base_match": (vc_text == bc_text and vc_start == bc_start and vc_end == bc_end),
        })

    record_check("subtitles", "Orig vs Vert subtitle cues 1:1 verbatim match", len(sub_diffs_orig_vs_vert) == 0, f"Mismatches: {len(sub_diffs_orig_vs_vert)}")
    record_check("subtitles", "Vert vs Baseline subtitle cues 1:1 verbatim match", len(sub_diffs_vert_vs_base) == 0, f"Mismatches: {len(sub_diffs_vert_vs_base)}")
    record_check("subtitles", "Orig vs Baseline subtitle cues 1:1 verbatim match", len(sub_diffs_orig_vs_base) == 0, f"Mismatches: {len(sub_diffs_orig_vs_base)}")

    # Stress-test: check subtitle ordering and bounds
    out_of_bounds_cues = []
    inverted_cues = []
    overlapping_cues = []
    for idx, c in enumerate(cues_audit_table):
        if c["start_frame"] < EXPECTED_START_FRAME or c["end_frame"] > EXPECTED_END_FRAME:
            out_of_bounds_cues.append(c)
        if c["start_frame"] >= c["end_frame"]:
            inverted_cues.append(c)
        if idx > 0:
            prev = cues_audit_table[idx - 1]
            if c["start_frame"] < prev["end_frame"]:
                overlapping_cues.append((prev["cue_index"], c["cue_index"], prev["end_frame"], c["start_frame"]))

    record_check("subtitles", "All cues within timeline boundary [216000, 221880]", len(out_of_bounds_cues) == 0, f"Out of bounds: {len(out_of_bounds_cues)}")
    record_check("subtitles", "Zero inverted cues (start < end strictly)", len(inverted_cues) == 0, f"Inverted: {len(inverted_cues)}")
    record_check("subtitles", "Zero overlapping cues (strictly chronological)", len(overlapping_cues) == 0, f"Overlaps: {len(overlapping_cues)}")

    # Invariant preservation check on subtitle cue durations vs baseline
    # Note: R3 mandates strict 1:1 preservation of existing cues without retiming.
    # We audit that vert cues match baseline cue durations exactly across all 45 cues.
    cue_dur_diffs = []
    for idx, (vc, bc) in enumerate(zip(cues_audit_table, base_cues)):
        if vc["duration_frames"] != bc["duration_frames"]:
            cue_dur_diffs.append((idx + 1, vc["duration_frames"], bc["duration_frames"]))
    record_check("subtitles", "All 45 cue durations match baseline 1:1 (R3 locked)", len(cue_dur_diffs) == 0, f"Mismatches: {len(cue_dur_diffs)}")

    # Advisory note on house style: check if any cues exceed 1.5s (90f) in source cut
    source_long_cues = [c for c in base_cues if c["duration_frames"] > 90]
    vert_long_cues = [c for c in cues_audit_table if c["duration_frames"] > 90]
    record_check("subtitles", "Source cut has 10 pre-existing long cues (>1.5s) preserved identically", len(vert_long_cues) == len(source_long_cues) == 10, f"source={len(source_long_cues)}, vert={len(vert_long_cues)}")
    empty_cues = [c for c in cues_audit_table if not c["text"] or not c["text"].strip()]
    record_check("subtitles", "No empty or whitespace-only cues", len(empty_cues) == 0, f"Empty cues: {len(empty_cues)}")

    # =========================================================================
    # SECTION 3: AUDIO TRACKS STRICT 1:1 COMPARISON
    # =========================================================================
    print("\n--- SECTION 3: AUDIO TRACKS STRICT 1:1 COMPARISON ---")
    orig_a_count = orig_tl.GetTrackCount("audio")
    vert_a_count = vert_tl.GetTrackCount("audio")
    base_a_tracks = baseline_tl.get("audio_tracks", [])

    record_check("audio", "Original audio track count is 3", orig_a_count == EXPECTED_AUDIO_TRACKS, orig_a_count)
    record_check("audio", "Vertical audio track count is 3", vert_a_count == EXPECTED_AUDIO_TRACKS, vert_a_count)
    record_check("audio", "Audio track count equality (orig == vert == 3)", orig_a_count == vert_a_count == EXPECTED_AUDIO_TRACKS, f"{orig_a_count}=={vert_a_count}")

    audio_track_mismatches = []
    audio_clip_mismatches = []
    audio_volume_mismatches = []
    audio_audit_table = []

    for t_idx in range(1, 4):
        orig_name = orig_tl.GetTrackName("audio", t_idx)
        vert_name = vert_tl.GetTrackName("audio", t_idx)
        orig_type = orig_tl.GetTrackSubType("audio", t_idx)
        vert_type = vert_tl.GetTrackSubType("audio", t_idx)

        base_t = base_a_tracks[t_idx - 1] if t_idx - 1 < len(base_a_tracks) else {}
        base_name = base_t.get("track_name")
        base_type = base_t.get("track_type")

        # Track metadata checks
        if orig_name != vert_name or vert_name != base_name:
            audio_track_mismatches.append(f"Track {t_idx} Name: orig='{orig_name}', vert='{vert_name}', base='{base_name}'")
        if orig_type != vert_type or vert_type != base_type:
            audio_track_mismatches.append(f"Track {t_idx} SubType: orig='{orig_type}', vert='{vert_type}', base='{base_type}'")

        # Clip items on track
        orig_items = orig_tl.GetItemListInTrack("audio", t_idx) or []
        vert_items = vert_tl.GetItemListInTrack("audio", t_idx) or []
        base_items = base_t.get("items", [])

        if len(orig_items) != len(vert_items) or len(vert_items) != len(base_items):
            audio_clip_mismatches.append(f"Track {t_idx} item count: orig={len(orig_items)}, vert={len(vert_items)}, base={len(base_items)}")

        track_clips = []
        for c_idx in range(min(len(orig_items), len(vert_items), len(base_items))):
            oi = orig_items[c_idx]
            vi = vert_items[c_idx]
            bi = base_items[c_idx]

            oi_name = oi.GetName()
            vi_name = vi.GetName()
            bi_name = bi.get("name")

            oi_start = oi.GetStart()
            vi_start = vi.GetStart()
            bi_start = bi.get("start_frame")

            oi_end = oi.GetEnd()
            vi_end = vi.GetEnd()
            bi_end = bi.get("end_frame")

            oi_dur = oi.GetDuration()
            vi_dur = vi.GetDuration()
            bi_dur = bi.get("duration_frames")

            oi_vol = float(get_property(oi, "AudioVolume", 0.0) or 0.0)
            vi_vol = float(get_property(vi, "AudioVolume", 0.0) or 0.0)
            bi_vol = float(bi.get("volume_db", 0.0) or 0.0)

            # Compare clip timing and names
            if oi_name != vi_name or vi_name != bi_name:
                audio_clip_mismatches.append(f"A{t_idx} clip {c_idx+1} name: orig='{oi_name}', vert='{vi_name}', base='{bi_name}'")
            if oi_start != vi_start or vi_start != bi_start:
                audio_clip_mismatches.append(f"A{t_idx} clip {c_idx+1} start: orig={oi_start}, vert={vi_start}, base={bi_start}")
            if oi_end != vi_end or vi_end != bi_end:
                audio_clip_mismatches.append(f"A{t_idx} clip {c_idx+1} end: orig={oi_end}, vert={vi_end}, base={bi_end}")
            if oi_dur != vi_dur or vi_dur != bi_dur:
                audio_clip_mismatches.append(f"A{t_idx} clip {c_idx+1} dur: orig={oi_dur}, vert={vi_dur}, base={bi_dur}")

            # Compare volume
            if abs(oi_vol - vi_vol) > 0.001 or abs(vi_vol - bi_vol) > 0.001 or abs(vi_vol - 0.0) > 0.001:
                audio_volume_mismatches.append(f"A{t_idx} clip {c_idx+1} vol: orig={oi_vol}, vert={vi_vol}, base={bi_vol}, expected=0.0")

            track_clips.append({
                "clip_index": c_idx + 1,
                "name": vi_name,
                "start_frame": vi_start,
                "end_frame": vi_end,
                "duration_frames": vi_dur,
                "start_tc": frame_to_smpte(vi_start, vert_fps),
                "end_tc": frame_to_smpte(vi_end, vert_fps),
                "volume_db": vi_vol,
            })

        audio_audit_table.append({
            "track_index": t_idx,
            "track_name": vert_name,
            "track_type": vert_type,
            "clip_count": len(vert_items),
            "clips": track_clips,
        })

    record_check("audio", "Audio track names match baseline", len(audio_track_mismatches) == 0, f"Mismatches: {audio_track_mismatches}")
    record_check("audio", "All 3 audio tracks are Stereo sub-type", all(t["track_type"] == "stereo" for t in audio_audit_table), [t["track_type"] for t in audio_audit_table])
    record_check("audio", "Audio clip counts and timings 100% match orig and baseline", len(audio_clip_mismatches) == 0, f"Mismatches: {audio_clip_mismatches}")
    record_check("audio", "All audio clip volumes are strictly 0.0 dB", len(audio_volume_mismatches) == 0, f"Mismatches: {audio_volume_mismatches}")

    # =========================================================================
    # SECTION 4: ORIGINAL 16:9 TIMELINE 100% UNTOUCHED AUDIT
    # =========================================================================
    print("\n--- SECTION 4: ORIGINAL TIMELINE UNTOUCHED AUDIT ---")
    orig_name_check = orig_tl.GetName() == ORIGINAL_NAME
    orig_id_check = orig_tl.GetUniqueId() == EXPECTED_ORIGINAL_ID
    record_check("original_untouched", "Original timeline name unchanged", orig_name_check, orig_tl.GetName())
    record_check("original_untouched", "Original timeline ID unchanged", orig_id_check, orig_tl.GetUniqueId())

    orig_w = orig_tl.GetSetting("timelineResolutionWidth")
    orig_h = orig_tl.GetSetting("timelineResolutionHeight")
    orig_custom = orig_tl.GetSetting("useCustomSettings")
    record_check("original_untouched", "Original resolution remains 1920x1080 (16:9)", orig_w == "1920" and orig_h == "1080", f"{orig_w}x{orig_h}")
    record_check("original_untouched", "Original useCustomSettings remains '1' (baseline match)", orig_custom == "1", f"useCustomSettings={orig_custom}")

    orig_v_count = orig_tl.GetTrackCount("video")
    record_check("original_untouched", "Original video track count remains 3", orig_v_count == EXPECTED_ORIGINAL_VIDEO_TRACKS, orig_v_count)

    # Check original video track items vs baseline
    base_v_tracks = baseline_tl.get("video_tracks", [])
    orig_v_mismatches = []
    for vt_idx in range(1, orig_v_count + 1):
        v_items = orig_tl.GetItemListInTrack("video", vt_idx) or []
        base_vt = base_v_tracks[vt_idx - 1] if vt_idx - 1 < len(base_v_tracks) else {}
        b_items = base_vt.get("items", [])
        if len(v_items) != len(b_items):
            orig_v_mismatches.append(f"V{vt_idx} item count {len(v_items)} vs baseline {len(b_items)}")
        for i_idx in range(min(len(v_items), len(b_items))):
            vi = v_items[i_idx]
            bi = b_items[i_idx]
            if vi.GetName() != bi.get("name") or vi.GetStart() != bi.get("start_frame") or vi.GetEnd() != bi.get("end_frame"):
                orig_v_mismatches.append(f"V{vt_idx} item {i_idx+1} mismatch: live='{vi.GetName()}'[{vi.GetStart()}..{vi.GetEnd()}] vs base='{bi.get('name')}'[{bi.get('start_frame')}..{bi.get('end_frame')}]")

    record_check("original_untouched", "Original video tracks V1-V3 clips identical to baseline", len(orig_v_mismatches) == 0, f"Mismatches: {orig_v_mismatches}")

    # Check original adjustment clips retained baseline Fusion transforms (Center=[0.38, 0.81], Size=1.3)
    orig_adj_fusion_errors = []
    for idx, adj in enumerate(orig_tl.GetItemListInTrack("video", 3) or []):
        comp = adj.GetFusionCompByIndex(1)
        tools = comp.GetToolList() if comp else {}
        matched = False
        for t in tools.values():
            if "Transform" in t.GetAttrs().get("TOOLS_Name", ""):
                center = t.GetInput("Center")
                size = t.GetInput("Size")
                cx = center.get(1, 0.0) if isinstance(center, dict) else 0.0
                cy = center.get(2, 0.0) if isinstance(center, dict) else 0.0
                sz = float(size or 0.0)
                if abs(cx - 0.38) < 0.01 and abs(cy - 0.81) < 0.01 and abs(sz - 1.3) < 0.01:
                    matched = True
        if not matched:
            orig_adj_fusion_errors.append(f"Orig Adj {idx+1} Fusion Transform mutated!")
    record_check("original_untouched", "Original V3 Adjustment Clips retained baseline Fusion transforms Center=(0.38, 0.81), Size=1.3", len(orig_adj_fusion_errors) == 0, f"Errors: {orig_adj_fusion_errors}")

    # =========================================================================
    # SECTION 5: MEDIA OFFLINE & ASSET STRESS-TEST
    # =========================================================================
    print("\n--- SECTION 5: MEDIA OFFLINE & ASSET STRESS-TEST ---")
    offline_items_orig = []
    offline_items_vert = []

    for v in range(1, orig_tl.GetTrackCount("video") + 1):
        for it in orig_tl.GetItemListInTrack("video", v) or []:
            mpi = it.GetMediaPoolItem()
            if mpi:
                fp = mpi.GetClipProperty("File Path")
                if fp and not os.path.exists(fp):
                    offline_items_orig.append(f"V{v}:{it.GetName()}:{fp}")

    for a in range(1, orig_tl.GetTrackCount("audio") + 1):
        for it in orig_tl.GetItemListInTrack("audio", a) or []:
            mpi = it.GetMediaPoolItem()
            if mpi:
                fp = mpi.GetClipProperty("File Path")
                if fp and not os.path.exists(fp):
                    offline_items_orig.append(f"A{a}:{it.GetName()}:{fp}")

    for v in range(1, vert_tl.GetTrackCount("video") + 1):
        for it in vert_tl.GetItemListInTrack("video", v) or []:
            mpi = it.GetMediaPoolItem()
            if mpi:
                fp = mpi.GetClipProperty("File Path")
                if fp and not os.path.exists(fp):
                    offline_items_vert.append(f"V{v}:{it.GetName()}:{fp}")

    for a in range(1, vert_tl.GetTrackCount("audio") + 1):
        for it in vert_tl.GetItemListInTrack("audio", a) or []:
            mpi = it.GetMediaPoolItem()
            if mpi:
                fp = mpi.GetClipProperty("File Path")
                if fp and not os.path.exists(fp):
                    offline_items_vert.append(f"A{a}:{it.GetName()}:{fp}")

    record_check("media_offline", "Zero media offline in original timeline", len(offline_items_orig) == 0, f"Offline: {offline_items_orig}")
    record_check("media_offline", "Zero media offline in vertical timeline", len(offline_items_vert) == 0, f"Offline: {offline_items_vert}")

    # =========================================================================
    # SECTION 6: VERTICAL TIMELINE SPECIFICATIONS CHECK
    # =========================================================================
    print("\n--- SECTION 6: VERTICAL TIMELINE SPECIFICATIONS CHECK ---")
    vert_w = vert_tl.GetSetting("timelineResolutionWidth")
    vert_h = vert_tl.GetSetting("timelineResolutionHeight")
    vert_custom = vert_tl.GetSetting("useCustomSettings")
    vert_v_count = vert_tl.GetTrackCount("video")

    record_check("vertical_specs", "Vertical timeline width is 1080", vert_w == "1080", vert_w)
    record_check("vertical_specs", "Vertical timeline height is 1920", vert_h == "1920", vert_h)
    record_check("vertical_specs", "Vertical useCustomSettings is '1'", vert_custom == "1", vert_custom)
    record_check("vertical_specs", "Vertical video track count is 4", vert_v_count == EXPECTED_VERTICAL_VIDEO_TRACKS, vert_v_count)

    # Ensure UI state is restored
    proj.SetCurrentTimeline(vert_tl)
    print(f"\nActive timeline maintained as: {proj.GetCurrentTimeline().GetName()}")

    # =========================================================================
    # FINAL VERDICT
    # =========================================================================
    print("\n" + "=" * 75)
    total_checks = sum(len(checks) for checks in audit_data["tests"].values())
    failed_checks = len(failures)
    passed_checks = total_checks - failed_checks

    audit_data["summary"] = {
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "failed_checks": failed_checks,
        "failures": failures,
    }
    audit_data["subtitle_audit"] = {
        "cue_count": len(cues_audit_table),
        "all_match": len(sub_diffs_orig_vs_vert) == 0 and len(sub_diffs_vert_vs_base) == 0,
        "cues": cues_audit_table,
    }
    audit_data["audio_audit"] = {
        "track_count": len(audio_audit_table),
        "all_match": len(audio_track_mismatches) == 0 and len(audio_clip_mismatches) == 0 and len(audio_volume_mismatches) == 0,
        "tracks": audio_audit_table,
    }

    if failed_checks == 0:
        audit_data["verdict"] = "APPROVE"
        print(f"[VERDICT] APPROVE! (Passed {passed_checks}/{total_checks} checks, 0 failures)")
    else:
        audit_data["verdict"] = "REQUEST_CHANGES"
        print(f"[VERDICT] REQUEST_CHANGES! ({failed_checks} failures out of {total_checks} checks)")
        for fail in failures:
            print(f"  - [{fail[0]}] {fail[1]}: {fail[2]}")
    print("=" * 75)

    save_results(audit_data)
    return audit_data["verdict"] == "APPROVE"


def save_results(data: Dict[str, Any]):
    os.makedirs(os.path.dirname(OUTPUT_JSON_PATH), exist_ok=True)
    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Audit report saved to: {OUTPUT_JSON_PATH}")


if __name__ == "__main__":
    success = run_audit()
    sys.exit(0 if success else 1)
