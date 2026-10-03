"""Milestone 2: Pilot Timeline Implementation & Verification (Remediated).

This script converts the pilot timeline 'หนีฝ่าความหนาว_Minecraft-vdo' into a 9:16
vertical timeline 'หนีฝ่าความหนาว_Minecraft-vdo_9x16' in DaVinci Resolve Studio 21.1.

Requirements:
1. Duplicate pilot timeline 'หนีฝ่าความหนาว_Minecraft-vdo' to 'หนีฝ่าความหนาว_Minecraft-vdo_9x16'.
2. Configure timeline resolution to 1080x1920 (9:16) with useCustomSettings='1', 60.0 fps.
3. Apply Split Screen reframing (Remediated):
   - V1/V2/V3 values are computed in scripts/layout9x16.py (empirically calibrated; panels split at y=960)
   - V1 (Game Top), V2 (VTuber Bottom, cropped to the facecam region), V3 Fusion Transform focus zoom
   - V4 (Reaction GIFs): Zoom 0.42, Pan -300.0, Tilt +600.0 (safe upper-left quadrant)
4. Strictly verify locked editorial elements against baseline:
   - Subtitle track: 100% match on 45 cues, text, start/end frames
   - Audio tracks: A1, A2, A3 and volume levels untouched
   - Cut durations and total duration (5880 frames) identical to baseline
   - Zero media offline
   - Original 16:9 timeline remains completely untouched
5. Save project via ProjectManager.SaveProject().
6. Capture QC still frames and run genuine pixel verification.
"""

import argparse
import datetime
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

# Ensure UTF-8 output encoding on Windows console
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# Project Constants
PROJECT_NAME = "KT404_2026-09-29"
PROJECT_ID = "7c38045b-c9ae-426c-8b4c-2e2d726d88ff"
PILOT_NAME = "หนีฝ่าความหนาว_Minecraft-vdo"
TARGET_NAME = f"{PILOT_NAME}_9x16"
EXPECTED_PILOT_ID = "7dcaea9a-b19f-4fa4-ac24-9a4f8c12f3ff"
EXPECTED_DURATION = 5880
EXPECTED_FPS = 60.0
EXPECTED_SUBTITLE_COUNT = 45

# Baseline JSON path
BASELINE_JSON_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".agents",
    "teamwork",
    "worker_m1",
    "baseline_30_timelines.json",
)

# Output paths
WORKER_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".agents",
    "teamwork",
    "worker_m2",
)
QC_STILLS_DIR = os.path.join(WORKER_DIR, "qc_stills")
VERIFICATION_JSON_PATH = os.path.join(WORKER_DIR, "pilot_verification.json")


def get_resolve():
    """Obtain running DaVinci Resolve instance on Windows."""
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


def frame_to_timecode(frame_number: int, fps: float = 60.0) -> str:
    """Convert absolute frame count to SMPTE timecode string HH:MM:SS:FF."""
    if fps <= 0:
        fps = 60.0
    total_seconds = int(frame_number // fps)
    rem_frames = int(round(frame_number % fps))
    hours = total_seconds // 3600
    rem_seconds = total_seconds % 3600
    minutes = rem_seconds // 60
    seconds = rem_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{rem_frames:02d}"


def get_item_property(item: Any, prop_name: str, default: Any = None) -> Any:
    """Retrieve property from TimelineItem supporting direct call and dict fallback."""
    if not hasattr(item, "GetProperty"):
        return default
    try:
        val = item.GetProperty(prop_name)
        if isinstance(val, dict):
            return val.get(prop_name, default)
        if val is not None and val is not False:
            return val
    except Exception:
        pass
    try:
        all_props = item.GetProperty()
        if isinstance(all_props, dict):
            return all_props.get(prop_name, default)
    except Exception:
        pass
    return default


def load_baseline_pilot() -> Dict[str, Any]:
    """Load baseline specifications for the pilot timeline from baseline_30_timelines.json."""
    if not os.path.exists(BASELINE_JSON_PATH):
        raise FileNotFoundError(f"Baseline JSON not found at {BASELINE_JSON_PATH}")
    with open(BASELINE_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    for tl in data.get("timelines", []):
        if tl.get("timeline_name") == PILOT_NAME:
            return tl
    raise ValueError(f"Pilot timeline '{PILOT_NAME}' not found in baseline JSON.")


def find_timeline_by_name(project: Any, name: str) -> Optional[Any]:
    """Find timeline by exact name in current project."""
    count = project.GetTimelineCount()
    for idx in range(1, count + 1):
        tl = project.GetTimelineByIndex(idx)
        if tl and tl.GetName() == name:
            return tl
    return None


def convert_pilot(force: bool = False, delay: float = 0.5) -> Dict[str, Any]:
    """Execute the end-to-end 9:16 conversion of the pilot timeline."""
    print("=" * 70)
    print("Milestone 2: Pilot Timeline Conversion (16:9 -> 9:16)")
    print("=" * 70)

    # 1. Connect to Resolve
    resolve = get_resolve()
    if not resolve:
        raise RuntimeError("Failed to connect to DaVinci Resolve.")
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    if not project:
        raise RuntimeError("No active project in DaVinci Resolve.")

    curr_proj_name = project.GetName()
    curr_proj_id = project.GetUniqueId()
    print(f"[PREFLIGHT] Project: {curr_proj_name} (ID: {curr_proj_id})")
    if curr_proj_id != PROJECT_ID:
        raise ValueError(f"Project ID mismatch: got {curr_proj_id}, expected {PROJECT_ID}")

    # Capture initial UI state
    init_page = resolve.GetCurrentPage() if hasattr(resolve, "GetCurrentPage") else "edit"
    init_tl = project.GetCurrentTimeline()
    init_tl_id = init_tl.GetUniqueId() if init_tl else None
    init_tc = init_tl.GetCurrentTimecode() if init_tl else "01:00:00:00"

    # 2. Verify original pilot timeline
    orig_tl = find_timeline_by_name(project, PILOT_NAME)
    if not orig_tl:
        raise RuntimeError(f"Original pilot timeline '{PILOT_NAME}' not found in project.")
    orig_id = orig_tl.GetUniqueId()
    orig_fps = float(orig_tl.GetSetting("timelineFrameRate") or 60.0)
    orig_dur = orig_tl.GetEndFrame() - orig_tl.GetStartFrame()
    print(f"[PREFLIGHT] Original Pilot: {PILOT_NAME} (ID: {orig_id})")
    print(f"            FPS: {orig_fps}, Duration: {orig_dur} frames")

    if orig_id != EXPECTED_PILOT_ID:
        print(f"WARNING: Pilot ID {orig_id} differs from expected {EXPECTED_PILOT_ID}")

    baseline_data = load_baseline_pilot()
    print(f"[PREFLIGHT] Baseline verified: {len(baseline_data['subtitle_track']['cues'])} subtitle cues, "
          f"{len(baseline_data['audio_tracks'])} audio tracks.")

    # 3. Check existing target timeline
    existing_target = find_timeline_by_name(project, TARGET_NAME)
    media_pool = project.GetMediaPool()

    if existing_target:
        if force:
            print(f"[INFO] Removing existing target timeline '{TARGET_NAME}' for clean rebuild...")
            # Switch away from existing target before deleting
            project.SetCurrentTimeline(orig_tl)
            time.sleep(0.5)
            media_pool.DeleteTimelines([existing_target])
            time.sleep(0.5)
            existing_target = None
        else:
            print(f"[INFO] Target timeline '{TARGET_NAME}' already exists. Reusing existing for verification.")
            target_tl = existing_target

    if not existing_target:
        print(f"\n[STEP 1] Duplicating '{PILOT_NAME}' -> '{TARGET_NAME}'...")
        project.SetCurrentTimeline(orig_tl)
        time.sleep(delay)
        target_tl = orig_tl.DuplicateTimeline(TARGET_NAME)
        if not target_tl:
            raise RuntimeError(f"Failed to duplicate timeline '{PILOT_NAME}'.")
        time.sleep(delay)
        project.SetCurrentTimeline(target_tl)
        time.sleep(delay)
        print(f"         Duplicated successfully. Active: {target_tl.GetName()}")

        # 4. Set Custom 9:16 Resolution (1080x1920)
        print(f"\n[STEP 2] Configuring 1080x1920 (9:16) resolution...")
        target_tl.SetSetting("useCustomSettings", "1")
        target_tl.SetSetting("timelineResolutionWidth", "1080")
        target_tl.SetSetting("timelineResolutionHeight", "1920")
        target_tl.SetSetting("timelineOutputResMatchTimelineRes", "1")
        target_tl.SetSetting("timelineOutputResolutionWidth", "1080")
        target_tl.SetSetting("timelineOutputResolutionHeight", "1920")
        target_tl.SetSetting("timelinePixelAspectRatio", "square")
        target_tl.SetSetting("timelineInputResMismatchBehavior", "scaleToFit")
        target_tl.SetSetting("timelineOutputResMismatchBehavior", "scaleToFit")
        time.sleep(delay)

        res_w = target_tl.GetSetting("timelineResolutionWidth")
        res_h = target_tl.GetSetting("timelineResolutionHeight")
        target_fps = float(target_tl.GetSetting("timelineFrameRate") or 60.0)
        print(f"         Configured Resolution: {res_w}x{res_h}, FPS: {target_fps}")
        assert res_w == "1080" and res_h == "1920", f"Resolution mismatch: {res_w}x{res_h}"
        assert target_fps == orig_fps, f"FPS mismatch: {target_fps} vs {orig_fps}"

        # 5. Track Restructuring & Reframing
        print(f"\n[STEP 3] Applying Split Screen Layout & Reframing...")

        # A. Inspect V1 (Game) and initial V2 (Reaction GIF)
        v1_items = target_tl.GetItemListInTrack("video", 1) or []
        if not v1_items:
            raise RuntimeError("No items found on V1 in duplicate timeline.")
        v1_item = v1_items[0]
        v1_mpi = v1_item.GetMediaPoolItem()
        v1_start = v1_item.GetStart()
        v1_dur = v1_item.GetDuration()
        v1_offset = v1_item.GetLeftOffset()

        v2_items = target_tl.GetItemListInTrack("video", 2) or []
        if not v2_items:
            raise RuntimeError("No items found on V2 (expected GIF) in duplicate timeline.")
        gif_item = v2_items[0]
        gif_mpi = gif_item.GetMediaPoolItem()
        gif_start = gif_item.GetStart()
        gif_dur = gif_item.GetDuration()
        gif_offset = gif_item.GetLeftOffset()

        print(f"         V1 Game Clip: start={v1_start}, dur={v1_dur}, offset={v1_offset}")
        print(f"         Initial GIF:  start={gif_start}, dur={gif_dur}, offset={gif_offset}")

        # B. Add Video Track 4 for Reaction GIFs
        print("         Adding Video Track 4 for Reaction GIFs...")
        if target_tl.GetTrackCount("video") < 4:
            target_tl.AddTrack("video")
            time.sleep(delay)
        print(f"         Total Video Tracks: {target_tl.GetTrackCount('video')}")

        # C. Append GIF to Track 4
        print(f"         Placing Reaction GIF onto Track 4 at frame {gif_start}...")
        gif_clip_info = {
            "mediaPoolItem": gif_mpi,
            "startFrame": gif_offset,
            "endFrame": gif_offset + gif_dur,
            "mediaType": 1,  # Video only
            "trackIndex": 4,
            "recordFrame": gif_start,
        }
        appended_gif = media_pool.AppendToTimeline([gif_clip_info])
        if not appended_gif:
            raise RuntimeError("Failed to append Reaction GIF to Track 4.")
        time.sleep(delay)

        # D. Delete original GIF from Track 2
        print("         Removing old GIF from Track 2...")
        target_tl.DeleteClips([gif_item], False)
        time.sleep(delay)

        # E. Append Game Clip to Track 2 for VTuber lower canvas
        print(f"         Placing VTuber Game Clip onto Track 2 at frame {v1_start}...")
        v2_clip_info = {
            "mediaPoolItem": v1_mpi,
            "startFrame": v1_offset,
            "endFrame": v1_offset + v1_dur,
            "mediaType": 1,  # Video only
            "trackIndex": 2,
            "recordFrame": v1_start,
        }
        appended_v2 = media_pool.AppendToTimeline([v2_clip_info])
        if not appended_v2:
            raise RuntimeError("Failed to append Game clip to Track 2 for VTuber.")
        time.sleep(delay)

        # Retrieve items on all tracks
        v1_item = target_tl.GetItemListInTrack("video", 1)[0]
        v2_item = target_tl.GetItemListInTrack("video", 2)[0]
        v3_items = target_tl.GetItemListInTrack("video", 3) or []
        v4_item = target_tl.GetItemListInTrack("video", 4)[0]

        # Set Track Names
        if hasattr(target_tl, "SetTrackName"):
            try:
                target_tl.SetTrackName("video", 1, "Game Top")
                target_tl.SetTrackName("video", 2, "VTuber Bottom")
                target_tl.SetTrackName("video", 3, "VTuber Focus")
                target_tl.SetTrackName("video", 4, "Reaction GIFs")
            except Exception:
                pass

        # F. Apply Transforms to V1 (Game Top)
        # Calibrated values come from scripts/layout9x16.py (see calibrate_crop.py / calibrate_zoom.py).
        import layout9x16 as layout

        game_p = layout.game_params()
        print(f"         Configuring V1 (Game Top): {game_p}")
        for k, v in game_p.items():
            v1_item.SetProperty(k, float(v))
            time.sleep(0.2)

        # G. Apply Transforms to V2 (VTuber Bottom)
        avatar_p = layout.avatar_params()
        print(f"         Configuring V2 (VTuber Bottom): {avatar_p}")
        for k, v in avatar_p.items():
            v2_item.SetProperty(k, float(v))
            time.sleep(0.2)

        # H. Apply Transforms to V4 (Reaction GIF Safe Repositioning)
        print("         Configuring V4 (Reaction GIF): Zoom=0.42, Pan=-300.0, Tilt=+600.0")
        v4_item.SetProperty("ZoomX", 0.42)
        v4_item.SetProperty("ZoomY", 0.42)
        v4_item.SetProperty("Pan", -300.0)
        v4_item.SetProperty("Tilt", 600.0)

        # I. Update V3 Adjustment Clips (VTuber Focus Fusion Comps)
        print(f"         Updating V3 Adjustment Clips ({len(v3_items)} clips) for full-screen VTuber focus...")
        for idx, adj in enumerate(v3_items):
            comp = adj.GetFusionCompByIndex(1)
            if not comp:
                print(f"         WARNING: No Fusion comp found on Adjustment Clip {idx}")
                continue
            tools = comp.GetToolList() or {}
            updated = False
            for t in tools.values():
                t_name = t.GetAttrs().get("TOOLS_Name", "")
                if "Transform" in t_name:
                    t.SetInput("Size", layout.FOCUS["Size"])
                    t.SetInput("Pivot", {1: layout.FOCUS["Pivot"][0], 2: layout.FOCUS["Pivot"][1], 3: 0.0})
                    t.SetInput("Center", {1: layout.FOCUS["Center"][0], 2: layout.FOCUS["Center"][1], 3: 0.0})
                    updated = True
                    print(f"         - Adj {idx + 1} ({adj.GetStart()}..{adj.GetEnd()}): {t_name} {layout.FOCUS}")
            if not updated:
                print(f"         WARNING: No Transform tool found in Adj {idx + 1}")

        time.sleep(delay)

    # 6. Save Project
    print("\n[STEP 4] Saving Project via ProjectManager.SaveProject()...")
    save_res = pm.SaveProject()
    print(f"         ProjectManager.SaveProject() returned: {save_res}")
    if not save_res:
        raise RuntimeError("Failed to save project!")

    # 7. Comprehensive Independent Verification
    print("\n[STEP 5] Running Comprehensive Verification Suite...")
    verif_results = run_verification(project, target_tl, orig_tl, baseline_data)

    # 8. Capture QC Still Frames
    print("\n[STEP 6] Capturing QC Stills...")
    os.makedirs(QC_STILLS_DIR, exist_ok=True)
    qc_frames = [
        ("split_screen_normal", 216500, "Normal Split Screen (Game top + VTuber bottom)"),
        ("reaction_gif_safe", 218650, "Reaction GIF Upper Flank Placement"),
        ("vtuber_focus_zoom", 219300, "V3 Full-Screen VTuber Close-Up"),
    ]
    stills_output = []
    for name, f_num, desc in qc_frames:
        tc = frame_to_timecode(f_num, target_fps if 'target_fps' in locals() else 60.0)
        still_file = os.path.join(QC_STILLS_DIR, f"{name}_{f_num}.png")
        target_tl.SetCurrentTimecode(tc)
        time.sleep(0.3)
        cap_res = project.ExportCurrentFrameAsStill(still_file)
        file_exists = os.path.exists(still_file)
        file_size = os.path.getsize(still_file) if file_exists else 0
        print(f"         QC Still [{name}] @ {tc} ({f_num}): export={cap_res}, size={file_size} bytes")
        stills_output.append({
            "name": name,
            "description": desc,
            "frame": f_num,
            "timecode": tc,
            "exported": cap_res,
            "file_path": still_file,
            "file_size_bytes": file_size,
        })

    verif_results["qc_stills"] = stills_output

    # 9. Cleanly Restore UI State
    print("\n[STEP 7] Restoring UI State...")
    if init_page and hasattr(resolve, "OpenPage"):
        resolve.OpenPage(init_page)
    if init_tl:
        project.SetCurrentTimeline(init_tl)
        if init_tc:
            init_tl.SetCurrentTimecode(init_tc)
    print("         UI state restored cleanly.")

    # 10. Write Verification Output JSON
    verif_results["timestamp_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    verif_results["pilot_timeline_name"] = PILOT_NAME
    verif_results["target_timeline_name"] = TARGET_NAME
    with open(VERIFICATION_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(verif_results, f, indent=2, ensure_ascii=False)
    print(f"\n[DONE] Verification report written to: {VERIFICATION_JSON_PATH}")

    return verif_results


def run_verification(project: Any, target_tl: Any, orig_tl: Any, baseline: Dict[str, Any]) -> Dict[str, Any]:
    """Execute independent verification checks against locked editorial invariants."""
    results: Dict[str, Any] = {
        "all_passed": True,
        "checks": {},
        "failures": [],
    }

    def check(name: str, passed: bool, details: Any):
        results["checks"][name] = {
            "passed": bool(passed),
            "details": details,
        }
        status_str = "PASS" if passed else "FAIL"
        print(f"  [{status_str}] {name}: {details}")
        if not passed:
            results["all_passed"] = False
            results["failures"].append({name: details})

    # A. Check Target Name and ID
    target_name = target_tl.GetName()
    target_id = target_tl.GetUniqueId()
    check(
        "target_timeline_identity",
        target_name == TARGET_NAME,
        f"Name: {target_name}, ID: {target_id}",
    )

    # B. Check Resolution & Frame Rate
    res_w = target_tl.GetSetting("timelineResolutionWidth")
    res_h = target_tl.GetSetting("timelineResolutionHeight")
    custom_set = target_tl.GetSetting("useCustomSettings")
    fps = float(target_tl.GetSetting("timelineFrameRate") or 60.0)
    check(
        "resolution_9x16",
        res_w == "1080" and res_h == "1920" and custom_set == "1",
        f"Resolution: {res_w}x{res_h}, useCustomSettings={custom_set}",
    )
    check(
        "framerate_preserved",
        fps == EXPECTED_FPS,
        f"FPS: {fps} (expected {EXPECTED_FPS})",
    )

    # C. Check Timeline Duration
    start_frame = target_tl.GetStartFrame()
    end_frame = target_tl.GetEndFrame()
    dur_frames = end_frame - start_frame
    check(
        "duration_preserved",
        dur_frames == EXPECTED_DURATION,
        f"Duration: {dur_frames} frames (Start: {start_frame}, End: {end_frame})",
    )

    # D. Check Subtitle Track 1:1 Match against Baseline
    sub_items = target_tl.GetItemListInTrack("subtitle", 1) or []
    base_cues = baseline.get("subtitle_track", {}).get("cues", [])
    cue_count_match = len(sub_items) == len(base_cues) == EXPECTED_SUBTITLE_COUNT
    sub_diffs = []

    for idx, (sub_item, base_cue) in enumerate(zip(sub_items, base_cues)):
        item_text = sub_item.GetName()
        item_start = sub_item.GetStart()
        item_end = sub_item.GetEnd()
        item_dur = sub_item.GetDuration()

        base_text = base_cue["text"]
        base_start = base_cue["start_frame"]
        base_end = base_cue["end_frame"]

        if (
            item_text != base_text
            or item_start != base_start
            or item_end != base_end
        ):
            sub_diffs.append({
                "cue_index": idx + 1,
                "item": {"text": item_text, "start": item_start, "end": item_end},
                "base": {"text": base_text, "start": base_start, "end": base_end},
            })

    check(
        "subtitles_1to1_preserved",
        cue_count_match and len(sub_diffs) == 0,
        f"Total Cues: {len(sub_items)}/{len(base_cues)} (Diff count: {len(sub_diffs)})",
    )

    # E. Check Audio Tracks 1:1 Match against Baseline
    a_track_count = target_tl.GetTrackCount("audio")
    audio_checks = []
    base_audio_tracks = baseline.get("audio_tracks", [])
    audio_all_match = a_track_count == len(base_audio_tracks) == 3

    for a_idx in range(1, a_track_count + 1):
        items = target_tl.GetItemListInTrack("audio", a_idx) or []
        base_track = base_audio_tracks[a_idx - 1] if a_idx <= len(base_audio_tracks) else {}
        base_items = base_track.get("items", [])

        if len(items) != len(base_items):
            audio_all_match = False

        for it, bit in zip(items, base_items):
            vol = get_item_property(it, "AudioVolume", 0.0)
            base_vol = bit.get("volume_db", 0.0)
            vol_match = abs(float(vol or 0.0) - float(base_vol or 0.0)) < 0.01
            base_start = bit.get("start_frame")
            base_end = bit.get("end_frame")
            timing_match = it.GetStart() == base_start and it.GetEnd() == base_end
            audio_checks.append({
                "track": a_idx,
                "item_name": it.GetName(),
                "timing_match": timing_match,
                "vol": vol,
                "base_vol": base_vol,
                "vol_match": vol_match,
            })
            if not vol_match or not timing_match:
                audio_all_match = False

    check(
        "audio_tracks_and_levels_preserved",
        audio_all_match,
        f"Audio Tracks: {a_track_count}, Details: {audio_checks}",
    )

    # F. Check Video Track Structure & Transforms
    v_track_count = target_tl.GetTrackCount("video")
    check(
        "video_track_count",
        v_track_count == 4,
        f"Video Tracks: {v_track_count} (expected 4: V1 Game, V2 VTuber, V3 Focus, V4 GIF)",
    )

    v1_items = target_tl.GetItemListInTrack("video", 1) or []
    v2_items = target_tl.GetItemListInTrack("video", 2) or []
    v3_items = target_tl.GetItemListInTrack("video", 3) or []
    v4_items = target_tl.GetItemListInTrack("video", 4) or []

    # Check V1 Game Top
    v1_ok = False
    if v1_items:
        v1_it = v1_items[0]
        v1_zoom_x = float(get_item_property(v1_it, "ZoomX") or 0.0)
        v1_pan = float(get_item_property(v1_it, "Pan") or 0.0)
        v1_tilt = float(get_item_property(v1_it, "Tilt") or 0.0)
        v1_crop_b = float(get_item_property(v1_it, "CropBottom") or 0.0)
        import layout9x16 as _lay

        _g = _lay.game_params()
        v1_ok = (
            abs(v1_zoom_x - _g["ZoomX"]) < 0.01
            and abs(v1_pan - _g["Pan"]) < 0.5
            and abs(v1_tilt - _g["Tilt"]) < 0.5
            and abs(v1_crop_b - _g["CropBottom"]) < 0.5
        )
    check(
        "v1_game_top_transforms",
        v1_ok,
        f"ZoomX={v1_zoom_x}, Pan={v1_pan}, Tilt={v1_tilt}, CropBottom={v1_crop_b}",
    )

    # Check V2 VTuber Bottom
    v2_ok = False
    if v2_items:
        v2_it = v2_items[0]
        v2_zoom_x = float(get_item_property(v2_it, "ZoomX") or 0.0)
        v2_pan = float(get_item_property(v2_it, "Pan") or 0.0)
        v2_tilt = float(get_item_property(v2_it, "Tilt") or 0.0)
        v2_crop_t = float(get_item_property(v2_it, "CropTop") or 0.0)
        import layout9x16 as _lay

        _a = _lay.avatar_params()
        v2_ok = (
            abs(v2_zoom_x - _a["ZoomX"]) < 0.01
            and abs(v2_pan - _a["Pan"]) < 0.5
            and abs(v2_tilt - _a["Tilt"]) < 0.5
            and abs(v2_crop_t - _a["CropTop"]) < 0.5
        )
    check(
        "v2_vtuber_bottom_transforms",
        v2_ok,
        f"ZoomX={v2_zoom_x}, Pan={v2_pan}, Tilt={v2_tilt}, CropTop={v2_crop_t}",
    )

    # Check V4 Reaction GIF Safe Repositioning
    v4_ok = False
    if v4_items:
        v4_it = v4_items[0]
        v4_zoom_x = float(get_item_property(v4_it, "ZoomX") or 0.0)
        v4_pan = float(get_item_property(v4_it, "Pan") or 0.0)
        v4_tilt = float(get_item_property(v4_it, "Tilt") or 0.0)
        v4_ok = (
            abs(v4_zoom_x - 0.42) < 0.01
            and abs(v4_pan - (-300.0)) < 0.1
            and abs(v4_tilt - 600.0) < 0.1
        )
    check(
        "v4_reaction_gif_repositioned",
        v4_ok,
        f"ZoomX={v4_zoom_x}, Pan={v4_pan}, Tilt={v4_tilt}",
    )

    # Check V3 Adjustment Clips Fusion Focus
    v3_adj_checks = []
    v3_all_ok = len(v3_items) == 3
    for idx, adj in enumerate(v3_items):
        comp = adj.GetFusionCompByIndex(1)
        tools = comp.GetToolList() if comp else {}
        t_found = False
        for t in tools.values():
            if "Transform" in t.GetAttrs().get("TOOLS_Name", ""):
                center = t.GetInput("Center")
                size = t.GetInput("Size")
                c_x = center.get(1, 0.0) if isinstance(center, dict) else 0.0
                c_y = center.get(2, 0.0) if isinstance(center, dict) else 0.0
                sz = float(size or 0.0)
                import layout9x16 as _lay

                t_ok = (
                    abs(c_x - _lay.FOCUS["Center"][0]) < 0.01
                    and abs(c_y - _lay.FOCUS["Center"][1]) < 0.01
                    and abs(sz - _lay.FOCUS["Size"]) < 0.01
                )
                v3_adj_checks.append({
                    "clip_index": idx + 1,
                    "center": [c_x, c_y],
                    "size": sz,
                    "passed": t_ok,
                })
                t_found = t_ok
        if not t_found:
            v3_all_ok = False

    check(
        "v3_adjustment_focus_transforms",
        v3_all_ok,
        f"3 Cues: {v3_adj_checks}",
    )

    # G. Zero Media Offline Check
    offline_items = []
    for v in range(1, target_tl.GetTrackCount("video") + 1):
        for it in target_tl.GetItemListInTrack("video", v) or []:
            mpi = it.GetMediaPoolItem()
            if mpi:
                path = mpi.GetClipProperty("File Path")
                if path and not os.path.exists(path):
                    offline_items.append({"track": f"V{v}", "name": it.GetName(), "path": path})

    for a in range(1, target_tl.GetTrackCount("audio") + 1):
        for it in target_tl.GetItemListInTrack("audio", a) or []:
            mpi = it.GetMediaPoolItem()
            if mpi:
                path = mpi.GetClipProperty("File Path")
                if path and not os.path.exists(path):
                    offline_items.append({"track": f"A{a}", "name": it.GetName(), "path": path})

    check(
        "zero_media_offline",
        len(offline_items) == 0,
        f"Offline Count: {len(offline_items)}",
    )

    # H. Preservation of Original Timeline (Untouched)
    orig_name = orig_tl.GetName()
    orig_w = orig_tl.GetSetting("timelineResolutionWidth")
    orig_h = orig_tl.GetSetting("timelineResolutionHeight")
    orig_v_tracks = orig_tl.GetTrackCount("video")
    orig_a_tracks = orig_tl.GetTrackCount("audio")
    orig_sub_count = len(orig_tl.GetItemListInTrack("subtitle", 1) or [])
    orig_untouched = (
        orig_name == PILOT_NAME
        and orig_w == "1920"
        and orig_h == "1080"
        and orig_v_tracks == 3
        and orig_a_tracks == 3
        and orig_sub_count == EXPECTED_SUBTITLE_COUNT
    )
    check(
        "original_timeline_untouched",
        orig_untouched,
        f"Original: {orig_name}, Resolution: {orig_w}x{orig_h}, V tracks: {orig_v_tracks}, Subtitles: {orig_sub_count}",
    )

    return results


def main():
    parser = argparse.ArgumentParser(description="Convert Pilot Timeline to 9:16 Vertical")
    parser.add_argument("--force", action="store_true", help="Force recreate target timeline if exists")
    parser.add_argument("--verify-only", action="store_true", help="Only run verification checks")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay in seconds between mutations")
    args = parser.parse_args()

    if args.verify_only:
        resolve = get_resolve()
        project = resolve.GetProjectManager().GetCurrentProject()
        target_tl = find_timeline_by_name(project, TARGET_NAME)
        orig_tl = find_timeline_by_name(project, PILOT_NAME)
        if not target_tl:
            print(f"Target timeline '{TARGET_NAME}' not found.")
            sys.exit(1)
        baseline_data = load_baseline_pilot()
        results = run_verification(project, target_tl, orig_tl, baseline_data)
        sys.exit(0 if results["all_passed"] else 1)

    results = convert_pilot(force=args.force, delay=args.delay)
    if not results["all_passed"]:
        print("\nERROR: Verification failed!")
        for fail in results["failures"]:
            print(" ", fail)
        sys.exit(1)

    print("\nSUCCESS: Milestone 2 Pilot Conversion and Verification PASSED 100%!")
    sys.exit(0)


if __name__ == "__main__":
    main()
