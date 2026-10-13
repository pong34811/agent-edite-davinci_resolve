"""Build the approved Armigon 9:16 pilot on a duplicate timeline.

MCP-GAP: timeline.duplicate/add_track/duplicate_clips/delete_clips/set_transform and
fusion_comp.set_input are exposed, but the community MCP applies version-on-mutate
to each structural call; this multi-step build would add unrequested archived
timelines and move the Media Pool folder. No atomic MCP build action exists. Use
the Resolve Scripting API through resolve_common so one preserved_state session
can make the changes, check each readback, and roll back only its own new timeline.

This is a single-timeline pilot. It deliberately does not batch any other timeline.
"""
from __future__ import annotations

import json
import zipfile
import time
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

from scripts.backup_drp import verify_drp
from scripts.resolve_common import connect_resolve, preserved_state


PROJECT_NAME = "armigon-2026-09"
PROJECT_ID = "9a7d3e92-e44c-4ba4-afba-7c2dbe1090e1"
ORIGINAL_NAME = "อ่า มอตที่เราเล่นกันวันนี้คือ มอต อ-RLcraft-vdo"
ORIGINAL_ID = "48cf6539-ca26-46cc-a3bf-d823ed8fe4f4"
TARGET_NAME = ORIGINAL_NAME + "_9x16"
BACKUP = Path(r"G:\My Drive\Projects\Armigon\2026-09\armigon-2026-09_pre-9x16_20261012.drp")
BASELINE = Path(r"G:\My Drive\Projects\Armigon\2026-09\armigon-2026-09_9x16_preflight_20261012.json")
OUT_DIR = Path(r"G:\My Drive\Projects\Armigon\2026-09\.superpowers\brainstorm\1617-1791799790\content")
DRT_REFERENCE = OUT_DIR / "pilot_source.drt"
DELAY = 1.25

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

# Source-frame estimates were measured on the pilot's real 1280x702 stream frames.
# The source's purple, cat-eared Armigon avatar is at lower-left; the approved
# focus target is the in-game chibi at the right side of the game panel.
CANVAS_W, CANVAS_H = 1080.0, 1920.0
SPLIT = 960.0
SRC_W, SRC_H = 1280.0, 702.0
FIT = min(CANVAS_W / SRC_W, CANVAS_H / SRC_H)
TILT_PX = SRC_H * FIT / CANVAS_H
GAME_CROP = (672.5, 0.0, 1280.0, 540.0)
AVATAR_CROP = (234.1875, 425.0, 545.8125, 702.0)
# Calibrated from the Resolve-rendered pilot frame so the in-game chibi (rather
# than the lower purple VTuber panel) sits centered in the focus view.
FOCUS = {"Size": 2.05, "Pivot": {1: 0.746, 2: 0.68, 3: 0.0}, "Center": {1: 0.28, 2: 0.292, 3: 0.0}}
GIF_ZOOM = 0.28
GIF_CENTER = (220.0, 260.0)
GIF_TILT_PX = CANVAS_W / CANVAS_H


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


def track_rows(tl, kind, properties=()):
    rows = []
    for index in range(1, tl.GetTrackCount(kind) + 1):
        rows.append({
            "index": index,
            "name": tl.GetTrackName(kind, index),
            "enabled": tl.GetIsTrackEnabled(kind, index),
            "locked": tl.GetIsTrackLocked(kind, index),
            "items": [item_signature(i, properties) for i in sorted(
                tl.GetItemListInTrack(kind, index) or [], key=lambda x: x.GetStart())],
        })
    return rows


def protected_signature(tl):
    """Fields explicitly protected by the request: duration/fps, audio and subtitles."""
    return {
        "range": (tl.GetStartFrame(), tl.GetEndFrame()),
        "fps": normalize(tl.GetSetting("timelineFrameRate")),
        "audio_tracks": track_rows(tl, "audio", AUDIO_PROPS),
        "subtitle_tracks": track_rows(tl, "subtitle"),
    }


def find_timeline(project, timeline_id=None, name=None):
    hits = []
    for i in range(1, project.GetTimelineCount() + 1):
        tl = project.GetTimelineByIndex(i)
        if (timeline_id is None or tl.GetUniqueId() == timeline_id) and (name is None or tl.GetName() == name):
            hits.append(tl)
    return hits


def folder_id(folder):
    return folder.GetUniqueId() if folder is not None and "GetUniqueId" in dir(folder) else None


def fusion_transform(item):
    count = item.GetFusionCompCount()
    check(count >= 1, "focus Adjustment Clip has no Fusion composition")
    comp = item.GetFusionCompByIndex(count)
    candidates = []
    for tool in (comp.GetToolList() or {}).values():
        attrs = tool.GetAttrs() or {}
        if attrs.get("TOOLS_RegID") == "Transform" and attrs.get("TOOLS_Name") == "Transform1":
            candidates.append(tool)
    check(len(candidates) == 1, f"expected one Fusion Transform1, found {len(candidates)}")
    return candidates[0]


def fusion_signature(item):
    t = fusion_transform(item)
    return {key: normalize(t.GetInput(key)) for key in ("Size", "Center", "Pivot", "Edges")}


def subtitle_drt_signature(path):
    """Read subtitle text, frame ranges, and track styling from a Resolve DRT export."""
    with zipfile.ZipFile(path) as archive:
        seq_files = [name for name in archive.namelist()
                     if name.startswith("SeqContainer/") and name.lower().endswith(".xml")]
        check(len(seq_files) == 1, f"expected one sequence XML in {path}, found {len(seq_files)}")
        root = ET.fromstring(archive.read(seq_files[0]))
    track_vec = root.find("SubtitleTrackVec")
    check(track_vec is not None, f"subtitle track container missing in {path}")
    tracks = track_vec.findall("./Element/Sm2TiTrack")
    check(len(tracks) == 1, f"expected one native subtitle track in {path}, found {len(tracks)}")
    track = tracks[0]

    def canonical(element):
        # Resolve assigns new database and sequence IDs to duplicates. The remaining
        # fields include track style (FieldsBlob) and cue text/timing (Name/Start/Duration).
        children = [canonical(child) for child in list(element) if child.tag != "Sequence"]
        return {
            "tag": element.tag,
            "attrs": {key: value for key, value in sorted(element.attrib.items()) if key != "DbId"},
            "text": element.text or "",
            "children": children,
        }

    items = track.find("Items")
    cues = []
    if items is not None:
        for wrapper in items.findall("./Element"):
            cue = wrapper.find("Sm2TiGenerator")
            if cue is None:
                continue
            fields = {child.tag: child.text or "" for child in list(cue)}
            if fields.get("PrettyType") == "Subtitle":
                start = int(fields["Start"])
                duration = int(fields["Duration"])
                cues.append((fields.get("Name", ""), start, start + duration))
    return {"track": canonical(track), "cues": cues}


def full_original_signature(tl):
    video = track_rows(tl, "video", VIDEO_PROPS)
    for track in range(1, tl.GetTrackCount("video") + 1):
        for idx, item in enumerate(sorted(tl.GetItemListInTrack("video", track) or [], key=lambda x: x.GetStart())):
            if item.GetName() == "Adjustment Clip":
                video[track - 1]["items"][idx]["fusion"] = fusion_signature(item)
    return {
        "id": tl.GetUniqueId(), "name": tl.GetName(),
        "settings": {k: normalize(tl.GetSetting(k)) for k in (
            "timelineResolutionWidth", "timelineResolutionHeight", "timelineFrameRate")},
        "range": (tl.GetStartFrame(), tl.GetEndFrame()),
        "video_tracks": video,
        "audio_tracks": track_rows(tl, "audio", AUDIO_PROPS),
        "subtitle_tracks": track_rows(tl, "subtitle"),
    }


def portrait_transform(crop, panel_top, crop_top_src=0.0):
    x0, y0, x1, y1 = crop
    scale = SPLIT / (y1 - y0)
    zoom = scale / FIT
    source_cx = (x0 + x1) / 2
    source_cy = (y0 + y1) / 2
    target_cy = panel_top + SPLIT / 2
    center_x = CANVAS_W / 2 + (SRC_W / 2 - source_cx) * scale
    center_y = target_cy + (SRC_H / 2 - source_cy) * scale
    return {
        "ZoomX": zoom,
        "ZoomY": zoom,
        "Pan": center_x - CANVAS_W / 2,
        "Tilt": -(center_y - CANVAS_H / 2) / TILT_PX,
        "CropLeft": 0.0,
        "CropRight": 0.0,
        # CropTop masks the source above the avatar seam so V3 does not cover V1's game panel.
        # This follows the already-QC'd p2 vertical layout convention: source px * fit scale.
        "CropTop": crop_top_src * FIT,
        "CropBottom": 0.0,
    }


def set_float(item, key, value, tolerance):
    last = None
    for _ in range(3):
        item.SetProperty(key, float(value))
        time.sleep(0.35)
        last = item.GetProperty(key)
        if last is not None and abs(float(last) - float(value)) <= tolerance:
            return float(last)
        time.sleep(0.5)
    raise RuntimeError(f"{key} readback mismatch: wanted {value}, got {last}")


def set_clip_transform(item, props):
    item.SetProperty("ZoomGang", True)
    time.sleep(0.35)
    check(bool(item.GetProperty("ZoomGang")), f"{item.GetName()}: ZoomGang not linked")
    for key, value in props.items():
        tol = 0.75 if key in ("Pan", "Tilt") else 0.006 if key.startswith("Zoom") else 0.01
        set_float(item, key, value, tol)
    return {key: normalize(item.GetProperty(key)) for key in (*props.keys(), "ZoomGang")}


def track_sig(tl, index):
    return [item_signature(i, VIDEO_PROPS) for i in sorted(
        tl.GetItemListInTrack("video", index) or [], key=lambda x: x.GetStart())]


def focus_signature(tl, index):
    items = sorted(tl.GetItemListInTrack("video", index) or [], key=lambda x: x.GetStart())
    return [(i.GetStart(), i.GetEnd(), i.GetName(), fusion_signature(i)) for i in items]


def main():
    backup_bytes = verify_drp(BACKUP)
    check(BASELINE.is_file(), f"baseline snapshot missing: {BASELINE}")
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    check(baseline.get("project", {}).get("name") == PROJECT_NAME, "baseline belongs to a different project")
    baseline_rows = [t for t in baseline.get("timelines", []) if t.get("timeline_id") == ORIGINAL_ID]
    check(len(baseline_rows) == 1, "baseline target ID is missing or duplicated")
    baseline_row = baseline_rows[0]
    check(baseline_row["name"] == ORIGINAL_NAME, "baseline target name mismatch")
    check((baseline_row["start_frame"], baseline_row["end_frame"], float(baseline_row["fps"])) == (0, 6658, 60.0),
          "baseline duration or frame rate differs from the approved pilot")
    check((str(baseline_row["width"]), str(baseline_row["height"])) == ("1920", "1080"),
          "baseline original is not 1920x1080")
    check(not baseline.get("existing_vertical_timelines"), "baseline already contains vertical timelines")
    check(DRT_REFERENCE.is_file(), f"original subtitle DRT reference missing: {DRT_REFERENCE}")

    resolve = connect_resolve()
    check(resolve is not None, "cannot connect to Resolve")
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    check(project is not None and project.GetName() == PROJECT_NAME and project.GetUniqueId() == PROJECT_ID,
          "active project is not the approved armigon-2026-09 project")
    check(not project.IsRenderingInProgress(), "Resolve is rendering; aborting before any edit")
    original_hits = find_timeline(project, ORIGINAL_ID, ORIGINAL_NAME)
    check(len(original_hits) == 1, "approved original timeline was not found uniquely")
    original = original_hits[0]
    check(project.GetCurrentTimeline().GetUniqueId() == ORIGINAL_ID,
          "the approved pilot is no longer the active timeline; refusing to change user state")
    check(not find_timeline(project, name=TARGET_NAME), f"target already exists: {TARGET_NAME}")
    baseline_targets = {(t["timeline_id"], t["name"]) for t in baseline.get("timelines", [])}
    live_targets = {
        (project.GetTimelineByIndex(i).GetUniqueId(), project.GetTimelineByIndex(i).GetName())
        for i in range(1, project.GetTimelineCount() + 1)
        if project.GetTimelineByIndex(i).GetName().endswith("-vdo")
    }
    check(len(baseline_targets) == int(baseline.get("expected_timeline_count", -1)) == 48,
          "baseline does not contain the expected 48 source timelines")
    check(live_targets == baseline_targets,
          "the live -vdo source timeline IDs/names drifted since the preflight snapshot")

    v1 = sorted(original.GetItemListInTrack("video", 1) or [], key=lambda x: x.GetStart())
    focus_items = sorted(original.GetItemListInTrack("video", 2) or [], key=lambda x: x.GetStart())
    gifs = sorted(original.GetItemListInTrack("video", 3) or [], key=lambda x: x.GetStart())
    check(len(v1) == 1 and v1[0].GetStart() == 0 and v1[0].GetEnd() == 6658,
          "unexpected source video layout")
    check(item_media_id(v1[0]) == "3db9772b-4371-4952-ace8-11983e3ef75b", "pilot source clip ID changed")
    check(len(focus_items) == 1 and focus_items[0].GetName() == "Adjustment Clip" and
          (focus_items[0].GetStart(), focus_items[0].GetEnd()) == (1613, 2065), "unexpected VTUBER FOCUS range")
    check(len(gifs) == 1 and gifs[0].GetName() == "งง - mochi-cat-what.gif" and
          (gifs[0].GetStart(), gifs[0].GetEnd(), gifs[0].GetSourceStartFrame(), gifs[0].GetSourceEndFrame()) ==
          (606, 721, 0, 47), "unexpected GIF identity or timing")
    original_signature = full_original_signature(original)
    protected_baseline = protected_signature(original)
    expected_audio_gif_ranges = [(606, 721)]
    check(len(protected_baseline["subtitle_tracks"]) == 1 and
          len(protected_baseline["subtitle_tracks"][0]["items"]) == 90, "subtitle baseline changed")
    subtitle_drt_before = subtitle_drt_signature(DRT_REFERENCE)
    api_cues = [(item["name"], item["start"], item["end"])
                for item in protected_baseline["subtitle_tracks"][0]["items"]]
    check(subtitle_drt_before["cues"] == api_cues,
          "original DRT subtitle text/timing does not match the live timeline readback")
    check(len(protected_baseline["audio_tracks"]) == 3, "audio track baseline changed")

    initial_timeline = project.GetCurrentTimeline()
    initial_timeline_id = initial_timeline.GetUniqueId()
    initial_timecode = initial_timeline.GetCurrentTimecode()
    initial_page = resolve.GetCurrentPage()
    initial_folder = project.GetMediaPool().GetCurrentFolder()
    initial_folder_id = folder_id(initial_folder)
    initial_count = project.GetTimelineCount()
    result = {
        "project": PROJECT_NAME,
        "original_id": ORIGINAL_ID,
        "original_name": ORIGINAL_NAME,
        "target_name": TARGET_NAME,
        "backup_path": str(BACKUP),
        "backup_bytes_verified": backup_bytes,
        "baseline_path": str(BASELINE),
        "layout": "Game Top / VTuber Bottom",
        "focus_subject": "in-game chibi on the right side of the game panel, identified by the user from reference image 2",
        "fps": 60,
        "raster": [1080, 1920],
        "focus_range": [(1613, 2065)],
        "gif_ranges": expected_audio_gif_ranges,
        "steps": [],
    }
    created = None
    media_pool = project.GetMediaPool()
    try:
        with preserved_state(resolve):
            created = original.DuplicateTimeline(TARGET_NAME)
            check(created is not None and created.GetName() == TARGET_NAME, "DuplicateTimeline failed")
            time.sleep(DELAY)
            created_id = created.GetUniqueId()
            result["new_timeline_id"] = created_id
            result["steps"].append("duplicated original")
            check(project.GetTimelineCount() == initial_count + 1, "duplicate created an unexpected number of timelines")
            check(project.SetCurrentTimeline(created), "could not activate new pilot")
            time.sleep(DELAY)
            check(project.GetCurrentTimeline().GetUniqueId() == created_id, "new pilot activation failed")
            check(protected_signature(created) == protected_baseline, "protected content differs immediately after duplicate")
            check(track_sig(created, 1) == track_sig(original, 1) and
                  [(i.GetStart(), i.GetEnd(), i.GetName()) for i in (created.GetItemListInTrack("video", 2) or [])] ==
                  [(i.GetStart(), i.GetEnd(), i.GetName()) for i in (original.GetItemListInTrack("video", 2) or [])],
                  "video content differs immediately after duplicate")

            # Add two empty video lanes at slot 2. Existing focus and GIF lanes must move intact to V4 and V5.
            for step in (1, 2):
                check(created.AddTrack("video", {"index": 2}), f"AddTrack(index=2), step {step}, failed")
                time.sleep(DELAY)
                result["steps"].append(f"inserted video track at index 2 ({step}/2)")
                check(created.GetTrackCount("video") == 3 + step, f"video track count mismatch after add {step}")
                check(track_sig(created, 1) == track_sig(original, 1), "V1 changed while inserting video tracks")
                check(protected_signature(created) == protected_baseline, "audio/subtitle drift while inserting video tracks")
                expected_focus_track, expected_gif_track = 2 + step, 3 + step
                check(track_sig(created, 2) == [] and
                      (track_sig(created, 3) == [] if step == 2 else True),
                      f"inserted track positions are incorrect after add {step}")
                check([(i.GetStart(), i.GetEnd(), i.GetName()) for i in created.GetItemListInTrack("video", expected_focus_track)] ==
                      [(1613, 2065, "Adjustment Clip")], f"focus did not shift intact after add {step}")
                check([(i.GetStart(), i.GetEnd(), i.GetSourceStartFrame(), i.GetSourceEndFrame())
                       for i in created.GetItemListInTrack("video", expected_gif_track)] == [(606, 721, 0, 47)],
                      f"GIF did not shift intact after add {step}")
            check(track_sig(created, 2) == [] and track_sig(created, 3) == [], "new video tracks are not empty")
            check([(i.GetStart(), i.GetEnd()) for i in created.GetItemListInTrack("video", 4)] == [(1613, 2065)],
                  "focus clip did not move intact to V4")
            check([(i.GetStart(), i.GetEnd(), i.GetSourceStartFrame(), i.GetSourceEndFrame())
                   for i in created.GetItemListInTrack("video", 5)] == [(606, 721, 0, 47)],
                  "GIF did not move intact to V5")

            source = sorted(created.GetItemListInTrack("video", 1), key=lambda x: x.GetStart())[0]
            avatar_info = {
                "mediaPoolItem": source.GetMediaPoolItem(),
                "startFrame": source.GetSourceStartFrame(),
                "endFrame": source.GetSourceEndFrame(),
                "mediaType": 1,
                "trackIndex": 3,
                "recordFrame": source.GetStart(),
            }
            appended = media_pool.AppendToTimeline([avatar_info])
            time.sleep(DELAY)
            check(appended and len(appended) == 1, "video-only avatar append failed")
            result["steps"].append("appended same-time video-only avatar source to V3")
            v3 = sorted(created.GetItemListInTrack("video", 3), key=lambda x: x.GetStart())
            check(len(v3) == 1 and item_media_id(v3[0]) == item_media_id(source) and
                  (v3[0].GetStart(), v3[0].GetEnd(), v3[0].GetSourceStartFrame(), v3[0].GetSourceEndFrame()) ==
                  (source.GetStart(), source.GetEnd(), source.GetSourceStartFrame(), source.GetSourceEndFrame()),
                  "avatar duplicate range/source readback mismatch")
            check(protected_signature(created) == protected_baseline, "audio/subtitle drift after avatar append")

            old_gif = sorted(created.GetItemListInTrack("video", 5), key=lambda x: x.GetStart())[0]
            if created.GetIsTrackLocked("video", 5):
                check(created.SetTrackLock("video", 5, False), "could not unlock V5 on the new copy for GIF relocation")
                time.sleep(0.35)
                check(not created.GetIsTrackLocked("video", 5), "V5 did not unlock on the new copy")
            gif_media = old_gif.GetMediaPoolItem()
            gif_info = {
                "mediaPoolItem": gif_media,
                "startFrame": old_gif.GetSourceStartFrame(),
                # TimelineItem reports an inclusive source end, while AppendToTimeline
                # consumes an exclusive end. Add one so both record and source ranges survive.
                "endFrame": old_gif.GetSourceEndFrame() + 1,
                "mediaType": 1,
                "trackIndex": 2,
                "recordFrame": old_gif.GetStart(),
            }
            appended_gif = media_pool.AppendToTimeline([gif_info])
            time.sleep(DELAY)
            check(appended_gif and len(appended_gif) == 1, "GIF duplicate append failed")
            result["steps"].append("replaced GIF placement on V2 with exact source/range")
            v2_gifs = sorted(created.GetItemListInTrack("video", 2), key=lambda x: x.GetStart())
            result["gif_append_return"] = [item_signature(item, VIDEO_PROPS) for item in appended_gif]
            result["video_tracks_after_gif_append"] = {
                str(i): [item_signature(item, VIDEO_PROPS) for item in sorted(
                    created.GetItemListInTrack("video", i) or [], key=lambda x: x.GetStart())]
                for i in range(1, created.GetTrackCount("video") + 1)
            }
            check(len(v2_gifs) == 1 and item_media_id(v2_gifs[0]) == item_media_id(old_gif) and
                  (v2_gifs[0].GetStart(), v2_gifs[0].GetEnd(), v2_gifs[0].GetSourceStartFrame(),
                   v2_gifs[0].GetSourceEndFrame()) == (606, 721, 0, 47), "GIF clone readback mismatch")
            result.pop("gif_append_return", None)
            result.pop("video_tracks_after_gif_append", None)
            check(created.DeleteClips([old_gif], False), "could not remove old GIF placement after verified clone")
            time.sleep(DELAY)
            result["steps"].append("removed old V5 GIF only after V2 clone passed verification")
            check(created.GetItemListInTrack("video", 5) == [], "old GIF lane is not empty")
            check(created.DeleteTrack("video", 5), "could not delete verified-empty V5")
            time.sleep(DELAY)
            result["steps"].append("removed verified-empty V5")
            check(created.GetTrackCount("video") == 4, "expected exactly four video tracks")

            # Names match the project's 9:16 track architecture.
            names = ((1, "Game Top"), (2, "REACTIONS"), (3, "VTuber Bottom"), (4, "VTuber Zoom"))
            for index, name in names:
                check(created.SetTrackName("video", index, name), f"could not name V{index} {name}")
                time.sleep(0.35)
                check(created.GetTrackName("video", index) == name, f"track name readback failed at V{index}")

            for key, value in RASTER:
                check(created.SetSetting(key, value), f"could not set {key}")
                time.sleep(0.35)
            time.sleep(DELAY)
            result["settings"] = {key: created.GetSetting(key) for key, _ in RASTER}
            for key, value in RASTER:
                check(str(result["settings"][key]) == value, f"setting readback mismatch {key}: {result['settings'][key]}")
            check(float(created.GetSetting("timelineFrameRate")) == 60.0, "pilot frame rate changed")
            result["steps"].append("set and verified 1080x1920 timeline raster")

            # Render layout: game crop fills the top 960 px; Armigon crop fills the lower 960 px.
            v1_new = sorted(created.GetItemListInTrack("video", 1), key=lambda x: x.GetStart())[0]
            v3_new = sorted(created.GetItemListInTrack("video", 3), key=lambda x: x.GetStart())[0]
            transform_locks = {index: created.GetIsTrackLocked("video", index) for index in (1, 3, 4)}
            for index, was_locked in transform_locks.items():
                if was_locked:
                    check(created.SetTrackLock("video", index, False), f"could not unlock V{index} on the new copy for framing")
                    time.sleep(0.35)
                    check(not created.GetIsTrackLocked("video", index), f"V{index} did not unlock on the new copy")
            result["game_transform"] = set_clip_transform(v1_new, portrait_transform(GAME_CROP, 0.0))
            result["avatar_transform"] = set_clip_transform(
                v3_new, portrait_transform(AVATAR_CROP, SPLIT, crop_top_src=AVATAR_CROP[1]))
            result["gif_transform"] = set_clip_transform(v2_gifs[0], {
                "ZoomX": GIF_ZOOM, "ZoomY": GIF_ZOOM,
                "Pan": GIF_CENTER[0] - CANVAS_W / 2,
                "Tilt": -(GIF_CENTER[1] - CANVAS_H / 2) / GIF_TILT_PX,
            })

            focus = sorted(created.GetItemListInTrack("video", 4), key=lambda x: x.GetStart())
            check(len(focus) == 1 and focus[0].GetName() == "Adjustment Clip" and
                  (focus[0].GetStart(), focus[0].GetEnd()) == (1613, 2065), "focus clip range changed")
            t = fusion_transform(focus[0])
            result["focus_before"] = fusion_signature(focus[0])
            original_focus = original_signature["video_tracks"][1]["items"][0]["fusion"]
            check(result["focus_before"] == original_focus,
                  "focus Fusion composition changed while moving tracks, before the approved reframing")
            for key in ("Size", "Pivot", "Center"):
                t.SetInput(key, FOCUS[key], 0.0)
                time.sleep(0.35)
            time.sleep(DELAY)
            result["focus_after"] = fusion_signature(focus[0])
            check(abs(float(result["focus_after"]["Size"]) - FOCUS["Size"]) < 0.0001,
                  f"focus Size readback mismatch: {result['focus_after']}")
            for key in ("Pivot", "Center"):
                rb = result["focus_after"][key]
                for axis in ("1", "2", "3"):
                    check(abs(float(rb[axis]) - float(FOCUS[key][int(axis)])) < 0.0001,
                          f"focus {key} readback mismatch: {result['focus_after']}")
            check(result["focus_after"]["Edges"] == result["focus_before"]["Edges"], "focus edge handling changed")
            for index, was_locked in transform_locks.items():
                check(created.SetTrackLock("video", index, was_locked), f"could not restore V{index} lock state")
                time.sleep(0.35)
                check(created.GetIsTrackLocked("video", index) == was_locked,
                      f"V{index} lock state readback mismatch")

            stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            drt_path = OUT_DIR / f"armigon_9x16_pilot_{stamp}.drt"
            OUT_DIR.mkdir(parents=True, exist_ok=True)
            check(created.Export(str(drt_path), resolve.EXPORT_DRT, resolve.EXPORT_NONE), "pilot DRT export failed")
            subtitle_drt_after = subtitle_drt_signature(drt_path)
            check(subtitle_drt_after == subtitle_drt_before,
                  "DRT subtitle text/timing/style changed in the duplicated pilot")
            result["subtitle_verification"] = {
                "method": "canonicalized SubtitleTrackVec from the original and pilot DRT exports",
                "cue_count": len(subtitle_drt_after["cues"]),
                "text_timing_style_equal": True,
                "drt_path": str(drt_path),
            }

            check(protected_signature(created) == protected_baseline,
                  "duration, audio/SFX/BGM levels, or subtitle cues changed in the new pilot")
            check([(i.GetStart(), i.GetEnd()) for i in created.GetItemListInTrack("video", 1)] == [(0, 6658)],
                  "game source timeline length changed")
            check([(i.GetStart(), i.GetEnd(), i.GetSourceStartFrame(), i.GetSourceEndFrame())
                   for i in created.GetItemListInTrack("video", 2)] == [(606, 721, 0, 47)], "GIF timing changed")
            check([(i.GetStart(), i.GetEnd()) for i in created.GetItemListInTrack("video", 3)] == [(0, 6658)],
                  "avatar layer timeline length changed")
            check([(i.GetStart(), i.GetEnd()) for i in created.GetItemListInTrack("video", 4)] == [(1613, 2065)],
                  "focus start/end changed")
            result["track_names"] = [created.GetTrackName("video", i) for i in range(1, 5)]
            result["protected_equal"] = protected_signature(created) == protected_baseline
            result["duration_frames"] = created.GetEndFrame() - created.GetStartFrame()
            result["subtitle_cues"] = len(protected_signature(created)["subtitle_tracks"][0]["items"])
            result["audio_track_count"] = created.GetTrackCount("audio")
            result["subtitle_track_count"] = created.GetTrackCount("subtitle")

            check(project.GetTimelineCount() == initial_count + 1, "unexpected timeline count change before save")
            check(pm.SaveProject(), "SaveProject failed")
            time.sleep(DELAY)
            result["saved"] = True
            result["steps"].append("saved and read back the new pilot")

        # preserved_state must restore the original active timeline, timecode, page and folder.
        after_tl = project.GetCurrentTimeline()
        after_folder = project.GetMediaPool().GetCurrentFolder()
        result["state_restored"] = bool(
            after_tl and after_tl.GetUniqueId() == initial_timeline_id and
            after_tl.GetCurrentTimecode() == initial_timecode and
            resolve.GetCurrentPage() == initial_page and
            folder_id(after_folder) == initial_folder_id)
        check(result["state_restored"], "Resolve user state did not fully restore")
        check(full_original_signature(original) == original_signature, "original timeline readback changed after restore")
        result["resolve_running"] = connect_resolve() is not None
        check(result["resolve_running"], "Resolve stopped responding after the pilot")
        result["timeline_count_before"] = initial_count
        result["timeline_count_after"] = project.GetTimelineCount()
        result["status"] = "PASS"
    except Exception as exc:
        result["status"] = "FAILED"
        result["error"] = repr(exc)
        # If creation got far enough to create a timeline, remove only this exact, previously-absent target.
        try:
            candidates = [created] if created is not None else find_timeline(project, name=TARGET_NAME)
            candidates = [c for c in candidates if c and c.GetName() == TARGET_NAME and c.GetUniqueId() != ORIGINAL_ID]
            if candidates:
                active = project.GetCurrentTimeline()
                if active and active.GetUniqueId() in {c.GetUniqueId() for c in candidates}:
                    project.SetCurrentTimeline(original)
                    time.sleep(DELAY)
                check(media_pool.DeleteTimelines(candidates), "cleanup DeleteTimelines returned False")
                time.sleep(DELAY)
                check(not find_timeline(project, name=TARGET_NAME), "cleanup did not remove the failed pilot")
                result["cleanup"] = "removed only the timeline created by this script"
                if not pm.SaveProject():
                    result["cleanup_complete"] = False
                    result["cleanup_save_warning"] = "SaveProject returned False; rollback is not confirmed on disk and needs inspection"
                else:
                    check(project.GetTimelineCount() == initial_count, "timeline count did not return to its preflight value")
                    check(full_original_signature(original) == original_signature,
                          "original timeline changed during rollback")
                    result["cleanup_complete"] = True
            else:
                result["cleanup"] = "no target timeline had been created"
        except Exception as cleanup_error:
            result["cleanup_error"] = repr(cleanup_error)
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        out = OUT_DIR / f"armigon_9x16_pilot_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        print(json.dumps(result, ensure_ascii=True, indent=2, default=str))
        raise

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"armigon_9x16_pilot_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
    result["log_path"] = str(out)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=True, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
