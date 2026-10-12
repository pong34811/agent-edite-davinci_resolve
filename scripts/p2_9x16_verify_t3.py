"""Verify `_9x16` timeline #3 (`คุยเรื่องโมเดล VTuber 2D บนมือถือ`) against its original.

Checks: raster, FPS, protected content (subtitles/audio/V1), track count, layout formulas.
Does NOT export stills or compute pixel checks — that is a separate step after structural pass.
"""
from __future__ import annotations

import json
import sys

from scripts.p2_9x16_build import RASTER, items, protected
from scripts.p2_9x16_common import diff, find, signature
from scripts.p2_9x16_layout import (
    STREAMS, avatar_params, focus_params, fusion_transform, game_params, stream_for, stream_params,
)
from scripts.resolve_common import connect_resolve


ORIG_NAME = "คุยเรื่องโมเดล VTuber 2D บนมือถือ-vdo"
TARGET_NAME = ORIG_NAME + "_9x16"


def main():
    r = connect_resolve()
    assert r is not None, "Resolve unavailable"
    pm = r.GetProjectManager()
    p = pm.GetCurrentProject()
    assert p is not None, "no current project"

    orig = find(p, name=ORIG_NAME)
    new = find(p, name=TARGET_NAME)
    assert orig is not None, f"original not found: {ORIG_NAME}"
    assert new is not None, f"target not found: {TARGET_NAME}"

    res = {}
    res["orig_name"], res["new_name"] = orig.GetName(), new.GetName()

    # --- Protected content ---
    po, pn = protected(orig), protected(new)
    res["subtitles_equal"] = po["sub"] == pn["sub"]
    res["subtitle_count"] = [len(po["sub"]), len(pn["sub"])]
    res["audio_equal"] = po["audio"] == pn["audio"]
    res["audio_count"] = [len(po["audio"]), len(pn["audio"])]
    res["v1_equal"] = po["v1"] == pn["v1"]
    res["range_fps"] = [po["range"], pn["range"], po["fps"], pn["fps"]]
    res["tracks"] = {k: new.GetTrackCount(k) for k in ("video", "audio", "subtitle")}

    # --- Raster ---
    res["settings"] = {k: new.GetSetting(k) for k, _ in RASTER}
    res["settings_ok"] = all(str(res["settings"][k]) == v for k, v in RASTER)

    # --- V3 focus (Adjustment Clip) vs original V2 ---
    res["focus_ranges"] = [
        [(x.GetName(), x.GetStart(), x.GetEnd()) for x in items(orig, "video", 2)],
        [(x.GetName(), x.GetStart(), x.GetEnd()) for x in items(new, "video", 3)],
    ]
    res["focus_equal"] = res["focus_ranges"][0] == res["focus_ranges"][1]

    # --- V4 GIFs vs original V3 ---
    g = lambda tl, n: [(x.GetName(), x.GetStart(), x.GetEnd(), x.GetSourceStartFrame(), x.GetSourceEndFrame())
                      for x in items(tl, "video", n)]
    res["gif_equal"] = g(orig, 3) == g(new, 4)

    # --- V2 panel range vs original V1 ---
    res["v2_equal_v1_range"] = g(new, 2) == g(orig, 1)

    # --- Transform checks: V1 game, V2 avatar, V3 Fusion focus ---
    stream_key, anchor = stream_for(orig.GetName())
    if stream_key is None:
        res["layout"] = {"error": f"no layout anchor for '{orig.GetName()}'"}
    else:
        game_p, av_p, _meta, focus_p = stream_params(anchor)
        v1 = items(new, "video", 1)[0]
        v2 = items(new, "video", 2)[0]
        v1_readback = {k: v1.GetProperty(k) for k in ("ZoomX", "ZoomY", "Pan", "Tilt", "CropTop", "CropBottom")}
        v2_readback = {k: v2.GetProperty(k) for k in ("ZoomX", "ZoomY", "Pan", "Tilt", "CropTop", "CropBottom")}
        foc = items(new, "video", 3)
        assert len(foc) == 1 and foc[0].GetName() == "Adjustment Clip", "V3 focus clip missing"
        t = fusion_transform(foc[0])
        focus_rb = {k: t.GetInput(k) for k in ("Size", "Pivot", "Center", "Edges")}

        # Compare floats within tolerance
        def close(a, b, tol=0.01):
            return abs(float(a) - float(b)) <= tol

        res["layout"] = {
            "stream": stream_key,
            "v1_expected": game_p,
            "v1_readback": v1_readback,
            "v1_ok": all(close(v1_readback[k], game_p[k]) for k in game_p),
            "v2_expected": av_p,
            "v2_readback": v2_readback,
            "v2_ok": all(close(v2_readback[k], av_p[k]) for k in av_p),
            "focus_expected": focus_p,
            "focus_readback": focus_rb,
            "focus_ok": (
                abs(float(focus_rb["Size"]) - float(focus_p["Size"])) < 1e-6 and
                all(abs(float(focus_rb[k][i]) - float(focus_p[k][i])) < 1e-6
                    for k in ("Pivot", "Center") for i in (1, 2))
            ),
        }

    # --- Offline check ---
    off = []
    for n in range(1, new.GetTrackCount("video") + 1):
        for x in items(new, "video", n):
            m = x.GetMediaPoolItem()
            if m is not None and str(m.GetClipProperty("Online Status") or "Online").lower().startswith("off"):
                off.append(x.GetName())
    res["offline"] = off

    res["ok"] = (
        not res["subtitles_equal"] is False
        and res["subtitles_equal"]
        and res["audio_equal"]
        and res["v1_equal"]
        and po["range"] == pn["range"]
        and float(po["fps"]) == float(pn["fps"])
        and res["settings_ok"]
        and res["focus_equal"]
        and res["gif_equal"]
        and res["v2_equal_v1_range"]
        and not off
        and res["tracks"] == {"video": 4, "audio": 3, "subtitle": 1}
        and res.get("layout", {}).get("v1_ok", False)
        and res.get("layout", {}).get("v2_ok", False)
        and res.get("layout", {}).get("focus_ok", False)
    )

    print(json.dumps(res, ensure_ascii=False, indent=1, default=str))
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())