"""Re-lay out V2 REACTIONS GIFs of the vertical (1080x1920) timelines so they sit fully inside the game panel.

MCP-GAP: timeline_item.set_property exists, but computing Zoom/Tilt from each GIF's raster, saving the previous
values and reading back needs one process with a restore of timeline/playhead -> scripting API via resolve_common.

Cause: V3 (VTuber Bottom, avatar) draws above V2 (GIFs) and starts at the seam (y~699), so GIFs whose lower part
fell below the seam were cut off (one was hidden completely). Layout: horizontally centred (Pan 0), at most
MAX_W x MAX_H canvas px, bottom edge at BOTTOM_Y. Tilt unit = fitted_h/canvas_h canvas px (+ up), measured.

Usage: python -m scripts.p2_9x16_gif_relayout <timeline index>... [--dry]
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
from scripts.resolve_common import connect_resolve, preserved_state
from scripts.p2_9x16_build import activate, set_float

CANVAS_W, CANVAS_H = 1080, 1920
SEAM_Y = 699
MAX_W, MAX_H, BOTTOM_Y = 540, 420, 670
OUT = Path(__file__).resolve().parents[1] / "exports" / "9x16-qc" / "gif_relayout_before.json"


def plan(w, h):
    s0 = min(CANVAS_W / w, CANVAS_H / h)
    fw, fh = w * s0, h * s0
    z = min(MAX_W / fw, MAX_H / fh, 1.0)
    dh = fh * z
    cy = BOTTOM_Y - dh / 2
    tilt = (CANVAS_H / 2 - cy) / (fh / CANVAS_H)
    return {"Pan": 0.0, "Tilt": tilt, "ZoomX": z, "ZoomY": z}, (fw * z, dh, cy)


def main():
    dry = "--dry" in sys.argv
    idx = [int(a) for a in sys.argv[1:] if a.isdigit()]
    r = connect_resolve(); r = r[0] if isinstance(r, tuple) else r
    pm = r.GetProjectManager(); p = pm.GetCurrentProject()
    before = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    with preserved_state(r):
        for i in idx:
            t = p.GetTimelineByIndex(i)
            assert t.GetSetting("timelineResolutionWidth") == "1080" and t.GetSetting("timelineResolutionHeight") == "1920"
            activate(p, t)
            for it in t.GetItemListInTrack("video", 2) or []:
                m = it.GetMediaPoolItem()
                w, h = [int(v) for v in m.GetClipProperty("Resolution").split("x")]
                key = f"{t.GetUniqueId()}:{it.GetStart()}"
                props, (dw, dh, cy) = plan(w, h)
                cur = {k: it.GetProperty(k) for k in props}
                before.setdefault(key, {"timeline": t.GetName(), "item": it.GetName(), "props": cur})
                print(i, it.GetName(), f"{w}x{h}", "cur", {k: round(v, 3) for k, v in cur.items()}, "->",
                      {k: round(v, 3) for k, v in props.items()}, f"display {dw:.0f}x{dh:.0f} y {cy-dh/2:.0f}..{cy+dh/2:.0f}")
                if dry:
                    continue
                for k, v in props.items():
                    set_float(it, k, v)
                    time.sleep(0.4)
                print("   readback", {k: round(float(it.GetProperty(k)), 3) for k in props})
    if not dry:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(before, ensure_ascii=False, indent=1), encoding="utf-8")
        print("saved before-values", OUT)
        print("SaveProject", pm.SaveProject())


if __name__ == "__main__":
    main()
