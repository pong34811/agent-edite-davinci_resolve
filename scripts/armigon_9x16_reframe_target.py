"""Reframe the already-created first 9:16 target without changing protected tracks."""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime

from scripts.armigon_9x16_batch_one import (
    BACKUP,
    BASELINE,
    CANVAS_H,
    OUT_DIR,
    PROJECT_ID,
    PROJECT_NAME,
    check,
    dimensions,
    find_timeline,
    folder_id,
    full_original_signature,
    item_media_id,
    portrait_transform,
    protected_signature,
    set_clip_transform,
)
from scripts.backup_drp import verify_drp
from scripts.resolve_common import connect_resolve, preserved_state


def main(target_id: str) -> int:
    backup_size = verify_drp(BACKUP)
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    resolve = connect_resolve()
    check(resolve is not None, "cannot connect to Resolve")
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    check(project is not None and project.GetName() == PROJECT_NAME and
          project.GetUniqueId() == PROJECT_ID, "wrong Resolve project")
    check(not project.IsRenderingInProgress(), "Resolve is rendering")

    target_hits = find_timeline(project, timeline_id=target_id)
    check(len(target_hits) == 1, f"expected one target ID match for {target_id}")
    target = target_hits[0]
    check(target.GetName().endswith("_9x16"), "target ID is not a 9x16 timeline")
    source_name = target.GetName()[:-5]
    source_rows = [row for row in baseline["timelines"] if row["name"] == source_name]
    check(len(source_rows) == 1, "target has no unique baseline source")
    source_id = source_rows[0]["timeline_id"]
    source_hits = find_timeline(project, timeline_id=source_id, name=source_name)
    check(len(source_hits) == 1, "could not locate the exact source timeline")
    source = source_hits[0]
    check(target.GetTrackCount("video") == 4 and target.GetTrackCount("audio") == 3 and
          target.GetTrackCount("subtitle") == 1, "target track architecture differs")
    check(source.GetTrackCount("video") == 3, "source track architecture differs")
    target_v1 = sorted(target.GetItemListInTrack("video", 1) or [], key=lambda item: item.GetStart())
    target_v3 = sorted(target.GetItemListInTrack("video", 3) or [], key=lambda item: item.GetStart())
    check(len(target_v1) == len(target_v3) == 1, "expected one continuous clip on V1 and V3")
    check((target_v1[0].GetStart(), target_v1[0].GetEnd(),
           target_v1[0].GetSourceStartFrame(), target_v1[0].GetSourceEndFrame(),
           item_media_id(target_v1[0])) ==
          (target_v3[0].GetStart(), target_v3[0].GetEnd(),
           target_v3[0].GetSourceStartFrame(), target_v3[0].GetSourceEndFrame(),
           item_media_id(target_v3[0])), "V3 no longer mirrors the source clip exactly")

    initial = project.GetCurrentTimeline()
    check(initial is not None, "no active timeline to preserve")
    initial_id = initial.GetUniqueId()
    initial_timecode = initial.GetCurrentTimecode()
    initial_page = resolve.GetCurrentPage()
    media_pool = project.GetMediaPool()
    initial_folder = media_pool.GetCurrentFolder()
    initial_folder_id = folder_id(initial_folder)
    result = {
        "project": PROJECT_NAME,
        "target_id": target_id,
        "target_name": target.GetName(),
        "source_id": source_id,
        "backup": str(BACKUP),
        "backup_bytes_verified": backup_size,
        "reframed_track": "V3 VTuber Bottom",
    }

    with preserved_state(resolve):
        check(project.SetCurrentTimeline(source), "could not activate source for baseline")
        time.sleep(0.8)
        source_before = full_original_signature(source)
        source_w, source_h = dimensions(target_v1[0])
        layout = {(1280, 702): (800.0, 100.0, 1280.0, 527.0),
                  (1920, 1080): (1170.0, 600.0, 1710.0, 1080.0)}.get((source_w, source_h))
        check(layout is not None, f"no reviewed lower-panel crop for {source_w}x{source_h}")
        check(project.SetCurrentTimeline(target), "could not activate target for reframe")
        time.sleep(0.8)
        protected_before = protected_signature(target)
        item = sorted(target.GetItemListInTrack("video", 3) or [], key=lambda x: x.GetStart())[0]
        old_v3_properties = {key: item.GetProperty(key) for key in (
            "ZoomX", "ZoomY", "ZoomGang", "Pan", "Tilt", "CropTop")}
        was_locked = target.GetIsTrackLocked("video", 3)
        if was_locked:
            check(target.SetTrackLock("video", 3, False), "could not unlock V3")
            time.sleep(0.25)
            check(not target.GetIsTrackLocked("video", 3), "V3 unlock did not read back")
        result["avatar_transform"] = set_clip_transform(
            item, portrait_transform(layout, 960.0, source_w, source_h, crop_top_src=layout[1]))
        if was_locked:
            check(target.SetTrackLock("video", 3, True), "could not restore V3 lock")
            time.sleep(0.25)
            check(target.GetIsTrackLocked("video", 3), "V3 lock did not restore")
        check(protected_signature(target) == protected_before,
              "audio/subtitle/duration signature changed during reframe")
        focus_items = sorted(target.GetItemListInTrack("video", 4) or [], key=lambda x: x.GetStart())
        check(len(focus_items) == 1 and focus_items[0].GetName() == "Adjustment Clip",
              "expected the original single V4 focus Adjustment Clip")
        focus_range = (focus_items[0].GetStart(), focus_items[0].GetEnd())
        base = sorted(target.GetItemListInTrack("video", 1) or [], key=lambda x: x.GetStart())[0]
        duration = focus_range[1] - focus_range[0]
        focus_source_start = base.GetSourceStartFrame() + focus_range[0] - base.GetStart()
        focus_source_end = focus_source_start + duration
        full_crop = {(1280, 702): (885.0, 0.0, 1280.0, 702.0),
                     (1920, 1080): (1190.0, 680.0, 1415.0, 1080.0)}.get((source_w, source_h))
        check(full_crop is not None, f"no full-screen focus crop for {source_w}x{source_h}")
        check(target.GetTrackCount("video") == 4, "unexpected track count before focus overlay")
        check(target.AddTrack("video", {"index": 5}), "could not add V5 full-screen focus track")
        time.sleep(0.8)
        check(target.GetTrackCount("video") == 5, "V5 did not read back")
        info = {
            "mediaPoolItem": base.GetMediaPoolItem(),
            "startFrame": focus_source_start,
            "endFrame": focus_source_end,
            "mediaType": 1,
            "trackIndex": 5,
            "recordFrame": focus_range[0],
        }
        appended = media_pool.AppendToTimeline([info])
        time.sleep(0.8)
        check(appended and len(appended) == 1, "could not append full-screen focus clip")
        full_focus = appended[0]
        check(item_media_id(full_focus) == item_media_id(base) and
              (full_focus.GetStart(), full_focus.GetEnd(), full_focus.GetSourceStartFrame(),
               full_focus.GetSourceEndFrame()) ==
              (focus_range[0], focus_range[1], focus_source_start, focus_source_end),
              "full-screen focus clip range/source mismatch")
        check(target.SetTrackName("video", 5, "VTuber Focus Fullscreen"), "could not name V5")
        time.sleep(0.25)
        check(target.GetTrackName("video", 5) == "VTuber Focus Fullscreen", "V5 name mismatch")
        result["focus_fullscreen_transform"] = set_clip_transform(
            full_focus, portrait_transform(full_crop, 0.0, source_w, source_h,
                                           crop_top_src=full_crop[1], panel_height=CANVAS_H))
        result["focus_fullscreen_clip"] = {
            "track": 5,
            "start": full_focus.GetStart(),
            "end": full_focus.GetEnd(),
            "source_start": full_focus.GetSourceStartFrame(),
            "source_end": full_focus.GetSourceEndFrame(),
            "media_id": item_media_id(full_focus),
        }
        check(protected_signature(target) == protected_before,
              "audio/subtitle/duration signature changed after focus overlay")
        result["focus_range"] = list(focus_range)
        check(project.SetCurrentTimeline(source), "could not activate source for preservation audit")
        time.sleep(0.8)
        check(full_original_signature(source) == source_before, "source timeline changed")
        result["source_unchanged"] = True
        check(project.SetCurrentTimeline(target), "could not reactivate target for save")
        time.sleep(0.8)
        check(pm.SaveProject(), "SaveProject failed")
        time.sleep(0.8)
        check(protected_signature(target) == protected_before,
              "protected signature changed after save")

    active = project.GetCurrentTimeline()
    result["resolve_state_restored"] = bool(
        active and active.GetUniqueId() == initial_id and
        active.GetCurrentTimecode() == initial_timecode and
        resolve.GetCurrentPage() == initial_page and
        folder_id(media_pool.GetCurrentFolder()) == initial_folder_id)
    check(result["resolve_state_restored"], "Resolve state did not restore")
    check(connect_resolve() is not None, "Resolve stopped responding")
    check(not project.IsRenderingInProgress(), "unexpected render started")
    result["resolve_running"] = True
    result["status"] = "PASS"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"reframe_{target_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
    result["log_path"] = str(path)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=True, indent=2, default=str))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-id", required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.target_id))
