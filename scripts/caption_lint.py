"""Lint a Thai short-form SRT against the house caption rules (read-only, offline).

Rules (AGENTS.md / house-style): a cue is at most ~14 Thai characters and 1.5 s,
has no spaces between Thai characters, and carries no more than two lines.
Spaces are allowed around Latin names. The checker reports; it never edits text,
because splitting or dropping speech is an editorial decision.

Usage: python scripts/caption_lint.py <file.srt> [--max-chars 14] [--max-seconds 1.5]
Exit code 1 when any cue violates a rule.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TIME = re.compile(r"(\d+):(\d\d):(\d\d)[,.](\d{3})\s*-->\s*(\d+):(\d\d):(\d\d)[,.](\d{3})")
THAI = re.compile(r"[฀-๿]")
THAI_GAP = re.compile(r"(?<=[฀-๿])[ \t ]+(?=[฀-๿])")


def _seconds(h, m, s, ms) -> float:
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


def parse_srt(text: str):
    """Yield (index, start, end, text) for each cue; tolerant of BOM and CRLF."""
    text = text.lstrip("﻿").replace("\r\n", "\n").replace("\r", "\n")
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = block.split("\n")
        for pos, line in enumerate(lines):
            match = TIME.search(line)
            if match:
                g = match.groups()
                index = lines[pos - 1].strip() if pos else "?"
                yield index, _seconds(*g[:4]), _seconds(*g[4:]), "\n".join(lines[pos + 1:]).strip()
                break


def lint(text: str, max_chars: int = 14, max_seconds: float = 1.5):
    problems = []
    for index, start, end, body in parse_srt(text):
        duration = end - start
        thai_chars = len(THAI.findall(body))
        if duration <= 0:
            problems.append((index, "non-positive duration"))
        elif duration > max_seconds + 1e-6:
            problems.append((index, "too long: %.2fs > %.2fs" % (duration, max_seconds)))
        if thai_chars > max_chars:
            problems.append((index, "too many Thai characters: %d > %d" % (thai_chars, max_chars)))
        if THAI_GAP.search(body):
            problems.append((index, "space between Thai characters"))
        if body.count("\n") >= 2:
            problems.append((index, "more than two lines"))
        if not body:
            problems.append((index, "empty cue"))
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("srt", type=Path)
    ap.add_argument("--max-chars", type=int, default=14)
    ap.add_argument("--max-seconds", type=float, default=1.5)
    args = ap.parse_args(argv)
    text = args.srt.read_text(encoding="utf-8-sig")
    cues = sum(1 for _ in parse_srt(text))
    problems = lint(text, args.max_chars, args.max_seconds)
    for index, message in problems:
        print("cue %s: %s" % (index, message))
    print("%d cue(s), %d problem(s)" % (cues, len(problems)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
