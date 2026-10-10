"""Offline plan: rule-fixed Thai captions for the 44 HORIZONTAL p2 timelines (indexes 1-44).

Reuses chunks()/fix()/ts()/tchars() from p2_fix_captions.py (not modified). Reads
exports/publish-qc/data.json, writes exports/captions-fixed-h/<index>.srt (UTF-8, from 00:00:00, 60 fps)
and plan.json. Applies nothing to Resolve and never connects to it.

Run from repo root: python scripts/p2_fix_captions_horizontal.py [--only 1,2]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from p2_fix_captions import MAX_CHARS, MAX_FRAMES, fix, tchars, ts  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "exports" / "publish-qc" / "data.json"
OUT = ROOT / "exports" / "captions-fixed-h"


def main():
    only = None
    if "--only" in sys.argv:
        only = {int(x) for x in sys.argv[sys.argv.index("--only") + 1].split(",")}
    data = json.loads(DATA.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    plan = []
    for x in data:
        if x["vertical"] or (only and x["index"] not in only):
            continue
        cues = [tuple(c) for c in x["subs"]["cues"]]
        new = fix(cues)
        srt = [f"{n}\n{ts(s)} --> {ts(e)}\n{t}\n" for n, (t, s, e) in enumerate(new, 1)]
        (OUT / f"{x['index']}.srt").write_text("\n".join(srt), encoding="utf-8")
        bad = [1 for t, s, e in new if tchars(t) > MAX_CHARS or e - s > MAX_FRAMES]
        over = [i for i in range(1, len(new)) if new[i][1] < new[i - 1][2]]
        changed = sum(1 for c in cues if tchars(c[0]) > MAX_CHARS or c[2] - c[1] > MAX_FRAMES)
        plan.append({"index": x["index"], "name": x["name"], "old": len(cues), "new": len(new),
                     "changed": changed, "bad": len(bad), "overlap": len(over)})
        print(x["index"], x["name"][:26], len(cues), "->", len(new), "changed", changed, "bad", len(bad), "overlap", len(over))
    (OUT / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
