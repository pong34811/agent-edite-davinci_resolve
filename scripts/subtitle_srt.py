"""Thai short-form SRT builder and validator.

Build (per job, from a hand-curated phrase list aligned onto ASR character times):
    python scripts/subtitle_srt.py build WORKSPACE [--jobs 1,2]
Validate an SRT:
    python scripts/subtitle_srt.py validate FILE.srt [--speech-start S] [--end 55]

Curation input: WORKSPACE/srt/job<N>.curation.json
    {"job": 1,
     "phrases": [{"text": "แล้วก็วันนี้ ก็ชิวๆ", "t0": 3.0, "t1": 7.2,
                  "src": "raw_chunk", "win": null, "note": "..."}],
     "omitted": [{"t0": 0.3, "t1": 3.0, "reason": "..."}],
     "uncertain": [{"term": "...", "t": 12.0, "note": "..."}],
     "changes": ["..."]}
A space inside phrase text marks a natural phrase boundary (preferred cue split);
it is never rendered between Thai characters. `src` names an ASR pass in
asr/job<N>.json or asr/job<N>_extra.json (`win` selects one overlapping window of
an extra pass); the phrase characters are aligned to that pass's character times
inside [t0, t1]. Without `src` the phrase is spread linearly over [t0, t1].
Outputs: srt/job<N>.srt, srt/job<N>.curation.md, srt/transcripts.md.
"""
import argparse
import difflib
import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import subtitle_asr as asr  # noqa: E402

MAX_WORDS = 3
MAX_CHARS = 14          # spacing (visible) characters; Thai combining marks are not counted
MAX_DUR = 1.5
MIN_GAP = 0.034
MIN_DUR = 0.4           # a cue may be extended into following silence up to this length
PAUSE_BREAK = 0.7
END_LIMIT = 55.0

THAI = asr.THAI_RE
LATIN_RE = re.compile("[A-Za-z0-9]")
ALLOWED_RE = re.compile(r"^[ก-ฺ฿-๛A-Za-z0-9 .,!?%'\"\-]*$")
COMBINING = re.compile("[ัิ-ฺ็-๎]")


# ---------------------------------------------------------------- text helpers
def visible_len(text):
    return sum(1 for c in text if c != " " and not COMBINING.match(c))


# Proper nouns that must count as one caption word (newmm splits them).
CUSTOM_WORDS = {"ไทกะ"}
_TRIE = None


def _tokenize(text):
    global _TRIE
    from pythainlp.tokenize import word_tokenize
    if _TRIE is None:
        from pythainlp.corpus.common import thai_words
        from pythainlp.util import dict_trie
        _TRIE = dict_trie(set(thai_words()) | CUSTOM_WORDS)
    return word_tokenize(text, custom_dict=_TRIE, engine="newmm")


def split_words(text, tokenizer=None):
    """Word list as captions count them: newmm tokens per space chunk, with lone Thai
    characters, leading combining marks, punctuation and ๆ merged into the previous word."""
    tok = tokenizer or _tokenize
    out = []
    for chunk in text.split():
        words = []
        for t in tok(chunk):
            if not t.strip():
                continue
            lone = len(t) == 1 and THAI.match(t)
            if words and (lone or asr.COMBINING_RE.match(t) or asr._is_punct_only(t) or t == "ๆ"):
                words[-1] += t
            else:
                words.append(t)
        out += words
    return out


def count_words(text, tokenizer=None):
    return len(split_words(text, tokenizer))


def join_display(pieces):
    """pieces: list of strings; join without spaces except where a Latin piece touches."""
    s = ""
    for p in pieces:
        if s and (LATIN_RE.search(s[-1]) or LATIN_RE.search(p[0])):
            s += " "
        s += p
    return s


# ---------------------------------------------------------------- timing helpers
def fmt_srt(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)


def parse_srt_time(s):
    h, m, rest = s.strip().split(":")
    sec, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000.0


def source_chars(segments, t0, t1, win=None, slack=0.25):
    chars = []
    for sg in segments:
        if win is not None and sg.get("window", [None])[0] != win:
            continue
        if sg["end"] < t0 - slack or sg["start"] > t1 + slack:
            continue
        for c in asr.clean_chars(asr.char_index(sg["tokens"])):
            mid = (c["start"] + c["end"]) / 2
            if t0 - slack <= mid <= t1 + slack and not c["ch"].isspace():
                chars.append(c)
    chars.sort(key=lambda c: c["start"])
    return chars


def align_times(text, src, t0, t1):
    """Map each non-space char of `text` to (start, end) using `src` char times.
    Returns list of (char, start, end) in text order (spaces excluded)."""
    cur = [c for c in text if not c.isspace() and c != "|"]
    n = len(cur)
    if not src:
        step = (t1 - t0) / max(n, 1)
        return [(ch, t0 + i * step, t0 + (i + 1) * step) for i, ch in enumerate(cur)]
    s_str = "".join(c["ch"] for c in src)
    times = [None] * n
    sm = difflib.SequenceMatcher(None, "".join(cur), s_str, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            for k in range(i2 - i1):
                c = src[j1 + k]
                times[i1 + k] = (c["start"], c["end"])
        elif op == "replace":
            a, b = src[j1]["start"], src[j2 - 1]["end"]
            step = (b - a) / (i2 - i1)
            for k in range(i2 - i1):
                times[i1 + k] = (a + k * step, a + (k + 1) * step)
    # interpolate unmatched ("delete") runs between anchors
    i = 0
    while i < n:
        if times[i] is not None:
            i += 1
            continue
        j = i
        while j < n and times[j] is None:
            j += 1
        a = times[i - 1][1] if i > 0 else max(t0, (times[j][0] if j < n else t1) - 0.08 * (j - i))
        b = times[j][0] if j < n else min(t1, a + 0.08 * (j - i))
        b = max(a, b)
        step = (b - a) / (j - i)
        for k in range(i, j):
            times[k] = (a + (k - i) * step, a + (k - i + 1) * step)
        i = j
    # clamp into the phrase window and enforce monotonic
    out, last = [], t0
    for ch, (a, b) in zip(cur, times):
        a, b = min(max(a, t0), t1), min(max(b, t0), t1)
        a = max(a, last)
        b = max(b, a)
        out.append((ch, a, b))
        last = a
    return out


def phrase_words(text, timed, tokenizer=None):
    """-> [{text,start,end,boundary,hard}] boundary=True at the start of each space chunk;
    hard=True after a "|" (forced cue split)."""
    words, pos, hard = [], 0, False
    for chunk in text.replace("|", " | ").split():
        if chunk == "|":
            hard = True
            continue
        ws = split_words(chunk, tokenizer)
        for wi, w in enumerate(ws):
            seg = timed[pos:pos + len(w)]
            pos += len(w)
            words.append({"text": w, "start": seg[0][1], "end": seg[-1][2], "boundary": wi == 0,
                          "hard": hard and wi == 0})
        hard = False
    return words


def lint_phrase(text, tokenizer=None):
    """Chunks that cannot be one cue (force a mid-chunk split)."""
    return [ch for ch in text.replace("|", " ").split()
            if count_words(ch, tokenizer) > MAX_WORDS or visible_len(ch) > MAX_CHARS]


def max_word_dur(text):
    """Plausible upper bound for one spoken word; Whisper stretches edge words over silence."""
    return max(0.3, 0.13 * visible_len(text) + 0.15)


def _overlap(a, b, regions):
    return sum(max(0.0, min(b, r[1]) - max(a, r[0])) for r in regions)


def clamp_to_speech(first, last, regions):
    """Cue (start, end) from its first/last word, pulled into VAD speech (never extended).
    Edge words are first shrunk to a plausible length; a first word lying mostly in
    silence starts at the next speech region, a last word mostly in silence ends at the
    previous region's end."""
    if first is last:
        start = first["start"]
    else:
        start = max(first["start"], first["end"] - max_word_dur(first["text"]))
    s0 = start
    e0 = max(min(last["end"], max(last["start"], start) + max_word_dur(last["text"])), start + 0.05)
    if not regions:
        return s0, e0
    fa, fb = start, max(first["end"], start + 0.01)
    low = _overlap(fa, fb, regions) < 0.3 * (fb - fa)
    if low or not any(r[0] <= start < r[1] for r in regions):
        nxt = [r[0] for r in regions if r[0] > start]
        if nxt and nxt[0] < last["end"] - 0.05:
            start = nxt[0]
    end = max(min(last["end"], max(last["start"], start) + max_word_dur(last["text"])), start + 0.05)
    e1 = end
    la, lb = min(last["start"], end - 0.01), end
    low = _overlap(la, lb, regions) < 0.3 * (lb - la)
    if low or not any(r[0] < end <= r[1] for r in regions):
        prv = [r[1] for r in regions if r[1] < end]
        if prv:
            end = prv[-1]
    if end - start < 0.05:
        end = e1
    if end - start < 0.05:
        return s0, e0
    return start, end


def silence_gaps(regions, min_gap=0.5):
    return [(regions[k][1], regions[k + 1][0]) for k in range(len(regions) - 1)
            if regions[k + 1][0] - regions[k][1] >= min_gap]


# ---------------------------------------------------------------- segmentation
def segment_words(words, tokenizer=None, max_words=MAX_WORDS, max_chars=MAX_CHARS, max_dur=MAX_DUR,
                  gaps=()):
    """DP split of a phrase's words into cues. Splits at space boundaries are free,
    mid-chunk splits cost more, single-word cues cost a little, fewer cues preferred.
    Mandatory split at pauses >= PAUSE_BREAK between word times, or where a VAD silence
    gap (`gaps`) lies between two word midpoints. Returns list of word lists."""
    n = len(words)

    def pause_after(k):
        if words[k + 1].get("hard") or words[k + 1]["start"] - words[k]["end"] >= PAUSE_BREAK:
            return True
        m0 = (words[k]["start"] + words[k]["end"]) / 2
        m1 = (words[k + 1]["start"] + words[k + 1]["end"]) / 2
        return any(m0 <= a and b <= m1 + 0.3 for a, b in gaps)
    best = [None] * (n + 1)
    best[0] = (0.0, None)
    for j in range(1, n + 1):
        for i in range(j - 1, -1, -1):
            if any(pause_after(k) for k in range(i, j - 1)):
                break
            grp = words[i:j]
            txt = join_display([w["text"] for w in grp])
            if j - i > 1 and (j - i > max_words or count_words(txt, tokenizer) > max_words or visible_len(txt) > max_chars
                              or grp[-1]["end"] - grp[0]["start"] > max_dur):
                break
            if best[i] is None:
                continue
            cost = best[i][0] + 1.0
            if i > 0 and not words[i]["boundary"]:
                gap = words[i]["start"] - words[i - 1]["end"]
                cost += 0.5 if gap >= 0.25 else 3.0
            if j - i == 1 and visible_len(txt) <= 4:
                cost += 0.6
            if grp[-1]["end"] - grp[0]["start"] < 0.35:
                cost += 0.8
            if best[j] is None or cost < best[j][0]:
                best[j] = (cost, i)
    groups, j = [], n
    while j > 0:
        i = best[j][1]
        groups.append(words[i:j])
        j = i
    return groups[::-1]


MIN_READ = 0.3


def rebalance_short(cues, end_limit=END_LIMIT):
    """Within runs of back-to-back cues (word-time boundaries are approximate), move a
    shared boundaries so very short cues get MIN_READ seconds, taking time from longer
    cues of the same run; the run's outer start/end never move."""
    k = 0
    while k < len(cues):
        j = k
        while j + 1 < len(cues) and cues[j + 1]["start"] - cues[j]["end"] <= MIN_GAP + 0.25:
            j += 1
        run = cues[k:j + 1]
        k = j + 1
        if len(run) < 2 or all(c["end"] - c["start"] >= MIN_READ for c in run):
            continue
        total = run[-1]["end"] - run[0]["start"] - MIN_GAP * (len(run) - 1)
        d = [max(c["end"] - c["start"], 0.0) for c in run]
        nd = [max(x, MIN_READ) for x in d]
        excess = sum(nd) - total
        slack = sum(x - MIN_READ for x in nd if x > MIN_READ)
        if excess > slack:  # borrow up to 0.3 s of the silence after the run
            nxt = cues[k]["start"] - MIN_GAP if k < len(cues) else end_limit
            room = max(0.0, min(0.3, nxt - run[-1]["end"], end_limit - run[-1]["end"]))
            take = min(room, excess - slack)
            total += take
            excess -= take
        if excess > 0:
            if slack < excess:
                continue
            nd = [x - (x - MIN_READ) * excess / slack if x > MIN_READ else x for x in nd]
        t = run[0]["start"]
        for c, x in zip(run, nd):
            c["start"], c["end"] = t, t + x
            t += x + MIN_GAP


def build_cues(phrases_words, regions=None, end_limit=END_LIMIT, tokenizer=None):
    cues = []
    gaps = silence_gaps(regions) if regions else ()
    for words in phrases_words:
        for grp in segment_words(words, tokenizer, gaps=gaps):
            start, end = clamp_to_speech(grp[0], grp[-1], regions)
            cues.append({"text": join_display([w["text"] for w in grp]), "start": start, "end": end})
    cues = sorted((c for c in cues if c["start"] < end_limit - 0.2), key=lambda c: c["start"])
    for k, c in enumerate(cues):
        nxt = cues[k + 1]["start"] if k + 1 < len(cues) else end_limit + MIN_GAP
        c["end"] = min(c["end"], c["start"] + MAX_DUR, nxt - MIN_GAP, end_limit)
    rebalance_short(cues, end_limit)
    for k, c in enumerate(cues):
        nxt = cues[k + 1]["start"] if k + 1 < len(cues) else end_limit + MIN_GAP
        c["end"] = min(c["end"], c["start"] + MAX_DUR, nxt - MIN_GAP, end_limit)
        if c["end"] - c["start"] < MIN_DUR:
            c["end"] = min(c["start"] + MIN_DUR, nxt - MIN_GAP, end_limit)
        c["start"] = round(c["start"], 3)
        c["end"] = round(c["end"], 3)
    return cues


def write_srt(path, cues):
    lines = []
    for k, c in enumerate(cues, 1):
        lines += [str(k), "%s --> %s" % (fmt_srt(c["start"]), fmt_srt(c["end"])), c["text"], ""]
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


# ---------------------------------------------------------------- validator
def parse_srt(text):
    blocks = [b for b in re.split(r"\n\s*\n", text.replace("\r\n", "\n").strip()) if b.strip()]
    out = []
    for b in blocks:
        ls = b.split("\n")
        a, z = ls[1].split("-->")
        out.append({"index": ls[0].strip(), "start": parse_srt_time(a), "end": parse_srt_time(z),
                    "lines": ls[2:]})
    return out


def validate_cues(cues, speech_start=None, end_limit=END_LIMIT, tokenizer=None):
    """cues: parsed SRT blocks. Returns a list of error strings (empty = valid)."""
    errs = []
    if not cues:
        return ["no cues"]
    for k, c in enumerate(cues):
        tag = "cue %d" % (k + 1)
        if c["index"] != str(k + 1):
            errs.append("%s: index %r not consecutive" % (tag, c["index"]))
        if len(c["lines"]) != 1:
            errs.append("%s: %d lines (one required)" % (tag, len(c["lines"])))
        text = " ".join(c["lines"])
        dur = c["end"] - c["start"]
        if dur <= 0:
            errs.append("%s: non-positive duration" % tag)
        if dur > MAX_DUR + 1e-6:
            errs.append("%s: %.3fs > %.1fs" % (tag, dur, MAX_DUR))
        if any(asr.is_foreign(ch) for ch in text) or not ALLOWED_RE.match(text):
            errs.append("%s: foreign/unexpected glyph in %r" % (tag, text))
        if re.search("[฀-๿] +[฀-๿]", text):
            errs.append("%s: space between Thai characters in %r" % (tag, text))
        if not text.strip():
            errs.append("%s: empty" % tag)
        nw = count_words(text, tokenizer)
        if nw > MAX_WORDS:
            errs.append("%s: %d words > %d in %r" % (tag, nw, MAX_WORDS, text))
        if visible_len(text) > MAX_CHARS:
            errs.append("%s: %d chars > %d in %r" % (tag, visible_len(text), MAX_CHARS, text))
        if k + 1 < len(cues):
            gap = cues[k + 1]["start"] - c["end"]
            if gap < 0:
                errs.append("%s: overlaps next by %.3fs" % (tag, -gap))
            elif gap < MIN_GAP - 1e-6:
                errs.append("%s: gap %.3fs < %.3fs" % (tag, gap, MIN_GAP))
    if speech_start is not None and cues[0]["start"] < speech_start - 1e-6:
        errs.append("first cue %.3fs before speech start %.3fs" % (cues[0]["start"], speech_start))
    if cues[-1]["end"] > end_limit + 1e-6:
        errs.append("last cue end %.3fs > %.1fs" % (cues[-1]["end"], end_limit))
    return errs


def validate_file(path, speech_start=None, end_limit=END_LIMIT):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    if raw.startswith("﻿"):
        raw = raw[1:]
    return validate_cues(parse_srt(raw), speech_start, end_limit)


# ---------------------------------------------------------------- job build
def load_passes(ws, n):
    passes = {}
    with open(os.path.join(ws, "asr", "job%d.json" % n), encoding="utf-8") as f:
        for k, v in json.load(f)["passes"].items():
            passes[k] = v["segments"]
    regions = []
    ex = os.path.join(ws, "asr", "job%d_extra.json" % n)
    if os.path.exists(ex):
        with open(ex, encoding="utf-8") as f:
            e = json.load(f)
        passes.update(e["passes"])
        regions = merge_regions(e.get("vad_raw", []) + e.get("vad_voice", []))
    return passes, regions


def merge_regions(rs):
    out = []
    for a, b in sorted(rs):
        if out and a <= out[-1][1] + 0.05:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def build_job(ws, n, tokenizer=None):
    with open(os.path.join(ws, "srt", "job%d.curation.json" % n), encoding="utf-8") as f:
        cur = json.load(f)
    passes, regions = load_passes(ws, n)
    pw = []
    for p in cur["phrases"]:
        segs = passes[p["src"]] if p.get("src") else []
        src = source_chars(segs, p["t0"], p["t1"], p.get("win")) if segs else []
        timed = align_times(p["text"], src, p["t0"], p["t1"])
        words = phrase_words(p["text"], timed, tokenizer)
        for bad in lint_phrase(p["text"], tokenizer):
            print("  lint job %d: chunk %r exceeds one cue (split mid-chunk)" % (n, bad))
        p["_start"], p["_end"] = words[0]["start"], words[-1]["end"]
        pw.append(words)
    use_vad = cur.get("vad_clamp", True)
    cues = build_cues(pw, regions if use_vad else None, tokenizer=tokenizer)
    speech_start = regions[0][0] if regions else None
    out = os.path.join(ws, "srt", "job%d.srt" % n)
    write_srt(out, cues)
    errs = validate_file(out, speech_start=None)
    if speech_start is not None and cues and cues[0]["start"] < speech_start - 1e-6:
        errs.append("first cue before VAD speech start %.2f" % speech_start)
    write_curation_md(ws, n, cur, cues, regions, errs)
    return cur, cues, errs


def plain(text):
    """Readable transcript form: Thai joined within each "|" group (spaces only around
    Latin), one space between groups."""
    return " ".join(join_display(g.split()) for g in text.split("|") if g.strip())


def _ts(t):
    m, s = divmod(t, 60)
    return "%02d:%05.2f" % (int(m), s)


def write_curation_md(ws, n, cur, cues, regions, errs):
    L = ["# Job %d curation log" % n, ""]
    if cur.get("summary"):
        L += [cur["summary"], ""]
    L += ["Times are WAV/timeline-relative seconds (t=0 = timeline start).", "",
          "## Final text (curated phrases)", ""]
    for p in cur["phrases"]:
        L.append("- [%s-%s] %s  (src: %s%s)" % (_ts(p["_start"]), _ts(p["_end"]), plain(p["text"]),
                                               p.get("src") or "linear",
                                               ", win %s" % p["win"] if p.get("win") is not None else ""))
        if p.get("note"):
            L.append("  - note: %s" % p["note"])
    L += ["", "## Changes vs ASR", ""]
    L += ["- " + c for c in cur.get("changes", [])] or ["- none"]
    L += ["", "## Omitted / unresolved spans", ""]
    om = cur.get("omitted", [])
    L += ["- [%s-%s] %s" % (_ts(o["t0"]), _ts(o["t1"]), o["reason"]) for o in om] or ["- none"]
    L += ["", "## Uncertain terms", ""]
    un = cur.get("uncertain", [])
    L += ["- %s @%s: %s" % (u["term"], _ts(u["t"]), u.get("note", "")) for u in un] or ["- none"]
    L += ["", "## Cues (%d)" % len(cues), "", "| # | start | end | dur | text |", "|---|---|---|---|---|"]
    for k, c in enumerate(cues, 1):
        L.append("| %d | %.3f | %.3f | %.2f | %s |" % (k, c["start"], c["end"], c["end"] - c["start"], c["text"]))
    L += ["", "VAD speech regions (raw+voice union): " +
          ", ".join("%.2f-%.2f" % (a, b) for a, b in regions), "",
          "Validator: " + ("PASS" if not errs else "FAIL: " + "; ".join(errs)), ""]
    with open(os.path.join(ws, "srt", "job%d.curation.md" % n), "w", encoding="utf-8") as f:
        f.write("\n".join(L))


def write_transcripts(ws, results):
    L = ["# Clean transcripts (FreeTalk_1, 10 jobs)", "",
         "Curated from 4 draft ASR passes + overlapping-window re-transcription. "
         "`[ไม่ชัด a-b s]` marks speech omitted as unresolvable; see job<N>.curation.md.", ""]
    for n, cur in results:
        L += ["## Job %d" % n, ""]
        items = [(p["_start"], plain(p["text"])) for p in cur["phrases"]]
        items += [(o["t0"], "[ไม่ชัด %.1f-%.1f s]" % (o["t0"], o["t1"])) for o in cur.get("omitted", [])]
        for t, txt in sorted(items):
            L.append("- %s %s" % (_ts(t), txt))
        L.append("")
    with open(os.path.join(ws, "srt", "transcripts.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("workspace")
    b.add_argument("--jobs")
    v = sub.add_parser("validate")
    v.add_argument("srt")
    v.add_argument("--speech-start", type=float)
    v.add_argument("--end", type=float, default=END_LIMIT)
    a = ap.parse_args()
    if a.cmd == "validate":
        errs = validate_file(a.srt, a.speech_start, a.end)
        print("PASS" if not errs else "\n".join(errs))
        sys.exit(1 if errs else 0)
    jobs = range(1, 11) if not a.jobs else [int(x) for x in a.jobs.split(",")]
    results, bad = [], 0
    for n in jobs:
        cur, cues, errs = build_job(a.workspace, n)
        results.append((n, cur))
        bad += bool(errs)
        print("job %d: %d cues, %s" % (n, len(cues), "PASS" if not errs else "FAIL " + "; ".join(errs)))
    if not a.jobs:
        write_transcripts(a.workspace, results)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
