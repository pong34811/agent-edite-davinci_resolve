"""Fix #3 _9x16 (`คุยเรื่องโมเดล VTuber 2D บนมือถือ-vdo_9x16`).

Current (wrong):
  V1: game clip (0-1298) + transforms
  V2: empty
  V3: game clip (0-1298) + transforms  ← wrong, should be Adjustment Clips
  V4: 7 Adjustment Clips             ← wrong, should be V3

Target (correct, 3 video tracks):
  V1: Game Top      — game clip + game transforms
  V2: VTuber Bottom — game clip + avatar transforms (copy of V1 source)
  V3: VTUBER_FOCUS  — 7 Adjustment Clips + Fusion transforms (copy of original V2)

Original timeline has 2 video tracks: V1 (game) + V2 (VTuber Focus / 7 Adjustment Clips).
"""
from __future__ import annotations

import json
import sys
import time

from scripts.p2_9x16_build import DELAY, FOCUS_GEN, RASTER, activate, items, protected, set_float

FOCUS_NAME = FOCUS_GEN
from scripts.p2_9x16_common import check, find
from scripts.p2_9x16_layout import PROPS, fusion_transform, stream_for, stream_params
from scripts.resolve_common import connect_resolve, preserved_state

ORIG_NAME = "คุยเรื่องโมเดล VTuber 2D บนมือถือ-vdo"
TARGET_NAME = ORIG_NAME + "_9x16"
POS_TOL = ("Pan", "Tilt", "CropTop", "CropBottom")


def main():
    r = connect_resolve()
    check(r is not None, "Resolve unavailable")
    pm = r.GetProjectManager()
    p = pm.GetCurrentProject()
    check(p is not None, "no current project")

    orig = find(p, name=ORIG_NAME)
    new = find(p, name=TARGET_NAME)
    check(orig is not None, f"original not found: {ORIG_NAME}")
    check(new is not None, f"target not found: {TARGET_NAME}")

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

    # Baseline protected content
    activate(p, orig)
    base = protected(orig)

    log = {"stream": stream_key, "game": game, "avatar": avatar, "focus": focus}

    with preserved_state(r):
        r.OpenPage("edit")
        time.sleep(2)
        check(r.GetCurrentPage() == "edit", "not on Edit page")

        activate(p, new)

        # --- Step 1: Delete V3 game clip (wrong) ---
        v3_items = items(new, "video", 3)
        check(len(v3_items) == 1, f"V3 has {len(v3_items)} items, expected 1")
        check(v3_items[0].GetName() != FOCUS_GEN, "V3 is already an Adjustment Clip, not the expected game clip")
        new.DeleteClips([v3_items[0].GetUniqueId()], False)
        time.sleep(DELAY)
        log["step1_delete_v3_game_clip"] = True

        # --- Step 2: Delete V4 Adjustment Clips (wrong) ---
        v4_items = items(new, "video", 4)
        check(len(v4_items) == 7, f"V4 has {len(v4_items)} items, expected 7")
        for x in v4_items:
            check(x.GetName() == FOCUS_GEN, f"V4 item {x.GetName()} is not an Adjustment Clip")
        new.DeleteClips([x.GetUniqueId() for x in v4_items], False)
        time.sleep(DELAY)
        log["step2_delete_v4_adjustment_clips"] = True

        # --- Step 3: Delete V4 track (now empty) ---
        check(new.GetTrackCount("video") == 4, f"video track count is {new.GetTrackCount('video')}, expected 4")
        new.DeleteTrack("video", 4)
        time.sleep(DELAY)
        check(new.GetTrackCount("video") == 3, f"video track count is {new.GetTrackCount('video')}, expected 3")
        log["step3_delete_v4_track"] = True

        # --- Step 4: Append game clip to V2 (same source as V1) ---
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
        log["step4_append_v2_panel"] = True

        # --- Step 5: Insert 7 Adjustment Clips to V3 (matching original V2 ranges) ---
        # First, lock all tracks except V3
        for n in range(1, 4):
            new.SetTrackLock("video", n, n != 3)
            time.sleep(0.3)
        time.sleep(DELAY)

        for i, orig_clip in enumerate(orig_focus):
            s, e = orig_clip.GetStart(), orig_clip.GetEnd()
            new.SetMarkInOut(s, e - 1)
            new.SetCurrentTimecode(f"{s // 1800:02d}:{(s // 30) % 60:02d}:{s % 30:02d}:00")
            time.sleep(DELAY)
            check(new.InsertGeneratorIntoTimeline(FOCUS_NAME), f"insert Adjustment Clip {i+1} failed")
            time.sleep(DELAY)
            new_items = items(new, "video", 3)
            check(len(new_items) == i + 1, f"V3 has {len(new_items)} items after insert {i+1}, expected {i+1}")
            new_clip = new_items[-1]
            check(new_clip.GetName() == FOCUS_GEN, f"inserted item {new_clip.GetName()} is not Adjustment Clip")
            check(int(new_clip.GetStart()) == s and int(new_clip.GetEnd()) == e,
                  f"inserted range {new_clip.GetStart()}-{new_clip.GetEnd()} != {s}-{e}")
            log[f"step5_insert_clip_{i+1}"] = {"start": s, "end": e}

        new.ClearMarkInOut()
        # Unlock all tracks
        for n in range(1, 4):
            new.SetTrackLock("video", n, False)
            time.sleep(0.3)
        time.sleep(DELAY)
        log["step5_insert_7_adjustment_clips"] = True

        # --- Step 6: Set V1/V2 transforms ---
        v1_new = items(new, "video", 1)[0]
        v2_new = items(new, "video", 2)[0]
        for item, props in ((v1_new, game), (v2_new, avatar)):
            for k, v in props.items():
                set_float(item, k, v, 0.5 if k in POS_TOL else 0.005)
        log["step6_v1_v2_transforms"] = True

        # --- Step 7: Set V3 Fusion transforms ---
        v3_new = items(new, "video", 3)
        check(len(v3_new) == 7, f"V3 has {len(v3_new)} items, expected 7")
        for x in v3_new:
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
        log["step7_v3_fusion_transforms"] = True

        # --- Step 8: Set track names ---
        for n, nm in ((1, "Game Top"), (2, "VTuber Bottom"), (3, "VTUBER_FOCUS")):
            new.SetTrackName("video", n, nm)
            time.sleep(0.3)
        log["step8_track_names"] = True

        # --- Step 9: Verify protected content ---
        check(protected(new) == base, "protected content changed")
        log["step9_protected_verified"] = True

        # --- Step 10: Save ---
        check(pm.SaveProject(), "SaveProject failed")
        time.sleep(DELAY)
        log["step10_saved"] = True

    print(json.dumps(log, ensure_ascii=False, indent=1, default=str))
    print("FIX_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())