"""Rebuild p2 vertical captions to the short-form house rule (<=14 Thai chars, <=1.5 s per cue).

Stage `plan` (offline, default): read exports/publish-qc/data.json, split/trim cues, write one UTF-8 SRT per
vertical timeline to exports/captions-fixed/<index>.srt plus plan.json. Never drops speech: an over-long cue is
split at Thai word boundaries (pythainlp newmm) and the original [start, end] window is shared out by character
count; a cue that is only too long in time is trimmed to 1.5 s.

Run from repo root: python scripts/p2_fix_captions.py [--only 45,46]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from pythainlp.tokenize import word_tokenize

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "exports" / "publish-qc" / "data.json"
OUT = ROOT / "exports" / "captions-fixed"
MAX_CHARS = 14
FPS = 60.0
MAX_FRAMES = 90  # 1.5 s
MIN_FRAMES = 12
THAI = re.compile(r"[฀-๿]")


def tchars(s: str) -> int:
    return len(THAI.findall(s))


def chunks(text: str):
    """Greedy word-boundary chunks of at most MAX_CHARS Thai characters (never splits inside a token)."""
    flat = " ".join(text.split("\n")).strip()
    toks = [t for t in word_tokenize(flat, engine="newmm", keep_whitespace=True)]
    out, cur = [], ""
    for t in toks:
        if cur and tchars(cur + t) > MAX_CHARS:
            out.append(cur.strip())
            cur = ""
        cur += t
    if cur.strip():
        out.append(cur.strip())
    return out


def fix(cues):
    res = []
    for k, (text, s, e) in enumerate(cues):
        nxt = cues[k + 1][1] if k + 1 < len(cues) else None
        e = min(e, nxt) if nxt is not None else e  # end never passes the next cue
        parts = chunks(text) if tchars(text) > MAX_CHARS else [text.replace("\n", "").strip()]
        n = len(parts)
        window = e - s
        if n > 1 and window < n * MIN_FRAMES:  # too short to read every piece: borrow the gap before the next cue
            avail = (nxt - s) if nxt is not None else n * MIN_FRAMES
            window = min(n * MIN_FRAMES, avail)
            if window < n * MIN_FRAMES:  # still no room: keep one cue (a few extra characters) rather than flash text
                parts, n, window = [text.replace(chr(10), "").strip()], 1, e - s
        total = sum(max(tchars(p), 1) for p in parts)
        cur = s
        for j, p in enumerate(parts):
            share = round(window * max(tchars(p), 1) / total) if n > 1 else window
            end = min(cur + share, cur + MAX_FRAMES)
            if j == n - 1:
                end = min(end, max(e, cur + 1))
            res.append((p, cur, max(end, cur + 1)))
            cur += share
    for i in range(len(res) - 1):  # never overlap the next cue
        t, a_, b_ = res[i]
        if b_ > res[i + 1][1]:
            res[i] = (t, a_, max(res[i + 1][1], a_ + 1))
    return res


def ts(frame: int) -> str:
    ms = int(frame * 1000 // 60) if FPS == 60.0 else int(frame * 1000.0 // FPS)  # floor: Resolve may ceil, so never round up
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main():
    only = None
    if "--only" in sys.argv:
        only = {int(x) for x in sys.argv[sys.argv.index("--only") + 1].split(",")}
    data = json.loads(DATA.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    plan = []
    for x in data:
        if not x["vertical"] or (only and x["index"] not in only):
            continue
        cues = [tuple(c) for c in x["subs"]["cues"]]
        new = fix(cues)
        srt = []
        for n, (t, s, e) in enumerate(new, 1):
            srt.append(f"{n}\n{ts(s)} --> {ts(e)}\n{t}\n")
        (OUT / f"{x['index']}.srt").write_text("\n".join(srt), encoding="utf-8")
        bad = [(t, s, e) for t, s, e in new if tchars(t) > MAX_CHARS or e - s > MAX_FRAMES]
        over = [i for i in range(1, len(new)) if new[i][1] < new[i - 1][2]]
        plan.append({"index": x["index"], "name": x["name"], "old": len(cues), "new": len(new),
                     "bad": len(bad), "overlap": len(over)})
        print(x["index"], x["name"][:26], len(cues), "->", len(new), "bad", len(bad), "overlap", len(over))
    (OUT / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
