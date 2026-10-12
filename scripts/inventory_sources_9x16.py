"""Read-only: source file, resolution and source range of V1 for every original lacking `_9x16` (see inventory_remaining_9x16).

MCP-GAP: same as inventory_remaining_9x16 (non-active timeline reads) -> scripting API. Writes nothing.
Usage: python -m scripts.inventory_sources_9x16 out.json
"""
from __future__ import annotations

import json
import sys

from scripts.p2_9x16_build import items
from scripts.resolve_common import connect_resolve


def main():
    r = connect_resolve()
    p = r.GetProjectManager().GetCurrentProject()
    tls = [p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1)]
    names = {t.GetName() for t in tls}
    out = []
    for t in tls:
        n = t.GetName()
        if n.endswith("_9x16") or n + "_9x16" in names:
            continue
        a = items(t, "video", 1)[0]
        m = a.GetMediaPoolItem()
        out.append({"name": n, "id": t.GetUniqueId(), "file": m.GetClipProperty("File Path"),
                    "res": m.GetClipProperty("Resolution"), "src_fps": m.GetClipProperty("FPS"),
                    "src_start": a.GetSourceStartFrame(), "src_end": a.GetSourceEndFrame(),
                    "rec": (a.GetStart(), a.GetEnd()),
                    "focus": [(x.GetStart(), x.GetEnd()) for k in range(2, t.GetTrackCount("video") + 1)
                              for x in items(t, "video", k) if x.GetName() == "Adjustment Clip"]})
    open(sys.argv[1], "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1, default=str))
    print(len(out), "timelines;", len({o["file"] for o in out}), "files;", {o["res"] for o in out}, {o["src_fps"] for o in out})
    return 0


if __name__ == "__main__":
    sys.exit(main())
