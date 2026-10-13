"""Read-only: dump V1 source file + source range per armigon-2026-09 timeline.

MCP-GAP: timeline.probe_timeline_structure needs the timeline active (changes UI state); this reads
GetSourceStartFrame/GetSourceEndFrame via GetTimelineByIndex without activating anything.

Run from repo root: python -m scripts.armigon_source_ranges
Writes exports/armigon-qc/source_ranges.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.resolve_common import connect_resolve  # noqa: E402

OUT = ROOT / "exports" / "armigon-qc" / "source_ranges.json"
PROJECT = "armigon-2026-09"


def main():
    r = connect_resolve()
    p = r.GetProjectManager().GetCurrentProject()
    if p is None or p.GetName() != PROJECT:
        raise SystemExit("project %s not open" % PROJECT)
    rows = []
    for i in range(1, p.GetTimelineCount() + 1):
        tl = p.GetTimelineByIndex(i)
        row = {"index": i, "name": tl.GetName(), "items": []}
        for it in tl.GetItemListInTrack("video", 1) or []:
            mp = it.GetMediaPoolItem()
            row["items"].append({
                "start": it.GetStart(), "end": it.GetEnd(),
                "src_start": it.GetSourceStartFrame(), "src_end": it.GetSourceEndFrame(),
                "path": mp.GetClipProperty("File Path") if mp else None,
                "fps": mp.GetClipProperty("FPS") if mp else None,
            })
        rows.append(row)
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print("WROTE", len(rows))


if __name__ == "__main__":
    main()
