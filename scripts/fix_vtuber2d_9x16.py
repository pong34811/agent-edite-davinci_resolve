"""Rebuild the picture layout of `คุยเรื่องโมเดล VTuber 2D บนมือถือ-vdo_9x16` (approved design, 2026-10-11).

MCP-GAP: timeline_item.set_transform/set_crop and timeline.add_track exist in the davinci-resolve MCP, but appending a
source range onto a NEW track (MediaPool.AppendToTimeline with trackIndex/recordFrame, video only) and exporting a
verification still in the same process have no MCP action -> scripting API through scripts/resolve_common.

Source is 1280x720 with the VTuber baked into the picture (no separate facecam). Layout:
  V1 "Game Top"      : source x 100..910 fills canvas rows 0..960 (stacked layout, top)
  V2 "REACTIONS"     : empty (a stray full-frame copy is removed; it was unlinked, video only)
  V3 "VTuber Bottom" : avatar window fills canvas rows 960..1920 (stacked layout, bottom)
  V4 "VTuber Full"   : full-screen avatar over the original VTuber-Focus ranges and every avatar-only scene
Subtitles, audio, V1 source range and the 16:9 original are never touched.

Geometry model (validated against the values of the earlier hand-built V1): canvas px per source px at zoom 1 is
S0 = 1080/1280; Pan is 1 canvas px/unit (+right); Tilt is TILT_PX canvas px/unit (+up); crop is a window in pre-zoom
S0 pixels that does not move the remaining pixels.

Usage: python -m scripts.fix_vtuber2d_9x16 [--apply]        (default: dry run, read-only)
       python -m scripts.fix_vtuber2d_9x16 verify            (exports stills + compares with an independent render)
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

from scripts.p2_9x16_build import DELAY, activate, items, protected, set_float, tc
from scripts.p2_9x16_common import check, find
from scripts.resolve_common import connect_resolve, preserved_state

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "exports" / "9x16-vtuber2d"
TARGET_ID = "f862003c-3025-467d-8c1f-3515deb61468"
TARGET_NAME = "คุยเรื่องโมเดล VTuber 2D บนมือถือ-vdo_9x16"
FPS = 30
SRC_W, SRC_H = 1280, 720
CW, CH = 1080, 1920
S0 = CW / SRC_W
TILT_PX = (SRC_H * S0) / CH  # 0.31640625 canvas px per Tilt unit

# Focus ranges of the 16:9 original (record frames, end exclusive). Everything from frame 240 on is full-screen avatar.
FULL_SEGMENTS = [  # (record start, record end exclusive, window key)
    (11, 204, "L"),
    (240, 863, "L"),
    (863, 1298, "C"),
]

# Avatar bbox measured on decoded source frames (pink-pixel mask, 0.5..99.5 percentile).
AV_STACK = (158.0, 500.0)    # Roblox scene / small avatar centre (x 86..238, y 388..612)
AV_SMALL = (162.0, 501.0)    # avatar-only scene, small avatar left (x 86..238, y 396..607)
AV_BIG = (526.0, 386.0)      # avatar-only scene, big avatar (x 348..724 + petals to ~310..735, y 128..645)


def place(centre_src, k, canvas_centre):
    """Properties that put source point `centre_src` at `canvas_centre` with k canvas px per source px."""
    sx, sy = centre_src
    cx, cy = canvas_centre
    pan = cx - (CW / 2 + (sx - SRC_W / 2) * k)
    tilt_px = (CH / 2 + (sy - SRC_H / 2) * k) - cy
    return {"ZoomX": k / S0, "ZoomY": k / S0, "Pan": pan, "Tilt": tilt_px / TILT_PX}


def window_crop(x0, y0, x1, y1):
    return {"CropLeft": x0 * S0, "CropRight": (SRC_W - x1) * S0, "CropTop": y0 * S0, "CropBottom": (SRC_H - y1) * S0}


def layouts():
    k_game = 960.0 / SRC_H  # 1.3333: whole source height fills the 960 px top panel
    v1 = place((505.0, 360.0), k_game, (540.0, 480.0))
    v1.update(window_crop(0, 0, SRC_W, SRC_H))
    k_av = 3.8
    w, h = CW / k_av, 960.0 / k_av
    v3 = place(AV_STACK, k_av, (540.0, 1440.0))
    v3.update(window_crop(AV_STACK[0] - w / 2, AV_STACK[1] - h / 2, AV_STACK[0] + w / 2, AV_STACK[1] + h / 2))
    k_l = 4.5
    full_l = place(AV_SMALL, k_l, (540.0, 1000.0))
    full_l.update(window_crop(0, 0, SRC_W, SRC_H))
    k_c = 2.6
    full_c = place(AV_BIG, k_c, (540.0, 960.0))
    full_c.update(window_crop(0, 0, SRC_W, SRC_H))
    return {"V1": v1, "V3": v3, "L": full_l, "C": full_c}


PROPS = ("ZoomX", "ZoomY", "Pan", "Tilt", "CropLeft", "CropRight", "CropTop", "CropBottom")


def apply_props(item, props):
    for k in ("CropLeft", "CropRight", "CropTop", "CropBottom"):
        set_float(item, k, props[k], 0.05)
    set_float(item, "ZoomX", props["ZoomX"], 0.002)
    set_float(item, "ZoomY", props["ZoomY"], 0.002)
    set_float(item, "Pan", props["Pan"], 0.5)
    set_float(item, "Tilt", props["Tilt"], 1.0)


def read_props(item):
    return {k: item.GetProperty(k) for k in PROPS}


def main():
    apply = "--apply" in sys.argv
    lay = layouts()
    print("LAYOUT", json.dumps(lay, indent=1))
    if not apply:
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    r = connect_resolve()
    check(r is not None, "Resolve unavailable")
    pm = r.GetProjectManager()
    p = pm.GetCurrentProject()
    check(p is not None and p.GetName() == "sakuyako-2026-09", "wrong project")
    check(not p.IsRenderingInProgress(), "render in progress")
    tl = find(p, TARGET_ID, TARGET_NAME)
    check(tl is not None, "target not found by id+name")
    check((tl.GetSetting("timelineResolutionWidth"), tl.GetSetting("timelineResolutionHeight")) == ("1080", "1920"), "raster")
    check(float(tl.GetSetting("timelineFrameRate")) == FPS, "fps")
    mp = p.GetMediaPool()
    log = {"before": {}, "steps": []}
    with preserved_state(r):
        r.OpenPage("edit")
        time.sleep(2)
        check(r.GetCurrentPage() == "edit", "not on Edit page")
        activate(p, tl)
        base = protected(tl)
        resume = tl.GetTrackCount("video") == 4 or not items(tl, "video", 2)
        check(tl.GetTrackCount("video") in (3, 4), "unexpected video track count")
        v1 = items(tl, "video", 1)
        v2 = items(tl, "video", 2)
        v3 = items(tl, "video", 3)
        check(len(v1) == 1 and len(v3) == 1 and len(v2) <= 1, "expected one item on V1/V3 and at most one on V2")
        a = v1[0]
        check((a.GetStart(), a.GetEnd()) == (0, 1298), "V1 range")
        if not resume:  # keep the pristine pre-fix values when resuming a partly applied run
            log["before"] = {"V1": read_props(v1[0]), "V2": read_props(v2[0]), "V3": read_props(v3[0])}
            (OUT / "before.json").write_text(json.dumps(log["before"], indent=1), encoding="utf-8")

        locks = {n: tl.GetIsTrackLocked("video", n) for n in (1, 2, 3)}
        log["locks_before"] = locks
        for n in (1, 2, 3):
            if locks[n]:
                check(tl.SetTrackLock("video", n, False), f"unlock V{n} failed")
        time.sleep(0.5)
        try:
            # 1. drop the stray full-frame copy on V2 (unlinked, video only)
            if v2:
                check(not (v2[0].GetLinkedItems() or []), "V2 item is linked; refusing to delete")
                check(tl.DeleteClips([v2[0]], False), "DeleteClips V2 failed")
                time.sleep(DELAY)
            check(items(tl, "video", 2) == [], "V2 not empty after delete")
            check(protected(tl) == base, "protected drift after V2 delete")

            # 2. V1 / V3 stacked layout
            v1 = items(tl, "video", 1)[0]
            v3 = items(tl, "video", 3)[0]
            apply_props(v1, lay["V1"])
            apply_props(v3, lay["V3"])
            log["steps"].append("v1_v3_props")

            # 3. V4 full-screen avatar items (video only, same source ranges)
            if tl.GetTrackCount("video") == 3:
                check(tl.AddTrack("video"), "AddTrack failed")
                time.sleep(DELAY)
            check(tl.GetTrackCount("video") == 4, "V4 not created")
            src0 = a.GetSourceStartFrame()
            mpi = a.GetMediaPoolItem()
            want = [(r0, r1, src0 + r0, src0 + r1) for r0, r1, _ in FULL_SEGMENTS]

            def sig4(x):
                return (x.GetStart(), x.GetEnd(), x.GetSourceStartFrame(), x.GetSourceEndFrame())

            bad = [x for x in items(tl, "video", 4) if sig4(x) not in want]
            if bad:  # leftovers of a previous partial run (V4 is our own new track)
                check(tl.DeleteClips(bad, False), "DeleteClips stale V4 failed")
                time.sleep(2 * DELAY)
            for rec0, rec1, key in FULL_SEGMENTS:
                w = (rec0, rec1, src0 + rec0, src0 + rec1)
                have = [x for x in items(tl, "video", 4) if sig4(x) == w]
                if not have:
                    info = {"mediaPoolItem": mpi, "startFrame": src0 + rec0, "endFrame": src0 + rec1,  # exclusive (measured)
                            "mediaType": 1, "trackIndex": 4, "recordFrame": rec0}
                    check(mp.AppendToTimeline([info]), f"append V4 {rec0}-{rec1} failed")
                    time.sleep(DELAY)
                    have = [x for x in items(tl, "video", 4) if sig4(x) == w]
                check(len(have) == 1, f"V4 item {w} missing after append: {[sig4(x) for x in items(tl, 'video', 4)]}")
                apply_props(have[0], lay[key])
                log["steps"].append(f"v4_{rec0}_{rec1}")
            check([sig4(x) for x in items(tl, "video", 4)] == want, "V4 final item list differs from plan")
            check(protected(tl) == base, "protected drift after V4")

            for n, nm in ((1, "Game Top"), (2, "REACTIONS"), (3, "VTuber Bottom"), (4, "VTuber Full")):
                tl.SetTrackName("video", n, nm)
                time.sleep(0.3)
            check(pm.SaveProject(), "SaveProject failed")
            time.sleep(DELAY)
            log["after"] = {f"V{n}": [(x.GetName(), x.GetStart(), x.GetEnd(), read_props(x)) for x in items(tl, "video", n)]
                            for n in (1, 2, 3, 4)}
            log["protected_equal"] = protected(tl) == base
            check(log["protected_equal"], "protected drift at end")
        finally:
            for n in (1, 2, 3):
                if locks[n]:
                    tl.SetTrackLock("video", n, True)
            time.sleep(0.5)
            log["locks_after"] = {n: tl.GetIsTrackLocked("video", n) for n in (1, 2, 3)}
    (OUT / "apply_log.json").write_text(json.dumps(log, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("APPLY_OK", log["steps"], "protected_equal", log["protected_equal"])
    return 0


# ---------------------------------------------------------------------------------------------------------------
# verify: independent expected render from decoded source frames vs Resolve still
# ---------------------------------------------------------------------------------------------------------------
SOURCE = r"G:/My Drive/Projects/Sakuyako-Cheris/sakuyako-2026-09/___BSgTZaT8-【LIVE】Sakuyako-Cheris #SakuyakoCheris.mp4"
SRC_START = 156482


def decode_source(frame, path):
    t = (SRC_START + frame) / FPS
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.4f}", "-i", SOURCE, "-frames:v", "1", str(path)], check=True)


def render_layer(canvas, src, props, region=None):
    """Paste a layer using the geometry model. region = (y0, y1) canvas rows the crop window may cover."""
    from PIL import Image
    k = props["ZoomX"] * S0
    x0 = props["CropLeft"] / S0
    x1 = SRC_W - props["CropRight"] / S0
    y0 = props["CropTop"] / S0
    y1 = SRC_H - props["CropBottom"] / S0
    win = src.crop((int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))))
    w, h = max(1, int(round(win.width * k))), max(1, int(round(win.height * k)))
    win = win.resize((w, h), Image.LANCZOS)
    left = CW / 2 + ((x0 + x1) / 2 - SRC_W / 2) * k + props["Pan"] - w / 2
    top = CH / 2 + ((y0 + y1) / 2 - SRC_H / 2) * k - props["Tilt"] * TILT_PX - h / 2
    canvas.paste(win, (int(round(left)), int(round(top))))
    return canvas


def full_at(frame):
    for a, b, key in FULL_SEGMENTS:
        if a <= frame < b:
            return key
    return None


def verify():
    import numpy as np
    from PIL import Image
    lay = layouts()
    r = connect_resolve()
    check(r is not None, "Resolve unavailable")
    pm = r.GetProjectManager()
    p = pm.GetCurrentProject()
    tl = find(p, TARGET_ID, TARGET_NAME)
    check(tl is not None, "target not found")
    d = OUT / "verify"
    d.mkdir(parents=True, exist_ok=True)
    frames = [5, 100, 220, 300, 500, 1000, 1200]
    results = []
    with preserved_state(r):
        r.OpenPage("edit")
        time.sleep(2)
        activate(p, tl)
        for f in frames:
            still = d / f"resolve_{f}.png"
            tl.SetCurrentTimecode(tc(f + 1, FPS))
            time.sleep(0.5)
            tl.SetCurrentTimecode(tc(f, FPS))
            time.sleep(1.0)
            ok = p.ExportCurrentFrameAsStill(str(still))
            time.sleep(0.5)
            check(ok and still.exists(), f"still export failed at {f}")
            src_png = d / f"src_{f}.png"
            decode_source(f, src_png)
            src = Image.open(src_png).convert("RGB")
            exp = Image.new("RGB", (CW, CH), (0, 0, 0))
            key = full_at(f)
            if key is None:
                render_layer(exp, src, lay["V1"])
                bottom = Image.new("RGB", (CW, CH), (0, 0, 0))
                render_layer(bottom, src, lay["V3"])
                exp.paste(bottom.crop((0, 960, CW, CH)), (0, 960))
            else:
                render_layer(exp, src, lay[key])
            exp.save(d / f"expected_{f}.png")
            got = Image.open(still).convert("RGB")
            if got.size != (CW, CH):
                got = got.resize((CW, CH), Image.LANCZOS)
            a = np.asarray(got).astype(int)
            b = np.asarray(exp).astype(int)
            diff = np.abs(a - b).sum(axis=2)
            bad = float((diff > 120).mean())
            black_rows_mid = float((a[480:1440].sum(axis=2) < 12).all(axis=1).mean())
            results.append({"frame": f, "layout": key or "stacked", "mean_abs_diff": round(float(np.abs(a - b).mean()), 2),
                            "frac_pixels_off": round(bad, 4), "black_row_frac_mid": round(black_rows_mid, 4)})
            print(results[-1], flush=True)
    (d / "verify.json").write_text(json.dumps(results, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(verify() if "verify" in sys.argv else main())
