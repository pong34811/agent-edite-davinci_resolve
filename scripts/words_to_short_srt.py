"""Group ASR word timings into a short-form Thai SRT (offline, read-only on media).

Input is the JSON written by `asr_words_th.py` (`segments` + char-timed `words`).
Each cue follows house style: <= 14 Thai characters, <= 1.5 s on screen, Thai words
joined with no spaces (a space only next to Latin), 2-frame gap, snapped to frames.
Whole segments that look like Whisper hallucination (low avg_logprob, stock outro
phrases, long repetition) are skipped and listed in a JSON report, never silently.

Usage: python scripts/words_to_short_srt.py asr.json out.srt [--fps 60] [--end-frame N]
       [--offset-seconds 0] [--report out.report.json] [--min-logprob -1.5]
       [--drop-latin --keep-latin VTuber]

`--drop-latin` removes Latin-script words (Whisper on Thai free talk often appends an
English translation of the sentence); `--keep-latin` whitelists real terms. Do not
use it on game footage, where English announcer lines are genuine audio.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

MAX_CHARS = 14
MAX_SECONDS = 1.5
PAUSE_BREAK = 0.7
MIN_LOGPROB = -1.5
GAP_FRAMES = 2
COUNTED = re.compile(r"[฀-๿0-9A-Za-z]")
LATIN = re.compile(r"[A-Za-z0-9]")
LATIN_WORD = re.compile(r"[A-Za-zÀ-ɏ]")
STOCK = ("โปรดติดตามตอนต่อไป", "ขอบคุณที่รับชม", "ซับไตเติ้ลโดย", "กดติดตาม")


def nchars(text: str) -> int:
    return len(COUNTED.findall(text))


def join_words(words) -> str:
    out = ""
    for w in words:
        tok = w["w"].strip()
        if not tok:
            continue
        if out and (LATIN.search(out[-1]) or LATIN.search(tok[0])):
            out += " "
        out += tok
    return out


def suspect_segment(seg, min_logprob=MIN_LOGPROB) -> str | None:
    text = seg["text"].strip()
    if seg.get("avg_logprob", 0) < min_logprob:
        return "avg_logprob %.2f" % seg["avg_logprob"]
    if any(p in text for p in STOCK):
        return "stock phrase"
    if re.search(r"(.{2,}?)\1{3,}", text.replace(" ", "")):
        return "repetition"
    return None


def should_break(cur, nxt) -> bool:
    """Return True when word `nxt` must start a new cue instead of joining `cur`.

    `cur` is the non-empty list of words already in the cue; each word is
    {"w": text, "s": start_s, "e": end_s, "seg": segment_id}.
    """
    if nxt["seg"] != cur[-1]["seg"]:
        return True
    if nxt["s"] - cur[-1]["e"] >= PAUSE_BREAK:
        return True
    # Compare STARTS: Whisper stretches a Thai word's end across silence, so an
    # end-based limit leaves one word per cue. The display itself is capped later.
    if nxt["s"] - cur[0]["s"] > MAX_SECONDS:
        return True
    return nchars(join_words(cur + [nxt])) > MAX_CHARS


def group(words):
    cues, cur = [], []
    for w in words:
        if not w["w"].strip():
            continue
        if cur and should_break(cur, w):
            cues.append(cur)
            cur = []
        cur.append(w)
    if cur:
        cues.append(cur)
    return cues


def fmt(frame: int, fps: float) -> str:
    ms = int(round(frame * 1000.0 / fps))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)


def to_frames(cues, fps, offset, end_frame=None):
    max_f = int(round(MAX_SECONDS * fps))
    rows = []
    for c in cues:
        s = int(round((c[0]["s"] + offset) * fps))
        e = int(round((c[-1]["e"] + offset) * fps))
        e = min(max(e, s + int(round(0.5 * fps))), s + max_f)
        rows.append([s, e, join_words(c)])
    for i in range(len(rows) - 1):
        rows[i][1] = min(rows[i][1], rows[i + 1][0] - GAP_FRAMES)
    if end_frame is not None:
        rows = [r for r in rows if r[0] < end_frame]
        if rows:
            rows[-1][1] = min(rows[-1][1], end_frame)
    return [r for r in rows if r[1] > r[0] and r[2]]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("asr_json")
    ap.add_argument("out_srt")
    ap.add_argument("--fps", type=float, default=60.0)
    ap.add_argument("--end-frame", type=int)
    ap.add_argument("--offset-seconds", type=float, default=0.0)
    ap.add_argument("--report")
    ap.add_argument("--min-logprob", type=float, default=MIN_LOGPROB)
    ap.add_argument("--drop-latin", action="store_true")
    ap.add_argument("--keep-latin", action="append", default=[])
    a = ap.parse_args(argv)
    data = json.loads(Path(a.asr_json).read_text(encoding="utf-8"))
    skipped = {}
    for seg in data["segments"]:
        why = suspect_segment(seg, a.min_logprob)
        if why:
            skipped[seg["id"]] = {"start": seg["start"], "end": seg["end"], "text": seg["text"], "why": why}
    words = [w for w in data["words"] if w["seg"] not in skipped]
    dropped = []
    if a.drop_latin:
        keep = {k.lower() for k in a.keep_latin}
        dropped = [w["w"] for w in words if LATIN_WORD.search(w["w"]) and w["w"].strip().lower() not in keep]
        words = [w for w in words if not (LATIN_WORD.search(w["w"]) and w["w"].strip().lower() not in keep)]
    rows = to_frames(group(words), a.fps, a.offset_seconds, a.end_frame)
    lines = []
    for i, (s, e, t) in enumerate(rows, 1):
        lines += [str(i), "%s --> %s" % (fmt(s, a.fps), fmt(e, a.fps)), t, ""]
    Path(a.out_srt).write_text("\n".join(lines), encoding="utf-8")
    report = {"cues": len(rows), "skipped_segments": list(skipped.values()),
              "over_chars": [t for _, _, t in rows if nchars(t) > MAX_CHARS],
              "dropped_latin": dropped}
    if a.report:
        Path(a.report).write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print("%d cues, %d segments skipped, %d over %d chars"
          % (len(rows), len(skipped), len(report["over_chars"]), MAX_CHARS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
