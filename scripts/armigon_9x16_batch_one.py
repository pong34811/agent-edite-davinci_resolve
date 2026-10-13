"""Build exactly one approved Armigon 9:16 variant and verify it before exit.

MCP-GAP: timeline.duplicate_clips/set_transform and MediaPool.AppendToTimeline /
TimelineItem.SetSpeed -> the community MCP has no explicit source-range append
or per-item speed action. Exact 30-to-60 fps focus windows with odd record-frame
edges require a video-only cadence compound built on a disposable duplicate.
Use the verified Resolve scripting API through resolve_common and read back
each step; remove only this invocation's target/assets if a check fails.

Run once per source with --source-id. Never edits a source timeline or renders.
"""
from __future__ import annotations

import argparse
import json
import re
import time
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

from scripts.backup_drp import verify_drp
from scripts.resolve_common import connect_resolve, preserved_state


PROJECT_NAME = "armigon-2026-09"
PROJECT_ID = "9a7d3e92-e44c-4ba4-afba-7c2dbe1090e1"
PILOT_ID = "8e8d12d6-a2a3-40a7-97b9-aff090641b2e"
BASELINE = Path(r"G:\My Drive\Projects\Armigon\2026-09\armigon-2026-09_9x16_preflight_20261012.json")
BACKUP = Path(r"G:\My Drive\Projects\Armigon\2026-09\armigon-2026-09_before_9x16_retry_20261012_2300.drp")
OUT_DIR = Path(r"G:\My Drive\Projects\Armigon\2026-09\.superpowers\brainstorm\1617-1791799790\content")
DELAY = 1.0

VIDEO_PROPS = (
    "Pan", "Tilt", "ZoomX", "ZoomY", "ZoomGang", "RotationAngle", "AnchorPointX", "AnchorPointY",
    "Pitch", "Yaw", "FlipX", "FlipY", "CropLeft", "CropRight", "CropTop", "CropBottom",
    "CropSoftness", "CropRetain", "DynamicZoomEase", "CompositeMode", "Opacity", "Distortion",
    "RetimeProcess", "MotionEstimation", "Scaling", "ResizeFilter", "TransformEnabled",
    "CroppingEnabled", "DynamicZoomEnabled", "CompositeEnabled", "LensCorrectionEnabled",
    "RetimeAndScalingEnabled",
)
AUDIO_PROPS = (
    "AudioVolumeEnabled", "AudioVolume", "AudioPanEnabled", "AudioPan", "AudioPitchCents",
    "AudioPitchSemiTones", "AudioPitchEnabled", "AudioSyncOffset", "AudioSyncOffsetIsManual",
)
RASTER = (
    ("useCustomSettings", "1"),
    ("timelineResolutionWidth", "1080"),
    ("timelineResolutionHeight", "1920"),
    ("timelineOutputResMatchTimelineRes", "1"),
    ("timelineOutputResolutionWidth", "1080"),
    ("timelineOutputResolutionHeight", "1920"),
    ("timelinePixelAspectRatio", "square"),
    ("timelineInputResMismatchBehavior", "scaleToFit"),
    ("timelineOutputResMismatchBehavior", "scaleToFit"),
)

CANVAS_W, CANVAS_H = 1080.0, 1920.0
SPLIT = 960.0
FOCUS = {"Size": 2.05, "Pivot": {1: 0.746, 2: 0.68, 3: 0.0}, "Center": {1: 0.28, 2: 0.292, 3: 0.0}}
GIF_ZOOM = 0.28
GIF_CENTER = (220.0, 260.0)

# The 1280x702 streams place the approved brown-cap/yellow-eye Armigon mascot
# at the right edge. Frame the game from the same approved right-side game crop
# and use a separate crop around the mascot's head and upper body for the lower
# panel. The one 1920x1080 Valorant VOD places the smaller mascot near the lower
# middle-right, so it uses a matching lower panel crop around that source area.
LAYOUTS = {
    (1280, 702): {
        "game": (672.5, 0.0, 1280.0, 540.0),
        # WYSIWYG-checked on the approved brown-cap/yellow-eye mascot.
        # These bounds keep the purple character below the lower panel/focus crop.
        "avatar": (830.0, 90.0, 1280.0, 490.0),
        "focus_fullscreen": (1049.375, 28.0, 1280.0, 438.0),
    },
    (1920, 1080): {
        "game": (352.5, 0.0, 1567.5, 1080.0),
        "avatar": (1170.0, 600.0, 1710.0, 1080.0),
        "focus_fullscreen": (1190.0, 680.0, 1415.0, 1080.0),
    },
}


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def normalize(value):
    if isinstance(value, dict):
        return {str(k): normalize(v) for k, v in sorted(value.items(), key=lambda row: str(row[0]))}
    if isinstance(value, (list, tuple)):
        return [normalize(v) for v in value]
    if isinstance(value, float):
        return round(value, 6)
    if value is None or isinstance(value, (str, int, bool)):
        return value
    return str(value)


def signature_diff(expected, actual, path="root", limit=40):
    """Small diagnostic for a failed readback; never changes project state."""
    diffs = []

    def walk(left, right, current):
        if len(diffs) >= limit:
            return
        if isinstance(left, dict) and isinstance(right, dict):
            for key in sorted(set(left) | set(right), key=str):
                if key not in left or key not in right:
                    diffs.append({"path": f"{current}.{key}", "expected": left.get(key), "actual": right.get(key)})
                else:
                    walk(left[key], right[key], f"{current}.{key}")
                if len(diffs) >= limit:
                    return
        elif isinstance(left, (list, tuple)) and isinstance(right, (list, tuple)):
            if len(left) != len(right):
                diffs.append({"path": f"{current}.length", "expected": len(left), "actual": len(right)})
            for index, (lvalue, rvalue) in enumerate(zip(left, right)):
                walk(lvalue, rvalue, f"{current}[{index}]")
                if len(diffs) >= limit:
                    return
        elif left != right:
            diffs.append({"path": current, "expected": left, "actual": right})

    walk(expected, actual, path)
    return diffs


def item_media_id(item):
    media = item.GetMediaPoolItem()
    return media.GetUniqueId() if media else None


def item_signature(item, properties=()):
    result = {
        "name": item.GetName(),
        "start": item.GetStart(),
        "end": item.GetEnd(),
        "source_start": item.GetSourceStartFrame(),
        "source_end": item.GetSourceEndFrame(),
        "media_id": item_media_id(item),
    }
    if properties:
        result["properties"] = {key: normalize(item.GetProperty(key)) for key in properties}
    return result


def fusion_transform(item):
    count = item.GetFusionCompCount()
    check(count >= 1, "focus Adjustment Clip has no Fusion composition")
    comp = item.GetFusionCompByIndex(count)
    matches = []
    for tool in (comp.GetToolList() or {}).values():
        attrs = tool.GetAttrs() or {}
        if attrs.get("TOOLS_RegID") == "Transform" and attrs.get("TOOLS_Name") == "Transform1":
            matches.append(tool)
    check(len(matches) == 1, f"expected one Fusion Transform1, found {len(matches)}")
    return matches[0]


def fusion_signature(item):
    transform = fusion_transform(item)
    return {key: normalize(transform.GetInput(key)) for key in ("Size", "Center", "Pivot", "Edges", "MotionBlur")}


def track_rows(tl, kind, properties=()):
    rows = []
    for index in range(1, tl.GetTrackCount(kind) + 1):
        rows.append({
            "index": index,
            "name": tl.GetTrackName(kind, index),
            "enabled": tl.GetIsTrackEnabled(kind, index),
            "locked": tl.GetIsTrackLocked(kind, index),
            "items": [item_signature(item, properties) for item in sorted(
                tl.GetItemListInTrack(kind, index) or [], key=lambda item: item.GetStart())],
        })
    return rows


def protected_signature(tl):
    return {
        "range": (tl.GetStartFrame(), tl.GetEndFrame()),
        "fps": normalize(tl.GetSetting("timelineFrameRate")),
        "audio_tracks": track_rows(tl, "audio", AUDIO_PROPS),
        "subtitle_tracks": track_rows(tl, "subtitle"),
    }


def full_original_signature(tl):
    video = track_rows(tl, "video", VIDEO_PROPS)
    for index in range(1, tl.GetTrackCount("video") + 1):
        for item_index, item in enumerate(sorted(tl.GetItemListInTrack("video", index) or [], key=lambda x: x.GetStart())):
            if item.GetName() == "Adjustment Clip":
                video[index - 1]["items"][item_index]["fusion"] = fusion_signature(item)
    return {
        "id": tl.GetUniqueId(),
        "name": tl.GetName(),
        "settings": {key: normalize(tl.GetSetting(key)) for key in (
            "timelineResolutionWidth", "timelineResolutionHeight", "timelineFrameRate")},
        "range": (tl.GetStartFrame(), tl.GetEndFrame()),
        "video_tracks": video,
        "audio_tracks": track_rows(tl, "audio", AUDIO_PROPS),
        "subtitle_tracks": track_rows(tl, "subtitle"),
    }


def find_timeline(project, timeline_id=None, name=None):
    hits = []
    for index in range(1, project.GetTimelineCount() + 1):
        timeline = project.GetTimelineByIndex(index)
        if ((timeline_id is None or timeline.GetUniqueId() == timeline_id) and
                (name is None or timeline.GetName() == name)):
            hits.append(timeline)
    return hits


def pool_items(folder):
    items = list(folder.GetClipList() or [])
    for subfolder in folder.GetSubFolderList() or []:
        items.extend(pool_items(subfolder))
    return items


def build_focus_overlay(project, source, target, source_clip, focus_range, media_pool, artifact_holder=None):
    """Append a full-height focus source, using a temporary compound for mixed-FPS odd edges."""
    start_record, end_record = map(int, focus_range)
    record_fps = float(target.GetSetting("timelineFrameRate"))
    media = source_clip.GetMediaPoolItem()
    check(media is not None, "base video has no MediaPoolItem")
    source_fps = float(media.GetClipProperty("FPS"))
    source_base = int(source_clip.GetSourceStartFrame())
    record_base = int(source_clip.GetStart(True))
    check(record_fps > 0 and source_fps > 0, "invalid source or record frame rate")
    source_start_exact = source_base + (start_record - record_base) * source_fps / record_fps
    source_end_exact = source_base + (end_record - record_base) * source_fps / record_fps

    # Every mixed-rate interval uses the cadence compound, including apparently
    # integral 30-to-60 boundaries. Direct appends can double the record span
    # for those boundaries on Resolve 21.1 (observed on source ec8b7414).
    if source_fps == record_fps:
        source_start = int(source_start_exact)
        source_end = int(source_end_exact)
        appended = media_pool.AppendToTimeline([{
            "mediaPoolItem": media, "startFrame": source_start, "endFrame": source_end,
            "mediaType": 1, "trackIndex": 5, "recordFrame": start_record,
        }])
        time.sleep(DELAY)
        check(appended and len(appended) == 1, "could not append full-screen focus source range")
        overlay = appended[0]
        check((overlay.GetStart(True), overlay.GetEnd(True), overlay.GetDuration(True)) ==
              (start_record, end_record, end_record - start_record),
              "full-screen focus source range did not map to the exact record interval")
        check(item_media_id(overlay) == media.GetUniqueId(),
              "full-screen focus source range references the wrong media")
        return overlay, None, {
            "method": "direct_source_range",
            "source_fps": source_fps,
            "record_fps": record_fps,
            "source_start": source_start,
            "source_end": source_end,
        }

    check(source_fps == 30.0 and record_fps == 60.0,
          f"unsupported mixed-FPS focus source: {source_fps:g}->{record_fps:g}")
    temp_name = f"TMP_9X16_FOCUS_{source.GetUniqueId()[:8]}_{datetime.now().strftime('%H%M%S_%f')}"
    check(not find_timeline(project, name=temp_name), "temporary focus builder name collision")
    original_active = project.GetCurrentTimeline()
    original_tc = original_active.GetCurrentTimecode() if original_active else None
    temp = None
    temp_id = None
    compound_media = None
    committed = False
    try:
        check(project.SetCurrentTimeline(source), "could not activate focus source for temporary builder")
        time.sleep(DELAY)
        temp = source.DuplicateTimeline(temp_name)
        check(temp is not None and temp.GetName() == temp_name, "could not duplicate focus source")
        temp_id = temp.GetUniqueId()
        check(bool(temp_id), "temporary focus builder returned no stable timeline ID")
        check(len(find_timeline(project, timeline_id=temp_id, name=temp_name)) == 1,
              "temporary focus builder ID/name failed its creation readback")
        if artifact_holder is not None:
            artifact_holder["temp_name"] = temp_name
            artifact_holder["temp_id"] = temp_id
        time.sleep(DELAY)
        check(project.SetCurrentTimeline(temp), "could not activate temporary focus builder")
        time.sleep(DELAY)
        temp_base = sorted(temp.GetItemListInTrack("video", 1) or [], key=lambda x: x.GetStart())[0]
        check(temp.GetTrackCount("video") == 3, "unexpected video layout in temporary focus builder")
        check(temp.AddTrack("video", {"index": 4}), "could not add temporary focus segment track")
        time.sleep(DELAY)
        check(temp.GetTrackCount("video") == 4, "temporary focus segment track did not read back")

        base_record = int(temp_base.GetStart(True))
        base_source = int(temp_base.GetSourceStartFrame())
        first_source = base_source + (start_record - base_record) // 2
        first_capacity = 2 - ((start_record - base_record) % 2)
        first_length = min(end_record - start_record, first_capacity)
        segments = [(first_source, first_source + 1, start_record,
                     start_record + first_length, 200.0 if first_length == 1 else 100.0)]
        cursor = start_record + first_length
        if cursor < end_record:
            full_samples = (end_record - cursor) // 2
            if full_samples:
                middle_source = base_source + (cursor - base_record) // 2
                middle_end = cursor + full_samples * 2
                segments.append((middle_source, middle_source + full_samples, cursor, middle_end, 100.0))
                cursor = middle_end
            if cursor < end_record:
                tail_source = base_source + (cursor - base_record) // 2
                segments.append((tail_source, tail_source + 1, cursor, cursor + 1, 200.0))

        segment_items = []
        segment_readbacks = []
        for source_start, source_end, record_start, record_end, speed in segments:
            appended = media_pool.AppendToTimeline([{
                "mediaPoolItem": temp_base.GetMediaPoolItem(), "startFrame": source_start,
                "endFrame": source_end, "mediaType": 1, "trackIndex": 4,
                "recordFrame": record_start,
            }])
            time.sleep(DELAY)
            check(appended and len(appended) == 1, "temporary focus segment append failed")
            item = appended[0]
            segment_items.append(item)
            if speed != 100.0:
                check(item.SetSpeed({"Percentage": speed, "RippleTimeline": True}),
                      f"temporary {speed:g}% cadence adjustment failed")
                time.sleep(DELAY)
            media_item = item.GetMediaPoolItem()
            segment_readbacks.append({
                "start": item.GetStart(True), "end": item.GetEnd(True),
                "duration": item.GetDuration(True), "source_start": item.GetSourceStartTime(),
                "source_end": item.GetSourceEndTime(), "speed": item.GetSpeed(),
                "media_id": media_item.GetUniqueId() if media_item else None,
            })
            check((segment_readbacks[-1]["start"], segment_readbacks[-1]["end"],
                   segment_readbacks[-1]["duration"]) ==
                  (record_start, record_end, record_end - record_start),
                  f"temporary focus segment did not match its planned record range: {segment_readbacks[-1]}")
            check(segment_readbacks[-1]["media_id"] == temp_base.GetMediaPoolItem().GetUniqueId(),
                  "temporary focus segment references the wrong source")

        compound = temp.CreateCompoundClip(segment_items, {
            "name": temp_name + "_COMPOUND",
            "startTimecode": "00:00:00:00",
        })
        time.sleep(DELAY)
        check(compound is not None, "CreateCompoundClip returned no focus item")
        compound_media = compound.GetMediaPoolItem()
        check(compound_media is not None, "focus compound has no MediaPoolItem")
        if artifact_holder is not None:
            artifact_holder["compound_media_id"] = compound_media.GetUniqueId()
        compound_fps = float(compound_media.GetClipProperty("FPS"))
        compound_frames = int(float(compound_media.GetClipProperty("Frames")))
        check((compound.GetStart(True), compound.GetEnd(True), compound.GetDuration(True)) ==
              (start_record, end_record, end_record - start_record),
              "focus compound record range failed readback")
        check(compound_fps == record_fps and compound_frames == end_record - start_record,
              f"focus compound source cadence/range mismatch: {compound_fps} fps, {compound_frames} frames")

        check(project.SetCurrentTimeline(target), "could not activate target after compound build")
        time.sleep(DELAY)
        appended = media_pool.AppendToTimeline([{
            "mediaPoolItem": compound_media, "startFrame": 0, "endFrame": compound_frames,
            "mediaType": 1, "trackIndex": 5, "recordFrame": start_record,
        }])
        time.sleep(DELAY)
        check(appended and len(appended) == 1, "could not append focus compound to target V5")
        overlay = appended[0]
        check(item_media_id(overlay) == compound_media.GetUniqueId() and
              (overlay.GetStart(True), overlay.GetEnd(True), overlay.GetDuration(True)) ==
              (start_record, end_record, end_record - start_record),
              "full-screen compound overlay failed exact target-range readback")
        committed = True
        return overlay, compound_media, {
            "method": "cadence_compound_30_to_60",
            "source_fps": source_fps,
            "record_fps": record_fps,
            "source_start_exact": source_start_exact,
            "source_end_exact": source_end_exact,
            "segments": segment_readbacks,
            "compound_media_id": compound_media.GetUniqueId(),
            "compound_fps": compound_fps,
            "compound_frames": compound_frames,
        }
    finally:
        try:
            current = project.GetCurrentTimeline()
            if original_active and (not current or current.GetUniqueId() != original_active.GetUniqueId()):
                check(project.SetCurrentTimeline(original_active), "could not restore target after focus builder")
                time.sleep(DELAY)
                if original_tc is not None:
                    original_active.SetCurrentTimecode(original_tc)
            if temp_id is not None:
                temp_matches = find_timeline(project, timeline_id=temp_id, name=temp_name)
            else:
                temp_matches = []
            if temp_matches:
                check(len(temp_matches) == 1, "temporary focus builder ID/name is not unique during cleanup")
                check(project.GetMediaPool().DeleteTimelines(temp_matches), "could not delete temporary focus builder")
                time.sleep(DELAY)
                check(not find_timeline(project, timeline_id=temp_id, name=temp_name),
                      "temporary focus builder remains after cleanup")
            if compound_media is not None and not committed:
                existing = {item.GetUniqueId(): item for item in pool_items(media_pool.GetRootFolder())}
                media_id = compound_media.GetUniqueId()
                if media_id in existing:
                    check(media_pool.DeleteClips([existing[media_id]]),
                          "could not delete unreferenced focus compound after failure")
                    time.sleep(DELAY)
                check(media_id not in {item.GetUniqueId() for item in pool_items(media_pool.GetRootFolder())},
                      "unreferenced focus compound remains after failure")
        except Exception as cleanup_error:
            if committed:
                raise RuntimeError(f"focus builder cleanup failed after compound append: {cleanup_error!r}")
            raise


def folder_id(folder):
    return folder.GetUniqueId() if folder is not None and "GetUniqueId" in dir(folder) else None


def subtitle_drt_signature(path):
    with zipfile.ZipFile(path) as archive:
        sequence_files = [name for name in archive.namelist()
                          if name.startswith("SeqContainer/") and name.lower().endswith(".xml")]
        subtitle_sequences = []
        for name in sequence_files:
            candidate = ET.fromstring(archive.read(name))
            track_vec = candidate.find("SubtitleTrackVec")
            tracks = track_vec.findall("./Element/Sm2TiTrack") if track_vec is not None else []
            if tracks:
                subtitle_sequences.append((name, candidate, tracks))
        check(len(subtitle_sequences) == 1,
              f"expected one sequence XML with native Subtitle tracks in {path}, "
              f"found {[(name, len(tracks)) for name, _, tracks in subtitle_sequences]}")
        _, root, tracks = subtitle_sequences[0]
    track_vec = root.find("SubtitleTrackVec")
    check(track_vec is not None, f"subtitle track container missing in {path}")
    check(len(tracks) == 1, f"expected one native subtitle track in {path}, found {len(tracks)}")
    track = tracks[0]

    def canonical(element):
        children = [canonical(child) for child in list(element) if child.tag != "Sequence"]
        return {
            "tag": element.tag,
            "attrs": {key: value for key, value in sorted(element.attrib.items()) if key != "DbId"},
            "text": element.text or "",
            "children": children,
        }

    cues = []
    items = track.find("Items")
    if items is not None:
        for wrapper in items.findall("./Element"):
            cue = wrapper.find("Sm2TiGenerator")
            if cue is None:
                continue
            fields = {child.tag: child.text or "" for child in list(cue)}
            if fields.get("PrettyType") == "Subtitle":
                start = int(fields["Start"])
                cues.append((fields.get("Name", ""), start, start + int(fields["Duration"])))
    return {"track": canonical(track), "cues": cues}


def portrait_transform(crop, panel_top, source_w, source_h, crop_top_src=0.0, panel_height=SPLIT):
    x0, y0, x1, y1 = crop
    scale = panel_height / (y1 - y0)
    fit = min(CANVAS_W / source_w, CANVAS_H / source_h)
    tilt_px = source_h * fit / CANVAS_H
    zoom = scale / fit
    source_cx = (x0 + x1) / 2
    source_cy = (y0 + y1) / 2
    target_cy = panel_top + panel_height / 2
    center_x = CANVAS_W / 2 + (source_w / 2 - source_cx) * scale
    center_y = target_cy + (source_h / 2 - source_cy) * scale
    return {
        "ZoomX": zoom,
        "ZoomY": zoom,
        "Pan": center_x - CANVAS_W / 2,
        "Tilt": -(center_y - CANVAS_H / 2) / tilt_px,
        "CropLeft": 0.0,
        "CropRight": 0.0,
        "CropTop": crop_top_src * fit,
        "CropBottom": 0.0,
    }


def set_float(item, key, value, tolerance):
    last = None
    for _ in range(3):
        item.SetProperty(key, float(value))
        time.sleep(0.25)
        last = item.GetProperty(key)
        if last is not None and abs(float(last) - float(value)) <= tolerance:
            return float(last)
        time.sleep(0.35)
    raise RuntimeError(f"{item.GetName()} {key} readback mismatch: wanted {value}, got {last}")


def set_clip_transform(item, properties):
    item.SetProperty("ZoomGang", True)
    time.sleep(0.25)
    check(bool(item.GetProperty("ZoomGang")), f"{item.GetName()}: ZoomGang did not read back as linked")
    for key, value in properties.items():
        tolerance = 0.8 if key in ("Pan", "Tilt") else 0.008 if key.startswith("Zoom") else 0.015
        set_float(item, key, value, tolerance)
    return {key: normalize(item.GetProperty(key)) for key in (*properties.keys(), "ZoomGang")}


def dimensions(item):
    media = item.GetMediaPoolItem()
    check(media is not None, f"source video item {item.GetName()} has no Media Pool item")
    props = media.GetClipProperty() or {}
    match = re.match(r"\s*(\d+)\s*x\s*(\d+)\s*$", str(props.get("Resolution", "")))
    check(match is not None, f"could not read source resolution: {props.get('Resolution')}")
    return int(match.group(1)), int(match.group(2))


def set_point_and_read(transform, key, wanted):
    transform.SetInput(key, wanted, 0.0)
    time.sleep(0.3)
    actual = normalize(transform.GetInput(key))
    for axis, value in wanted.items():
        check(abs(float(actual[str(axis)]) - float(value)) < 0.0001,
              f"{key} readback mismatch: {actual}")
    return actual


def verify_focus(transform, duration):
    times = (0.0, max(0.0, (duration - 1) / 2.0), float(max(0, duration - 1)))
    samples = []
    for sample_time in times:
        sample = {key: normalize(transform.GetInput(key, sample_time)) for key in ("Size", "Pivot", "Center")}
        check(abs(float(sample["Size"]) - FOCUS["Size"]) < 0.0001,
              f"focus Size differs at Fusion frame {sample_time}: {sample}")
        for key in ("Pivot", "Center"):
            for axis, value in FOCUS[key].items():
                check(abs(float(sample[key][str(axis)]) - float(value)) < 0.0001,
                      f"focus {key} differs at Fusion frame {sample_time}: {sample}")
        samples.append({"time": sample_time, "inputs": sample})
    return samples


def main(source_id):
    backup_bytes = verify_drp(BACKUP)
    check(BASELINE.is_file(), f"preflight baseline missing: {BASELINE}")
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    check(baseline.get("project", {}).get("name") == PROJECT_NAME,
          "baseline belongs to a different project")
    source_rows = [row for row in baseline.get("timelines", []) if row.get("timeline_id") == source_id]
    check(len(source_rows) == 1, f"source ID is absent or duplicated in the preflight baseline: {source_id}")
    baseline_row = source_rows[0]
    source_name = baseline_row["name"]
    check(source_name.endswith("-vdo"), f"source is not one of the approved -vdo timelines: {source_name}")
    target_name = source_name + "_9x16"
    target_name = target_name.replace("\x00", "")

    resolve = connect_resolve()
    check(resolve is not None, "cannot connect to Resolve")
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    check(project is not None and project.GetName() == PROJECT_NAME and project.GetUniqueId() == PROJECT_ID,
          "active project is not the approved armigon-2026-09 project")
    check(not project.IsRenderingInProgress(), "Resolve is rendering; refusing this timeline")

    baseline_sources = {(row["timeline_id"], row["name"]) for row in baseline.get("timelines", [])}
    live_sources = {
        (project.GetTimelineByIndex(index).GetUniqueId(), project.GetTimelineByIndex(index).GetName())
        for index in range(1, project.GetTimelineCount() + 1)
        if project.GetTimelineByIndex(index).GetName().endswith("-vdo")
    }
    check(len(baseline_sources) == 48 and live_sources == baseline_sources,
          "live source timeline IDs/names drifted from the preflight snapshot")
    expected_vertical_names = {row["name"] + "_9x16" for row in baseline.get("timelines", [])}
    existing_vertical_names = {
        project.GetTimelineByIndex(index).GetName()
        for index in range(1, project.GetTimelineCount() + 1)
        if project.GetTimelineByIndex(index).GetName().endswith("_9x16")
    }
    check(existing_vertical_names <= expected_vertical_names,
          "unexpected _9x16 timeline already exists; refusing to overwrite it")
    check(not find_timeline(project, name=target_name), f"target already exists: {target_name}")

    source_hits = find_timeline(project, timeline_id=source_id, name=source_name)
    check(len(source_hits) == 1, "source timeline ID/name is not unique")
    source = source_hits[0]
    check((source.GetStartFrame(), source.GetEndFrame()) ==
          (baseline_row["start_frame"], baseline_row["end_frame"]),
          "source timeline range changed since preflight")
    check(float(source.GetSetting("timelineFrameRate")) == float(baseline_row["fps"]),
          "source timeline frame rate changed since preflight")
    check((str(source.GetSetting("timelineResolutionWidth")), str(source.GetSetting("timelineResolutionHeight"))) ==
          (str(baseline_row["width"]), str(baseline_row["height"])),
          "source timeline raster changed since preflight")
    check((source.GetTrackCount("video"), source.GetTrackCount("audio"), source.GetTrackCount("subtitle")) ==
          (3, 3, 1), "source track counts differ from the approved pattern")

    original_v1 = sorted(source.GetItemListInTrack("video", 1) or [], key=lambda item: item.GetStart())
    original_focus = sorted(source.GetItemListInTrack("video", 2) or [], key=lambda item: item.GetStart())
    original_reactions = sorted(source.GetItemListInTrack("video", 3) or [], key=lambda item: item.GetStart())
    check(len(original_v1) == 1 and (original_v1[0].GetStart(), original_v1[0].GetEnd()) ==
          (source.GetStartFrame(), source.GetEndFrame()), "source V1 is not one continuous base clip")
    check(len(original_focus) == 1 and original_focus[0].GetName() == "Adjustment Clip",
          "source V2 does not contain exactly one VTUBER FOCUS adjustment clip")
    check(len(original_reactions) <= 1, "source has multiple reaction overlays; requires a per-timeline review")
    focus_range = (original_focus[0].GetStart(), original_focus[0].GetEnd())
    check(focus_range[1] > focus_range[0], "source focus interval has an invalid range")

    source_w, source_h = dimensions(original_v1[0])
    layout = LAYOUTS.get((source_w, source_h))
    check(layout is not None, f"no reviewed portrait crop layout for {source_w}x{source_h}")

    initial_timeline = project.GetCurrentTimeline()
    check(initial_timeline is not None, "Resolve has no active timeline to preserve")
    initial_timeline_id = initial_timeline.GetUniqueId()
    initial_timecode = initial_timeline.GetCurrentTimecode()
    initial_page = resolve.GetCurrentPage()
    media_pool = project.GetMediaPool()
    initial_folder = media_pool.GetCurrentFolder()
    initial_folder_id = folder_id(initial_folder)
    initial_count = project.GetTimelineCount()

    result = {
        "project": PROJECT_NAME,
        "project_id": PROJECT_ID,
        "source_id": source_id,
        "source_name": source_name,
        "target_name": target_name,
        "backup_path": str(BACKUP),
        "backup_bytes_verified": backup_bytes,
        "layout": "Game Top / VTuber Bottom",
        "source_resolution": [source_w, source_h],
        "crop_profile": f"{source_w}x{source_h}",
        "focus_target": "user-approved brown-cap, yellow-eye chibi from reference image 2",
        "focus_range": list(focus_range),
        "gif_count": len(original_reactions),
        "fps": float(baseline_row["fps"]),
        "raster": [1080, 1920],
        "steps": [],
    }
    created = None
    created_compound_media = None
    focus_artifact = {}
    source_signature = None
    protected_before = None
    api_cues = None
    original_states = None
    subtitle_source_path = OUT_DIR / f"source_{source_id}.drt"
    subtitle_target_path = OUT_DIR / f"target_{source_id}.drt"

    try:
        with preserved_state(resolve):
            check(project.SetCurrentTimeline(source), "could not activate source for DRT baseline export")
            time.sleep(DELAY)
            # Read track enable state only while this timeline is active. On
            # Resolve 21.1, GetIsTrackEnabled can report false for audio and
            # subtitle tracks when queried through an inactive Timeline object.
            source_signature = full_original_signature(source)
            protected_before = protected_signature(source)
            check(len(protected_before["subtitle_tracks"]) == 1,
                  "source does not have exactly one Subtitle track")
            api_cues = [(item["name"], item["start"], item["end"])
                        for item in protected_before["subtitle_tracks"][0]["items"]]
            original_states = {
                "game": (source.GetIsTrackEnabled("video", 1), source.GetIsTrackLocked("video", 1)),
                "focus": (source.GetIsTrackEnabled("video", 2), source.GetIsTrackLocked("video", 2)),
                "reactions": (source.GetIsTrackEnabled("video", 3), source.GetIsTrackLocked("video", 3)),
            }
            check(source.Export(str(subtitle_source_path), resolve.EXPORT_DRT, resolve.EXPORT_NONE),
                  "source DRT export failed")
            source_drt = subtitle_drt_signature(subtitle_source_path)
            check(source_drt["cues"] == api_cues,
                  "source DRT subtitle text/timing disagrees with the live API readback")
            result["subtitle_source_cues"] = len(source_drt["cues"])
            result["steps"].append("captured per-source subtitle text/timing/style baseline")

            created = source.DuplicateTimeline(target_name)
            check(created is not None and created.GetName() == target_name,
                  "DuplicateTimeline failed or returned an unexpected name")
            time.sleep(DELAY)
            created_id = created.GetUniqueId()
            result["target_id"] = created_id
            check(project.GetTimelineCount() == initial_count + 1,
                  "timeline count did not increase by exactly one")
            check(project.SetCurrentTimeline(created), "could not activate the new target")
            time.sleep(DELAY)
            check(project.GetCurrentTimeline().GetUniqueId() == created_id,
                  "new target activation readback mismatch")
            protected_after_duplicate = protected_signature(created)
            if protected_after_duplicate != protected_before:
                result["duplicate_protected_diff"] = signature_diff(protected_before, protected_after_duplicate)
                result["duplicate_protected_diff_truncated"] = len(result["duplicate_protected_diff"]) >= 40
            check(protected_after_duplicate == protected_before,
                  "audio, subtitle, duration, or fps differs immediately after duplicate")
            result["steps"].append("duplicated source without changing it")

            # Insert two empty lanes at V2: focus and reactions shift intact to V4/V5.
            for step in (1, 2):
                check(created.AddTrack("video", {"index": 2}), f"AddTrack at V2 failed ({step}/2)")
                time.sleep(DELAY)
                check(created.GetTrackCount("video") == 3 + step,
                      f"video track count mismatch after insertion {step}")
                check(protected_signature(created) == protected_before,
                      "audio/subtitle/duration changed while inserting video lanes")
            check(created.GetItemListInTrack("video", 2) == [] and created.GetItemListInTrack("video", 3) == [],
                  "the inserted V2/V3 lanes are not empty")
            focus_after_insert = sorted(created.GetItemListInTrack("video", 4) or [], key=lambda item: item.GetStart())
            reactions_after_insert = sorted(created.GetItemListInTrack("video", 5) or [], key=lambda item: item.GetStart())
            check([(item.GetStart(), item.GetEnd(), item.GetName()) for item in focus_after_insert] ==
                  [(focus_range[0], focus_range[1], "Adjustment Clip")],
                  "VTUBER FOCUS did not move intact to V4")
            check([(item.GetStart(), item.GetEnd(), item.GetSourceStartFrame(), item.GetSourceEndFrame())
                   for item in reactions_after_insert] ==
                  [(item.GetStart(), item.GetEnd(), item.GetSourceStartFrame(), item.GetSourceEndFrame())
                   for item in original_reactions],
                  "reaction overlays did not move intact to V5")
            result["steps"].append("inserted video lanes and preserved focus/reaction ranges")

            source_v1 = sorted(created.GetItemListInTrack("video", 1) or [], key=lambda item: item.GetStart())[0]
            avatar_info = {
                "mediaPoolItem": source_v1.GetMediaPoolItem(),
                "startFrame": source_v1.GetSourceStartFrame(),
                "endFrame": source_v1.GetSourceEndFrame(),
                "mediaType": 1,
                "trackIndex": 3,
                "recordFrame": source_v1.GetStart(),
            }
            appended_avatar = media_pool.AppendToTimeline([avatar_info])
            time.sleep(DELAY)
            check(appended_avatar and len(appended_avatar) == 1, "video-only avatar append failed")
            avatar_items = sorted(created.GetItemListInTrack("video", 3) or [], key=lambda item: item.GetStart())
            check(len(avatar_items) == 1 and item_media_id(avatar_items[0]) == item_media_id(source_v1) and
                  (avatar_items[0].GetStart(), avatar_items[0].GetEnd(),
                   avatar_items[0].GetSourceStartFrame(), avatar_items[0].GetSourceEndFrame()) ==
                  (source_v1.GetStart(), source_v1.GetEnd(),
                   source_v1.GetSourceStartFrame(), source_v1.GetSourceEndFrame()),
                  "avatar duplicate record/source range mismatch")
            result["steps"].append("appended the same source range video-only to V3")

            gif_clones = []
            old_gif_ids = []
            for old_gif in reactions_after_insert:
                gif_info = {
                    "mediaPoolItem": old_gif.GetMediaPoolItem(),
                    "startFrame": old_gif.GetSourceStartFrame(),
                    "endFrame": old_gif.GetSourceEndFrame() + 1,
                    "mediaType": 1,
                    "trackIndex": 2,
                    "recordFrame": old_gif.GetStart(),
                }
                appended = media_pool.AppendToTimeline([gif_info])
                time.sleep(DELAY)
                check(appended and len(appended) == 1, f"reaction append failed: {old_gif.GetName()}")
                new_gif = appended[0]
                check(item_media_id(new_gif) == item_media_id(old_gif) and
                      (new_gif.GetStart(), new_gif.GetEnd(), new_gif.GetSourceStartFrame(),
                       new_gif.GetSourceEndFrame()) ==
                      (old_gif.GetStart(), old_gif.GetEnd(), old_gif.GetSourceStartFrame(),
                       old_gif.GetSourceEndFrame()),
                      f"reaction clone range/source mismatch: {old_gif.GetName()}")
                gif_clones.append(new_gif)
                old_gif_ids.append(old_gif.GetUniqueId())

            if old_gif_ids:
                old_items = [item for item in (created.GetItemListInTrack("video", 5) or [])
                             if item.GetUniqueId() in set(old_gif_ids)]
                check(len(old_items) == len(old_gif_ids), "could not re-identify every old V5 reaction")
                if created.GetIsTrackLocked("video", 5):
                    check(created.SetTrackLock("video", 5, False), "could not unlock V5 for reaction relocation")
                    time.sleep(0.25)
                    check(not created.GetIsTrackLocked("video", 5), "V5 unlock did not read back")
                check(created.DeleteClips(old_items, False), "could not delete old reactions after verified V2 clones")
                time.sleep(DELAY)
            check(created.GetItemListInTrack("video", 5) == [], "old V5 reactions remain after relocation")
            check(created.DeleteTrack("video", 5), "could not remove the verified-empty V5")
            time.sleep(DELAY)
            check(created.GetTrackCount("video") == 4, "expected four final video tracks")
            result["steps"].append("relocated reactions to V2 at the original times")

            # New tracks inherit the source track's enable/lock states by role.
            role_states = ((1, "game"), (2, "reactions"), (3, "game"), (4, "focus"))
            for index, role in role_states:
                enabled, locked = original_states[role]
                check(created.SetTrackEnable("video", index, enabled), f"could not restore V{index} enable state")
                check(created.GetIsTrackEnabled("video", index) == enabled,
                      f"V{index} enable state did not read back")
                if created.GetIsTrackLocked("video", index) != locked:
                    check(created.SetTrackLock("video", index, locked), f"could not restore V{index} lock state")
                check(created.GetIsTrackLocked("video", index) == locked,
                      f"V{index} lock state did not read back")
            for index, name in ((1, "Game Top"), (2, "REACTIONS"), (3, "VTuber Bottom"), (4, "VTuber Zoom")):
                check(created.SetTrackName("video", index, name), f"could not name V{index}")
                time.sleep(0.2)
                check(created.GetTrackName("video", index) == name, f"V{index} track name did not read back")

            for key, value in RASTER:
                check(created.SetSetting(key, value), f"could not set {key}")
                time.sleep(0.2)
            check(float(created.GetSetting("timelineFrameRate")) == float(baseline_row["fps"]),
                  "target frame rate changed")
            for key, value in RASTER:
                check(str(created.GetSetting(key)) == value, f"timeline setting mismatch for {key}")
            result["steps"].append("set and verified 1080x1920 timeline raster")

            game = sorted(created.GetItemListInTrack("video", 1) or [], key=lambda item: item.GetStart())[0]
            avatar = sorted(created.GetItemListInTrack("video", 3) or [], key=lambda item: item.GetStart())[0]
            original_locks = {index: created.GetIsTrackLocked("video", index) for index in (1, 3, 4)}
            for index, was_locked in original_locks.items():
                if was_locked:
                    check(created.SetTrackLock("video", index, False), f"could not unlock V{index} for framing")
                    time.sleep(0.2)
                    check(not created.GetIsTrackLocked("video", index), f"V{index} unlock did not read back")

            result["game_transform"] = set_clip_transform(
                game, portrait_transform(layout["game"], 0.0, source_w, source_h))
            result["avatar_transform"] = set_clip_transform(
                avatar, portrait_transform(layout["avatar"], SPLIT, source_w, source_h,
                                           crop_top_src=layout["avatar"][1]))

            gif_transforms = []
            for gif in gif_clones:
                gif_transforms.append(set_clip_transform(gif, {
                    "ZoomX": GIF_ZOOM,
                    "ZoomY": GIF_ZOOM,
                    "Pan": GIF_CENTER[0] - CANVAS_W / 2,
                    "Tilt": -(GIF_CENTER[1] - CANVAS_H / 2) / (CANVAS_W / CANVAS_H),
                }))
            result["gif_transforms"] = gif_transforms

            focus_items = sorted(created.GetItemListInTrack("video", 4) or [], key=lambda item: item.GetStart())
            check(len(focus_items) == 1 and focus_items[0].GetName() == "Adjustment Clip" and
                  (focus_items[0].GetStart(), focus_items[0].GetEnd()) == focus_range,
                  "VTUBER FOCUS interval changed")
            transform = fusion_transform(focus_items[0])
            focus_before = {key: normalize(transform.GetInput(key)) for key in
                            ("Size", "Pivot", "Center", "Edges", "MotionBlur")}
            # Preserve the source focus's edge and motion-blur behavior while
            # replacing its scale/center with the approved image-2 target.
            transform.SetInput("Size", FOCUS["Size"], 0.0)
            time.sleep(0.25)
            set_point_and_read(transform, "Pivot", FOCUS["Pivot"])
            set_point_and_read(transform, "Center", FOCUS["Center"])
            duration = focus_range[1] - focus_range[0]
            result["focus_before"] = focus_before
            result["focus_after"] = {
                key: normalize(transform.GetInput(key))
                for key in ("Size", "Pivot", "Center", "Edges", "MotionBlur")
            }
            check(abs(float(result["focus_after"]["Size"]) - FOCUS["Size"]) < 0.0001,
                  "focus Size readback mismatch")
            for key in ("Pivot", "Center"):
                for axis, value in FOCUS[key].items():
                    check(abs(float(result["focus_after"][key][str(axis)]) - float(value)) < 0.0001,
                          f"focus {key} readback mismatch")
            check(result["focus_after"]["Edges"] == focus_before["Edges"], "focus edge handling changed")
            check(result["focus_after"]["MotionBlur"] == focus_before["MotionBlur"],
                  "focus motion-blur setting changed")
            result["focus_samples"] = verify_focus(transform, duration)

            for index, was_locked in original_locks.items():
                if created.GetIsTrackLocked("video", index) != was_locked:
                    check(created.SetTrackLock("video", index, was_locked), f"could not restore V{index} lock state")
                    time.sleep(0.2)
                check(created.GetIsTrackLocked("video", index) == was_locked,
                      f"V{index} lock state did not restore")

            # The Adjustment Clip zooms the entire lower stack, which otherwise
            # magnifies both split panels at once. A source-range overlay above it
            # replaces that composite only during the original focus interval.
            duration = focus_range[1] - focus_range[0]
            check(created.GetTrackCount("video") == 4, "unexpected track count before V5 focus overlay")
            check(created.AddTrack("video", {"index": 5}), "could not add V5 full-screen focus track")
            time.sleep(DELAY)
            check(created.GetTrackCount("video") == 5, "V5 focus track did not read back")
            check(created.SetTrackEnable("video", 5, True), "could not enable V5 focus track")
            check(created.GetIsTrackEnabled("video", 5), "V5 focus track enable did not read back")
            check(not created.GetIsTrackLocked("video", 5), "V5 focus track unexpectedly locked")
            focus_overlay, created_compound_media, focus_build = build_focus_overlay(
                project, source, created, game, focus_range, media_pool, focus_artifact)
            result["focus_fullscreen_build"] = focus_build
            if created_compound_media is not None:
                result["focus_compound_media_id"] = created_compound_media.GetUniqueId()
            check(item_media_id(focus_overlay) ==
                  (created_compound_media.GetUniqueId() if created_compound_media else item_media_id(game)),
                  "full-screen focus overlay references the wrong media source")
            check(created.SetTrackName("video", 5, "VTuber Focus Fullscreen"),
                  "could not name V5 full-screen focus")
            time.sleep(0.25)
            check(created.GetTrackName("video", 5) == "VTuber Focus Fullscreen",
                  "V5 track name did not read back")
            result["focus_fullscreen_transform"] = set_clip_transform(
                focus_overlay,
                portrait_transform(layout["focus_fullscreen"], 0.0, source_w, source_h,
                                   crop_top_src=layout["focus_fullscreen"][1], panel_height=CANVAS_H))
            result["focus_fullscreen_clip"] = {
                "track": 5,
                "start": focus_overlay.GetStart(),
                "end": focus_overlay.GetEnd(),
                "source_start": focus_overlay.GetSourceStartFrame(),
                "source_end": focus_overlay.GetSourceEndFrame(),
                "media_id": item_media_id(focus_overlay),
            }
            focus_overlapping_gifs = [gif for gif in gif_clones
                                      if gif.GetStart() < focus_range[1] and focus_range[0] < gif.GetEnd()]
            if focus_overlapping_gifs:
                # V5 must cover the split layout, so lift only GIFs that overlap
                # this focus interval to V6, above the focus image. Their timing,
                # source range and transform stay identical.
                check(created.GetTrackCount("video") == 5,
                      "unexpected track count before V6 reaction overlay")
                check(created.AddTrack("video", {"index": 6}),
                      "could not add V6 reaction overlay track")
                time.sleep(DELAY)
                check(created.GetTrackCount("video") == 6, "V6 reaction track did not read back")
                check(created.SetTrackEnable("video", 6, True), "could not enable V6 reaction track")
                check(created.GetIsTrackEnabled("video", 6), "V6 reaction track enable did not read back")
                check(not created.GetIsTrackLocked("video", 6), "V6 reaction track unexpectedly locked")
                v6_gifs = []
                for gif in focus_overlapping_gifs:
                    gif_info = {
                        "mediaPoolItem": gif.GetMediaPoolItem(),
                        "startFrame": gif.GetSourceStartFrame(),
                        "endFrame": gif.GetSourceEndFrame() + 1,
                        "mediaType": 1,
                        "trackIndex": 6,
                        "recordFrame": gif.GetStart(),
                    }
                    v6_appended = media_pool.AppendToTimeline([gif_info])
                    time.sleep(DELAY)
                    check(v6_appended and len(v6_appended) == 1,
                          f"could not duplicate overlapping GIF above focus: {gif.GetName()}")
                    v6_gif = v6_appended[0]
                    check(item_media_id(v6_gif) == item_media_id(gif) and
                          (v6_gif.GetStart(), v6_gif.GetEnd(), v6_gif.GetSourceStartFrame(),
                           v6_gif.GetSourceEndFrame()) ==
                          (gif.GetStart(), gif.GetEnd(), gif.GetSourceStartFrame(), gif.GetSourceEndFrame()),
                          f"V6 GIF range/source mismatch: {gif.GetName()}")
                    copied_props = {key: float(gif.GetProperty(key)) for key in
                                    ("ZoomX", "ZoomY", "Pan", "Tilt")}
                    result["gif_focus_overlay_transforms"] = result.get(
                        "gif_focus_overlay_transforms", [])
                    result["gif_focus_overlay_transforms"].append(
                        set_clip_transform(v6_gif, copied_props))
                    v6_gifs.append(v6_gif)
                was_v2_locked = created.GetIsTrackLocked("video", 2)
                if was_v2_locked:
                    check(created.SetTrackLock("video", 2, False), "could not unlock V2 to relocate focus GIF")
                    time.sleep(0.25)
                    check(not created.GetIsTrackLocked("video", 2), "V2 unlock did not read back")
                check(created.DeleteClips(focus_overlapping_gifs, False),
                      "could not remove overlapping GIFs after V6 verification")
                time.sleep(DELAY)
                if was_v2_locked:
                    check(created.SetTrackLock("video", 2, True), "could not restore V2 lock")
                    time.sleep(0.25)
                    check(created.GetIsTrackLocked("video", 2), "V2 lock did not restore")
                check(created.SetTrackName("video", 6, "REACTIONS ABOVE FOCUS"),
                      "could not name V6 reaction overlay")
                time.sleep(0.25)
                check(created.GetTrackName("video", 6) == "REACTIONS ABOVE FOCUS",
                      "V6 reaction overlay name did not read back")
                result["focus_gif_overlay_clips"] = [
                    {"start": gif.GetStart(), "end": gif.GetEnd(),
                     "source_start": gif.GetSourceStartFrame(), "source_end": gif.GetSourceEndFrame(),
                     "media_id": item_media_id(gif)} for gif in v6_gifs]
            check(protected_signature(created) == protected_before,
                  "audio/subtitle/duration changed after V5 focus overlay")
            result["steps"].append("added exact-range full-screen focus video above the split layout")

            check(created.Export(str(subtitle_target_path), resolve.EXPORT_DRT, resolve.EXPORT_NONE),
                  "target DRT export failed")
            target_drt = subtitle_drt_signature(subtitle_target_path)
            check(target_drt == source_drt, "Subtitle track text, timing, or styling changed in target DRT")
            result["subtitle_drt_check"] = {
                "cue_count": len(target_drt["cues"]),
                "text_timing_style_equal": True,
                "source_drt": str(subtitle_source_path),
                "target_drt": str(subtitle_target_path),
            }

            check(protected_signature(created) == protected_before,
                  "duration, audio/SFX/BGM, or subtitle API signature changed")
            check([(item.GetStart(), item.GetEnd(), item.GetSourceStartFrame(), item.GetSourceEndFrame(),
                    item_media_id(item)) for item in (created.GetItemListInTrack("video", 1) or [])] ==
                  [(item.GetStart(), item.GetEnd(), item.GetSourceStartFrame(), item.GetSourceEndFrame(),
                    item_media_id(item)) for item in (source.GetItemListInTrack("video", 1) or [])],
                  "Game Top source cut or time range changed")
            check([(item.GetStart(), item.GetEnd(), item.GetSourceStartFrame(), item.GetSourceEndFrame(),
                    item_media_id(item)) for item in (created.GetItemListInTrack("video", 3) or [])] ==
                  [(item.GetStart(), item.GetEnd(), item.GetSourceStartFrame(), item.GetSourceEndFrame(),
                    item_media_id(item)) for item in (source.GetItemListInTrack("video", 1) or [])],
                  "VTuber Bottom source cut or time range changed")
            expected_gifs = sorted((item.GetStart(), item.GetEnd(), item.GetSourceStartFrame(),
                                    item.GetSourceEndFrame(), item_media_id(item))
                                   for item in original_reactions)
            actual_gifs = sorted((item.GetStart(), item.GetEnd(), item.GetSourceStartFrame(),
                                  item.GetSourceEndFrame(), item_media_id(item))
                                 for track_index in range(2, created.GetTrackCount("video") + 1)
                                 for item in (created.GetItemListInTrack("video", track_index) or [])
                                 if item.GetMediaPoolItem() and item_media_id(item) in
                                 {item_media_id(source_item) for source_item in original_reactions})
            check(actual_gifs == expected_gifs,
                  "reaction timing/source ranges changed across V2/V6")
            check(project.SetCurrentTimeline(source), "could not activate source for preservation audit")
            time.sleep(DELAY)
            check(full_original_signature(source) == source_signature,
                  "source 16:9 timeline changed during target creation")
            result["source_unchanged"] = True
            result["duration_frames"] = source.GetEndFrame() - source.GetStartFrame()
            check(project.SetCurrentTimeline(created), "could not reactivate target after source audit")
            time.sleep(DELAY)
            result["audio_track_count"] = created.GetTrackCount("audio")
            result["subtitle_track_count"] = created.GetTrackCount("subtitle")
            result["subtitle_cues"] = len(target_drt["cues"])
            expected_track_count = 5 + (1 if focus_overlapping_gifs else 0)
            check(created.GetTrackCount("video") == expected_track_count,
                  "video track count differs after focus/GIF overlays")
            result["video_track_count"] = created.GetTrackCount("video")
            result["track_names"] = [created.GetTrackName("video", index)
                                     for index in range(1, created.GetTrackCount("video") + 1)]

            check(project.GetTimelineCount() == initial_count + 1,
                  "timeline count changed unexpectedly before save")
            check(pm.SaveProject(), "SaveProject failed")
            time.sleep(DELAY)
            check(protected_signature(created) == protected_before,
                  "protected audio/subtitle/duration signature changed after save")
            check(project.SetCurrentTimeline(source), "could not activate source for post-save audit")
            time.sleep(DELAY)
            check(full_original_signature(source) == source_signature,
                  "source timeline changed after saving target")
            check(project.SetCurrentTimeline(created), "could not reactivate saved target")
            time.sleep(DELAY)
            result["saved"] = True
            result["steps"].append("saved and read back the target")

        current = project.GetCurrentTimeline()
        restored = bool(
            current and current.GetUniqueId() == initial_timeline_id and
            current.GetCurrentTimecode() == initial_timecode and
            resolve.GetCurrentPage() == initial_page and
            folder_id(media_pool.GetCurrentFolder()) == initial_folder_id)
        result["resolve_state_restored"] = restored
        check(restored, "Resolve page/timeline/playhead/folder state did not restore")
        check(connect_resolve() is not None, "Resolve stopped responding after target save")
        check(not project.IsRenderingInProgress(), "Resolve unexpectedly started a render")
        check(project.GetTimelineCount() == initial_count + 1, "Resolve timeline count readback mismatch")
        result["resolve_running"] = True
        result["target_id_verified"] = len(find_timeline(project, timeline_id=created.GetUniqueId(), name=target_name)) == 1
        check(result["target_id_verified"], "target ID/name failed final lookup")
        result["status"] = "PASS"
    except Exception as exc:
        result["status"] = "FAILED"
        result["error"] = repr(exc)
        try:
            candidates = [created] if created is not None else find_timeline(project, name=target_name)
            candidates = [candidate for candidate in candidates if candidate and candidate.GetName() == target_name
                          and candidate.GetUniqueId() != source_id]
            if candidates:
                current = project.GetCurrentTimeline()
                if current and current.GetUniqueId() in {candidate.GetUniqueId() for candidate in candidates}:
                    check(project.SetCurrentTimeline(source), "could not activate source before rollback")
                    time.sleep(DELAY)
                check(media_pool.DeleteTimelines(candidates), "DeleteTimelines failed during rollback")
                time.sleep(DELAY)
                check(not find_timeline(project, name=target_name), "failed target remains after rollback")
                check(pm.SaveProject(), "SaveProject failed after rollback")
                result["rollback"] = "deleted only the target created by this invocation and saved"
            else:
                result["rollback"] = "no new target timeline existed to remove"
            compound_id = (created_compound_media.GetUniqueId() if created_compound_media is not None
                           else focus_artifact.get("compound_media_id"))
            if compound_id:
                check(not find_timeline(project, name=target_name),
                      "cannot delete focus compound while the failed target still exists")
                temp_name = focus_artifact.get("temp_name")
                check(not temp_name or not find_timeline(project, name=temp_name),
                      "cannot delete focus compound while its temporary builder still exists")
                existing_items = {item.GetUniqueId(): item for item in pool_items(media_pool.GetRootFolder())}
                if compound_id in existing_items:
                    check(media_pool.DeleteClips([existing_items[compound_id]]),
                          "could not delete unreferenced focus compound after target rollback")
                    time.sleep(DELAY)
                check(compound_id not in {item.GetUniqueId() for item in pool_items(media_pool.GetRootFolder())},
                      "focus compound remains after target rollback")
                result["focus_compound_rollback"] = "deleted after target removal"
            if source_signature is not None:
                check(project.SetCurrentTimeline(source), "could not activate source for rollback audit")
                time.sleep(DELAY)
                check(full_original_signature(source) == source_signature,
                      "source changed during failed-target rollback")
        except Exception as rollback_error:
            result["rollback_error"] = repr(rollback_error)
        try:
            current = project.GetCurrentTimeline()
            if not current or current.GetUniqueId() != initial_timeline_id:
                restore = next((project.GetTimelineByIndex(i) for i in range(1, project.GetTimelineCount() + 1)
                                if project.GetTimelineByIndex(i).GetUniqueId() == initial_timeline_id), None)
                check(restore is not None and project.SetCurrentTimeline(restore),
                      "could not restore previous active timeline after failure")
                time.sleep(DELAY)
                restore.SetCurrentTimecode(initial_timecode)
            if folder_id(media_pool.GetCurrentFolder()) != initial_folder_id:
                check(media_pool.SetCurrentFolder(initial_folder), "could not restore Media Pool folder after failure")
            if initial_page and resolve.GetCurrentPage() != initial_page:
                check(resolve.OpenPage(initial_page), "could not restore Resolve page after failure")
            restored = project.GetCurrentTimeline()
            result["resolve_state_restored_after_failure"] = bool(
                restored and restored.GetUniqueId() == initial_timeline_id and
                restored.GetCurrentTimecode() == initial_timecode and
                resolve.GetCurrentPage() == initial_page and
                folder_id(media_pool.GetCurrentFolder()) == initial_folder_id)
        except Exception as restore_error:
            result["state_restore_error"] = repr(restore_error)

        OUT_DIR.mkdir(parents=True, exist_ok=True)
        log_path = OUT_DIR / f"batch_{source_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
        result["log_path"] = str(log_path)
        log_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        print(json.dumps(result, ensure_ascii=True, indent=2, default=str))
        raise

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    log_path = OUT_DIR / f"batch_{source_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
    result["log_path"] = str(log_path)
    log_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=True, indent=2, default=str))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id", required=True, help="unique ID of one source timeline ending in -vdo")
    args = parser.parse_args()
    raise SystemExit(main(args.source_id))
