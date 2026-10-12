"""Layout, calibration, apply and still-QC for the p2 9:16 pilot (`ชนะรอบแล้วบ่นเหนื่อย-strinova-vdo_9x16`).

MCP-GAP: timeline_item.set_property / timeline_item_fusion / project_settings.export_frame_as_still exist, but
calibration needs set -> export still -> numpy measure -> restore (props + track enables) in one process with a
`finally`, and Fusion Transform inputs (Size/Pivot/Center) are not settable through timeline_item_fusion
(add/load/import comp only) -> scripting API via scripts/resolve_common (connect_resolve, preserved_state).

Adapted from the archived layout9x16.py (caa1a64) — formula only; the per-stream anchors there are for other
projects. This stream (Strinova 005) has the facecam bottom-LEFT; anchors were read from clean ffmpeg source stills
(exports/9x16-pilot/source_*.png): eye y ~755 (frames 1650s/1690s: 757-760 / 750-752), eye-mid x 283..384
(the avatar leans), head/ear top y ~537, avatar/hair right edge <= ~645.

Usage:
  python -m scripts.p2_9x16_layout calibrate   # probes V1 only, restores everything
  python -m scripts.p2_9x16_layout apply       # sets V1/V2 transforms + V3 Fusion Transform, saves
  python -m scripts.p2_9x16_layout stills      # exports normal / gif / focus stills + numpy checks
"""
from __future__ import annotations

import json
import sys
import time

import numpy as np
from PIL import Image

from scripts.p2_9x16_common import OUT, TARGET_NAME, check, find, project_and_timeline
from scripts.p2_9x16_build import activate, items, set_float, tc
from scripts.resolve_common import preserved_state

TARGET_ID = "1d5238ed-414a-45b7-8458-7310de771be3"
CANVAS_W, CANVAS_H = 1080, 1920
SRC_W, SRC_H = 1920, 1080
FIT = min(CANVAS_W / SRC_W, CANVAS_H / SRC_H)  # 0.5625
SPLIT_Y = 960
# Calibrated on 21.1.0.17 (see calibrate()): Pan 1 canvas px/unit (+right), Tilt TILT_PX canvas px/unit (+up).
TILT_PX = (SRC_H * FIT) / CANVAS_H

# Game panel: whole source height (rows 0..1080) fills the 960 px panel; source x from GAME_X0 (right of the facecam)
GAME_SCALE = SPLIT_Y / SRC_H
GAME_X0 = 660.0
# VTuber panel: eyes (source y EYE_Y) land on canvas EYE_TARGET_Y; panel bottom = source bottom
EYE_Y, EYE_X = 755.0, 340.0
EYE_TARGET_Y = 1456.0
AVATAR_SCALE = (CANVAS_H - EYE_TARGET_Y) / (SRC_H - EYE_Y)
# V3 focus (Fusion Transform on the Adjustment Clip): scale the lower panel to fill the canvas.
# Measured on 21.1.0.17 (focus still): Size scales about Pivot WITHOUT moving it, so Center (0.5, 0.5) left the
# lower-panel centre at y=0.25 (game HUD on top, chin cut). Center y = 0.5 + (0.5 - 0.25) puts it at the canvas centre.
FOCUS = {"Size": 2.05, "Pivot": {1: 0.5, 2: 0.25, 3: 0.0}, "Center": {1: 0.5, 2: 0.75, 3: 0.0}}


def focus_params(pivot_x=0.5, pivot_y=0.25, size=2.05):
    """Fusion Transform for the V3 focus clip: Size scales about Pivot without moving it, so Center = Pivot shifted by
    (0.5 - Pivot) puts the pivot point at the canvas centre (Fusion coords, y up). Pilot = FOCUS (0.5, 0.25)."""
    return {"Size": size, "Pivot": {1: pivot_x, 2: pivot_y, 3: 0.0},
            "Center": {1: 0.5 + (0.5 - pivot_x), 2: 0.5 + (0.5 - pivot_y), 3: 0.0}}


# Per-stream anchors, keyed by a substring of the V1 source clip name. Each measured from clean ffmpeg source stills
# (exports/9x16-pilot/source_*.png, exports/9x16-batch/sources/*). A stream not listed here is NOT converted.
#   eye_y / eye_x : source px of the eye line / eye midpoint;  game_x0: first source column of the game panel (right
#   of the facecam, so the panel excludes it);  focus: Fusion pivot (lower-panel centre in Fusion coords).
STREAMS = {
    # Pilot. Strinova 005: facecam bottom-left, eye y ~755, eye-mid x 283..384, ear top ~537-584, hair right <= ~645.
    "strinova - 005": {"eye_y": EYE_Y, "eye_x": EYE_X, "game_x0": GAME_X0, "focus": FOCUS, "head_top_src": 575,
                       "evidence": "exports/9x16-pilot/source_1615s|1650s|1690s.png; batch sources 01-07,44 hair-mask "
                                   "top 574-584, right edge 575-641"},
    # Strinova 006: same overlay layout as 005 (measured, not assumed): eye y ~745-755 (08_246s, 11_5695s grids),
    # ear top 572-586, hair x 26..641 (eye-mid 262..345, lean), facecam bottom-left, donation bar y ~1010-1050.
    "strinova - 006": {"eye_y": 755.0, "eye_x": 340.0, "game_x0": 660.0, "focus": FOCUS, "head_top_src": 576,
                       "evidence": "exports/9x16-batch/sources/08_246s_grid.png, 11_5695s_grid.png; hair-mask "
                                   "top 572-586, right edge 503-593"},
    # Minecraft Server Dreamlight 003 (p2 idx 16-22, one file): facecam bottom-left like Strinova but eyes ~13 px lower:
    # eye y ~770 (gridded 17 @140115, 16 @89428), eye-mid x 380..400, ear tips ~530, hair x 40..649 (16 frames over
    # idx 16-19) -> game_x0 660 still excludes it. Hotbar hearts (x~690-800, y~965-990) bleed into the lower panel's
    # right edge, as Strinova HUD does.
    "Dreamlight - 003": {"eye_y": 768.0, "eye_x": 390.0, "game_x0": 660.0, "focus": FOCUS, "head_top_src": 530,
                         "evidence": "exports/9x16-batch/sources/mc_grid_16.png, mc_grid_17.png; range sheets "
                                     "contact_16..22_range.png; hair-mask top 572-586 (one 503)"},
    # Becastled 001 (p2 idx 24-29 game layout; idx 23 is a chat scene -> p2_9x16_charscene): facecam bottom-left,
    # eye y ~765 (gridded 25 @180817, 27 @444... ), eye-mid x 255..280, ear tips ~535, hair x 12..623 -> game_x0 660.
    # Game hotkey toolbar at source x 10-40, y 760-1030 sits inside the facecam panel (as in the 16:9 source).
    "Becastled - 001": {"eye_y": 765.0, "eye_x": 270.0, "game_x0": 660.0, "focus": FOCUS, "head_top_src": 535,
                        "evidence": "exports/9x16-batch/sources/bc1_grid_25.png, bc1_grid_27.png; range sheets "
                                    "contact_23_26/27_30_range.png; hair-mask top 570-582"},
    # Becastled 002 (p2 idx 30-35; 30 fps source on 60 fps timelines; idx 30 is a room/chat scene -> charscene):
    # facecam bottom-left, eye y ~765, eye-mid x 300..380, ear tips ~535, hair x 24..609 -> game_x0 660.
    "Becastled - 002": {"eye_y": 765.0, "eye_x": 335.0, "game_x0": 660.0, "focus": FOCUS, "head_top_src": 535,
                        "evidence": "exports/9x16-batch/sources/bc2_grid_32.png; range sheet contact_31_34_range.png; "
                                    "hair-mask top 569-578"},
    # Becastled 003 (p2 idx 37-43 game layout; idx 36 is a room scene -> charscene): facecam bottom-left, eye y ~760,
        # eye-mid x 250..300, ear tips ~530, hair x 12..617 -> game_x0 660.
        "Becastled - 003": {"eye_y": 760.0, "eye_x": 270.0, "game_x0": 660.0, "focus": FOCUS, "head_top_src": 530,
                            "evidence": "exports/9x16-batch/sources/bc3_grid_40.png; range sheets contact_36_39/40_43_range.png;"
                                        " hair-mask top 569-578"},
        # Sakuyako 2026-09 (sakuyako-2026-09 project): facecam bottom-left, user-approved defaults
        # (eye_y=755, eye_x=340, game_x0=660) from strinova - 005. V3 must be 7 Adjustment Clips matching
        # original V2 ranges (11-204, 240-300, 335-408, 458-556, 609-669, 732-932, 1013-1289).
        "คุยเรื่องโมเดล VTuber 2D บนมือถือ-vdo": {
            "eye_y": 755.0, "eye_x": 340.0, "game_x0": 660.0, "focus": FOCUS, "head_top_src": 575,
            "evidence": "user-approved defaults from strinova - 005 (facecam bottom-left); V3 must be "
                        "Adjustment Clips matching original V2 ranges"
        },
    }


def stream_for(clip_name):
    hits = [k for k in STREAMS if k in clip_name]
    return (hits[0], STREAMS[hits[0]]) if len(hits) == 1 else (None, None)


def _pan(cx):
    return cx - CANVAS_W / 2


def _tilt(cy):
    return -(cy - CANVAS_H / 2) / TILT_PX


def game_params(game_x0=GAME_X0):
    zoom = GAME_SCALE / FIT
    cx = (SRC_W / 2 - game_x0) * GAME_SCALE
    cy = (SRC_H / 2) * GAME_SCALE
    return {"ZoomX": zoom, "ZoomY": zoom, "Pan": _pan(cx), "Tilt": _tilt(cy), "CropTop": 0.0, "CropBottom": 0.0}


def avatar_scale(eye_y=EYE_Y):
    """Lower-panel scale that lands source eye line eye_y on EYE_TARGET_Y (pilot: AVATAR_SCALE)."""
    return (CANVAS_H - EYE_TARGET_Y) / (SRC_H - eye_y)


def stream_params(anchor):
    """(V1 game props, V2 avatar props, avatar meta, Fusion focus inputs) for one stream's anchors."""
    a, meta = avatar_params(avatar_scale(anchor["eye_y"]), anchor["eye_x"])
    return game_params(anchor["game_x0"]), a, meta, anchor["focus"]


def avatar_params(scale=AVATAR_SCALE, cx_src=EYE_X):
    zoom = scale / FIT
    pw, ph = CANVAS_W / scale, SPLIT_Y / scale
    y0 = SRC_H - ph
    x0 = min(max(cx_src - pw / 2, 0.0), SRC_W - pw)
    cxs, cys = x0 + pw / 2, y0 + ph / 2
    cx = CANVAS_W / 2 + (SRC_W / 2 - cxs) * scale
    cy = SPLIT_Y + SPLIT_Y / 2 + (SRC_H / 2 - cys) * scale
    return {"ZoomX": zoom, "ZoomY": zoom, "Pan": _pan(cx), "Tilt": _tilt(cy), "CropTop": y0 * FIT, "CropBottom": 0.0}, \
        {"x0": x0, "y0": y0, "scale": scale}


def bbox(path, thr=16):
    a = np.array(Image.open(path).convert("RGB")).max(axis=2)
    rows = np.where((a > thr).mean(axis=1) > 0.02)[0]
    cols = np.where((a > thr).mean(axis=0) > 0.02)[0]
    return {"size": list(a.shape[::-1]), "y": [int(rows.min()), int(rows.max())] if len(rows) else None,
            "x": [int(cols.min()), int(cols.max())] if len(cols) else None}


def export(p, tl, frame, path):
    tl.SetCurrentTimecode(tc(frame + 1))
    time.sleep(0.5)
    tl.SetCurrentTimecode(tc(frame))
    time.sleep(1.0)
    ok = p.ExportCurrentFrameAsStill(str(path))
    time.sleep(0.5)
    check(ok and path.exists(), f"still export failed {path}")
    return path


def target(p):
    t = find(p, TARGET_ID, TARGET_NAME)
    check(t is not None, "target not found by id+name")
    check(t.GetSetting("timelineResolutionWidth") == "1080" and t.GetSetting("timelineResolutionHeight") == "1920", "raster")
    return t


PROPS = ("ZoomX", "ZoomY", "Pan", "Tilt", "CropTop", "CropBottom", "CropLeft", "CropRight")


def calibrate():
    r, pm, p, _ = project_and_timeline()
    d = OUT / "calibration"
    d.mkdir(parents=True, exist_ok=True)
    res = {}
    with preserved_state(r):
        tl = target(p)
        activate(p, tl)
        en = {i: tl.GetIsTrackEnabled("video", i) for i in range(1, 5)}
        v1 = items(tl, "video", 1)[0]
        saved = {k: v1.GetProperty(k) for k in PROPS}
        frame = 600
        probes = [("A_zoom1_pan100_tilt100", {"ZoomX": 1.0, "ZoomY": 1.0, "Pan": 100.0, "Tilt": 100.0}),
                  ("B_zoom2_croptop100", {"ZoomX": 2.0, "ZoomY": 2.0, "CropTop": 100.0}),
                  ("C_zoom2_tilt-200", {"ZoomX": 2.0, "ZoomY": 2.0, "Tilt": -200.0})]
        try:
            for i in (2, 3, 4):
                tl.SetTrackEnable("video", i, False)
                time.sleep(1.25)
            for name, props in probes:
                for k, v in saved.items():
                    set_float(v1, k, v, 0.5)
                for k, v in props.items():
                    set_float(v1, k, v, 0.5 if k in ("Pan", "Tilt", "CropTop") else 0.005)
                res[name] = {"props": props, "bbox": bbox(export(p, tl, frame, d / f"{name}.png"))}
                print(name, res[name], flush=True)
        finally:
            for k, v in saved.items():
                set_float(v1, k, v, 0.5)
            for i, v in en.items():
                tl.SetTrackEnable("video", i, v)
                time.sleep(1.25)
            res["restored_props"] = {k: v1.GetProperty(k) for k in PROPS} == saved
            res["restored_enables"] = {i: tl.GetIsTrackEnabled("video", i) for i in range(1, 5)} == en
    (d / "calibration.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print("RESTORED", res["restored_props"], res["restored_enables"])


def fusion_transform(item):
    n = item.GetFusionCompCount()
    check(n >= 1, "no Fusion comp on focus clip")
    comp = item.GetFusionCompByIndex(n)  # the LAST comp is the one rendered
    ts = [t for t in comp.GetToolList().values() if t.GetAttrs().get("TOOLS_RegID") == "Transform"]
    check(len(ts) == 1, f"expected one Transform, got {len(ts)}")
    return ts[0]


def apply():
    r, pm, p, _ = project_and_timeline()
    out = {}
    with preserved_state(r):
        tl = target(p)
        activate(p, tl)
        g = game_params()
        a, meta = avatar_params()
        out["game"], out["avatar"], out["avatar_meta"] = g, a, meta
        v1, v2 = items(tl, "video", 1)[0], items(tl, "video", 2)[0]
        for item, props in ((v1, g), (v2, a)):
            for k, v in props.items():
                set_float(item, k, v, 0.5 if k in ("Pan", "Tilt", "CropTop", "CropBottom") else 0.005)
        out["v1_readback"] = {k: v1.GetProperty(k) for k in PROPS}
        out["v2_readback"] = {k: v2.GetProperty(k) for k in PROPS}
        foc = items(tl, "video", 3)
        check(len(foc) == 1 and foc[0].GetName() == "Adjustment Clip", "V3 focus clip missing")
        t = fusion_transform(foc[0])
        out["focus_before"] = {k: t.GetInput(k) for k in ("Size", "Center", "Pivot", "Edges")}
        for k in ("Size", "Pivot", "Center"):
            t.SetInput(k, FOCUS[k])
            time.sleep(0.5)
        time.sleep(1.25)
        rb = {k: t.GetInput(k) for k in ("Size", "Center", "Pivot", "Edges")}
        out["focus_readback"] = rb
        check(abs(float(rb["Size"]) - FOCUS["Size"]) < 1e-6 and
              all(abs(float(rb[k][i]) - FOCUS[k][i]) < 1e-6 for k in ("Pivot", "Center") for i in (1, 2)), f"focus readback {rb}")
        check(pm.SaveProject(), "save failed")
        time.sleep(1.25)
    (OUT / "apply_log.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(json.dumps(out, indent=1, default=str))


def pixel_check(path):
    a = np.array(Image.open(path).convert("RGB"))
    g = a.max(axis=2)
    dark = g.max(axis=1) < 16
    return {"size": [a.shape[1], a.shape[0]], "dark_rows": int(dark.sum()), "top_dark_rows": int(dark[:960].sum()),
            "bottom_dark_rows": int(dark[1300:].sum()), "dark_cols": int((g.max(axis=0) < 16).sum())}


def stills():
    r, pm, p, _ = project_and_timeline()
    d = OUT
    res = {}
    with preserved_state(r):
        tl = target(p)
        activate(p, tl)
        v3 = items(tl, "video", 3)
        v4 = items(tl, "video", 4)
        busy = [(i.GetStart() - 30, i.GetEnd() + 30) for i in v3 + v4]
        normal = next(f for f in range(600, tl.GetEndFrame(), 60) if not any(a <= f <= b for a, b in busy))
        frames = [("normal", normal), ("gif", (v4[0].GetStart() + v4[0].GetEnd()) // 2),
                  ("gif2", (v4[1].GetStart() + v4[1].GetEnd()) // 2), ("focus", (v3[0].GetStart() + v3[0].GetEnd()) // 2)]
        for label, f in frames:
            path = export(p, tl, f, d / f"{label}_{f}.png")
            res[label] = {"path": str(path), "frame": f, **pixel_check(path)}
            print(label, res[label], flush=True)
    (d / "stills_check.json").write_text(json.dumps(res, indent=1), encoding="utf-8")


if __name__ == "__main__":
    {"calibrate": calibrate, "apply": apply, "stills": stills}[sys.argv[1]]()
