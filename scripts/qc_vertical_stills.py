"""Read-only still sampler for the other `_9x16` timelines (QC only; restores project/timeline/playhead/page).

MCP-GAP: timeline_frame.capture hung on this build (render 'Ready for background render', ~4 min, left render format
changed) -> ExportCurrentFrameAsStill through scripts/resolve_common, same method as fix_vtuber2d_9x16.verify.
Also reports Fusion comp count + Transform inputs on Adjustment Clips (the structural QC cannot see them).

Usage: python -m scripts.qc_vertical_stills
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from scripts.p2_9x16_build import activate, items, tc
from scripts.p2_9x16_common import check, find
from scripts.resolve_common import connect_resolve, preserved_state

OUT = Path(__file__).resolve().parents[1] / "exports" / "9x16-vtuber2d" / "qc_others"
PLAN = {  # timeline -> (non-focus frame, focus frame, other focus frame)
    "คุยลงทุนจนแฮมสเตอร์เป็นประธานบริษัท-vdo_9x16": (5, 300, 700),
    "จบเกมด้วยผล Defeat 51–42-vdo_9x16": (100, 2000, 2700),
    "ปะทะกลางเลนก่อนตัวละครล้ม-vdo_9x16": (20, 300, 2200),
}


def fusion_info(it):
    out = []
    try:
        n = it.GetFusionCompCount() or 0
        for i in range(1, n + 1):
            comp = it.GetFusionCompByIndex(i)
            tools = comp.GetToolList(False) or {}
            tr = [t for t in tools.values() if t.GetAttrs().get("TOOLS_RegID") == "Transform"]
            out.append({"tools": len(tools), "transforms": [{k: t.GetInput(k) for k in ("Size", "Center", "Pivot")} for t in tr]})
    except Exception as exc:  # noqa: BLE001 - report, never raise in a QC
        out.append({"error": repr(exc)})
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    r = connect_resolve()
    check(r is not None, "Resolve unavailable")
    p = r.GetProjectManager().GetCurrentProject()
    report = {}
    with preserved_state(r):
        r.OpenPage("edit")
        time.sleep(2)
        for name, frames in PLAN.items():
            tl = find(p, name=name)
            check(tl is not None, f"missing {name}")
            activate(p, tl)
            report[name] = {"fusion": [fusion_info(x) for x in items(tl, "video", 4)][:3], "stills": []}
            for f in frames:
                path = OUT / f"{name[:12].strip()}_{f}.png".replace(" ", "_")
                tl.SetCurrentTimecode(tc(f + 1, 30))
                time.sleep(0.5)
                tl.SetCurrentTimecode(tc(f, 30))
                time.sleep(1.0)
                ok = p.ExportCurrentFrameAsStill(str(path))
                time.sleep(0.5)
                report[name]["stills"].append((f, str(path), bool(ok and path.exists())))
                print(name[:20], f, ok, flush=True)
    (OUT / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
