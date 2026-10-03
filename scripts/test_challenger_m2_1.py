"""Challenger M2-1 Independent Verification & Stress-Test Script.

Empirically tests and stress-tests:
1. Timeline resolution (1080x1920) and frame rate (60.0 fps).
2. V1 Game Top transforms: Zoom=1.60, Pan=0.0, Tilt=+480.0, CropBottom=486.0.
3. V2 VTuber Bottom transforms: Zoom=2.60, Pan=-936.0, Tilt=-200.0, CropTop=480.0.
4. V3 Adjustment Clip Fusion tools: Center=(0.50, 0.25), Size=2.0 on all 3 adjustment clips.
5. V4 Reaction GIF properties: Pan=-300.0, Tilt=+600.0, Zoom=0.42.
6. Zero media offline across all tracks.
7. Original 16:9 timeline non-destructive preservation.
8. 1:1 Subtitle and Audio preservation against baseline.
"""

import json
import math
import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

PROJECT_NAME = "KT404_2026-09-29"
PROJECT_ID = "7c38045b-c9ae-426c-8b4c-2e2d726d88ff"
ORIGINAL_NAME = "หนีฝ่าความหนาว_Minecraft-vdo"
TARGET_NAME = "หนีฝ่าความหนาว_Minecraft-vdo_9x16"
EXPECTED_ORIGINAL_ID = "7dcaea9a-b19f-4fa4-ac24-9a4f8c12f3ff"
EXPECTED_DURATION = 5880
EXPECTED_FPS = 60.0
EXPECTED_SUBTITLE_COUNT = 45


def get_resolve():
    """Connect to live DaVinci Resolve Studio instance."""
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


def get_prop(item: Any, key: str, default: Any = None) -> Any:
    """Safely extract property from a TimelineItem."""
    if not hasattr(item, "GetProperty"):
        return default
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


def main() -> int:
    print("=" * 80)
    print("CHALLENGER M2-1: EMPIRICAL VERIFICATION & STRESS TEST")
    print("=" * 80)

    results = {
        "success": True,
        "tests": [],
        "errors": [],
        "evidence": {}
    }

    def record_test(name: str, passed: bool, observed: Any, expected: Any, details: str = ""):
        test_entry = {
            "name": name,
            "passed": bool(passed),
            "observed": observed,
            "expected": expected,
            "details": details,
        }
        results["tests"].append(test_entry)
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {name}")
        print(f"       Expected: {expected}")
        print(f"       Observed: {observed}")
        if details:
            print(f"       Details:  {details}")
        if not passed:
            results["success"] = False
            results["errors"].append(test_entry)

    # 1. Connect to Resolve
    resolve = get_resolve()
    if not resolve:
        print("[FATAL] Could not connect to DaVinci Resolve Scripting API.")
        return 1

    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    if not proj:
        print("[FATAL] No project currently open in Resolve.")
        return 1

    proj_name = proj.GetName()
    proj_id = proj.GetUniqueId()
    record_test(
        "Project Connection & ID Verification",
        proj_name == PROJECT_NAME and proj_id == PROJECT_ID,
        {"name": proj_name, "id": proj_id},
        {"name": PROJECT_NAME, "id": PROJECT_ID}
    )

    # 2. Locate Timelines
    orig_tl = None
    target_tl = None
    tl_count = proj.GetTimelineCount()
    for i in range(1, tl_count + 1):
        tl = proj.GetTimelineByIndex(i)
        if tl.GetName() == TARGET_NAME:
            target_tl = tl
        elif tl.GetName() == ORIGINAL_NAME:
            orig_tl = tl

    record_test(
        "Target Timeline Existence",
        target_tl is not None,
        target_tl.GetName() if target_tl else None,
        TARGET_NAME
    )
    record_test(
        "Original Timeline Existence",
        orig_tl is not None,
        orig_tl.GetName() if orig_tl else None,
        ORIGINAL_NAME
    )

    if not target_tl or not orig_tl:
        print("[FATAL] Required timelines not found. Aborting.")
        return 1

    # 3. Check Target Timeline Resolution, FPS, and Duration
    res_w = target_tl.GetSetting("timelineResolutionWidth")
    res_h = target_tl.GetSetting("timelineResolutionHeight")
    custom_set = target_tl.GetSetting("useCustomSettings")
    fps_val = float(target_tl.GetSetting("timelineFrameRate") or 0.0)
    dur_frames = target_tl.GetEndFrame() - target_tl.GetStartFrame()

    record_test(
        "Target Resolution (1080x1920 9:16)",
        res_w == "1080" and res_h == "1920",
        f"{res_w}x{res_h}",
        "1080x1920"
    )
    record_test(
        "Target useCustomSettings == 1",
        custom_set == "1",
        custom_set,
        "1"
    )
    record_test(
        "Target Timeline Frame Rate (60.0 fps)",
        math.isclose(fps_val, EXPECTED_FPS, abs_tol=0.01),
        fps_val,
        EXPECTED_FPS
    )
    record_test(
        "Target Timeline Duration (5880 frames)",
        dur_frames == EXPECTED_DURATION,
        dur_frames,
        EXPECTED_DURATION
    )

    # 4. Check Track Counts
    v_track_count = target_tl.GetTrackCount("video")
    a_track_count = target_tl.GetTrackCount("audio")
    sub_track_count = target_tl.GetTrackCount("subtitle")

    record_test(
        "Target Video Track Count (4 tracks: V1-V4)",
        v_track_count == 4,
        v_track_count,
        4
    )
    record_test(
        "Target Audio Track Count (3 tracks: A1-A3)",
        a_track_count == 3,
        a_track_count,
        3
    )

    # 5. Query V1 Item Properties (Game Top)
    v1_items = target_tl.GetItemListInTrack("video", 1) or []
    record_test("V1 Item Count >= 1", len(v1_items) >= 1, len(v1_items), ">= 1")
    if v1_items:
        v1_it = v1_items[0]
        v1_zx = float(get_prop(v1_it, "ZoomX", 0.0) or 0.0)
        v1_zy = float(get_prop(v1_it, "ZoomY", 0.0) or 0.0)
        v1_pan = float(get_prop(v1_it, "Pan", 0.0) or 0.0)
        v1_tilt = float(get_prop(v1_it, "Tilt", 0.0) or 0.0)
        v1_crop_b = float(get_prop(v1_it, "CropBottom", 0.0) or 0.0)

        record_test(
            "V1 Game Top: Zoom == 1.60",
            math.isclose(v1_zx, 1.60, abs_tol=0.01) and math.isclose(v1_zy, 1.60, abs_tol=0.01),
            f"ZoomX={v1_zx}, ZoomY={v1_zy}",
            "Zoom=1.60"
        )
        record_test(
            "V1 Game Top: Pan == 0.0",
            math.isclose(v1_pan, 0.0, abs_tol=0.1),
            v1_pan,
            0.0
        )
        record_test(
            "V1 Game Top: Tilt == +480.0",
            math.isclose(v1_tilt, 480.0, abs_tol=0.1),
            v1_tilt,
            480.0
        )
        record_test(
            "V1 Game Top: CropBottom == 486.0",
            math.isclose(v1_crop_b, 486.0, abs_tol=0.1),
            v1_crop_b,
            486.0
        )

    # 6. Query V2 Item Properties (VTuber Bottom)
    v2_items = target_tl.GetItemListInTrack("video", 2) or []
    record_test("V2 Item Count >= 1", len(v2_items) >= 1, len(v2_items), ">= 1")
    if v2_items:
        v2_it = v2_items[0]
        v2_zx = float(get_prop(v2_it, "ZoomX", 0.0) or 0.0)
        v2_zy = float(get_prop(v2_it, "ZoomY", 0.0) or 0.0)
        v2_pan = float(get_prop(v2_it, "Pan", 0.0) or 0.0)
        v2_tilt = float(get_prop(v2_it, "Tilt", 0.0) or 0.0)
        v2_crop_t = float(get_prop(v2_it, "CropTop", 0.0) or 0.0)

        record_test(
            "V2 VTuber Bottom: Zoom == 2.60",
            math.isclose(v2_zx, 2.60, abs_tol=0.01) and math.isclose(v2_zy, 2.60, abs_tol=0.01),
            f"ZoomX={v2_zx}, ZoomY={v2_zy}",
            "Zoom=2.60"
        )
        record_test(
            "V2 VTuber Bottom: Pan == -936.0",
            math.isclose(v2_pan, -936.0, abs_tol=0.1),
            v2_pan,
            -936.0
        )
        record_test(
            "V2 VTuber Bottom: Tilt == -200.0",
            math.isclose(v2_tilt, -200.0, abs_tol=0.1),
            v2_tilt,
            -200.0
        )
        record_test(
            "V2 VTuber Bottom: CropTop == 480.0",
            math.isclose(v2_crop_t, 480.0, abs_tol=0.1),
            v2_crop_t,
            480.0
        )

    # 7. Query V3 Adjustment Clip Fusion Tools (VTuber Focus)
    v3_items = target_tl.GetItemListInTrack("video", 3) or []
    record_test(
        "V3 Adjustment Clip Count == 3",
        len(v3_items) == 3,
        len(v3_items),
        3
    )

    for idx, adj in enumerate(v3_items):
        comp = adj.GetFusionCompByIndex(1)
        tools = comp.GetToolList() if comp else {}
        matched_transform = None
        for t in tools.values():
            attrs = t.GetAttrs() or {}
            t_name = attrs.get("TOOLS_Name", "")
            if "Transform" in t_name:
                center = t.GetInput("Center")
                size = t.GetInput("Size")
                cx = center.get(1, 0.0) if isinstance(center, dict) else 0.0
                cy = center.get(2, 0.0) if isinstance(center, dict) else 0.0
                sz = float(size or 0.0)
                matched_transform = {
                    "tool_name": t_name,
                    "cx": cx,
                    "cy": cy,
                    "size": sz,
                    "start": adj.GetStart(),
                    "end": adj.GetEnd(),
                }
                break

        clip_valid = (
            matched_transform is not None
            and math.isclose(matched_transform["cx"], 0.50, abs_tol=0.01)
            and math.isclose(matched_transform["cy"], 0.25, abs_tol=0.01)
            and math.isclose(matched_transform["size"], 2.0, abs_tol=0.01)
        )
        record_test(
            f"V3 Adjustment Clip #{idx+1} Fusion Transform Center=(0.50, 0.25), Size=2.0",
            clip_valid,
            matched_transform,
            {"cx": 0.50, "cy": 0.25, "size": 2.0},
            f"Clip range: {adj.GetStart()}..{adj.GetEnd()}"
        )

    # 8. Query V4 GIF Properties (Reaction GIFs Safe Repositioning)
    v4_items = target_tl.GetItemListInTrack("video", 4) or []
    record_test("V4 Reaction GIF Count >= 1", len(v4_items) >= 1, len(v4_items), ">= 1")
    if v4_items:
        v4_it = v4_items[0]
        v4_zx = float(get_prop(v4_it, "ZoomX", 0.0) or 0.0)
        v4_zy = float(get_prop(v4_it, "ZoomY", 0.0) or 0.0)
        v4_pan = float(get_prop(v4_it, "Pan", 0.0) or 0.0)
        v4_tilt = float(get_prop(v4_it, "Tilt", 0.0) or 0.0)

        record_test(
            "V4 Reaction GIF: Zoom == 0.42",
            math.isclose(v4_zx, 0.42, abs_tol=0.01) and math.isclose(v4_zy, 0.42, abs_tol=0.01),
            f"ZoomX={v4_zx}, ZoomY={v4_zy}",
            "Zoom=0.42"
        )
        record_test(
            "V4 Reaction GIF: Pan == -300.0",
            math.isclose(v4_pan, -300.0, abs_tol=0.1),
            v4_pan,
            -300.0
        )
        record_test(
            "V4 Reaction GIF: Tilt == +600.0",
            math.isclose(v4_tilt, 600.0, abs_tol=0.1),
            v4_tilt,
            600.0
        )

    # 9. Verify Zero Media Offline
    offline_items = []
    total_clips_checked = 0

    for v in range(1, target_tl.GetTrackCount("video") + 1):
        items = target_tl.GetItemListInTrack("video", v) or []
        for it in items:
            total_clips_checked += 1
            mpi = it.GetMediaPoolItem()
            if mpi:
                path = mpi.GetClipProperty("File Path")
                if path and not os.path.exists(path):
                    offline_items.append({"track": f"V{v}", "name": it.GetName(), "path": path})

    for a in range(1, target_tl.GetTrackCount("audio") + 1):
        items = target_tl.GetItemListInTrack("audio", a) or []
        for it in items:
            total_clips_checked += 1
            mpi = it.GetMediaPoolItem()
            if mpi:
                path = mpi.GetClipProperty("File Path")
                if path and not os.path.exists(path):
                    offline_items.append({"track": f"A{a}", "name": it.GetName(), "path": path})

    record_test(
        "Zero Media Offline Across All Tracks",
        len(offline_items) == 0,
        {"offline_count": len(offline_items), "checked": total_clips_checked, "offline_items": offline_items},
        {"offline_count": 0}
    )

    # 10. Check Original Timeline Untouched (Non-Destructive Invariant)
    orig_name = orig_tl.GetName()
    orig_id = orig_tl.GetUniqueId()
    orig_w = orig_tl.GetSetting("timelineResolutionWidth")
    orig_h = orig_tl.GetSetting("timelineResolutionHeight")
    orig_v_cnt = orig_tl.GetTrackCount("video")
    orig_a_cnt = orig_tl.GetTrackCount("audio")
    orig_sub_cnt = len(orig_tl.GetItemListInTrack("subtitle", 1) or [])

    record_test(
        "Original Timeline Identity Untouched",
        orig_name == ORIGINAL_NAME and orig_id == EXPECTED_ORIGINAL_ID,
        {"name": orig_name, "id": orig_id},
        {"name": ORIGINAL_NAME, "id": EXPECTED_ORIGINAL_ID}
    )
    record_test(
        "Original Timeline Resolution Untouched (1920x1080)",
        orig_w == "1920" and orig_h == "1080",
        f"{orig_w}x{orig_h}",
        "1920x1080"
    )
    record_test(
        "Original Timeline Video Tracks Untouched (3 tracks)",
        orig_v_cnt == 3,
        orig_v_cnt,
        3
    )
    record_test(
        "Original Timeline Audio Tracks Untouched (3 tracks)",
        orig_a_cnt == 3,
        orig_a_cnt,
        3
    )
    record_test(
        "Original Timeline Subtitle Cues Untouched (45 cues)",
        orig_sub_cnt == EXPECTED_SUBTITLE_COUNT,
        orig_sub_cnt,
        EXPECTED_SUBTITLE_COUNT
    )

    # 11. Locked Editorial Preservation: Subtitles & Audio Match Between Target and Original
    target_subs = target_tl.GetItemListInTrack("subtitle", 1) or []
    orig_subs = orig_tl.GetItemListInTrack("subtitle", 1) or []

    sub_matches = len(target_subs) == len(orig_subs) == EXPECTED_SUBTITLE_COUNT
    sub_diffs = []
    if sub_matches:
        for i, (t_sub, o_sub) in enumerate(zip(target_subs, orig_subs)):
            t_name = t_sub.GetName()
            t_start = t_sub.GetStart()
            t_end = t_sub.GetEnd()
            o_name = o_sub.GetName()
            o_start = o_sub.GetStart()
            o_end = o_sub.GetEnd()
            if t_name != o_name or t_start != o_start or t_end != o_end:
                sub_diffs.append({"index": i+1, "target": (t_name, t_start, t_end), "orig": (o_name, o_start, o_end)})

    record_test(
        "Locked Subtitle Cues 1:1 Preservation",
        sub_matches and len(sub_diffs) == 0,
        {"total_cues": len(target_subs), "mismatches": len(sub_diffs)},
        {"total_cues": EXPECTED_SUBTITLE_COUNT, "mismatches": 0}
    )

    # Audio checks
    audio_diffs = []
    for a in range(1, 4):
        t_items = target_tl.GetItemListInTrack("audio", a) or []
        o_items = orig_tl.GetItemListInTrack("audio", a) or []
        if len(t_items) != len(o_items):
            audio_diffs.append(f"A{a} clip count {len(t_items)} vs {len(o_items)}")
        for t_it, o_it in zip(t_items, o_items):
            t_vol = float(get_prop(t_it, "AudioVolume", 0.0) or 0.0)
            o_vol = float(get_prop(o_it, "AudioVolume", 0.0) or 0.0)
            if not math.isclose(t_vol, o_vol, abs_tol=0.01):
                audio_diffs.append(f"A{a} volume mismatch {t_vol} vs {o_vol}")
            if t_it.GetStart() != o_it.GetStart() or t_it.GetEnd() != o_it.GetEnd():
                audio_diffs.append(f"A{a} timing mismatch {t_it.GetStart()}..{t_it.GetEnd()} vs {o_it.GetStart()}..{o_it.GetEnd()}")

    record_test(
        "Locked Audio Tracks 1:1 Preservation",
        len(audio_diffs) == 0,
        {"diffs": audio_diffs},
        {"diffs": []}
    )

    print("=" * 80)
    passed_count = sum(1 for t in results["tests"] if t["passed"])
    total_count = len(results["tests"])
    print(f"SUMMARY: {passed_count}/{total_count} tests PASSED.")

    # Write results to JSON in scripts output for audit
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "challenger_m2_1_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Audit results written to: {out_path}")

    if results["success"]:
        print("[VERDICT] ALL CHALLENGER TESTS PASSED EMPIRICALLY.")
        return 0
    else:
        print(f"[VERDICT] CHALLENGER FAILED with {len(results['errors'])} errors!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
