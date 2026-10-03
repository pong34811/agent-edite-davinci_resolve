"""Independent Verification Script for Milestone 2: Pilot Timeline.

Author: Worker M2 (teamwork_preview_worker)
Purpose: Independently audit and verify that 'หนีฝ่าความหนาว_Minecraft-vdo_9x16'
conforms 100% to all Milestone 2 acceptance criteria and locked editorial invariants
without importing or relying on m2_convert_pilot.py.
"""

import datetime
import json
import os
import sys

# Ensure UTF-8 output encoding
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
EXPECTED_FPS = 60.0
EXPECTED_SUBTITLE_COUNT = 45

BASELINE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "worker_m1",
    "baseline_30_timelines.json",
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


def main():
    print("=" * 70)
    print("INDEPENDENT AUDIT: Milestone 2 Pilot Timeline Verification")
    print("=" * 70)

    # 1. Connect
    resolve = get_resolve()
    if not resolve:
        print("[FAIL] Cannot connect to DaVinci Resolve.")
        sys.exit(1)

    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    if not proj:
        print("[FAIL] No active project.")
        sys.exit(1)

    print(f"[AUDIT] Project: {proj.GetName()} (ID: {proj.GetUniqueId()})")
    assert proj.GetUniqueId() == PROJECT_ID, "Project ID mismatch!"

    # 2. Load baseline
    with open(BASELINE_PATH, "r", encoding="utf-8") as f:
        baseline_file = json.load(f)

    baseline = None
    for tl in baseline_file.get("timelines", []):
        if tl.get("timeline_name") == ORIGINAL_NAME:
            baseline = tl
            break
    assert baseline is not None, f"Baseline not found for {ORIGINAL_NAME}"

    # 3. Locate timelines
    target_tl = None
    orig_tl = None
    for idx in range(1, proj.GetTimelineCount() + 1):
        tl = proj.GetTimelineByIndex(idx)
        if tl.GetName() == TARGET_NAME:
            target_tl = tl
        elif tl.GetName() == ORIGINAL_NAME:
            orig_tl = tl

    assert orig_tl is not None, f"Original timeline '{ORIGINAL_NAME}' missing!"
    assert target_tl is not None, f"Target vertical timeline '{TARGET_NAME}' missing!"

    print(f"[AUDIT] Original Timeline: {orig_tl.GetName()} (ID: {orig_tl.GetUniqueId()})")
    print(f"[AUDIT] Target 9:16 Timeline: {target_tl.GetName()} (ID: {target_tl.GetUniqueId()})")

    failures = []

    def check(desc, condition, info=""):
        status = "PASS" if condition else "FAIL"
        print(f"  [{status}] {desc}: {info}")
        if not condition:
            failures.append((desc, info))

    # Test 1: Resolution & Aspect Ratio
    w = target_tl.GetSetting("timelineResolutionWidth")
    h = target_tl.GetSetting("timelineResolutionHeight")
    custom = target_tl.GetSetting("useCustomSettings")
    fps = float(target_tl.GetSetting("timelineFrameRate") or 0.0)
    check("Resolution is 1080x1920 (9:16)", w == "1080" and h == "1920", f"{w}x{h}")
    check("Custom timeline settings enabled", custom == "1", f"useCustomSettings={custom}")
    check("Frame rate matches source 60.0 fps", fps == EXPECTED_FPS, f"FPS={fps}")

    # Test 2: Duration
    start_f = target_tl.GetStartFrame()
    end_f = target_tl.GetEndFrame()
    dur = end_f - start_f
    check("Timeline duration preserved", dur == EXPECTED_DURATION, f"{dur} frames (Start: {start_f}, End: {end_f})")

    # Test 3: Subtitles 1:1 against Baseline
    sub_items = target_tl.GetItemListInTrack("subtitle", 1) or []
    base_cues = baseline["subtitle_track"]["cues"]
    check("Subtitle cue count is exact 45", len(sub_items) == EXPECTED_SUBTITLE_COUNT == len(base_cues), f"{len(sub_items)} cues")

    sub_diffs = []
    for idx, (it, base) in enumerate(zip(sub_items, base_cues)):
        t_text = it.GetName()
        t_start = it.GetStart()
        t_end = it.GetEnd()
        b_text = base["text"]
        b_start = base["start_frame"]
        b_end = base["end_frame"]
        if t_text != b_text or t_start != b_start or t_end != b_end:
            sub_diffs.append((idx + 1, t_text, b_text, t_start, b_start, t_end, b_end))

    check("100% Subtitle text and frame bounds bit-for-bit preserved", len(sub_diffs) == 0, f"Mismatches: {len(sub_diffs)}")

    # Test 4: Audio Tracks 1:1 against Baseline
    a_count = target_tl.GetTrackCount("audio")
    check("Audio track count is 3", a_count == 3, f"Track count={a_count}")
    audio_mismatches = []
    for a_idx in range(1, 4):
        items = target_tl.GetItemListInTrack("audio", a_idx) or []
        base_items = baseline["audio_tracks"][a_idx - 1]["items"]
        if len(items) != len(base_items):
            audio_mismatches.append(f"A{a_idx} item count {len(items)} vs {len(base_items)}")
        for it, bit in zip(items, base_items):
            vol = float(get_property(it, "AudioVolume", 0.0) or 0.0)
            b_vol = float(bit.get("volume_db", 0.0) or 0.0)
            if abs(vol - b_vol) > 0.01:
                audio_mismatches.append(f"A{a_idx} volume {vol} vs {b_vol}")
            if it.GetStart() != bit["start_frame"] or it.GetEnd() != bit["end_frame"]:
                audio_mismatches.append(f"A{a_idx} timing {it.GetStart()}..{it.GetEnd()} vs {bit['start_frame']}..{bit['end_frame']}")

    check("Audio clips, timings, and volume levels 100% preserved", len(audio_mismatches) == 0, f"Mismatches: {audio_mismatches}")

    # Test 5: Video Tracks and Split Screen Reframing
    v_count = target_tl.GetTrackCount("video")
    check("Video track count is 4", v_count == 4, f"Track count={v_count}")

    v1_items = target_tl.GetItemListInTrack("video", 1) or []
    v2_items = target_tl.GetItemListInTrack("video", 2) or []
    v3_items = target_tl.GetItemListInTrack("video", 3) or []
    v4_items = target_tl.GetItemListInTrack("video", 4) or []

    # V1 (Game Top)
    if v1_items:
        it = v1_items[0]
        zx = float(get_property(it, "ZoomX", 0.0) or 0.0)
        pan = float(get_property(it, "Pan", 0.0) or 0.0)
        tilt = float(get_property(it, "Tilt", 0.0) or 0.0)
        crop_b = float(get_property(it, "CropBottom", 0.0) or 0.0)
        v1_ok = abs(zx - 1.60) < 0.01 and abs(pan - 0.0) < 0.1 and abs(tilt - 480.0) < 0.1 and abs(crop_b - 486.0) < 0.1
        check("V1 Game Top framing (Zoom=1.60, Pan=0, Tilt=+480, CropBottom=486)", v1_ok, f"ZoomX={zx}, Pan={pan}, Tilt={tilt}, CropBottom={crop_b}")
    else:
        check("V1 Game Top item exists", False, "No item on V1")

    # V2 (VTuber Bottom)
    if v2_items:
        it = v2_items[0]
        zx = float(get_property(it, "ZoomX", 0.0) or 0.0)
        pan = float(get_property(it, "Pan", 0.0) or 0.0)
        tilt = float(get_property(it, "Tilt", 0.0) or 0.0)
        crop_t = float(get_property(it, "CropTop", 0.0) or 0.0)
        v2_ok = abs(zx - 2.60) < 0.01 and abs(pan - (-936.0)) < 0.1 and abs(tilt - (-200.0)) < 0.1 and abs(crop_t - 480.0) < 0.1
        check("V2 VTuber Bottom framing (Zoom=2.60, Pan=-936, Tilt=-200, CropTop=480)", v2_ok, f"ZoomX={zx}, Pan={pan}, Tilt={tilt}, CropTop={crop_t}")
    else:
        check("V2 VTuber Bottom item exists", False, "No item on V2")

    # V4 (Reaction GIF Safe Area)
    if v4_items:
        it = v4_items[0]
        zx = float(get_property(it, "ZoomX", 0.0) or 0.0)
        pan = float(get_property(it, "Pan", 0.0) or 0.0)
        tilt = float(get_property(it, "Tilt", 0.0) or 0.0)
        v4_ok = abs(zx - 0.42) < 0.01 and abs(pan - (-300.0)) < 0.1 and abs(tilt - 600.0) < 0.1
        check("V4 Reaction GIF safe placement (Zoom=0.42, Pan=-300, Tilt=+600)", v4_ok, f"ZoomX={zx}, Pan={pan}, Tilt={tilt}")
    else:
        check("V4 Reaction GIF item exists", False, "No item on V4")

    # V3 (VTuber Focus Adjustment Clips)
    check("V3 Adjustment Clip count is 3", len(v3_items) == 3, f"Count={len(v3_items)}")
    adj_errors = []
    for idx, adj in enumerate(v3_items):
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
                if abs(cx - 0.50) < 0.01 and abs(cy - 0.25) < 0.01 and abs(sz - 2.0) < 0.01:
                    matched = True
        if not matched:
            adj_errors.append(f"Adj {idx + 1} ({adj.GetStart()}..{adj.GetEnd()}) not configured to Center=(0.50, 0.25), Size=2.0")

    check("V3 Adjustment Clips Fusion Transform Center=(0.50, 0.25), Size=2.0", len(adj_errors) == 0, f"Errors: {adj_errors}")

    # Test 6: Zero Media Offline
    offline_items = []
    for v in range(1, 5):
        for it in target_tl.GetItemListInTrack("video", v) or []:
            mpi = it.GetMediaPoolItem()
            if mpi:
                path = mpi.GetClipProperty("File Path")
                if path and not os.path.exists(path):
                    offline_items.append(f"V{v}:{it.GetName()}:{path}")

    for a in range(1, 4):
        for it in target_tl.GetItemListInTrack("audio", a) or []:
            mpi = it.GetMediaPoolItem()
            if mpi:
                path = mpi.GetClipProperty("File Path")
                if path and not os.path.exists(path):
                    offline_items.append(f"A{a}:{it.GetName()}:{path}")

    check("Zero media offline across all tracks", len(offline_items) == 0, f"Offline items: {offline_items}")

    # Test 7: Original Timeline Completely Untouched
    check("Original timeline name unchanged", orig_tl.GetName() == ORIGINAL_NAME, orig_tl.GetName())
    check("Original timeline ID unchanged", orig_tl.GetUniqueId() == EXPECTED_ORIGINAL_ID, orig_tl.GetUniqueId())
    check("Original resolution 1920x1080 untouched", orig_tl.GetSetting("timelineResolutionWidth") == "1920" and orig_tl.GetSetting("timelineResolutionHeight") == "1080", f"{orig_tl.GetSetting('timelineResolutionWidth')}x{orig_tl.GetSetting('timelineResolutionHeight')}")
    check("Original video track count 3 untouched", orig_tl.GetTrackCount("video") == 3, f"V tracks={orig_tl.GetTrackCount('video')}")
    check("Original audio track count 3 untouched", orig_tl.GetTrackCount("audio") == 3, f"A tracks={orig_tl.GetTrackCount('audio')}")
    check("Original subtitle cue count 45 untouched", len(orig_tl.GetItemListInTrack("subtitle", 1) or []) == EXPECTED_SUBTITLE_COUNT, f"Cues={len(orig_tl.GetItemListInTrack('subtitle', 1) or [])}")

    # Test 8: QC Still Files Exist
    qc_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qc_stills")
    stills = ["split_screen_normal_216500.png", "reaction_gif_safe_218650.png", "vtuber_focus_zoom_219300.png"]
    still_checks = []
    for st in stills:
        st_path = os.path.join(qc_dir, st)
        exists = os.path.exists(st_path) and os.path.getsize(st_path) > 1000000
        still_checks.append(exists)
    check("QC stills generated and valid (>1MB PNG)", all(still_checks), f"Verified {len(still_checks)} stills in {qc_dir}")

    print("-" * 70)
    if failures:
        print(f"[RESULT] AUDIT FAILED with {len(failures)} failures:")
        for f in failures:
            print("  -", f)
        sys.exit(1)
    else:
        print("[RESULT] AUDIT PASSED 100%! All Milestone 2 requirements verified.")
        sys.exit(0)


if __name__ == "__main__":
    main()
