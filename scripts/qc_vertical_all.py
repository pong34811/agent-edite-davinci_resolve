"""Read-only QC of every `<name>_9x16` timeline against its 16:9 original (project sakuyako-2026-09).

MCP-GAP: davinci-resolve MCP reads only the CURRENT timeline; comparing 4 vertical timelines with their originals
(raster, fps, subtitles, audio, source ranges, track layout, transforms, locks) needs non-active reads in one process
-> scripting API through scripts/resolve_common. Nothing is written to the project.

Usage: python -m scripts.qc_vertical_all [--json out.json]
"""
from __future__ import annotations

import json
import sys

from scripts.p2_9x16_build import items
from scripts.p2_9x16_common import find
from scripts.resolve_common import connect_resolve

SUFFIX = "_9x16"
XF = ("Pan", "Tilt", "ZoomX", "ZoomY", "CropLeft", "CropRight", "CropTop", "CropBottom")


def track_items(tl, kind):
    return {n: items(tl, kind, n) for n in range(1, tl.GetTrackCount(kind) + 1)}


def sig(x):
    return (x.GetName(), x.GetStart(), x.GetEnd(), x.GetSourceStartFrame() if x.GetMediaPoolItem() else None)


def qc(p, v):
    base = v.GetName()[: -len(SUFFIX)]
    o = find(p, name=base)
    res = {"timeline": v.GetName(), "original_found": o is not None, "fail": [], "warn": [], "info": {}}
    if o is None:
        res["fail"].append("original not found")
        res["verdict"] = "FAIL"
        return res
    g = lambda t, k: t.GetSetting(k)
    res["info"]["raster"] = (g(v, "timelineResolutionWidth"), g(v, "timelineResolutionHeight"))
    res["info"]["fps"] = (g(o, "timelineFrameRate"), g(v, "timelineFrameRate"))
    if res["info"]["raster"] != ("1080", "1920"):
        res["fail"].append(f"raster {res['info']['raster']}")
    if str(res["info"]["fps"][0]) != str(res["info"]["fps"][1]):
        res["fail"].append(f"fps {res['info']['fps']}")
    if (o.GetStartFrame(), o.GetEndFrame()) != (v.GetStartFrame(), v.GetEndFrame()):
        res["fail"].append(f"range {(o.GetStartFrame(), o.GetEndFrame())} vs {(v.GetStartFrame(), v.GetEndFrame())}")
    for kind in ("subtitle", "audio"):
        so, sv = track_items(o, kind), track_items(v, kind)
        if {n: [sig(x) for x in xs] for n, xs in so.items()} != {n: [sig(x) for x in xs] for n, xs in sv.items()}:
            res["fail"].append(f"{kind} differs from original")
        res["info"][kind] = {n: len(xs) for n, xs in sv.items()}
    o1 = [(x.GetStart(), x.GetEnd(), x.GetSourceStartFrame()) for x in items(o, "video", 1)]
    v1 = [(x.GetStart(), x.GetEnd(), x.GetSourceStartFrame()) for x in items(v, "video", 1)]
    if o1 != v1:
        res["warn"].append(f"V1 ranges differ (orig {len(o1)} items, vertical {len(v1)})")
    res["info"]["orig_video_tracks"] = {n: (o.GetTrackName("video", n), len(xs)) for n, xs in track_items(o, "video").items()}
    vt = {}
    for n, xs in track_items(v, "video").items():
        vt[n] = {"name": v.GetTrackName("video", n), "locked": v.GetIsTrackLocked("video", n),
                 "items": [{"name": x.GetName()[:24], "start": x.GetStart(), "end": x.GetEnd(),
                            "xf": {k: round(float(x.GetProperty(k)), 2) for k in XF if x.GetProperty(k) is not None}}
                           for x in xs]}
    res["info"]["vertical_video_tracks"] = vt
    for kind in ("video", "audio"):
        for n, xs in track_items(v, kind).items():
            for x in xs:
                m = x.GetMediaPoolItem()
                if m is not None and not m.GetClipProperty("File Path"):
                    res["fail"].append(f"{kind} V/A{n} item without file path: {x.GetName()}")
    names = {n: d["name"] for n, d in vt.items()}
    if names.get(1) != "Game Top":
        res["warn"].append(f"V1 track name {names.get(1)!r}")
    for n, d in vt.items():
        for it in d["items"]:
            xf = it["xf"]
            if n != 1 and it["name"] != "Adjustment Clip" and xf.get("ZoomX") == 1.0 and xf.get("Pan") == 0.0 \
                    and xf.get("Tilt") == 0.0 and not any(xf.get(k) for k in XF[4:]):
                res["fail"].append(f"V{n} '{d['name']}': untransformed full-frame clip {it['start']}-{it['end']}")
    orig_focus = [(x.GetStart(), x.GetEnd()) for xs in track_items(o, "video").values() for x in xs if x.GetName() == "Adjustment Clip"]
    vert_focus = [(it["start"], it["end"]) for d in vt.values() for it in d["items"] if it["name"] == "Adjustment Clip"]
    res["info"]["orig_focus_ranges"] = orig_focus
    res["info"]["vertical_adjustment_ranges"] = vert_focus
    if orig_focus and not vert_focus and len(vt) < 4:
        res["warn"].append("original has focus ranges; vertical has no Adjustment/full-screen track")
    res["verdict"] = "FAIL" if res["fail"] else ("WARN" if res["warn"] else "PASS")
    return res


def main():
    r = connect_resolve()
    p = r.GetProjectManager().GetCurrentProject()
    out = []
    for i in range(1, p.GetTimelineCount() + 1):
        t = p.GetTimelineByIndex(i)
        if t.GetName().endswith(SUFFIX):
            out.append(qc(p, t))
    if "--json" in sys.argv:
        open(sys.argv[sys.argv.index("--json") + 1], "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1, default=str))
    for d in out:
        print(d["verdict"], d["timeline"], "| fail:", d["fail"], "| warn:", d["warn"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
