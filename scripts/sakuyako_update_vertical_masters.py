"""Promote the cover-prepended vertical timeline variants to project masters.

The script is dry-run by default. With --apply it exports a verified DRP, uses
the existing DRT prepend pipeline to build/verify each vertical variant, swaps
the variant into the original timeline name, then removes the superseded source
timelines and task-created __cover_tmp variants.

MCP-GAP: community davinci-resolve timeline import/rename/delete actions are
not exposed in this session; the Studio MCP exposes script execution only.
The Resolve Python API is used through resolve_common.py for the missing edit.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PROJECT = "sakuyako-2026-09"
COVERS = Path(r"I:\.shortcut-targets-by-id\1EfyfEGeG4UTUmNzTR2IDLUPjm386Fqlu\Projects\Sakuyako-Cheris\sakuyako-2026-09\vdo")
FRAMES = 30
TMP = "__cover_tmp"
GAP = 1.3


def timeline_map(project):
    count = project.GetTimelineCount() or 0
    items = [project.GetTimelineByIndex(i) for i in range(1, count + 1)]
    items = [item for item in items if item]
    result = {}
    for item in items:
        name = item.GetName()
        if name in result:
            raise RuntimeError("duplicate timeline name: " + name)
        result[name] = item
    return result


def validate_variant(project, src, variant, frames, p2, cover_name):
    """Require the variant to preserve every original track/item after a shift."""
    previous = project.GetCurrentTimeline()
    assert project.SetCurrentTimeline(src), "could not activate source for readback"
    time.sleep(0.5)
    base = p2.content_signature(src)
    assert project.SetCurrentTimeline(variant), "could not activate variant for readback"
    time.sleep(0.5)
    shifted = p2.content_signature(variant, frames)
    if previous:
        assert project.SetCurrentTimeline(previous), "could not restore timeline after readback"
        time.sleep(0.5)
    if len(shifted["video"]) != len(base["video"]) + 1:
        raise RuntimeError("variant video track count is not source + cover track")
    cover_track = variant.GetTrackCount("video")
    cover_items = variant.GetItemListInTrack("video", cover_track) or []
    start = variant.GetStartFrame()
    if len(cover_items) != 1:
        raise RuntimeError("cover track must contain exactly one item")
    cover = cover_items[0]
    pool_item = cover.GetMediaPoolItem()
    if not pool_item or pool_item.GetName() != cover_name:
        raise RuntimeError("cover item does not match " + cover_name)
    if cover.GetStart() != start or cover.GetEnd() != start + frames:
        raise RuntimeError("cover is not exactly 30 frames at timeline start")
    shifted["video"] = shifted["video"][:-1]
    if shifted != base:
        differences = []
        for kind in ("video", "audio", "subtitle"):
            before_rows, after_rows = base[kind], shifted[kind]
            if before_rows == after_rows:
                continue
            for index in range(max(len(before_rows), len(after_rows))):
                before = before_rows[index] if index < len(before_rows) else None
                after = after_rows[index] if index < len(after_rows) else None
                if before != after:
                    differences.append({
                        "kind": kind, "track_index": index + 1,
                        "before_header": before[:2] if before else None,
                        "after_header": after[:2] if after else None,
                        "before_items": [(row[0], row[1], row[2], row[3]) for row in before[2][:3]] if before else None,
                        "after_items": [(row[0], row[1], row[2], row[3]) for row in after[2][:3]] if after else None,
                        "before_count": len(before[2]) if before else 0,
                        "after_count": len(after[2]) if after else 0,
                    })
                    break
        raise RuntimeError("source video/audio/subtitle content differs after offset normalization: "
                           + json.dumps(differences[:3], ensure_ascii=False))
    if variant.GetEndFrame() != src.GetEndFrame() + frames:
        raise RuntimeError("variant duration did not grow by exactly 30 frames")
    for kind in ("audio", "subtitle"):
        for _, _, rows in shifted[kind]:
            if any(row[1] < 0 for row in rows):
                raise RuntimeError(kind + " item begins before the inserted cover")
    return {
        "source": src.GetName(),
        "variant": variant.GetName(),
        "source_frames": src.GetEndFrame() - src.GetStartFrame(),
        "variant_frames": variant.GetEndFrame() - variant.GetStartFrame(),
        "cover": cover_name,
        "cover_start": cover.GetStart(),
        "cover_end": cover.GetEnd(),
        "audio_tracks": variant.GetTrackCount("audio"),
        "subtitle_tracks": variant.GetTrackCount("subtitle"),
    }


def validate_shifted_without_cover(project, src, variant, frames, p2):
    """Recognize a DRT import that was interrupted before its cover was appended."""
    previous = project.GetCurrentTimeline()
    assert project.SetCurrentTimeline(src), "could not activate source for readback"
    time.sleep(0.5)
    base = p2.content_signature(src)
    assert project.SetCurrentTimeline(variant), "could not activate partial variant for readback"
    time.sleep(0.5)
    shifted = p2.content_signature(variant, frames)
    if previous:
        assert project.SetCurrentTimeline(previous), "could not restore timeline after readback"
        time.sleep(0.5)
    if shifted != base:
        raise RuntimeError("partial DRT variant does not preserve source tracks/items after 30-frame shift")
    if variant.GetTrackCount("video") != src.GetTrackCount("video"):
        raise RuntimeError("partial DRT variant has an unexpected video track count")
    if variant.GetEndFrame() != src.GetEndFrame() + frames:
        raise RuntimeError("partial DRT variant has an unexpected duration")
    return {"source": src.GetName(), "variant": variant.GetName(), "status": "shifted_no_cover"}


def add_cover(project, media_pool, timeline, cover_item):
    assert project.SetCurrentTimeline(timeline), "could not activate cover variant"
    time.sleep(GAP)
    assert timeline.AddTrack("video"), "could not add cover video track"
    time.sleep(GAP)
    top = timeline.GetTrackCount("video")
    start = timeline.GetStartFrame()
    assert cover_item.SetMarkInOut(0, FRAMES - 1, "video"), "could not mark cover for 30 frames"
    try:
        assert media_pool.AppendToTimeline([{
            "mediaPoolItem": cover_item,
            "mediaType": 1,
            "trackIndex": top,
            "recordFrame": start,
        }]), "could not append cover"
    finally:
        cover_item.ClearMarkInOut("all")
    time.sleep(GAP)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="perform the master timeline update")
    parser.add_argument("--project", default=PROJECT)
    parser.add_argument("--covers", type=Path, default=COVERS)
    args = parser.parse_args()

    from scripts import p2_export_final as p2
    from scripts.backup_drp import export_verified
    from scripts.resolve_common import connect_resolve, preserved_state

    p2.OUT = ROOT / "exports" / "final-export" / args.project
    resolve = connect_resolve()
    if not resolve:
        raise SystemExit("Cannot connect to DaVinci Resolve")
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    if not project or project.GetName() != args.project:
        raise SystemExit(f"Open project {args.project!r} before running this script")

    initial_timeline = project.GetCurrentTimeline()
    initial_uid = initial_timeline.GetUniqueId() if initial_timeline else None
    initial_name = initial_timeline.GetName() if initial_timeline else None
    initial_timecode = initial_timeline.GetCurrentTimecode() if initial_timeline else None
    active_source_to_defer = None
    promoted_by_name = {}
    with preserved_state(resolve):
        timelines = timeline_map(project)
        bases = sorted(name for name in timelines if name.endswith("_9x16") and TMP not in name)
        temp_names = sorted(name for name in timelines if name.endswith(TMP))
        if len(bases) != 35:
            raise RuntimeError(f"expected 35 vertical masters, found {len(bases)}")
        stray = sorted(name for name in temp_names if name[:-len(TMP)] not in bases)
        if stray:
            raise RuntimeError("unmatched cover temp timelines: " + ", ".join(stray))
        backup_like = sorted(name for name in timelines if re.search(r"(?:__bak|__backup|__src_bak|_backup)", name, re.I))
        unexpected = [name for name in backup_like if not name.endswith(TMP)]
        if unexpected:
            raise RuntimeError("found other backup-like timelines; refusing to delete them: " + ", ".join(unexpected))

        missing_covers = [name for name in bases if not (args.covers / f"{name}.jpg").is_file()]
        if missing_covers:
            raise RuntimeError("missing matching cover(s): " + ", ".join(missing_covers))
        if project.IsRenderingInProgress():
            raise RuntimeError("Resolve still reports a render in progress")

        plan = [{"master": name, "existing_variant": name + TMP in timelines,
                 "cover": str(args.covers / f"{name}.jpg")} for name in bases]
        existing_audits = []
        for name in bases:
            variant = timelines.get(name + TMP)
            if variant:
                src = timelines[name]
                if variant.GetTrackCount("video") == src.GetTrackCount("video") + 1:
                    existing_audits.append(validate_variant(project, src, variant, FRAMES, p2,
                                                             f"{name}.jpg"))
                elif variant.GetTrackCount("video") == src.GetTrackCount("video"):
                    existing_audits.append(validate_shifted_without_cover(project, src, variant, FRAMES, p2))
                else:
                    raise RuntimeError("existing temp has unexpected video tracks: " + variant.GetName())
        print(json.dumps({"project": args.project, "vertical_masters": len(bases),
                          "existing_cover_temps": len(temp_names),
                          "existing_temp_readback": existing_audits, "plan": plan},
                         ensure_ascii=False, indent=2), flush=True)
        if not args.apply:
            return 0

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = ROOT / "backups" / f"{stamp}-before-update-vertical-masters-{args.project}.drp"
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup_bytes = export_verified(pm, project, backup)
        print(json.dumps({"backup": str(backup), "bytes": backup_bytes}, ensure_ascii=False), flush=True)

        media_pool = project.GetMediaPool()
        root = media_pool.GetRootFolder()
        cover_folder = next((folder for folder in root.GetSubFolderList() or []
                             if folder.GetName() == "P2 Covers"), None)
        if cover_folder is None:
            cover_folder = media_pool.AddSubFolder(root, "P2 Covers")
        assert cover_folder, "could not find/create P2 Covers bin"
        assert media_pool.SetCurrentFolder(cover_folder), "could not select P2 Covers bin"
        time.sleep(GAP)
        cover_items = {item.GetName(): item for item in cover_folder.GetClipList() or []}
        need = [str(args.covers / f"{name}.jpg") for name in bases
                if f"{name}.jpg" not in cover_items]
        if need:
            assert media_pool.ImportMedia(need), "cover import failed"
            time.sleep(GAP * 2)
            cover_items = {item.GetName(): item for item in cover_folder.GetClipList() or []}
        for name in bases:
            if f"{name}.jpg" not in cover_items:
                raise RuntimeError("cover missing from Media Pool: " + name + ".jpg")

        # Prepare and verify all 35 candidates before renaming or deleting any source.
        candidates = {}
        for idx, name in enumerate(bases, start=1):
            src = timelines[name]
            temp_name = name + TMP
            variant = timelines.get(temp_name)
            if variant is None:
                assert project.SetCurrentTimeline(src), "could not activate source before DRT export"
                time.sleep(GAP)
                variant = p2.shifted_cover_timeline(resolve, project, media_pool, src, temp_name, FRAMES)
                add_cover(project, media_pool, variant, cover_items[f"{name}.jpg"])
                time.sleep(GAP)
            elif variant.GetTrackCount("video") == src.GetTrackCount("video"):
                validate_shifted_without_cover(project, src, variant, FRAMES, p2)
                add_cover(project, media_pool, variant, cover_items[f"{name}.jpg"])
                time.sleep(GAP)
            report = validate_variant(project, src, variant, FRAMES, p2, f"{name}.jpg")
            candidates[name] = (src, variant, report)
            print(f"PREPARED {idx}/35 {name}", flush=True)

        # If the active timeline is one of the original masters, its replacement
        # gets a new UID. Leave it present until after preserved_state restores;
        # the current task begins on a __cover_tmp timeline, which is promoted in
        # place and keeps its active UID.
        active_source_to_defer = next((src for src, _, _ in candidates.values()
                                       if initial_uid and src.GetUniqueId() == initial_uid), None)

        old_masters = []
        promoted = []
        try:
            for idx, name in enumerate(bases, start=1):
                src, variant, _ = candidates[name]
                backup_name = f"{name}__src_bak_{stamp[-6:]}"
                if not src.SetName(backup_name):
                    raise RuntimeError("could not stage original as backup: " + name)
                if not variant.SetName(name):
                    src.SetName(name)
                    raise RuntimeError("could not promote prepared variant: " + name)
                old_masters.append(src)
                promoted.append((src, variant, name))
                promoted_by_name[name] = variant
                print(f"PROMOTED {idx}/35 {name}", flush=True)

            # Read back each promoted master against its staged source before deleting sources.
            for src, master, name in promoted:
                validate_variant(project, src, master, FRAMES, p2, f"{name}.jpg")

            delete_now = [old for old in old_masters if old is not active_source_to_defer]
            if delete_now and not media_pool.DeleteTimelines(delete_now):
                raise RuntimeError("Resolve failed to delete the superseded source timelines")
            expected_count = 71 if active_source_to_defer else 70
            if project.GetTimelineCount() != expected_count:
                raise RuntimeError(f"expected {expected_count} timelines before final state restore, got {project.GetTimelineCount()}")
            remaining = timeline_map(project)
            unexpected_temps = sorted(name for name in remaining if name.endswith(TMP))
            backup_names = sorted(name for name in remaining if "__src_bak_" in name
                                   and (not active_source_to_defer or name != active_source_to_defer.GetName()))
            if unexpected_temps or backup_names:
                raise RuntimeError(f"backup timelines remain: temps={unexpected_temps}, source backups={backup_names}")
            if not active_source_to_defer and not pm.SaveProject():
                raise RuntimeError("SaveProject failed after master update")
        except Exception:
            # Preserve recoverability on any failure. The verified DRP remains the
            # authoritative rollback point, and any still-live old masters remain
            # in the project under their backup names.
            try:
                pm.SaveProject()
            except Exception:
                pass
            raise

    # If the user's original active timeline was one of the replaced masters,
    # preserved_state restored it by UID while it was still safely staged. Now
    # return to the updated master with the same timeline name and playhead time,
    # then remove that final superseded timeline.
    if active_source_to_defer:
        updated = promoted_by_name.get(initial_name)
        if not updated:
            raise RuntimeError("updated active timeline could not be found: " + str(initial_name))
        assert project.SetCurrentTimeline(updated), "could not restore updated active timeline"
        if initial_timecode:
            updated.SetCurrentTimecode(initial_timecode)
        time.sleep(GAP)
        if not project.GetMediaPool().DeleteTimelines([active_source_to_defer]):
            raise RuntimeError("could not delete the superseded active source timeline")
        if not pm.SaveProject():
            raise RuntimeError("SaveProject failed after deleting the superseded active timeline")
        if project.GetTimelineCount() != 70:
            raise RuntimeError(f"expected 70 remaining timelines, got {project.GetTimelineCount()}")
        final_map = timeline_map(project)
        leftovers = sorted(name for name in final_map if name.endswith(TMP) or "__src_bak_" in name)
        if leftovers:
            raise RuntimeError("backup timelines remain after final cleanup: " + ", ".join(leftovers))

    print(json.dumps({"status": "complete", "updated_masters": len(promoted),
                          "deleted_source_timelines": len(old_masters), "remaining_timelines": project.GetTimelineCount(),
                          "backup": str(backup), "backup_bytes": backup_bytes},
                         ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
