"""Offline rule check for ASR SRT files (Thai short-form caption contract).

Usage: python scripts/pipeline/check_srt.py <dir with T<N>.srt> [N ...]
Flags per cue: format/numbering, duration > 1.5 s (+tolerance), overlap, > 14 characters, foreign scripts,
U+FFFD replacement characters, and runaway repetition (e.g. หาๆๆๆๆๆ or one phrase repeated 3+ times).
Also reports clips whose cues are dominated by one repeated phrase (ASR hallucination loops, seen on game
lobby noise): >= 40% of cues identical or starting with the same 3 characters.
Exit code 1 when any flag is raised.
"""
import glob
import os
import re
import sys

FOREIGN = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff\uac00-\ud7af\u0400-\u04ff\u0600-\u06ff\u0900-\u097f]")
REPEAT = re.compile(r"(.)\1{4,}|(\S+)( \2){3,}")


def ts(s):
    h, m, r = s.split(":")
    sec, ms = r.split(",")
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000


def parse(path):
    raw = open(path, encoding="utf-8-sig").read()
    return [b for b in re.split(r"\r?\n\r?\n", raw.strip()) if b.strip()]


def check(path):
    blocks = parse(path)
    bad, prev, texts = [], -1.0, []
    for i, b in enumerate(blocks, 1):
        lines = b.splitlines()
        if len(lines) < 3 or not lines[0].strip().isdigit() or int(lines[0]) != i:
            bad.append((i, "fmt"))
            continue
        a, e = (ts(x.strip()) for x in lines[1].split("-->"))
        txt = "".join(lines[2:])
        texts.append(txt)
        if e - a > 1.55:
            bad.append((i, "dur%.2f" % (e - a)))
        if a < prev - 1e-6:
            bad.append((i, "overlap"))
        if len(txt.replace(" ", "")) > 14:
            bad.append((i, "len%d" % len(txt)))
        if FOREIGN.search(txt):
            bad.append((i, "foreign:" + txt))
        if "\ufffd" in txt:
            bad.append((i, "FFFD:" + txt))
        if REPEAT.search(txt):
            bad.append((i, "rep:" + txt))
        prev = e
    if len(texts) >= 8:
        from collections import Counter
        top = Counter(t[:3] for t in texts).most_common(1)[0]
        if top[1] >= 0.4 * len(texts):
            bad.append((0, "loop?:%r x%d/%d" % (top[0], top[1], len(texts))))
    return len(blocks), bad


def main():
    d = sys.argv[1]
    nums = [int(x) for x in sys.argv[2:]] or sorted(int(re.search(r"T(\d+)\.srt$", p).group(1)) for p in glob.glob(os.path.join(d, "T*.srt")))
    rc = 0
    for n in nums:
        path = os.path.join(d, "T%d.srt" % n)
        if not os.path.exists(path):
            print("T%d: missing" % n)
            continue
        cues, bad = check(path)
        print("T%d: cues=%d bad=%s" % (n, cues, bad[:8]))
        rc |= bool(bad)
    return rc


if __name__ == "__main__":
    sys.exit(main())
