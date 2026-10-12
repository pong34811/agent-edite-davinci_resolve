"""Build a short-form Thai SRT from curated cue starts (offline).

Input is a TSV: `start_seconds<TAB>text[<TAB>end_seconds]`, one cue per line, `#` comments.
Starts come from ASR word times; text is human-reviewed. A cue's end defaults to
`start + 0.3 + 0.085 * chars` (Thai, digits, Latin) (capped at --max-seconds), then is clamped to
`next_start - gap` and to the timeline end. Times snap to whole frames.
A numeral spoken as words ("1,950" = หนึ่งพันเก้าร้อยห้าสิบ) is far longer than its glyphs: give it an explicit end.

Usage: python scripts/build_dynamic_srt.py cues.tsv out.srt [--fps 60] [--end-frame 4326]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Thai letters AND digits/Latin: a digits-only cue ("1,950") must not default to a 0.3 s hold.
THAI = re.compile(r"[฀-๿0-9A-Za-z]")


def fmt(frame: int, fps: float) -> str:
    ms = int(round(frame * 1000.0 / fps))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)


def build(rows, fps=60.0, end_frame=None, max_seconds=1.5, gap_frames=2, min_frames=None):
    min_frames = min_frames or int(round(0.5 * fps))
    cues = []
    for i, (start, text, end) in enumerate(rows):
        s = int(round(start * fps))
        if end is None:
            end = start + min(max_seconds, 0.3 + 0.085 * len(THAI.findall(text)))
        e = min(int(round(end * fps)), s + int(max_seconds * fps + 1e-6))
        if i + 1 < len(rows):
            e = min(e, int(round(rows[i + 1][0] * fps)) - gap_frames)
        if end_frame is not None:
            e = min(e, end_frame)
        e = max(e, s + 1)
        cues.append((s, e, text))
    return cues


def read_rows(path: Path):
    rows = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.split("\t")
        rows.append((float(parts[0]), parts[1].strip(), float(parts[2]) if len(parts) > 2 and parts[2].strip() else None))
    rows.sort(key=lambda r: r[0])
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("tsv", type=Path)
    ap.add_argument("srt", type=Path)
    ap.add_argument("--fps", type=float, default=60.0)
    ap.add_argument("--end-frame", type=int, default=None)
    ap.add_argument("--max-seconds", type=float, default=1.5)
    a = ap.parse_args(argv)
    cues = build(read_rows(a.tsv), a.fps, a.end_frame, a.max_seconds)
    out = []
    for n, (s, e, t) in enumerate(cues, 1):
        out.append("%d\n%s --> %s\n%s\n" % (n, fmt(s, a.fps), fmt(e, a.fps), t))
    a.srt.write_text("\n".join(out), encoding="utf-8")
    print("%d cues -> %s" % (len(cues), a.srt))


if __name__ == "__main__":
    sys.exit(main())
