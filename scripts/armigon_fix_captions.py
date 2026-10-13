"""OFFLINE plan: rebuild armigon-2026-09 captions to the short-form house rule. Touches no Resolve state.

Reuses scripts.p2_fix_captions.fix (<=14 Thai chars, <=1.5 s, split at Thai word boundaries, no speech dropped)
and additionally removes spaces between Thai characters (house-style: no inter-word spaces).
Reads exports/armigon-qc/data.json; writes exports/armigon-qc/captions-fixed/<index>.srt + plan.json.
The pilot timeline (#2) is skipped. Applying the SRTs to Resolve is a separate, approved step.

Run from repo root: python -m scripts.armigon_fix_captions
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts import p2_fix_captions as fc  # noqa: E402

DATA = ROOT / "exports" / "armigon-qc" / "data.json"
OUT = ROOT / "exports" / "armigon-qc" / "captions-fixed"
THAI_GAP = re.compile(r"(?<=[฀-๿])[ \t ]+(?=[฀-๿])")


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    plan = []
    for x in data:
        if x["name"] == "ARMIGON_FOCUS_MCP_PILOT_TEMP":
            continue
        cues = [(THAI_GAP.sub("", t), s, e) for t, s, e in x["subs"]["cues"]]
        new = [(THAI_GAP.sub("", t), s, e) for t, s, e in fc.fix(cues)]
        srt = ["%d\n%s --> %s\n%s\n" % (n, fc.ts(s), fc.ts(e), t) for n, (t, s, e) in enumerate(new, 1)]
        (OUT / f"{x['index']}.srt").write_text("\n".join(srt), encoding="utf-8")
        bad = [c for c in new if fc.tchars(c[0]) > fc.MAX_CHARS or c[2] - c[1] > fc.MAX_FRAMES]
        over = [i for i in range(1, len(new)) if new[i][1] < new[i - 1][2]]
        gap = [c for c in new if THAI_GAP.search(c[0])]
        plan.append({"index": x["index"], "name": x["name"], "old": len(cues), "new": len(new),
                     "bad": len(bad), "overlap": len(over), "thai_space": len(gap)})
    (OUT / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    print("clips", len(plan), "cues", sum(p["old"] for p in plan), "->", sum(p["new"] for p in plan),
          "bad", sum(p["bad"] for p in plan), "overlap", sum(p["overlap"] for p in plan),
          "thai_space", sum(p["thai_space"] for p in plan))


if __name__ == "__main__":
    main()
