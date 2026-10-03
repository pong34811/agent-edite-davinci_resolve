"""Milestone 1: Project Backup & Baseline Validation.

Connects to DaVinci Resolve Studio 21.1, verifies project KT404_2026-09-29,
saves the project, exports a full .drp backup to Google Drive, validates
backup integrity, and captures a comprehensive 30-timeline baseline snapshot.
"""

import argparse
import datetime
import json
import os
import sys
import time
import zipfile
from typing import Any, Dict, List, Optional

# Ensure UTF-8 output encoding on Windows console
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# Default parameters per specification
DEFAULT_PROJECT_NAME = "KT404_2026-09-29"
EXPECTED_PROJECT_ID = "7c38045b-c9ae-426c-8b4c-2e2d726d88ff"
DEFAULT_BACKUP_PATH = (
    r"G:\My Drive\Projects\Katy404\2026-09-29\KT404_2026-09-29_pre_9x16_conversion_2026-10-01.drp"
)
DEFAULT_OUTPUT_JSON = (
    r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\worker_m1\baseline_30_timelines.json"
)


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
    """Convert absolute frame count or duration to SMPTE timecode string HH:MM:SS:FF."""
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


def get_fusion_comp_info(item: Any) -> Optional[Dict[str, Any]]:
    """Inspect Fusion composition on an item (e.g. Adjustment Clip)."""
    if not hasattr(item, "GetFusionCompCount"):
        return None
    try:
        comp_count = item.GetFusionCompCount()
        if comp_count == 0:
            return None
        comp = item.GetFusionCompByIndex(1)
        if not comp:
            return {"comp_count": comp_count, "tools": []}
        tools_info = []
        tool_list = comp.GetToolList()
        if isinstance(tool_list, dict):
            for _, tool in tool_list.items():
                attrs = tool.GetAttrs() if hasattr(tool, "GetAttrs") else {}
                tool_name = attrs.get("TOOLS_Name", "")
                tool_entry: Dict[str, Any] = {"name": tool_name}
                if "Transform" in tool_name:
                    try:
                        center = tool.GetInput("Center")
                        if isinstance(center, dict):
                            tool_entry["Center"] = [center.get(1, 0.5), center.get(2, 0.5)]
                        else:
                            tool_entry["Center"] = center
                    except Exception:
                        pass
                    try:
                        tool_entry["Size"] = tool.GetInput("Size")
                    except Exception:
                        pass
                    try:
                        tool_entry["Angle"] = tool.GetInput("Angle")
                    except Exception:
                        pass
                tools_info.append(tool_entry)
        return {"comp_count": comp_count, "tools": tools_info}
    except Exception:
        return None


def capture_ui_state(resolve: Any, project: Any) -> Dict[str, Any]:
    """Capture current page, active timeline, playhead timecode, and media pool folder."""
    state: Dict[str, Any] = {
        "page": resolve.GetCurrentPage() if hasattr(resolve, "GetCurrentPage") else None,
        "timeline_id": None,
        "timeline_name": None,
        "timecode": None,
    }
    if project:
        curr_tl = project.GetCurrentTimeline()
        if curr_tl:
            state["timeline_id"] = curr_tl.GetUniqueId()
            state["timeline_name"] = curr_tl.GetName()
            state["timecode"] = curr_tl.GetCurrentTimecode()
    return state


def restore_ui_state(resolve: Any, project: Any, state: Dict[str, Any]) -> bool:
    """Restore UI page, active timeline, and playhead position."""
    success = True
    target_page = state.get("page")
    if target_page and hasattr(resolve, "OpenPage"):
        resolve.OpenPage(target_page)
        for _ in range(10):
            if resolve.GetCurrentPage() == target_page:
                break
            time.sleep(0.1)

    target_tl_id = state.get("timeline_id")
    if target_tl_id and project:
        tl_count = project.GetTimelineCount()
        for i in range(1, tl_count + 1):
            tl = project.GetTimelineByIndex(i)
            if tl and tl.GetUniqueId() == target_tl_id:
                project.SetCurrentTimeline(tl)
                break

    target_tc = state.get("timecode")
    if target_tc and project:
        curr_tl = project.GetCurrentTimeline()
        if curr_tl and hasattr(curr_tl, "SetCurrentTimecode"):
            curr_tl.SetCurrentTimecode(target_tc)

    return success


def save_project(pm: Any) -> bool:
    """Execute ProjectManager.SaveProject() and verify success."""
    print("Executing ProjectManager.SaveProject()...")
    saved = pm.SaveProject()
    if not saved:
        raise RuntimeError("ProjectManager.SaveProject() returned False.")
    print("Project saved successfully.")
    return True


def export_drp_backup(pm: Any, project_name: str, backup_path: str) -> bool:
    """Export project .drp backup via ProjectManager.ExportProject()."""
    parent_dir = os.path.dirname(os.path.abspath(backup_path))
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)

    print(f"Exporting full .drp backup to:\n  {backup_path}")
    success = pm.ExportProject(project_name, backup_path, True)
    if not success:
        raise RuntimeError(f"pm.ExportProject('{project_name}', '{backup_path}') returned False.")
    print("ExportProject API call returned True.")
    return True


def verify_drp_integrity(
    backup_path: str, expected_project_id: str = EXPECTED_PROJECT_ID
) -> Dict[str, Any]:
    """Thoroughly verify .drp backup integrity: existence, size, CRC32, project.xml DbId, MediaPool."""
    print("Verifying .drp backup file integrity...")
    if not os.path.exists(backup_path):
        raise FileNotFoundError(f"Exported .drp file does not exist: {backup_path}")

    size_bytes = os.path.getsize(backup_path)
    size_mb = size_bytes / (1024 * 1024)
    print(f"File size: {size_bytes:,} bytes ({size_mb:.2f} MB)")
    if size_bytes < 500_000:
        raise ValueError(
            f"Exported .drp file size is suspiciously small: {size_bytes} bytes (< 500 KB threshold)."
        )

    if not zipfile.is_zipfile(backup_path):
        raise zipfile.BadZipFile(f"File is not a valid zip archive: {backup_path}")

    with zipfile.ZipFile(backup_path, "r") as z:
        bad_file = z.testzip()
        if bad_file is not None:
            raise zipfile.BadZipFile(f"CRC32 checksum mismatch on archive member: {bad_file}")
        print("Archive CRC32 checksums: PASS (testzip() returned None)")

        namelist = z.namelist()
        if "project.xml" not in namelist:
            raise KeyError("Archive is missing required 'project.xml' member.")

        info = z.getinfo("project.xml")
        print(f"project.xml uncompressed size: {info.file_size:,} bytes")
        if info.file_size < 10_000:
            raise ValueError(f"project.xml uncompressed size too small: {info.file_size} bytes")

        # Check project DbId in project.xml header
        header = z.read("project.xml")[:2000].decode("utf-8", errors="ignore")
        if expected_project_id not in header:
            raise ValueError(
                f"project.xml does not contain expected DbId='{expected_project_id}' in header."
            )
        print(f"project.xml header DbId matched: '{expected_project_id}'")

        has_mediapool = any("MediaPool" in n for n in namelist)
        if not has_mediapool:
            raise ValueError("Archive is missing MediaPool folder structure.")
        print("MediaPool structure verified.")

    verification_info = {
        "backup_path": backup_path,
        "exists": True,
        "size_bytes": size_bytes,
        "size_mb": round(size_mb, 2),
        "crc32_valid": True,
        "testzip_result": None,
        "project_xml_size_bytes": info.file_size,
        "expected_project_id": expected_project_id,
        "project_id_verified": True,
        "has_mediapool": True,
        "total_archive_members": len(namelist),
    }
    print("All .drp integrity checks passed successfully!")
    return verification_info


def extract_timeline_baseline(tl: Any, timeline_index: int) -> Dict[str, Any]:
    """Capture full baseline metadata for a single timeline."""
    name = tl.GetName()
    tl_id = tl.GetUniqueId()
    fps = float(tl.GetSetting("timelineFrameRate") or 60.0)
    width = int(tl.GetSetting("timelineResolutionWidth") or 1920)
    height = int(tl.GetSetting("timelineResolutionHeight") or 1080)
    start_frame = int(tl.GetStartFrame())
    end_frame = int(tl.GetEndFrame())
    duration_frames = end_frame - start_frame
    start_tc = tl.GetStartTimecode() or frame_to_timecode(start_frame, fps)
    end_tc = frame_to_timecode(end_frame, fps)
    duration_tc = frame_to_timecode(duration_frames, fps)

    v_count = int(tl.GetTrackCount("video") or 0)
    a_count = int(tl.GetTrackCount("audio") or 0)
    sub_count = int(tl.GetTrackCount("subtitle") or 0)

    # Subtitle Track Details
    subtitle_track_info: Dict[str, Any] = {
        "track_name": tl.GetTrackName("subtitle", 1) if sub_count > 0 else None,
        "cue_count": 0,
        "cues": [],
    }
    if sub_count > 0:
        sub_items = tl.GetItemListInTrack("subtitle", 1) or []
        subtitle_track_info["cue_count"] = len(sub_items)
        for cue_idx, cue_item in enumerate(sub_items, start=1):
            c_start = int(cue_item.GetStart())
            c_end = int(cue_item.GetEnd())
            c_dur = int(cue_item.GetDuration())
            c_text = cue_item.GetName()
            subtitle_track_info["cues"].append(
                {
                    "cue_index": cue_idx,
                    "text": c_text,
                    "start_frame": c_start,
                    "end_frame": c_end,
                    "duration_frames": c_dur,
                    "start_tc": frame_to_timecode(c_start, fps),
                    "end_tc": frame_to_timecode(c_end, fps),
                    "duration_tc": frame_to_timecode(c_dur, fps),
                }
            )

    # Audio Tracks Details
    audio_tracks_info: List[Dict[str, Any]] = []
    for a_idx in range(1, a_count + 1):
        a_name = tl.GetTrackName("audio", a_idx)
        a_type = tl.GetTrackSubType("audio", a_idx)
        a_items = tl.GetItemListInTrack("audio", a_idx) or []
        track_entry: Dict[str, Any] = {
            "track_index": a_idx,
            "track_name": a_name,
            "track_type": a_type,
            "item_count": len(a_items),
            "items": [],
        }
        for item in a_items:
            i_start = int(item.GetStart())
            i_end = int(item.GetEnd())
            i_dur = int(item.GetDuration())
            vol = get_item_property(item, "AudioVolume")
            pan = get_item_property(item, "Pan")
            fades = item.GetFades() if hasattr(item, "GetFades") else None
            track_entry["items"].append(
                {
                    "name": item.GetName(),
                    "start_frame": i_start,
                    "end_frame": i_end,
                    "duration_frames": i_dur,
                    "start_tc": frame_to_timecode(i_start, fps),
                    "end_tc": frame_to_timecode(i_end, fps),
                    "volume_db": float(vol) if vol is not None else None,
                    "pan": float(pan) if pan is not None else None,
                    "fades": fades,
                }
            )
        audio_tracks_info.append(track_entry)

    # Video Tracks Details
    video_tracks_info: List[Dict[str, Any]] = []
    for v_idx in range(1, v_count + 1):
        v_name = tl.GetTrackName("video", v_idx)
        v_items = tl.GetItemListInTrack("video", v_idx) or []
        track_entry = {
            "track_index": v_idx,
            "track_name": v_name,
            "item_count": len(v_items),
            "items": [],
        }
        for item in v_items:
            i_start = int(item.GetStart())
            i_end = int(item.GetEnd())
            i_dur = int(item.GetDuration())
            mpi = item.GetMediaPoolItem()
            is_adj = mpi is None
            fusion_info = get_fusion_comp_info(item) if is_adj else None

            transforms = {
                "ZoomX": get_item_property(item, "ZoomX"),
                "ZoomY": get_item_property(item, "ZoomY"),
                "Pan": get_item_property(item, "Pan"),
                "Tilt": get_item_property(item, "Tilt"),
                "CropBottom": get_item_property(item, "CropBottom"),
                "CropTop": get_item_property(item, "CropTop"),
                "CropLeft": get_item_property(item, "CropLeft"),
                "CropRight": get_item_property(item, "CropRight"),
                "Opacity": get_item_property(item, "Opacity"),
            }
            # Clean transforms to floats where available
            cleaned_transforms = {
                k: float(v) if v is not None else None for k, v in transforms.items()
            }

            track_entry["items"].append(
                {
                    "name": item.GetName(),
                    "start_frame": i_start,
                    "end_frame": i_end,
                    "duration_frames": i_dur,
                    "start_tc": frame_to_timecode(i_start, fps),
                    "end_tc": frame_to_timecode(i_end, fps),
                    "is_adjustment_clip": is_adj,
                    "transforms": cleaned_transforms,
                    "fusion_comp": fusion_info,
                }
            )
        video_tracks_info.append(track_entry)

    return {
        "timeline_index": timeline_index,
        "timeline_name": name,
        "timeline_id": tl_id,
        "frame_rate": fps,
        "resolution_width": width,
        "resolution_height": height,
        "is_16_by_9": (width == 1920 and height == 1080),
        "start_frame": start_frame,
        "end_frame": end_frame,
        "duration_frames": duration_frames,
        "start_tc": start_tc,
        "end_tc": end_tc,
        "duration_tc": duration_tc,
        "track_counts": {
            "video": v_count,
            "audio": a_count,
            "subtitle": sub_count,
        },
        "subtitle_track": subtitle_track_info,
        "audio_tracks": audio_tracks_info,
        "video_tracks": video_tracks_info,
    }


def capture_all_baselines(project: Any) -> List[Dict[str, Any]]:
    """Capture baseline metadata across all 30 timelines."""
    total_count = project.GetTimelineCount()
    print(f"Total timelines detected in project: {total_count}")
    if total_count != 30:
        print(f"WARNING: Expected exactly 30 timelines, found {total_count}", file=sys.stderr)

    baselines: List[Dict[str, Any]] = []
    for i in range(1, total_count + 1):
        tl = project.GetTimelineByIndex(i)
        if not tl:
            raise RuntimeError(f"Could not retrieve timeline at index {i}")
        tl_name = tl.GetName()
        print(f"  [{i:02d}/30] Extracting baseline for: '{tl_name}'...")
        baseline = extract_timeline_baseline(tl, i)
        baselines.append(baseline)

    return baselines


def run_m1(
    backup_path: str = DEFAULT_BACKUP_PATH,
    output_json: str = DEFAULT_OUTPUT_JSON,
    skip_backup: bool = False,
) -> Dict[str, Any]:
    """Execute Milestone 1 end-to-end workflow."""
    start_time = datetime.datetime.now(datetime.timezone.utc)
    print(f"=== Starting Milestone 1 Execution ({start_time.isoformat()}) ===")

    # 1. Connect to Resolve
    resolve = get_resolve()
    if not resolve:
        raise RuntimeError("Could not connect to DaVinci Resolve Studio.")
    pm = resolve.GetProjectManager()
    if not pm:
        raise RuntimeError("Could not obtain ProjectManager from Resolve.")
    project = pm.GetCurrentProject()
    if not project:
        raise RuntimeError("No active project open in DaVinci Resolve.")

    proj_name = project.GetName()
    proj_id = project.GetUniqueId()
    print(f"Connected to project: '{proj_name}' (ID: {proj_id})")

    if proj_name != DEFAULT_PROJECT_NAME:
        raise ValueError(
            f"Active project name mismatch: expected '{DEFAULT_PROJECT_NAME}', found '{proj_name}'"
        )
    if proj_id != EXPECTED_PROJECT_ID:
        raise ValueError(
            f"Active project ID mismatch: expected '{EXPECTED_PROJECT_ID}', found '{proj_id}'"
        )

    # 2. Capture UI state for clean restoration
    initial_ui_state = capture_ui_state(resolve, project)
    print(f"Captured initial UI state: {initial_ui_state}")

    backup_verification = None
    if not skip_backup:
        # 3. Save Project
        save_project(pm)

        # 4. Export .drp Backup
        export_drp_backup(pm, proj_name, backup_path)

        # 5. Verify .drp Backup Integrity
        backup_verification = verify_drp_integrity(backup_path, EXPECTED_PROJECT_ID)
    else:
        print("Skipping backup export per --skip-backup flag.")

    # 6. Capture Baseline Metadata for All 30 Timelines
    print("Capturing baseline metadata for all timelines...")
    timelines_baseline = capture_all_baselines(project)

    # 7. Assemble Master Snapshot Object
    snapshot = {
        "milestone": "Milestone 1: Project Backup & Baseline Validation",
        "timestamp_utc": start_time.isoformat(),
        "project_name": proj_name,
        "project_id": proj_id,
        "backup_path": backup_path if not skip_backup else None,
        "backup_verification": backup_verification,
        "total_timelines": len(timelines_baseline),
        "timelines_summary": [
            {
                "index": tl["timeline_index"],
                "name": tl["timeline_name"],
                "id": tl["timeline_id"],
                "fps": tl["frame_rate"],
                "duration_frames": tl["duration_frames"],
                "duration_tc": tl["duration_tc"],
                "subtitle_cues": tl["subtitle_track"]["cue_count"],
                "video_tracks": tl["track_counts"]["video"],
                "audio_tracks": tl["track_counts"]["audio"],
            }
            for tl in timelines_baseline
        ],
        "timelines": timelines_baseline,
    }

    # 8. Save Baseline JSON
    output_dir = os.path.dirname(os.path.abspath(output_json))
    os.makedirs(output_dir, exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    print(f"Saved baseline JSON to:\n  {output_json}")

    # 9. Restore UI State
    print("Restoring initial UI state...")
    restore_ui_state(resolve, project, initial_ui_state)
    print("UI state cleanly restored.")

    end_time = datetime.datetime.now(datetime.timezone.utc)
    elapsed = (end_time - start_time).total_seconds()
    print(f"=== Milestone 1 Completed Successfully in {elapsed:.2f}s ===")
    return snapshot


def main():
    parser = argparse.ArgumentParser(
        description="Milestone 1: Project Backup and 30-Timeline Baseline Snapshot"
    )
    parser.add_argument(
        "--backup-path",
        default=DEFAULT_BACKUP_PATH,
        help="Target path for .drp project backup export",
    )
    parser.add_argument(
        "--output-json",
        default=DEFAULT_OUTPUT_JSON,
        help="Target path for baseline snapshot JSON",
    )
    parser.add_argument(
        "--skip-backup",
        action="store_true",
        help="Skip project save and .drp export (snapshot only)",
    )
    args = parser.parse_args()

    try:
        run_m1(
            backup_path=args.backup_path,
            output_json=args.output_json,
            skip_backup=args.skip_backup,
        )
    except Exception as exc:
        print(f"\nFATAL ERROR during Milestone 1 execution: {exc}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
