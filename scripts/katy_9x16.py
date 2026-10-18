"""Build and lay out `<original>_9x16` for the Katy404 day-23 project (one 16:9 clip with the VTuber baked into the
bottom-right corner of the gameplay frame, black letterbox rows 0-40 / 1040-1080 in 1080p space).

MCP-GAP: davinci-resolve MCP failed to connect this session (CONNECTION_CLOSED); its duplicate/add_track actions also
trigger version-on-mutate copies (see p2_9x16_build). -> scripting API via scripts/resolve_common.

Structure (same proven order as p2_9x16_build): DuplicateTimeline -> raster 1080x1920 -> AddTrack("video", index 2) ->
append the V1 clip to V2.   V1 Game Top / V2 VTuber Bottom / V3 VTuber Zoom (Adjustment Clips, Fusion Transform) /
V4 REACTIONS (GIFs, drawn over the zoom so they are never scaled). Subtitles, audio, V1 ranges are asserted unchanged.

Usage: py -m scripts.katy_9x16 build [--apply] | layout | stills
"""
from __future__ import annotations

import sys
import time

from scripts.p2_9x16_build import RASTER, activate, items, protected, set_float, tc
from scripts.p2_9x16_common import check, find
from scripts.resolve_common import connect_resolve, preserved_state

ORIG_ID = "0145e0a9-6bdf-425c-a5fd-f0ef40532579"
CW, CH = 1080, 1920
SW, SH = 1920, 1080
FIT = CW / SW  # 0.5625: source fitted to canvas width
TU = SH * FIT / CH  # Tilt unit in canvas px (+up), for a 16:9 clip
SPLIT = 960
BAR = 40  # black letterbox rows top and bottom of the source (1080p space)
# Game panel: rows BAR..SH-BAR fill 960 px; source columns from GX0 (stops left of the baked-in avatar, hair x>=1470)
GS = SPLIT / (SH - 2 * BAR)
GX0 = 270.0  # right edge 1395: clears the avatar jacket (left edge ~1405 at row 1040)
# Avatar panel: scale AS, window x AX0..1920, bottom row SH-BAR sits on the canvas bottom
AS = 1.6
AX0 = SW - CW / AS
AWIN_H = SPLIT / AS
FOCUS_SIZE = 2.0

AVATAR_CX_SRC = 1620.0  # measured avatar centre x (1080p space)
FOCUS_SHIFT_X = -((AVATAR_CX_SRC - AX0) * AS - CW / 2) * FOCUS_SIZE / CW
GIF_MAX_W, GIF_MAX_H, GIF_BOTTOM = 540, 330, 420  # inside the game panel's sky area


def pan(cx):
    return cx - CW / 2


def tilt(cy):
    return -(cy - CH / 2) / TU


def game_params():
    zoom = GS / FIT
    cx = CW / 2 + (SW / 2 - (GX0 + CW / GS / 2)) * GS
    cy = SPLIT / 2 + (SH / 2 - SH / 2) * GS
    return {"ZoomX": zoom, "ZoomY": zoom, "Pan": pan(cx), "Tilt": tilt(cy),
            "CropTop": BAR * FIT, "CropBottom": BAR * FIT, "CropLeft": 0.0, "CropRight": 0.0}


def avatar_params():
    y0 = SH - BAR - AWIN_H
    cxs, cys = AX0 + CW / AS / 2, y0 + AWIN_H / 2
    cx = CW / 2 + (SW / 2 - cxs) * AS
    cy = SPLIT + SPLIT / 2 + (SH / 2 - cys) * AS
    return {"ZoomX": AS / FIT, "ZoomY": AS / FIT, "Pan": pan(cx), "Tilt": tilt(cy),
            "CropTop": y0 * FIT, "CropBottom": BAR * FIT, "CropLeft": 0.0, "CropRight": 0.0}


def gif_plan(w, h):
    s0 = min(CW / w, CH / h)
    fw, fh = w * s0, h * s0
    z = min(GIF_MAX_W / fw, GIF_MAX_H / fh, 1.0)
    cy = GIF_BOTTOM - fh * z / 2
    return {"Pan": 0.0, "Tilt": (CH / 2 - cy) / (fh / CH), "ZoomX": z, "ZoomY": z}


def session():
    r = connect_resolve()
    r = r[0] if isinstance(r, tuple) else r
    check(r is not None, "Resolve unavailable")
    pm = r.GetProjectManager()
    return r, pm, pm.GetCurrentProject()


def orig_tl(p):
    t = find(p, ORIG_ID, None)
    check(t is not None, "original timeline not found by id")
    return t, t.GetName() + "_9x16"


def build(apply):
    r, pm, p = session()
    orig, target = orig_tl(p)
    check(find(p, None, target) is None, "target exists: " + target)
    check(not p.IsRenderingInProgress(), "render in progress")
    check(orig.GetTrackName("video", 2) == "VTuber Zoom" and orig.GetTrackName("video", 3) == "REACTIONS", "layout")
    check(all(x.GetName() == "Adjustment Clip" for x in items(orig, "video", 2)), "V2 not only Adjustment Clips")
    mp = p.GetMediaPool()
    base = protected(orig)
    v1 = items(orig, "video", 1)
    check(len(v1) == 1, "expected a single V1 clip")
    sig = lambda t, n: [(x.GetName(), x.GetStart(), x.GetEnd()) for x in items(t, "video", n)]
    orig_v = [sig(orig, n) for n in (1, 2, 3)]
    print("PLAN", target, "focus", len(orig_v[1]), "gifs", len(orig_v[2]), flush=True)
    if not apply:
        return
    with preserved_state(r):
        r.OpenPage("edit")
        time.sleep(2)
        activate(p, orig)
        new = orig.DuplicateTimeline(target)
        check(new is not None and new.GetName() == target, "DuplicateTimeline failed")
        time.sleep(1.25)
        activate(p, new)
        check(protected(new) == base, "duplicate protected content differs")
        check([sig(new, n) for n in (1, 2, 3)] == orig_v, "duplicate video tracks differ")
        for k, v in RASTER:
            new.SetSetting(k, v)
            time.sleep(0.3)
        time.sleep(1.25)
        for k, v in RASTER:
            check(str(new.GetSetting(k)) == v, f"setting {k}={new.GetSetting(k)} want {v}")
        check(float(new.GetSetting("timelineFrameRate")) == 60.0, "fps changed")
        check(new.AddTrack("video", {"index": 2}), "AddTrack failed")
        time.sleep(1.25)
        check(new.GetTrackCount("video") == 4 and [sig(new, n) for n in (1, 2, 3, 4)] == [orig_v[0], [], orig_v[1], orig_v[2]],
              "track shift wrong")
        a = v1[0]
        info = {"mediaPoolItem": a.GetMediaPoolItem(), "startFrame": a.GetSourceStartFrame(),
                "endFrame": a.GetSourceEndFrame() + 1, "mediaType": 1, "trackIndex": 2, "recordFrame": a.GetStart()}
        check(mp.AppendToTimeline([info]), "append V2 failed")
        time.sleep(1.25)
        n2 = items(new, "video", 2)
        check(len(n2) == 1 and (n2[0].GetStart(), n2[0].GetEnd(), n2[0].GetSourceStartFrame(), n2[0].GetSourceEndFrame())
              == (a.GetStart(), a.GetEnd(), a.GetSourceStartFrame(), a.GetSourceEndFrame()), "V2 range mismatch")
        check([sig(new, n) for n in (3, 4)] == [orig_v[1], orig_v[2]], "V3/V4 drift")
        for n, nm in ((1, "Game Top"), (2, "VTuber Bottom"), (3, "VTuber Zoom"), (4, "REACTIONS")):
            new.SetTrackName("video", n, nm)
            time.sleep(0.3)
        check(protected(new) == base, "protected drift at end")
        check(pm.SaveProject(), "SaveProject failed")
    print("BUILD_OK", new.GetUniqueId(), {k: new.GetTrackCount(k) for k in ("video", "audio", "subtitle")})


def new_tl(p):
    o, target = orig_tl(p)
    t = find(p, None, target)
    check(t is not None, "9x16 timeline missing")
    return o, t


def focus_transform(item):
    comp = item.GetFusionCompByIndex(item.GetFusionCompCount())
    ts = [t for t in comp.GetToolList().values() if t.GetAttrs().get("TOOLS_RegID") == "Transform"]
    check(len(ts) == 1, "expected one Transform")
    return ts[0]


def layout():
    r, pm, p = session()
    o, t = new_tl(p)
    base = protected(o)
    with preserved_state(r):
        activate(p, t)
        g, a = game_params(), avatar_params()
        v1, v2 = items(t, "video", 1)[0], items(t, "video", 2)[0]
        for item, props in ((v1, g), (v2, a)):
            for k, v in props.items():
                set_float(item, k, v, 0.5 if k in ("Pan", "Tilt", "CropTop", "CropBottom") else 0.005)
        for x in items(t, "video", 3):
            tr = focus_transform(x)
            tr.SetInput("Size", FOCUS_SIZE)
            tr.SetInput("Pivot", {1: 0.5, 2: 0.0, 3: 0.0})
            tr.SetInput("Center", {1: 0.5 + FOCUS_SHIFT_X, 2: 0.5, 3: 0.0})
            time.sleep(0.4)
            rb = {k: tr.GetInput(k) for k in ("Size", "Center", "Pivot")}
            check(abs(float(rb["Size"]) - FOCUS_SIZE) < 1e-6 and abs(float(rb["Center"][1]) - (0.5 + FOCUS_SHIFT_X)) < 1e-6
                  and abs(float(rb["Pivot"][2])) < 1e-6, f"focus readback {rb}")
        for x in items(t, "video", 4):
            w, h = [int(v) for v in x.GetMediaPoolItem().GetClipProperty("Resolution").split("x")]
            for k, v in gif_plan(w, h).items():
                set_float(x, k, v)
                time.sleep(0.3)
        print("V1", {k: v1.GetProperty(k) for k in g}, "\nV2", {k: v2.GetProperty(k) for k in a})
        check(protected(o) == base, "ORIGINAL changed")
        check(pm.SaveProject(), "save failed")
    print("LAYOUT_OK")


def stills():
    r, pm, p = session()
    o, t = new_tl(p)
    out = sys.argv[2] if len(sys.argv) > 2 else "exports/9x16-katy"
    frames = [int(x) for x in sys.argv[3:]] or [300, 700, 1100, 1500]
    with preserved_state(r):
        activate(p, t)
        for f in frames:
            t.SetCurrentTimecode(tc(f + 1))
            time.sleep(0.5)
            t.SetCurrentTimecode(tc(f))
            time.sleep(1.0)
            print(f, p.ExportCurrentFrameAsStill(f"{out}/v_{f}.png"))


if __name__ == "__main__":
    cmd = sys.argv[1]
    {"build": lambda: build("--apply" in sys.argv), "layout": layout, "stills": stills}[cmd]()
