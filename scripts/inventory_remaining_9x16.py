"""Read-only inventory of the 16:9 originals that still lack a `_9x16` sibling (project sakuyako-2026-09).

MCP-GAP: davinci-resolve MCP reads only the current timeline; 31 timelines would need 31 set_current switches ->
scripting API (non-active reads) through scripts/resolve_common. Writes nothing.

Usage: python -m scripts.inventory_remaining_9x16 [out.json]
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict

from scripts.p2_9x16_build import items
from scripts.resolve_common import connect_resolve


def main():
    r = connect_resolve()
    p = r.GetProjectManager().GetCurrentProject()
    tls = [p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1)]
    names = {t.GetName() for t in tls}
    rows = []
    for t in tls:
        n = t.GetName()
        if n.endswith("_9x16") or n + "_9x16" in names:
            continue
        v = {}
        for k in range(1, t.GetTrackCount("video") + 1):
            xs = items(t, "video", k)
            v[k] = {"name": t.GetTrackName("video", k), "n": len(xs),
                    "adj": sum(1 for x in xs if x.GetName() == "Adjustment Clip"),
                    "sources": sorted({x.GetName()[:14] for x in xs if x.GetName() != "Adjustment Clip"})}
        v1 = items(t, "video", 1)
        rows.append({
            "name": n, "id": t.GetUniqueId(), "fps": t.GetSetting("timelineFrameRate"),
            "raster": (t.GetSetting("timelineResolutionWidth"), t.GetSetting("timelineResolutionHeight")),
            "frames": (t.GetStartFrame(), t.GetEndFrame()), "video": v,
            "v1_src": v1[0].GetName()[:14] if v1 else None, "v1_items": len(v1),
            "audio": {k: len(items(t, "audio", k)) for k in range(1, t.GetTrackCount("audio") + 1)},
            "subs": {k: len(items(t, "subtitle", k)) for k in range(1, t.GetTrackCount("subtitle") + 1)},
        })
    groups = defaultdict(list)
    for x in rows:
        groups[x["v1_src"]].append(x["name"])
    print("remaining", len(rows))
    for s, ns in groups.items():
        print(s, len(ns))
    odd = [x["name"] for x in rows if str(x["fps"]) != "30.0" or x["raster"] != ("1920", "1080") or x["v1_items"] != 1]
    print("odd (fps!=30 / raster!=1920x1080 / v1_items!=1):", odd)
    if len(sys.argv) > 1:
        open(sys.argv[1], "w", encoding="utf-8").write(json.dumps(rows, ensure_ascii=False, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
