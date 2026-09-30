"""Pilot Implementation & Verification on Timeline 1 in DaVinci Resolve.

Targets:
- Project: KT404_2026-09-29
- Timeline 1: "ขุดมั่วเจอเหล็กกองใหญ่_Minecraft-vdo"
- Video 2: Centered GIFs (ZoomX=0.55, ZoomY=0.55, Pan=0, Tilt=0)
- Audio 2: SFX (AudioVolume=-11.0 dB)
- Audio 3: BGM (AudioVolume=-23.0 dB, 0.5s fade-in, 1.0s fade-out, spans full timeline)
- Subtitle 1: 51 cues untouched
- Mutation delay spacing: 1.2s between structural modifications
- Full readback verification and visual frame capture
"""

import json
import os
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional

# Ensure project root is in sys.path
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from scripts.enrichment_assets import get_resolve, ingest_enrichment_assets
from scripts.enrichment_engine import (
    plan_timeline_enrichment,
    apply_enrichment_plan,
)

TARGET_TIMELINE_INDEX = 1
TARGET_TIMELINE_NAME = "ขุดมั่วเจอเหล็กกองใหญ่_Minecraft-vdo"
EXPECTED_SUBTITLE_COUNT = 51


def frame_to_timecode(frame_number: int, fps: float = 60.0) -> str:
    """Convert absolute frame count to SMPTE timecode string HH:MM:SS:FF."""
    total_seconds = int(frame_number // fps)
    rem_frames = int(frame_number % fps)
    hours = total_seconds // 3600
    rem_seconds = total_seconds % 3600
    minutes = rem_seconds // 60
    seconds = rem_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{rem_frames:02d}"


def _get_item_property(item: Any, prop_name: str, default: Any = None) -> Any:
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


def verify_timeline_readback(timeline: Any) -> Dict[str, Any]:
    """Perform comprehensive readback verification against Timeline 1 constraints.

    Verification Criteria:
    - Video track count >= 2
    - Audio track count >= 3
    - Subtitle track count == 1
    - Subtitle track 1 count == 51 (completely intact)
    - Video 2 (GIFs) count >= 1, ZoomX=0.55, ZoomY=0.55, Pan=0, Tilt=0
    - Audio 2 (SFX) count >= 2, AudioVolume=-11.0 dB
    - Audio 3 (BGM) count == 1, AudioVolume=-23.0 dB

    Returns:
        Dict containing boolean 'passed', 'checks' dict, and 'details' dict.
    """
    v_track_count = timeline.GetTrackCount("video") if hasattr(timeline, "GetTrackCount") else 0
    a_track_count = timeline.GetTrackCount("audio") if hasattr(timeline, "GetTrackCount") else 0
    sub_track_count = timeline.GetTrackCount("subtitle") if hasattr(timeline, "GetTrackCount") else 0

    sub_items = timeline.GetItemListInTrack("subtitle", 1) or [] if hasattr(timeline, "GetItemListInTrack") else []
    v2_items = timeline.GetItemListInTrack("video", 2) or [] if hasattr(timeline, "GetItemListInTrack") else []
    a2_items = timeline.GetItemListInTrack("audio", 2) or [] if hasattr(timeline, "GetItemListInTrack") else []
    a3_items = timeline.GetItemListInTrack("audio", 3) or [] if hasattr(timeline, "GetItemListInTrack") else []

    checks: Dict[str, bool] = {}
    details: Dict[str, Any] = {
        "video_track_count": v_track_count,
        "audio_track_count": a_track_count,
        "subtitle_track_count": sub_track_count,
        "subtitle_cues_count": len(sub_items),
        "v2_items_count": len(v2_items),
        "a2_items_count": len(a2_items),
        "a3_items_count": len(a3_items),
        "v2_properties": [],
        "a2_properties": [],
        "a3_properties": [],
    }

    # Track counts
    checks["video_tracks_min_2"] = (v_track_count >= 2)
    checks["audio_tracks_min_3"] = (a_track_count >= 3)
    checks["subtitle_tracks_exact_1"] = (sub_track_count == 1)

    # Subtitles intact
    checks["subtitles_untouched_51"] = (len(sub_items) == EXPECTED_SUBTITLE_COUNT)

    # V2 GIFs verification
    checks["v2_gifs_count_min_1"] = (len(v2_items) >= 1)
    v2_props_valid = len(v2_items) >= 1
    for item in v2_items:
        zx = float(_get_item_property(item, "ZoomX", 0.0) or 0.0)
        zy = float(_get_item_property(item, "ZoomY", 0.0) or 0.0)
        pan = float(_get_item_property(item, "Pan", 0.0) or 0.0)
        tilt = float(_get_item_property(item, "Tilt", 0.0) or 0.0)
        details["v2_properties"].append({"ZoomX": zx, "ZoomY": zy, "Pan": pan, "Tilt": tilt})
        if abs(zx - 0.55) > 0.05 or abs(zy - 0.55) > 0.05 or abs(pan) > 0.05 or abs(tilt) > 0.05:
            v2_props_valid = False
    checks["v2_gifs_properties_valid"] = v2_props_valid

    # A2 SFX verification
    checks["a2_sfx_count_min_2"] = (len(a2_items) >= 2)
    a2_props_valid = len(a2_items) >= 2
    for item in a2_items:
        vol = float(_get_item_property(item, "AudioVolume", 999.0) or 0.0)
        details["a2_properties"].append({"AudioVolume": vol})
        if abs(vol - (-11.0)) > 0.2:
            a2_props_valid = False
    checks["a2_sfx_properties_valid"] = a2_props_valid

    # A3 BGM verification
    checks["a3_bgm_count_exact_1"] = (len(a3_items) == 1)
    a3_props_valid = len(a3_items) == 1
    for item in a3_items:
        vol = float(_get_item_property(item, "AudioVolume", 999.0) or 0.0)
        details["a3_properties"].append({"AudioVolume": vol})
        if abs(vol - (-23.0)) > 0.2:
            a3_props_valid = False
    checks["a3_bgm_properties_valid"] = a3_props_valid

    overall_passed = all(checks.values())

    return {
        "passed": overall_passed,
        "checks": checks,
        "details": details,
    }


def capture_verification_frame(
    project: Any,
    timeline: Any,
    target_frame: int,
    output_path: str,
    fps: float = 60.0,
) -> Optional[str]:
    """Capture still image at target frame and verify with ffprobe."""
    tc = frame_to_timecode(target_frame, fps)
    print(f"Setting playhead to frame {target_frame} ({tc})...")
    if hasattr(timeline, "SetCurrentTimecode"):
        timeline.SetCurrentTimecode(tc)
        time.sleep(0.5)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    if os.path.exists(output_path):
        try:
            os.remove(output_path)
        except Exception:
            pass

    print(f"Exporting still to {output_path}...")
    if hasattr(project, "ExportCurrentFrameAsStill"):
        success = project.ExportCurrentFrameAsStill(output_path)
        if not success or not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            print(f"ExportCurrentFrameAsStill returned {success}, file exists: {os.path.exists(output_path)}")
            return None

    # Probe image with ffprobe
    try:
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,codec_name",
            "-of",
            "json",
            output_path,
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        probe_data = json.loads(res.stdout)
        streams = probe_data.get("streams", [])
        if streams:
            w = streams[0].get("width")
            h = streams[0].get("height")
            print(f"Verified captured frame: {w}x{h} ({streams[0].get('codec_name')})")
            if w == 1920 and h == 1080:
                return output_path
    except Exception as exc:
        print(f"ffprobe verification warning: {exc}")
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path

    return output_path if os.path.exists(output_path) else None


def run_pilot(
    timeline_index: int = TARGET_TIMELINE_INDEX,
    delay_between_mutations: float = 1.2,
    capture_frame: bool = True,
    output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute complete pilot enrichment and verification on Timeline 1."""
    resolve = get_resolve()
    if not resolve:
        raise RuntimeError("Failed to connect to DaVinci Resolve Studio.")

    pm = resolve.GetProjectManager()
    if not pm:
        raise RuntimeError("Failed to get ProjectManager.")

    project = pm.GetCurrentProject()
    if not project:
        raise RuntimeError("No current project open in DaVinci Resolve.")

    project_name = project.GetName()
    print(f"Connected to project: {project_name}")

    timeline_count = project.GetTimelineCount()
    if timeline_index < 1 or timeline_index > timeline_count:
        raise IndexError(f"Timeline index {timeline_index} out of bounds (1-{timeline_count}).")

    timeline = project.GetTimelineByIndex(timeline_index)
    tl_name = timeline.GetName()
    print(f"Selected Timeline {timeline_index}: {tl_name}")

    # Set as active timeline
    project.SetCurrentTimeline(timeline)
    time.sleep(0.5)

    media_pool = project.GetMediaPool()
    root_folder = media_pool.GetRootFolder()

    # Discover / Ensure asset catalog
    catalog: Dict[str, List[Any]] = {}
    for f in root_folder.GetSubFolderList() or []:
        if "Enrichment" in f.GetName():
            catalog[f.GetName()] = f.GetClipList() or []

    required_bins = ["Enrichment_SFX", "Enrichment_BGM", "Enrichment_GIF"]
    if not all(bin_name in catalog and len(catalog[bin_name]) > 0 for bin_name in required_bins):
        print("Enrichment bins missing or empty in MediaPool. Ingesting curated assets...")
        catalog = ingest_enrichment_assets(resolve_obj=resolve)

    # Timeline bounds and metadata
    start_frame = int(timeline.GetStartFrame())
    end_frame = int(timeline.GetEndFrame())
    subtitles = timeline.GetItemListInTrack("subtitle", 1) or []
    fps = 60.0

    print(f"Timeline bounds: start={start_frame}, end={end_frame}, duration={end_frame - start_frame} frames")
    print(f"Subtitle cues on Sub 1: {len(subtitles)}")

    # Plan enrichment
    tl_info = {
        "name": tl_name,
        "start_frame": start_frame,
        "end_frame": end_frame,
        "fps": fps,
        "subtitles": subtitles,
        "game": "Minecraft",
    }

    plan = plan_timeline_enrichment(tl_info, catalog)
    print(f"Plan generated:")
    print(f"  BGM: {plan.bgm_item.asset_name if plan.bgm_item else 'None'} on A{plan.bgm_item.track_index if plan.bgm_item else 'N/A'}")
    print(f"  SFX: {len(plan.sfx_items)} cues on A2")
    print(f"  GIF: {len(plan.gif_items)} overlays on V2")

    # Apply enrichment with enforced mutation delay (1.2s spacing)
    print(f"Applying enrichment plan with delay {delay_between_mutations}s...")
    apply_ok = apply_enrichment_plan(
        timeline=timeline,
        plan=plan,
        media_pool=media_pool,
        resolve_obj=resolve,
        delay_between_mutations=delay_between_mutations,
    )
    if not apply_ok:
        raise RuntimeError("Failed to apply enrichment plan to timeline.")

    # Save project state
    pm.SaveProject()
    time.sleep(1.0)
    print("Project saved via pm.SaveProject().")

    # Readback verification
    print("Performing readback verification on Timeline 1...")
    verification = verify_timeline_readback(timeline)
    print("Verification checks:", json.dumps(verification["checks"], indent=2))
    print("Verification passed:", verification["passed"])

    # Frame capture at first GIF cue
    captured_file = None
    if capture_frame and plan.gif_items:
        first_cue_frame = plan.gif_items[0].start_frame
        out_dir = output_dir or os.path.abspath("scratch")
        os.makedirs(out_dir, exist_ok=True)
        still_path = os.path.join(out_dir, "pilot_timeline1_cue_frame.png")
        captured_file = capture_verification_frame(project, timeline, first_cue_frame, still_path, fps)

    # Save project again after playhead repositioning
    pm.SaveProject()

    return {
        "timeline_name": tl_name,
        "timeline_index": timeline_index,
        "plan_items": len(plan.items),
        "verification": verification,
        "captured_frame": captured_file,
    }


if __name__ == "__main__":
    import argparse

    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Pilot Enrichment on Timeline 1")
    parser.add_argument("--index", type=int, default=TARGET_TIMELINE_INDEX, help="Timeline index (default: 1)")
    parser.add_argument("--delay", type=float, default=1.2, help="Mutation spacing in seconds (default: 1.2)")
    parser.add_argument("--no-capture", action="store_true", help="Skip still frame capture")
    args = parser.parse_args()

    result = run_pilot(
        timeline_index=args.index,
        delay_between_mutations=args.delay,
        capture_frame=not args.no_capture,
    )
    print("\n--- Pilot Summary ---")
    print(f"Timeline: {result['timeline_name']}")
    print(f"Verification Passed: {result['verification']['passed']}")
    if result["captured_frame"]:
        print(f"Captured Still: {result['captured_frame']}")
