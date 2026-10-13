"""Read-only QC data pass over every timeline of armigon-2026-09 (reuses scripts.p2_publish_qc.read).

MCP-GAP: davinci-resolve MCP timeline.list returns names/ids only; per-item/per-cue reads across 80
timelines without activating each one need a script. Reads only: no edits, no saves, no renders,
no timeline activation.

Run from repo root: python -m scripts.armigon_publish_qc
Writes exports/armigon-qc/data.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.p2_publish_qc import read  # noqa: E402
from scripts.resolve_common import connect_resolve  # noqa: E402

OUT = ROOT / "exports" / "armigon-qc"
PROJECT = "armigon-2026-09"


def main():
    r = connect_resolve()
    p = r.GetProjectManager().GetCurrentProject()
    if p is None or p.GetName() != PROJECT:
        raise SystemExit("project %s not open" % PROJECT)
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for i in range(1, p.GetTimelineCount() + 1):
        tl = p.GetTimelineByIndex(i)
        row = read(tl, None)
        row["index"] = i
        rows.append(row)
        print(i, row["name"], row["w"], row["h"], row["dur_s"], "cues", row["subs"]["count"],
              "issues", len(row["subs"]["issues"]), flush=True)
    (OUT / "data.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print("WROTE", len(rows))


if __name__ == "__main__":
    main()
