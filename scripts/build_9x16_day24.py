"""Build `<name>_9x16` for the Katy404 Minecraft "day 24" project (1920x1080 @ 60 fps, avatar baked bottom-right).

MCP-GAP: timeline.duplicate / add_track / delete_clips exist in the davinci-resolve MCP but each auto-archives the
timeline (unrequested project change); appending a source range onto a chosen track and exporting verification stills
have no MCP action -> scripting API through scripts/resolve_common (same reason as build_9x16_batch).

Geometry is expressed in 1280x720 "preview" coordinates of the fitted source (the 2560x1440 file shown in a 16:9
timeline); the fit raster is 16:9 so fix_vtuber2d_9x16.place/window_crop apply unchanged. Source content rows 26..693
(letterbox bars), avatar bbox x ~935..1200, y ~420..720 (ahoge tip at y ~420).

Layout: V1 "Game Top" (rows 0..960), V2 "REACTIONS" (original GIFs, same record range), V3 "VTuber Bottom"
(rows 960..1920), V4 "VTuber Full" (full-screen avatar over the merged original VTuber-Focus ranges).
Subtitles, audio and the V1 source range are checked identical before and after; the original is never touched.

Usage: python -m scripts.build_9x16_day24 [--apply]      (default: dry run, read-only)
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from scripts.fix_vtuber2d_9x16 import CH, CW, S0, SRC_H, SRC_W, apply_props, place, read_props, window_crop
from scripts.p2_9x16_build import DELAY, RASTER, activate, items, protected, set_float
from scripts.p2_9x16_common import check, find
from scripts.resolve_common import connect_resolve, preserved_state

OUT = Path(__file__).resolve().parents[1] / "exports" / "9x16-day24"
ORIG_NAME = "วันที่ 24 ปลูกข้าวจนกว่าจะ 10K ผู้ติดตาม - Katy404"
FPS = 60
GAME_WIN = (300.0, 90.0, 930.0, 650.0)   # 630x560 (1.125 = 1080:960); keeps the avatar's shoulder out of the panel
AV_CENTRE = (1065.0, 532.0)              # avatar window centre; window bottom = 692 = last non-letterbox row (no black band)
K_STACK = 3.0                            # window 360x320 -> y 372..692: ahoge tip (y ~420) with ~15% headroom
K_FULL = 3.6                             # canvas width covers 300 src px; avatar ~265 px wide -> ~88%
SRC_BOTTOM = 692.0                       # bottom letterbox bar starts ~693
GIF_ZOOM = 0.42                          # saved "vdo" zoom (same as the 16:9 originals); square GIF -> ~454 px wide
GIF_TILT = 960.0 - 330.0                # Tilt is 1 canvas px/unit on an uncropped item (the 0.316 factor only applies to cropped ones); centre the GIF at canvas y 330: inside the game panel, clear of avatar/subtitles


def layouts():
    x0, y0, x1, y1 = GAME_WIN
    k_game = 960.0 / (y1 - y0)
    v1 = place(((x0 + x1) / 2, (y0 + y1) / 2), k_game, (540.0, 480.0))
    v1.update(window_crop(x0, y0, x1, y1))
    w, h = CW / K_STACK, 960.0 / K_STACK
    cx, cy = AV_CENTRE
    v3 = place((cx, cy), K_STACK, (540.0, 1440.0))
    v3.update(window_crop(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))
    fy = SRC_BOTTOM - (CH / K_FULL) / 2
    full = place((cx, fy), K_FULL, (540.0, 960.0))
    full.update(window_crop(0, 0, SRC_W, SRC_H))
    return {"V1": v1, "V3": v3, "FULL": full}


def merge(ranges):
    out = []
    for a, b in sorted(ranges):
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return [tuple(x) for x in out]


def build(apply):
    r = connect_resolve()
    check(r is not None, "Resolve unavailable")
    pm = r.GetProjectManager()
    p = pm.GetCurrentProject()
    check(p is not None, "no project")
    check(not p.IsRenderingInProgress(), "render in progress")
    target_name = ORIG_NAME + "_9x16"
    orig = find(p, name=ORIG_NAME)
    check(orig is not None, "original not found")
    check(find(p, name=target_name) is None, f"target already exists: {target_name}")
    check(float(orig.GetSetting("timelineFrameRate")) == FPS, "fps")
    check(orig.GetTrackCount("video") == 3, f"original has {orig.GetTrackCount('video')} video tracks")
    v1 = items(orig, "video", 1)
    v2 = items(orig, "video", 2)
    v3 = items(orig, "video", 3)
    check(len(v1) == 1 and v2 and all(x.GetName() == "Adjustment Clip" for x in v2), "unexpected V1/V2")
    gifs = [{"mpi": x.GetMediaPoolItem(), "name": x.GetName(), "start": x.GetStart(), "end": x.GetEnd(),
             "src0": x.GetSourceStartFrame(), "src1": x.GetSourceEndFrame()} for x in v3]
    check(all(g["mpi"] is not None for g in gifs), "GIF without media pool item")
    focus = merge([(x.GetStart(), x.GetEnd()) for x in v2])
    for g in gifs:
        check(not any(a < g["end"] and g["start"] < b for a, b in focus), f"GIF {g['name']} overlaps a focus range")
    lay = layouts()
    plan = {"target": target_name, "focus_merged": focus, "gifs": [{k: g[k] for k in ("name", "start", "end", "src0", "src1")} for g in gifs],
            "layouts": lay, "orig_tracks": [orig.GetTrackName("video", n) for n in (1, 2, 3)]}
    print("PLAN", json.dumps(plan, ensure_ascii=False))
    if not apply:
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    mp = p.GetMediaPool()
    log = {"plan": plan}
    with preserved_state(r):
        r.OpenPage("edit")
        time.sleep(2)
        check(r.GetCurrentPage() == "edit", "not on Edit page")
        activate(p, orig)
        base = protected(orig)
        new = orig.DuplicateTimeline(target_name)
        check(new is not None and new.GetName() == target_name, "DuplicateTimeline failed")
        time.sleep(DELAY)
        activate(p, new)
        check(protected(new) == base, "duplicate protected content differs from original")
        for k, v in RASTER:
            new.SetSetting(k, v)
            time.sleep(0.3)
        time.sleep(DELAY)
        for k, v in RASTER:
            check(str(new.GetSetting(k)) == v, f"setting {k}={new.GetSetting(k)} (want {v})")
        check(float(new.GetSetting("timelineFrameRate")) == FPS, "fps changed")
        locks = {n: new.GetIsTrackLocked("video", n) for n in (1, 2, 3)}
        for n in (1, 2, 3):
            if locks[n]:
                check(new.SetTrackLock("video", n, False), f"unlock V{n}")
        try:
            # drop the duplicate's own focus adjustment clips and GIFs (they are re-added on the new layout)
            old = items(new, "video", 2) + items(new, "video", 3)
            check(len(old) == len(v2) + len(v3), "duplicate V2/V3 count differs")
            check(new.DeleteClips(old, False), "DeleteClips failed")
            time.sleep(DELAY)
            check(items(new, "video", 2) == [] and items(new, "video", 3) == [], "V2/V3 not empty after delete")
            check(new.AddTrack("video"), "AddTrack failed")
            time.sleep(DELAY)
            check(new.GetTrackCount("video") == 4, "expected 4 video tracks")
            a = items(new, "video", 1)[0]
            src0, mpi = a.GetSourceStartFrame(), a.GetMediaPoolItem()

            def append(track, rec0, rec1, item=None, s0=None, s1=None):
                m = item or mpi
                if s0 is None:   # base footage: source frames == record frames (same fps)
                    base0, end0 = src0 + (rec0 - a.GetStart()), src0 + (rec1 - a.GetStart())
                else:            # GIF: source frames at the GIF's own fps (25), inclusive end as read from the original
                    base0, end0 = s0, s1
                info = {"mediaPoolItem": m, "startFrame": base0, "endFrame": end0,
                        "mediaType": 1, "trackIndex": track, "recordFrame": rec0}
                check(mp.AppendToTimeline([info]), f"append V{track} {rec0}-{rec1} failed")
                time.sleep(DELAY)
                got = [x for x in items(new, "video", track) if x.GetStart() == rec0]
                check(len(got) == 1 and abs(got[0].GetEnd() - rec1) <= 3, f"V{track} item {rec0}-{rec1} mismatch")
                return got[0]

            apply_props(a, lay["V1"])
            av = append(3, a.GetStart(), a.GetEnd())
            apply_props(av, lay["V3"])
            for f0, f1 in focus:
                apply_props(append(4, f0, f1), lay["FULL"])
            for g in gifs:
                gi = append(2, g["start"], g["end"], g["mpi"], g["src0"], g["src1"])
                set_float(gi, "ZoomX", GIF_ZOOM, 0.002)
                set_float(gi, "ZoomY", GIF_ZOOM, 0.002)
                set_float(gi, "Pan", 0.0, 0.5)
                set_float(gi, "Tilt", GIF_TILT, 1.0)
                log.setdefault("gifs_placed", []).append((g["name"], gi.GetStart(), gi.GetEnd()))
            for n, nm in ((1, "Game Top"), (2, "REACTIONS"), (3, "VTuber Bottom"), (4, "VTuber Full")):
                new.SetTrackName("video", n, nm)
                time.sleep(0.3)
            check(protected(new) == base, "protected drift")
            check(pm.SaveProject(), "SaveProject failed")
            time.sleep(DELAY)
            log["after"] = {f"V{n}": [(x.GetName(), x.GetStart(), x.GetEnd(), read_props(x)) for x in items(new, "video", n)] for n in (1, 2, 3, 4)}
            log["protected_equal"] = protected(new) == base
            check(log["protected_equal"], "protected drift at end")
        finally:
            for n in (1, 2, 3):
                if locks.get(n):
                    new.SetTrackLock("video", n, True)
    (OUT / "build_day24_9x16.json").write_text(json.dumps(log, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("BUILD_OK", target_name, "protected_equal", log["protected_equal"])
    return 0


def update():
    """Re-apply the layout values on the already built target (structure unchanged)."""
    r = connect_resolve()
    pm = r.GetProjectManager()
    p = pm.GetCurrentProject()
    tl = find(p, name=ORIG_NAME + "_9x16")
    orig = find(p, name=ORIG_NAME)
    check(tl is not None and orig is not None, "target/original not found")
    lay = layouts()
    with preserved_state(r):
        r.OpenPage("edit")
        time.sleep(2)
        activate(p, orig)
        base = protected(orig)
        activate(p, tl)
        check(protected(tl) == base, "target protected content differs from original")
        locks = {n: tl.GetIsTrackLocked("video", n) for n in (1, 2, 3, 4)}
        for n, v in locks.items():
            if v:
                check(tl.SetTrackLock("video", n, False), f"unlock V{n}")
        try:
            apply_props(items(tl, "video", 1)[0], lay["V1"])
            apply_props(items(tl, "video", 3)[0], lay["V3"])
            for x in items(tl, "video", 4):
                apply_props(x, lay["FULL"])
            for gi in items(tl, "video", 2):
                set_float(gi, "Pan", 0.0, 0.5)
                set_float(gi, "Tilt", GIF_TILT, 1.0)
            check(protected(tl) == base, "protected drift")
            check(pm.SaveProject(), "SaveProject failed")
        finally:
            for n, v in locks.items():
                if v:
                    tl.SetTrackLock("video", n, True)
    print("UPDATE_OK")
    return 0


if __name__ == "__main__":
    sys.exit(update() if "--update" in sys.argv else build("--apply" in sys.argv))
