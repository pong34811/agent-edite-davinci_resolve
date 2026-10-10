"""Read-only still export (3 frames per timeline) of every p2 timeline for visual publish QC.

MCP-GAP: no MCP action exports a still of an arbitrary timeline frame in bulk; needs activate + playhead + export.
No project edits: session state (timeline/playhead/page) is restored. Native still export omits subtitles.
Run from repo root: python -m scripts.p2_publish_stills [--start N]
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.resolve_common import connect_resolve, preserved_state  # noqa: E402

OUT = ROOT / "exports" / "publish-qc" / "stills"
POS = (("a", 0.12), ("b", 0.5), ("c", 0.88))


def tc(frame, fps=60):
    s, f = divmod(int(frame), fps)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}:{f:02d}"


def main():
    start = int(sys.argv[sys.argv.index("--start") + 1]) if "--start" in sys.argv else 1
    OUT.mkdir(parents=True, exist_ok=True)
    r = connect_resolve()
    p = r.GetProjectManager().GetCurrentProject()
    with preserved_state(r):
        r.OpenPage("edit")
        time.sleep(1.5)
        for i in range(start, p.GetTimelineCount() + 1):
            tl = p.GetTimelineByIndex(i)
            p.SetCurrentTimeline(tl)
            time.sleep(1.2)
            s, e = tl.GetStartFrame(), tl.GetEndFrame()
            for tag, k in POS:
                f = s + int((e - s) * k)
                path = OUT / f"{i:02d}_{tag}.png"
                tl.SetCurrentTimecode(tc(f + 1))
                time.sleep(0.4)
                tl.SetCurrentTimecode(tc(f))
                time.sleep(0.9)
                ok = p.ExportCurrentFrameAsStill(str(path))
                time.sleep(0.3)
                print(i, tag, f, bool(ok and path.exists()), flush=True)


if __name__ == "__main__":
    main()
