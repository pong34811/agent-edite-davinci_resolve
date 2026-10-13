"""Capture a read-only baseline for Armigon's 48 horizontal vdo timelines.

This uses the Resolve scripting API only because the attached MCP exposes
snapshots for the current timeline, not a complete project-wide inventory.
Timeline navigation is restored with scripts.resolve_common.preserved_state.
No timeline, project, media, or render settings are changed or saved.
"""
from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

from scripts.resolve_common import connect_resolve, preserved_state


OUTPUT = Path(
    r"G:\My Drive\Projects\Armigon\2026-09\armigon-2026-09_9x16_preflight_20261012.json"
)
EXPECTED_PROJECT = "armigon-2026-09"
EXPECTED_TIMELINE_COUNT = 48


def read(obj, method: str, *args):
    if obj is None or method not in dir(obj):
        return {"unavailable": method}
    try:
        return getattr(obj, method)(*args)
    except Exception as exc:  # Preserve evidence of a read failure in the snapshot.
        return {"error": type(exc).__name__, "method": method}


def item_record(item):
    pool = read(item, "GetMediaPoolItem")
    if isinstance(pool, dict):
        pool = None
    pool_properties = read(pool, "GetClipProperty") if pool is not None else None
    return {
        "id": read(item, "GetUniqueId"),
        "name": read(item, "GetName"),
        "start": read(item, "GetStart"),
        "end": read(item, "GetEnd"),
        "duration": read(item, "GetDuration"),
        "source_start": read(item, "GetSourceStartFrame"),
        "source_end": read(item, "GetSourceEndFrame"),
        "left_offset": read(item, "GetLeftOffset"),
        "right_offset": read(item, "GetRightOffset"),
        "properties": read(item, "GetProperty"),
        "media_id": read(pool, "GetUniqueId") if pool is not None else None,
        "media_properties": pool_properties,
    }


def main():
    if OUTPUT.exists():
        raise RuntimeError(f"Refusing to overwrite existing baseline: {OUTPUT}")
    resolve = connect_resolve()
    if resolve is None:
        raise RuntimeError("Cannot connect to DaVinci Resolve")
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    if project is None or project.GetName() != EXPECTED_PROJECT:
        raise RuntimeError("Current project is not armigon-2026-09")
    if not all(m in dir(project) for m in ("GetTimelineCount", "GetTimelineByIndex", "SetCurrentTimeline")):
        raise RuntimeError("Required project timeline methods are unavailable")

    entry_timeline = project.GetCurrentTimeline()
    entry = {
        "timeline_id": read(entry_timeline, "GetUniqueId"),
        "timecode": read(entry_timeline, "GetCurrentTimecode"),
        "page": read(resolve, "GetCurrentPage"),
    }
    candidates = []
    vertical_names = []
    for index in range(1, project.GetTimelineCount() + 1):
        timeline = project.GetTimelineByIndex(index)
        name = read(timeline, "GetName")
        if isinstance(name, str) and name.endswith("_9x16"):
            vertical_names.append({"id": read(timeline, "GetUniqueId"), "name": name})
        if isinstance(name, str) and name.endswith("-vdo"):
            candidates.append((index, timeline))
    if len(candidates) != EXPECTED_TIMELINE_COUNT:
        raise RuntimeError(f"Expected {EXPECTED_TIMELINE_COUNT} -vdo timelines; found {len(candidates)}")
    ids = [read(timeline, "GetUniqueId") for _, timeline in candidates]
    if any(not isinstance(value, str) or not value for value in ids) or len(set(ids)) != len(ids):
        raise RuntimeError("Candidate timeline IDs are missing or duplicated")

    rows = []
    with preserved_state(resolve):
        for ordinal, (index, timeline) in enumerate(candidates, 1):
            if not project.SetCurrentTimeline(timeline):
                raise RuntimeError(f"Could not activate timeline {index}")
            time.sleep(0.15)
            active = project.GetCurrentTimeline()
            timeline_id = read(active, "GetUniqueId")
            if timeline_id != ids[ordinal - 1]:
                raise RuntimeError(f"Active timeline identity mismatch at {index}")
            row = {
                "ordinal": index,
                "timeline_id": timeline_id,
                "name": read(active, "GetName"),
                "start_frame": read(active, "GetStartFrame"),
                "end_frame": read(active, "GetEndFrame"),
                "start_timecode": read(active, "GetStartTimecode"),
                "fps": read(active, "GetSetting", "timelineFrameRate"),
                "width": read(active, "GetSetting", "timelineResolutionWidth"),
                "height": read(active, "GetSetting", "timelineResolutionHeight"),
                "tracks": [],
                "audio_track_level_api_methods": sorted(
                    name for name in dir(active) if "track" in name.lower() and "audio" in name.lower()
                ),
            }
            for kind in ("video", "audio", "subtitle"):
                count = read(active, "GetTrackCount", kind)
                if not isinstance(count, int):
                    row[kind + "_track_error"] = count
                    continue
                for track_index in range(1, count + 1):
                    raw_items = read(active, "GetItemListInTrack", kind, track_index)
                    items = raw_items if isinstance(raw_items, list) else []
                    row["tracks"].append({
                        "kind": kind,
                        "index": track_index,
                        "name": read(active, "GetTrackName", kind, track_index),
                        "enabled": read(active, "GetIsTrackEnabled", kind, track_index),
                        "locked": read(active, "GetIsTrackLocked", kind, track_index),
                        "item_count": len(items),
                        "items": [item_record(item) for item in items],
                        "read_error": raw_items if isinstance(raw_items, dict) else None,
                    })
            rows.append(row)

    restored_timeline = project.GetCurrentTimeline()
    after = {
        "timeline_id": read(restored_timeline, "GetUniqueId"),
        "timecode": read(restored_timeline, "GetCurrentTimecode"),
        "page": read(resolve, "GetCurrentPage"),
    }
    if after != entry:
        raise RuntimeError(f"Resolve UI state did not restore exactly: before={entry}, after={after}")

    payload = {
        "schema_version": 1,
        "captured_at": datetime.now().astimezone().isoformat(),
        "capture_method": "Resolve Python scripting API via scripts.resolve_common; read-only",
        "project": {
            "name": project.GetName(),
            "id": read(project, "GetUniqueId"),
            "resolve_build": read(resolve, "GetVersion"),
            "timeline_fps": read(project, "GetSetting", "timelineFrameRate"),
            "playback_fps": read(project, "GetSetting", "timelinePlaybackFrameRate"),
            "width": read(project, "GetSetting", "timelineResolutionWidth"),
            "height": read(project, "GetSetting", "timelineResolutionHeight"),
        },
        "active_state_before": entry,
        "active_state_after": after,
        "existing_vertical_timelines": vertical_names,
        "expected_timeline_count": EXPECTED_TIMELINE_COUNT,
        "timeline_count": len(rows),
        "timelines": rows,
        "notes": [
            "Timeline item properties include clip-level audio properties where Resolve exposes them.",
            "Track-level audio controls are recorded only where the scripting API exposes a getter.",
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps({"written": str(OUTPUT), "timelines": len(rows), "restoration_verified": True}))


if __name__ == "__main__":
    main()
