"""Disposable readback probe for mixed-FPS fullscreen focus intervals.

MCP-GAP: the community timeline MCP can duplicate timelines but has no action
for MediaPool.AppendToTimeline with fractional source-frame bounds or exact
GetStart/GetEnd(subframePrecision=True) readback. Use the Resolve scripting
API through resolve_common on a duplicate, then delete only that duplicate.
"""
from __future__ import annotations

import json
import time
from datetime import datetime

from scripts.resolve_common import preserved_state, require_resolve


PROJECT_NAME = "armigon-2026-09"
SOURCE_ID = "687e65a3-df94-4d56-8866-dd3e76bfb243"
DELAY = 1.2


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def find_timeline(project, timeline_id):
    return next((project.GetTimelineByIndex(i) for i in range(1, project.GetTimelineCount() + 1)
                 if project.GetTimelineByIndex(i).GetUniqueId() == timeline_id), None)


def protected_rows(timeline):
    rows = {"end_frame": timeline.GetEndFrame(), "video": [], "audio": [], "subtitle": []}
    for kind, count_key in (("video", "video"), ("audio", "audio"), ("subtitle", "subtitle")):
        for track_index in range(1, timeline.GetTrackCount(kind) + 1):
            if kind == "video" and track_index >= 4:
                continue
            rows[kind].append((track_index, tuple(
                (item.GetName(), item.GetStart(True), item.GetEnd(True))
                for item in sorted(timeline.GetItemListInTrack(kind, track_index) or [], key=lambda x: x.GetStart())
            )))
    return rows


def pool_items(folder):
    items = list(folder.GetClipList() or [])
    for subfolder in folder.GetSubFolderList() or []:
        items.extend(pool_items(subfolder))
    return items


def main():
    resolve = require_resolve()
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    check(project is not None and project.GetName() == PROJECT_NAME, "unexpected active project")
    source = find_timeline(project, SOURCE_ID)
    check(source is not None, "probe source timeline is missing")
    initial_timeline = project.GetCurrentTimeline()
    initial_count = project.GetTimelineCount()
    source_signature = (source.GetName(), source.GetStartFrame(), source.GetEndFrame(),
                        source.GetTrackCount("video"), source.GetTrackCount("audio"),
                        source.GetTrackCount("subtitle"))
    temp_name = "TMP_FRACTIONAL_9X16_PROBE_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    temp = None
    compound_media = None
    result = {"source_id": SOURCE_ID, "temp_name": temp_name, "status": "STARTED"}

    with preserved_state(resolve):
        try:
            base = sorted(source.GetItemListInTrack("video", 1) or [], key=lambda x: x.GetStart())[0]
            focus = next(item for item in (source.GetItemListInTrack("video", 2) or [])
                         if item.GetName() == "Adjustment Clip")
            media = base.GetMediaPoolItem()
            source_fps = float(media.GetClipProperty("FPS"))
            record_fps = float(source.GetSetting("timelineFrameRate"))
            focus_start = float(focus.GetStart(True))
            focus_end = float(focus.GetEnd(True))
            base_record_start = int(base.GetStart(True))
            base_source_start = int(base.GetSourceStartFrame())
            source_start = float(base_source_start) + (focus_start - base_record_start) * source_fps / record_fps
            source_end = float(base_source_start) + (focus_end - base_record_start) * source_fps / record_fps
            result.update({"source_fps": source_fps, "record_fps": record_fps,
                           "focus_record": [focus_start, focus_end],
                           "source_frame_bounds_sent": [source_start, source_end],
                           "source_start_time_expected": float(base.GetSourceStartTime()) +
                               (focus_start - float(base.GetStart(True))) / record_fps,
                           "source_duration_expected_seconds": (focus_end - focus_start) / record_fps})
            check(source_fps == 30.0 and record_fps == 60.0, "probe source is not the intended 30-to-60 case")
            check(focus_start.is_integer() and focus_end.is_integer() and focus_end - focus_start == 461,
                  "probe focus is not the intended 461-record-frame interval")
            check(not any(project.GetTimelineByIndex(i).GetName() == temp_name
                          for i in range(1, project.GetTimelineCount() + 1)), "temporary name collision")

            temp = source.DuplicateTimeline(temp_name)
            check(temp is not None and temp.GetName() == temp_name, "could not duplicate probe source")
            time.sleep(DELAY)
            check(project.GetTimelineCount() == initial_count + 1, "unexpected timeline count after duplicate")
            check(project.SetCurrentTimeline(temp), "could not activate disposable duplicate")
            time.sleep(DELAY)
            temp_base = sorted(temp.GetItemListInTrack("video", 1) or [], key=lambda x: x.GetStart())[0]
            check(temp.GetTrackCount("video") == 3, "unexpected video track layout in source duplicate")
            check(temp.AddTrack("video", {"index": 4}), "could not add temporary probe track")
            time.sleep(DELAY)
            check(temp.GetTrackCount("video") == 4, "temporary probe track did not read back")
            protected_before = protected_rows(temp)
            # A 30-to-60 source has a 2-record-frame cadence. At an odd start,
            # the first source sample has only one record frame left. Represent
            # that edge sample at 200% and keep the contiguous middle at 100%.
            # This avoids unsupported fractional source-frame bounds.
            first_source = base_source_start + (int(focus_start) - base_record_start) // 2
            first_capacity = 2 - ((int(focus_start) - base_record_start) % 2)
            first_length = min(int(focus_end - focus_start), first_capacity)
            segments = [(first_source, first_source + 1, int(focus_start),
                         int(focus_start) + first_length, 200.0 if first_length == 1 else 100.0)]
            cursor = int(focus_start) + first_length
            if cursor < int(focus_end):
                full_samples = (int(focus_end) - cursor) // 2
                if full_samples:
                    middle_source = base_source_start + (cursor - base_record_start) // 2
                    middle_end = cursor + full_samples * 2
                    segments.append((middle_source, middle_source + full_samples, cursor, middle_end, 100.0))
                    cursor = middle_end
                if cursor < int(focus_end):
                    tail_source = base_source_start + (cursor - base_record_start) // 2
                    segments.append((tail_source, tail_source + 1, cursor, cursor + 1, 200.0))
            result["integer_cadence_segments"] = segments
            result["readback"] = []
            segment_items = []
            for start_src, end_src, start_rec, end_rec, speed in segments:
                appended = project.GetMediaPool().AppendToTimeline([{
                    "mediaPoolItem": temp_base.GetMediaPoolItem(), "startFrame": start_src,
                    "endFrame": end_src, "mediaType": 1, "trackIndex": 4,
                    "recordFrame": start_rec}])
                time.sleep(DELAY)
                check(appended and len(appended) == 1, "AppendToTimeline did not return one probe segment")
                item = appended[0]
                segment_items.append(item)
                if speed != 100.0:
                    check(item.SetSpeed({"Percentage": speed, "RippleTimeline": True}),
                          f"SetSpeed {speed}% failed on a one-frame cadence segment")
                    time.sleep(DELAY)
                media = item.GetMediaPoolItem()
                actual = {"record_start": float(item.GetStart(True)),
                          "record_end": float(item.GetEnd(True)),
                          "record_duration": float(item.GetDuration(True)),
                          "source_start_time": float(item.GetSourceStartTime()),
                          "source_end_time": float(item.GetSourceEndTime()),
                          "source_start_frame_integer_api": item.GetSourceStartFrame(),
                          "source_end_frame_integer_api": item.GetSourceEndFrame(),
                          "speed": item.GetSpeed(),
                          "media_id": media.GetUniqueId() if media else None,
                          "expected_source_start_time": float(base.GetSourceStartTime()) +
                              (start_src - base_source_start) / source_fps}
                result["readback"].append(actual)
            compound = temp.CreateCompoundClip(segment_items, {
                "name": temp_name + "_FOCUS",
                "startTimecode": "00:00:00:00",
            })
            time.sleep(DELAY)
            check(compound is not None, "CreateCompoundClip returned no item")
            compound_media = compound.GetMediaPoolItem()
            check(compound_media is not None, "compound clip has no MediaPoolItem")
            result["compound"] = {
                "name": compound.GetName(),
                "record_start": float(compound.GetStart(True)),
                "record_end": float(compound.GetEnd(True)),
                "record_duration": float(compound.GetDuration(True)),
                "media_id": compound_media.GetUniqueId(),
                "media_fps": float(compound_media.GetClipProperty("FPS")),
                "media_frames": int(float(compound_media.GetClipProperty("Frames"))),
            }
            check(temp.GetTrackCount("video") == 4 and compound.GetStart(True) == focus_start and
                  compound.GetEnd(True) == focus_end and compound.GetDuration(True) == focus_end - focus_start,
                  f"compound range was not exact: {result['compound']}")
            check(temp.AddTrack("video", {"index": 5}), "could not add compound overlay probe track")
            time.sleep(DELAY)
            frame_count = int(float(compound_media.GetClipProperty("Frames")))
            compound_item = project.GetMediaPool().AppendToTimeline([{
                "mediaPoolItem": compound_media, "startFrame": 0, "endFrame": frame_count,
                "mediaType": 1, "trackIndex": 5, "recordFrame": focus_start}])
            time.sleep(DELAY)
            check(compound_item and len(compound_item) == 1, "compound overlay append failed")
            final_overlay = compound_item[0]
            result["final_overlay_readback"] = {
                "start": float(final_overlay.GetStart(True)), "end": float(final_overlay.GetEnd(True)),
                "duration": float(final_overlay.GetDuration(True)),
                "source_start_time": float(final_overlay.GetSourceStartTime()),
                "source_end_time": float(final_overlay.GetSourceEndTime()),
                "media_id": final_overlay.GetMediaPoolItem().GetUniqueId(),
            }
            protected_after = protected_rows(temp)
            result["protected_tracks_unchanged"] = protected_after == protected_before
            result["protected_diffs"] = []
            if protected_after != protected_before:
                if protected_after["end_frame"] != protected_before["end_frame"]:
                    result["protected_diffs"].append({"kind": "timeline", "before_end": protected_before["end_frame"],
                                                       "after_end": protected_after["end_frame"]})
                for kind in ("video", "audio", "subtitle"):
                    old_tracks = {row[0]: row[1] for row in protected_before[kind]}
                    new_tracks = {row[0]: row[1] for row in protected_after[kind]}
                    for track_index in sorted(set(old_tracks) | set(new_tracks)):
                        old_items = old_tracks.get(track_index, ())
                        new_items = new_tracks.get(track_index, ())
                        if old_items != new_items:
                            changed = [{"before": left, "after": right}
                                       for left, right in zip(old_items, new_items) if left != right][:4]
                            result["protected_diffs"].append({"kind": kind, "track": track_index,
                                                              "before_count": len(old_items),
                                                              "after_count": len(new_items),
                                                              "changed_sample": changed})
            result["status"] = "PASS" if (
                result["readback"][0]["record_start"] == focus_start and
                result["readback"][-1]["record_end"] == focus_end and
                all(a["record_end"] == b["record_start"] for a, b in zip(result["readback"], result["readback"][1:])) and
                result["compound"]["media_fps"] == 60.0 and result["compound"]["media_frames"] == int(focus_end - focus_start) and
                result["final_overlay_readback"]["start"] == focus_start and
                result["final_overlay_readback"]["end"] == focus_end and
                result["final_overlay_readback"]["duration"] == focus_end - focus_start and
                result["final_overlay_readback"]["media_id"] == compound_media.GetUniqueId()) else "FAIL_READBACK"
            print(json.dumps({"probe": result}, ensure_ascii=True, indent=2), flush=True)
        except Exception as exc:
            result["status"] = "FAILED"
            result["error"] = repr(exc)
            print(json.dumps({"probe": result}, ensure_ascii=True, indent=2), flush=True)
            raise
        finally:
            try:
                if temp is not None:
                    current = project.GetCurrentTimeline()
                    if current and current.GetUniqueId() == temp.GetUniqueId():
                        restore = initial_timeline or source
                        check(project.SetCurrentTimeline(restore), "could not restore active timeline before probe cleanup")
                        time.sleep(DELAY)
                    check(project.GetMediaPool().DeleteTimelines([temp]), "could not delete disposable duplicate")
                    time.sleep(DELAY)
                    check(find_timeline(project, temp.GetUniqueId()) is None, "disposable duplicate remains")
                    check(project.GetTimelineCount() == initial_count, "timeline count did not return after cleanup")
                if compound_media is not None:
                    existing = {item.GetUniqueId(): item for item in pool_items(project.GetMediaPool().GetRootFolder())}
                    if compound_media.GetUniqueId() in existing:
                        check(project.GetMediaPool().DeleteClips([existing[compound_media.GetUniqueId()]]),
                              "could not delete disposable compound media item")
                        time.sleep(DELAY)
                    check(compound_media.GetUniqueId() not in {
                        item.GetUniqueId() for item in pool_items(project.GetMediaPool().GetRootFolder())},
                        "disposable compound media item remains in the Media Pool")
                check((source.GetName(), source.GetStartFrame(), source.GetEndFrame(),
                       source.GetTrackCount("video"), source.GetTrackCount("audio"),
                       source.GetTrackCount("subtitle")) == source_signature,
                      "probe source signature changed")
                check(pm.SaveProject(), "SaveProject failed after disposable probe cleanup")
                result["cleanup"] = "temporary duplicate deleted; project saved; source structure unchanged"
            except Exception as cleanup_error:
                result["cleanup_error"] = repr(cleanup_error)
                result["status"] = "CLEANUP_FAILED"
                raise

    print(json.dumps(result, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
