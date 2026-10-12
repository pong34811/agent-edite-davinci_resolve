"""Inspect #3 _9x16 in detail: V2/V3/V4 item names, ranges, source ranges, props."""
from __future__ import annotations

import json
import sys

from scripts.p2_9x16_build import items
from scripts.p2_9x16_common import find
from scripts.resolve_common import connect_resolve


def main():
    r = connect_resolve()
    assert r is not None
    p = r.GetProjectManager().GetCurrentProject()
    assert p is not None

    orig = find(p, name="คุยเรื่องโมเดล VTuber 2D บนมือถือ-vdo")
    new = find(p, name="คุยเรื่องโมเดล VTuber 2D บนมือถือ-vdo_9x16")
    assert orig is not None and new is not None

    out = {"original": {}, "new": {}}
    for n in range(1, orig.GetTrackCount("video") + 1):
        out["original"][f"V{n}"] = [
            {"name": x.GetName(), "start": x.GetStart(), "end": x.GetEnd(),
             "src_start": x.GetSourceStartFrame(), "src_end": x.GetSourceEndFrame(),
             "props": {k: x.GetProperty(k) for k in ("ZoomX", "ZoomY", "Pan", "Tilt", "CropTop", "CropBottom")}}
            for x in items(orig, "video", n)
        ]
    for n in range(1, new.GetTrackCount("video") + 1):
        out["new"][f"V{n}"] = [
            {"name": x.GetName(), "start": x.GetStart(), "end": x.GetEnd(),
             "src_start": x.GetSourceStartFrame(), "src_end": x.GetSourceEndFrame(),
             "props": {k: x.GetProperty(k) for k in ("ZoomX", "ZoomY", "Pan", "Tilt", "CropTop", "CropBottom")}}
            for x in items(new, "video", n)
        ]

    # Also check V3 fusion comp on each item
    out["new"]["V3_fusion"] = []
    for x in items(new, "video", 3):
        try:
            n = x.GetFusionCompCount()
            if n >= 1:
                comp = x.GetFusionCompByIndex(n)
                ts = [t for t in comp.GetToolList().values() if t.GetAttrs().get("TOOLS_RegID") == "Transform"]
                out["new"]["V3_fusion"].append({"name": x.GetName(), "comps": n, "transform": {k: ts[0].GetInput(k) for k in ("Size", "Pivot", "Center", "Edges")}} if ts else None)
            else:
                out["new"]["V3_fusion"].append({"name": x.GetName(), "comps": 0})
        except Exception as e:
            out["new"]["V3_fusion"].append({"name": x.GetName(), "error": str(e)})

    print(json.dumps(out, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    sys.exit(main())