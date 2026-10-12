"""Remove the black band at the bottom of the VTuber-Focus frames in the 3 Mobile-Legends `_9x16` timelines.

MCP-GAP: timeline_item_fusion only adds/loads/imports comps; Transform inputs (Size/Center/Pivot) are not settable
through it -> scripting API (Fusion tool SetInput) through scripts/resolve_common.

Cause (measured, 9.4% = 180 px black at the bottom of every focus still): the Adjustment Clip Fusion Transform has
Size 2.0, Pivot (0.5, 0.5), Center (0.296, 1.094). A canvas row u shows composite row 0.5 + (u - Center_y)/Size, so the
composite bottom (0) lands at output row Center_y - Size*Pivot_y = 0.094. Setting Center_y = Size*Pivot_y puts the
composite bottom exactly on the frame bottom (no band) and keeps the horizontal framing (Center_x unchanged).

Pass 2 (measured on stills): the avatar panel is canvas rows 1056..1919 (864 px; rows 1047..1055 are a black seam, 0..8 a
black top edge), NOT the lower 960 px, so a Size 2.0 window also pulled in 90 px of game HUD. The focus window is now the
avatar panel only: rows PANEL_TOP..1920 -> Size = 1920 / (1920 - PANEL_TOP), bottom-aligned (Center_y = Size * Pivot_y),
horizontal window centre kept at the original author's X0 = 0.5 + (0.5 - 0.296) / 2 = 0.602.

Usage: python -m scripts.fix_focus_black_band [--apply]      (default: dry run, read-only)
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from scripts.p2_9x16_build import activate, items
from scripts.p2_9x16_common import check, find
from scripts.p2_9x16_layout import fusion_transform
from scripts.resolve_common import connect_resolve, preserved_state

OUT = Path(__file__).resolve().parents[1] / "exports" / "9x16-vtuber2d"
NAMES = [
    "คุยลงทุนจนแฮมสเตอร์เป็นประธานบริษัท-vdo_9x16",
    "จบเกมด้วยผล Defeat 51–42-vdo_9x16",
    "ปะทะกลางเลนก่อนตัวละครล้ม-vdo_9x16",
]
EXPECT_FOCUS = {NAMES[0]: 3, NAMES[1]: 9, NAMES[2]: 11}
V4 = 4
PANEL_TOP = 1063          # seam ends at row 1055; 7 px safety
X0 = 0.602                # original horizontal window centre (pass 1 log: Size 2.0, Center_x 0.296)
NEW_SIZE = 1920.0 / (1920.0 - PANEL_TOP)


def read(t):
    return {k: t.GetInput(k) for k in ("Size", "Center", "Pivot")}


def main():
    apply = "--apply" in sys.argv
    r = connect_resolve()
    check(r is not None, "Resolve unavailable")
    pm = r.GetProjectManager()
    p = pm.GetCurrentProject()
    check(p is not None and p.GetName() == "sakuyako-2026-09", "wrong project")
    check(not p.IsRenderingInProgress(), "render in progress")
    log = {}
    with preserved_state(r):
        r.OpenPage("edit")
        time.sleep(2)
        for name in NAMES:
            tl = find(p, name=name)
            check(tl is not None, f"missing {name}")
            check(not tl.GetIsTrackLocked("video", V4), f"V{V4} locked in {name}")
            activate(p, tl)
            clips = [x for x in items(tl, "video", V4) if x.GetName() == "Adjustment Clip"]
            check(len(clips) == EXPECT_FOCUS[name], f"{name}: {len(clips)} adjustment clips, expected {EXPECT_FOCUS[name]}")
            rows = []
            for c in clips:
                t = fusion_transform(c)
                b = read(t)
                size, piv, cen = float(b["Size"]), b["Pivot"], b["Center"]
                new_cy = NEW_SIZE * float(piv[2])
                new_cx = float(piv[1]) - (X0 - float(piv[1])) * NEW_SIZE
                row = {"start": c.GetStart(), "end": c.GetEnd(), "before": b, "new_size": NEW_SIZE, "new_center": [new_cx, new_cy]}
                if apply and (abs(float(cen[2]) - new_cy) > 1e-6 or abs(float(cen[1]) - new_cx) > 1e-6 or abs(size - NEW_SIZE) > 1e-6):
                    t.SetInput("Size", float(NEW_SIZE))
                    time.sleep(0.4)
                    t.SetInput("Center", {1: float(new_cx), 2: float(new_cy), 3: 0.0})
                    time.sleep(0.6)
                    rb = read(t)
                    check(abs(float(rb["Center"][2]) - new_cy) < 1e-6 and abs(float(rb["Center"][1]) - new_cx) < 1e-6
                          and abs(float(rb["Size"]) - NEW_SIZE) < 1e-6, f"readback {rb}")
                    row["after"] = rb
                rows.append(row)
            log[name] = rows
            print(name[:24], len(rows), "clips", "applied" if apply else "dry-run", flush=True)
        if apply:
            check(pm.SaveProject(), "SaveProject failed")
            time.sleep(1.25)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / ("focus_fix_log_pass2.json" if apply else "focus_fix_plan_pass2.json")).write_text(
        json.dumps(log, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
