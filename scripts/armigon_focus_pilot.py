"""Disposable Adjustment Clip pilot for the Armigon focus edit.

MCP-GAP: timeline.add_track / timeline.insert_generator expose no exact mark-range
or batch Fusion-transform operation. `resolve_preflight.py` found Timeline.AddTrack,
Timeline.SetMarkInOut, Timeline.SetCurrentTimecode, Timeline.InsertGeneratorIntoTimeline,
and TimelineItem.AddFusionComp in the Studio scripting API, so this pilot uses
scripts/resolve_common.py and a temporary duplicate that is deleted before exit.
"""
from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.resolve_common import connect_resolve, preserved_state


def require(value, message):
    if not value:
        raise RuntimeError(message)


def tc(frame: int, fps: int = 60) -> str:
    seconds, ff = divmod(frame, fps)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{ff:02d}"


def signatures(timeline, counts):
    data = []
    for kind in ("video", "audio", "subtitle"):
        for index in range(1, counts[kind] + 1):
            items = timeline.GetItemListInTrack(kind, index) or []
            data.append((kind, index, timeline.GetTrackName(kind, index), tuple(
                (item.GetName(), int(item.GetStart()), int(item.GetEnd()))
                for item in items
            )))
    return data


def main():
    resolve = connect_resolve()
    require(resolve is not None, "Resolve unavailable")
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    require(project is not None and project.GetName() == "armigon-2026-09", "wrong project")
    require(not project.IsRenderingInProgress(), "Resolve is rendering")
    base = project.GetCurrentTimeline()
    require(base is not None and base.GetName() == "อ๋อ หลอก คือเลย อ่า โอเค เย็นและก็ค-Minecraft-vdo",
            "unexpected entry timeline")
    fps = int(float(base.GetSetting("timelineFrameRate")))
    require(fps == 60, f"unexpected pilot fps {fps}")
    start, end = 2722, 2988
    frame = (start + end) // 2
    before_counts = {k: base.GetTrackCount(k) for k in ("video", "audio", "subtitle")}
    before = signatures(base, before_counts)
    duplicate = None
    original_locks = {}
    output = {}

    with preserved_state(resolve):
        try:
            duplicate = base.DuplicateTimeline(base.GetName() + "_focus_pilot_TEMP")
            require(duplicate is not None, "could not make disposable timeline")
            require(project.SetCurrentTimeline(duplicate), "could not activate disposable timeline")
            time.sleep(1.25)
            require(resolve.OpenPage("edit"), "could not switch to Edit page")
            time.sleep(2.0)
            counts = {k: duplicate.GetTrackCount(k) for k in ("video", "audio", "subtitle")}
            original_locks = {(k, i): duplicate.GetIsTrackLocked(k, i)
                              for k, n in counts.items() for i in range(1, n + 1)}
            for k, i in original_locks:
                require(duplicate.SetTrackLock(k, i, True), f"could not lock {k}{i}")
            time.sleep(1.25)
            require(duplicate.AddTrack("video"), "AddTrack failed")
            time.sleep(1.25)
            track = counts["video"] + 1
            require(duplicate.GetTrackCount("video") == track, "video track count mismatch")
            require(duplicate.SetTrackName("video", track, "VTuber Zoom PILOT"), "track naming failed")
            require(duplicate.SetTrackLock("video", track, False), "could not unlock focus track")
            time.sleep(1.25)
            require(duplicate.SetMarkInOut(start, end - 1), "SetMarkInOut failed")
            require(duplicate.SetCurrentTimecode(tc(start, fps)), "could not set pilot playhead")
            time.sleep(1.25)
            item = duplicate.InsertGeneratorIntoTimeline("Adjustment Clip")
            if item is None:
                diagnostic = {
                    "page": resolve.GetCurrentPage(),
                    "current_timeline": project.GetCurrentTimeline().GetName(),
                    "current_timecode": duplicate.GetCurrentTimecode(),
                    "mark_in_out": duplicate.GetMarkInOut(),
                    "video_track_count": duplicate.GetTrackCount("video"),
                    "track_lock_states": {f"video{i}": duplicate.GetIsTrackLocked("video", i)
                                          for i in range(1, duplicate.GetTrackCount("video") + 1)},
                    "track_items": {f"V{i}": [
                        {"name": x.GetName(), "start": int(x.GetStart()), "end": int(x.GetEnd())}
                        for x in (duplicate.GetItemListInTrack("video", i) or [])]
                        for i in range(1, duplicate.GetTrackCount("video") + 1)},
                    "current_video_item": (duplicate.GetCurrentVideoItem().GetName()
                                           if duplicate.GetCurrentVideoItem() else None),
                }
                require(False, "Adjustment Clip insertion returned None: " +
                        json.dumps(diagnostic, ensure_ascii=False, default=str))
            duplicate.ClearMarkInOut()
            time.sleep(1.0)
            actual_track = item.GetTrackTypeAndIndex()
            require(actual_track == ["video", track] or actual_track == ("video", track),
                    f"clip landed on {actual_track}, expected video track {track}")
            require(int(item.GetStart()) == start and int(item.GetEnd()) == end,
                    f"clip range is {item.GetStart()}-{item.GetEnd()}, expected {start}-{end}")
            new_counts = {k: duplicate.GetTrackCount(k) for k in ("video", "audio", "subtitle")}
            for k in before_counts:
                require(new_counts[k] == before_counts[k] + (1 if k == "video" else 0),
                        f"{k} track count changed unexpectedly")
            require(signatures(duplicate, before_counts) == before,
                    "original tracks changed during insertion")

            comp = item.AddFusionComp()
            require(comp is not None, "AddFusionComp failed")
            nodes = list(comp.GetToolList().values())
            media_in = [n for n in nodes if n.GetAttrs().get("TOOLS_RegID") == "MediaIn"]
            media_out = [n for n in nodes if n.GetAttrs().get("TOOLS_RegID") == "MediaOut"]
            require(len(media_in) == 1 and len(media_out) == 1, "Fusion IO is ambiguous")
            transform = comp.AddTool("Transform", -32768, -32768)
            require(transform is not None, "could not add Transform")
            require(transform.ConnectInput("Input", media_in[0]), "Transform input connection failed")
            require(media_out[0].ConnectInput("Input", transform), "MediaOut connection failed")
            values = {"Size": 1.6, "Center": {1: -0.14, 2: 0.368, 3: 0.0}}
            for key, value in values.items():
                require(transform.SetInput(key, value), f"could not set Transform {key}")
            require(transform.SetInput("Edges", 0.0), "could not set Edges=Canvas")
            readback = {key: transform.GetInput(key) for key in ("Size", "Center", "Edges")}
            require(float(readback["Size"]) == values["Size"], "Size readback mismatch")
            center = readback["Center"]
            require(abs(float(center[1]) - values["Center"][1]) < 1e-6
                    and abs(float(center[2]) - values["Center"][2]) < 1e-6,
                    f"Center readback mismatch: {center}")
            require(duplicate.SetCurrentTimecode(tc(frame, fps)), "could not move to preview frame")
            stills = {}
            for label, edges in (("canvas", 0.0), ("duplicate-edge", 2.0)):
                require(transform.SetInput("Edges", edges), f"could not set Edges={edges}")
                path = Path(tempfile.gettempdir()) / f"armigon-focus-pilot-{label}.png"
                require(project.ExportCurrentFrameAsStill(str(path)), f"still export failed: {label}")
                require(path.is_file() and path.stat().st_size > 0, f"still missing: {path}")
                stills[label] = str(path)
            output = {"timeline": base.GetName(), "duplicate": duplicate.GetName(),
                      "range": [start, end], "track": track, "clip_id": item.GetUniqueId(),
                      "fusion_readback": readback, "stills": stills,
                      "original_tracks_unchanged": signatures(duplicate, before_counts) == before}
        finally:
            try:
                if duplicate is not None:
                    duplicate.ClearMarkInOut()
                    for (kind, index), locked in original_locks.items():
                        duplicate.SetTrackLock(kind, index, locked)
                    project.SetCurrentTimeline(base)
                    require(project.GetMediaPool().DeleteTimelines([duplicate]),
                            "could not delete disposable pilot timeline")
            except NameError:
                pass
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
