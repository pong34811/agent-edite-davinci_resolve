"""Rebuild #3 _9x16 from scratch: delete the broken copy, duplicate original, apply layout.

The original has 2 video tracks: V1 (game) + V2 (VTuber Focus / 7 Adjustment Clips).
Target structure: V1 Game Top, V2 VTuber Bottom, V3 VTUBER_FOCUS (7 Adjustment Clips).

Usage: python -m scripts.rebuild_t3_9x16 [--apply]
"""
from __future__ import annotations

import json
import sys
import time

from scripts.p2_9x16_build import DELAY, FOCUS_GEN, RASTER, SHORT, activate, items, protected, set_float
from scripts.p2_9x16_common import check, find
from scripts.p2_9x16_layout import PROPS, fusion_transform, stream_for, stream_params
from scripts.resolve_common import connect_resolve, preserved_state

ORIG_NAME = "คุยเรื่องโมเดล VTuber 2D บนมือถือ-vdo"
TARGET_NAME = ORIG_NAME + "_9x16"
POS_TOL = ("Pan", "Tilt", "CropTop", "CropBottom")


def main():
    apply = "--apply" in sys.argv
    r = connect_resolve()
    check(r is not None, "Resolve unavailable")
    pm = r.GetProjectManager()
    p = pm.GetCurrentProject()
    check(p is not None, "no current project")

    orig = find(p, name=ORIG_NAME)
    check(orig is not None, f"original not found: {ORIG_NAME}")

    # Verify original structure
    nv_orig = orig.GetTrackCount("video")
    check(nv_orig == 2, f"original has {nv_orig} video tracks, expected 2")
    check(orig.GetTrackName("video", 2) == "VTuber Focus", "original V2 not named 'VTuber Focus'")
    orig_focus = items(orig, "video", 2)
    check(len(orig_focus) == 7, f"original V2 has {len(orig_focus)} items, expected 7")
    check(all(x.GetName() == FOCUS_GEN for x in orig_focus), "original V2 not all Adjustment Clips")

    # Get layout params
    stream_key, anchor = stream_for(orig.GetName())
    check(stream_key is not None, f"no layout anchor for '{orig.GetName()}'")
    game, avatar, meta, focus = stream_params(anchor)

    log = {"stream": stream_key, "game": game, "avatar": avatar, "focus": focus}

    if not apply:
        print("DRY RUN - would delete existing target and rebuild from original")
        return 0

    with preserved_state(r):
        r.OpenPage("edit")
        time.sleep(2)
        check(r.GetCurrentPage() == "edit", "not on Edit page")

        # Delete existing broken target
        old = find(p, name=TARGET_NAME)
        if old is not None:
            # Delete all items on all video tracks first (DeleteTrack fails if items exist)
            for n in range(old.GetTrackCount("video"), 0, -1):
                track_items = items(old, "video", n)
                if track_items:
                    old.DeleteClips([x.GetUniqueId() for x in track_items], False)
                    time.sleep(DELAY)
                old.DeleteTrack("video", n)
                time.sleep(DELAY)
            # Delete the timeline itself
            p.DeleteTimeline(old.GetUniqueId())
            time.sleep(DELAY)
            log["deleted_old_target"] = True

        # Verify deletion
        check(find(p, name=TARGET_NAME) is None, "target still exists after deletion")

        # Duplicate
        activate(p, orig)
        base = protected(orig)
        new = orig.DuplicateTimeline(TARGET_NAME)
        check(new is not None and new.GetName() == TARGET_NAME, "DuplicateTimeline failed")
        time.sleep(DELAY)
        log["new_id"] = new.GetUniqueId()

        # Set raster
        activate(p, new)
        check(protected(new) == base, "duplicate protected content differs")
        for k, v in RASTER:
            new.SetSetting(k, v)
            time.sleep(0.3)
        time.sleep(DELAY)
        log["settings"] = {k: new.GetSetting(k) for k, _ in RASTER}
        for k, v in RASTER:
            check(str(log["settings"][k]) == v, f"setting {k} = {log['settings'][k]} (want {v})")

        # AddTrack at index 2: V1 game -> V1, V2 empty, V3 focus (was V2)
        check(new.AddTrack("video", {"index": 2}), "AddTrack index 2 failed")
        time.sleep(DELAY)
        check(new.GetTrackCount("video") == 3, f"video track count is {new.GetTrackCount('video')}, expected 3")

        # V2 = same source clip, same ranges, video only (VTuber panel)
        v1_orig = items(orig, "video", 1)
        check(len(v1_orig) == 1, f"original V1 has {len(v1_orig)} items, expected 1")
        a = v1_orig[0]
        mp = p.GetMediaPool()
        info = {
            "mediaPoolItem": a.GetMediaPoolItem(),
            "startFrame": a.GetSourceStartFrame(),
            "endFrame": a.GetSourceEndFrame(),
            "mediaType": 1,
            "trackIndex": 2,
            "recordFrame": a.GetStart(),
        }
        check(mp.AppendToTimeline([info]), "append V2 panel failed")
        time.sleep(DELAY)
        v2_items = items(new, "video", 2)
        check(len(v2_items) == 1, f"V2 has {len(v2_items)} items after append, expected 1")
        check(
            (v2_items[0].GetStart(), v2_items[0].GetEnd(), v2_items[0].GetSourceStartFrame(), v2_items[0].GetSourceEndFrame())
            == (a.GetStart(), a.GetEnd(), a.GetSourceStartFrame(), a.GetSourceEndFrame()),
            "V2 panel range mismatch",
        )
        check(protected(new) == base, "protected drift after V2 append")

        # V1/V2 transforms
        v1_new = items(new, "video", 1)[0]
        v2_new = items(new, "video", 2)[0]
        for item, props in ((v1_new, game), (v2_new, avatar)):
            for k, v in props.items():
                set_float(item, k, v, 0.5 if k in POS_TOL else 0.005)
        log["v1_readback"] = {k: v1_new.GetProperty(k) for k in PROPS}
        log["v2_readback"] = {k: v2_new.GetProperty(k) for k in PROPS}

        # V3 Fusion transforms (Adjustment Clips already in place from duplicate)
        v3_items = items(new, "video", 3)
        check(len(v3_items) == 7, f"V3 has {len(v3_items)} items, expected 7")
        check(all(x.GetName() == FOCUS_GEN for x in v3_items), "V3 not all Adjustment Clips")
        # Verify ranges match original V2
        orig_ranges = [(x.GetStart(), x.GetEnd()) for x in orig_focus]
        new_ranges = [(x.GetStart(), x.GetEnd()) for x in v3_items]
        check(new_ranges == orig_ranges, f"V3 ranges {new_ranges} != original V2 ranges {orig_ranges}")

        for x in v3_items:
            t = fusion_transform(x)
            for k in ("Size", "Pivot", "Center"):
                t.SetInput(k, focus[k])
                time.sleep(0.5)
            time.sleep(DELAY)
            rb = {k: t.GetInput(k) for k in ("Size", "Center", "Pivot", "Edges")}
            check(
                abs(float(rb["Size"]) - focus["Size"]) < 1e-6
                and all(abs(float(rb[k][i]) - focus[k][i]) < 1e-6 for k in ("Pivot", "Center") for i in (1, 2)),
                f"focus readback {rb}",
            )

        # Track names
        for n, nm in ((1, "Game Top"), (2, "VTuber Bottom"), (3, "VTUBER_FOCUS")):
            new.SetTrackName("video", n, nm)
            time.sleep(0.3)

        # Final protected check
        check(protected(new) == base, "protected drift at end of build")

        # Save
        check(pm.SaveProject(), "SaveProject failed")
        time.sleep(DELAY)
        log["saved"] = True

    print(json.dumps(log, ensure_ascii=False, indent=1, default=str))
    print("REBUILD_OK", log["new_id"])
    return 0


if __name__ == "__main__":
    sys.exit(main())