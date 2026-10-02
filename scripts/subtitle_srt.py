"""Thai short-form SRT builder and validator.

Build (per job, from a hand-curated phrase list aligned onto ASR character times):
    python scripts/subtitle_srt.py build WORKSPACE [--jobs 1,2]
Validate an SRT:
    python scripts/subtitle_srt.py validate FILE.srt [--speech-start S] [--end 55 | --workspace WS --job N]

The end limit of every job is its `duration_s` in WORKSPACE/jobs.json (END_LIMIT only
when jobs.json has no entry), so clips of different lengths need no code change.

Curation input: WORKSPACE/srt/job<N>.curation.json
    {"job": 1,
     "phrases": [{"text": "แล้วก็วันนี้ ก็ชิวๆ", "t0": 3.0, "t1": 7.2,
                  "src": "raw_chunk", "win": null, "note": "..."}],
     "omitted": [{"t0": 0.3, "t1": 3.0, "reason": "..."}],
     "uncertain": [{"term": "...", "t": 12.0, "note": "..."}],
     "changes": ["..."],
     "custom_words": ["..."],   # optional extra one-word proper nouns for the tokenizer
     "vad_clamp": true}         # optional; false = silero misses this job's speech (no VAD
                                # snapping, no VAD speech-start check; use inspect check)
A phrase may carry "split_before": true - its first word never shares a cue with the
previous phrase (no DP join, no readable-floor merge across that boundary).
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
CUSTOM_WORDS = {"ไทกะ", "โกโกนอล", "ฟรีทอล์ค"}
_TRIE = None


BASE_CUSTOM_WORDS = frozenset(CUSTOM_WORDS)
COUNT_MAIYAMOK = False      # opt-in rule, see set_job_rules / job_rules
RULES_FILE = "subtitle_rules.json"   # optional WORKSPACE/subtitle_rules.json: {"count_maiyamok": true}


def set_job_rules(custom_words=(), count_maiyamok=False):
    """Per-job word-count state: the base proper nouns plus THIS job's custom_words only
    (no leak from earlier jobs of the same run), and the opt-in count_maiyamok rule."""
    global _TRIE, COUNT_MAIYAMOK
    want = set(BASE_CUSTOM_WORDS) | set(custom_words or ())
    if want != CUSTOM_WORDS:
        CUSTOM_WORDS.clear()
        CUSTOM_WORDS.update(want)
        _TRIE = None
    COUNT_MAIYAMOK = bool(count_maiyamok)


def job_rules(ws, n):
    """(custom_words, count_maiyamok) of a job. count_maiyamok comes from the job's
    curation JSON key "count_maiyamok" if present, else from WORKSPACE/subtitle_rules.json,
    else False (the historical rule)."""
    rules = {}
    rp = os.path.join(ws, RULES_FILE)
    if os.path.exists(rp):
        with open(rp, encoding="utf-8") as f:
            rules.update(json.load(f))
    cp = os.path.join(ws, "srt", "job%d.curation.json" % n)
    cur = {}
    if os.path.exists(cp):
        with open(cp, encoding="utf-8") as f:
            cur = json.load(f)
    cm = cur["count_maiyamok"] if "count_maiyamok" in cur else rules.get("count_maiyamok", False)
    return cur.get("custom_words", []), bool(cm)


def add_custom_words(words):
    """Register extra one-word proper nouns (per job curation); rebuilds the tokenizer trie."""
    global _TRIE
    new = set(words or ()) - CUSTOM_WORDS
    if new:
        CUSTOM_WORDS.update(new)
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


# Natural-word rule for the "<= 3 short words" cap (house style counts words a Thai
# reader perceives, not tokenizer fragments):
#   * newmm tokens (lone chars, combining marks, punctuation and ๆ already merged);
#   * a SUFFIX token (sentence particle, bound auxiliary/complement or demonstrative)
#     joins the word before it: ไป|แล้ว, บอก|ว่า, มี|นะ|ครับ, เล่า|ให้, คน|นั้น;
#   * a PREFIX token (negation / pre-verbal auxiliary) joins the word after it:
#     ไม่|มี, ไม่|ได้, ไม่|ใช่, จะ|ไป, ก็|ได้, ยัง|ไม่มี.
# Suffixes are merged first, then prefixes, so ไม่|มี|นะ|ครับ is one natural word.
# A prefix/suffix with nothing to attach to stays a word of its own.
SUFFIX_WORDS = {
    "ครับ", "ค่ะ", "คะ", "ค่า", "ฮะ", "จ้ะ", "จ้า", "นะ", "น่ะ", "นะคะ", "นะครับ", "เลย",
    "อ่ะ", "อะ", "ล่ะ", "ละ", "ป่ะ", "ปะ", "เว้ย", "วะ", "ว่ะ", "แหละ", "หรอ", "เหรอ",
    "เนี่ย", "เนี้ย", "ไหม", "มั้ย", "หรอก", "ด้วย", "แล้ว", "ว่า", "ได้", "ไป", "มา",
    "กัน", "อีก", "เอง", "หน่อย", "สิ", "ซิ", "ดิ", "ให้", "อยู่", "ไว้", "นั้น", "นี้", "นี่"}
PREFIX_WORDS = {"ไม่", "จะ", "ก็", "ยัง", "ต้อง", "กำลัง", "ได้"}


def natural_words(text, tokenizer=None):
    toks = split_words(text, tokenizer)
    words = []
    for t in toks:  # suffixes attach backwards
        if words and t in SUFFIX_WORDS and words[-1] not in PREFIX_WORDS - {"ได้"}:
            words[-1] += t
        else:
            words.append(t)
    out, pend = [], ""
    for w in words:  # prefixes attach forwards
        if w in PREFIX_WORDS:
            pend += w
        else:
            out.append(pend + w)
            pend = ""
    if pend:
        out.append(pend)
    return out


def spoken_tokens(text, tokenizer=None):
    """count_maiyamok view of the tokens: every ๆ repeats its word (ต่อๆ -> ต่อ ต่อ) and a
    leading negation/auxiliary is split off (ไม่เอา -> ไม่ เอา), so spoken repeats show."""
    out = []
    for t in split_words(text, tokenizer):
        base = t.replace("ๆ", "").replace(" ", "")
        for _ in range(1 + t.count("ๆ")):
            pre = [p for p in PREFIX_WORDS if base.startswith(p) and len(base) > len(p)]
            out += [pre[0], base[len(pre[0]):]] if pre else [base]
    return out


def count_words(text, tokenizer=None):
    """Natural words (see the rule above SUFFIX_WORDS). Stutter/repetition rule: if any
    token occurs more than once in the text (ไม่ไม่ไม่ใช่, ไม่มีอะไรอ่ะไม่มี, ลืมลืม), every
    token counts individually (no attachment), so repeats are never hidden in one word.
    With COUNT_MAIYAMOK (opt-in per job) the check runs on spoken_tokens, so ต่อๆได้ๆ is
    4 words and ไม่เอาไม่ต้องแล้ว is 5."""
    if COUNT_MAIYAMOK:
        sp = spoken_tokens(text, tokenizer)
        if len(set(sp)) < len(sp):
            return len(sp)
    toks = split_words(text, tokenizer)
    if len(set(toks)) < len(toks):
        return len(toks)
    return len(natural_words(text, tokenizer))


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
TARGET_MIN = 0.8        # typical cue length band (house ruling: 0.8-1.3 s, avg ~1.0-1.3)
TARGET_MAX = 1.3
PHRASE_JOIN_GAP = 0.25  # adjacent curated phrases may share a cue only across a gap < this


def segment_words(words, tokenizer=None, max_words=MAX_WORDS, max_chars=MAX_CHARS, max_dur=MAX_DUR,
                  gaps=(), omitted=()):
    """DP split of a word sequence (one or more curated phrases) into cues.

    Hard breaks: word gap >= PAUSE_BREAK, a VAD silence >= PAUSE_BREAK between two word
    midpoints, an omitted span between two words, or a curated-phrase boundary (a sentence
    end) with gap >= PHRASE_JOIN_GAP. Limits: <= max_words natural words, <= max_chars
    visible chars, word span <= max_dur. Cost: 1 per cue (fewer, longer cues preferred),
    plus a penalty for cues shorter than TARGET_MIN or longer than TARGET_MAX, a penalty
    for splitting inside a curator chunk, and a large one for cutting a prefix/suffix
    (ไม่|มี, มี|ครับ) away from its head. Returns list of word lists."""
    n = len(words)

    def pause_after(k):
        a, b = words[k], words[k + 1]
        gap = b["start"] - a["end"]
        if b.get("split_before"):
            return True          # curator forced a cue break before this phrase
        if gap >= PAUSE_BREAK:
            return True
        if b.get("phrase") != a.get("phrase") and gap >= PHRASE_JOIN_GAP:
            return True          # curated phrases join only across a short gap
        m0 = (a["start"] + a["end"]) / 2
        m1 = (b["start"] + b["end"]) / 2
        if any(m0 <= g0 and g1 <= m1 + 0.3 for g0, g1 in gaps):
            return True
        return any(m0 < (o0 + o1) / 2 < m1 for o0, o1 in omitted)

    def split_cost(i):  # cost of a cue boundary before words[i]
        if i == 0 or i == n:
            return 0.0
        prev, cur = words[i - 1]["text"], words[i]["text"]
        cost = 0.0
        if (prev in PREFIX_WORDS or cur in SUFFIX_WORDS) and not words[i]["boundary"]:
            cost += 3.0          # cutting a prefix/particle off its head inside a chunk
        if words[i].get("phrase") == words[i - 1].get("phrase"):
            if not words[i]["boundary"]:
                cost += 5.0          # inside a curator chunk
            elif not words[i].get("hard"):
                cost += 0.3          # at a space; "|" boundaries are free
        return cost

    def join_cost(grp):  # crossing a curated-phrase boundary (rescue only) or a "|" in one cue
        return sum(3.5 if a.get("phrase") != b.get("phrase") else 1.5 if b.get("hard") else 0.0
                   for a, b in zip(grp, grp[1:]))

    best = [None] * (n + 1)
    best[0] = (0.0, None)
    for j in range(1, n + 1):
        for i in range(j - 1, -1, -1):
            if i < j - 1 and pause_after(i):
                break
            grp = words[i:j]
            txt = join_display([w["text"] for w in grp])
            span = grp[-1]["end"] - grp[0]["start"]
            if j - i > 1 and (count_words(txt, tokenizer) > max_words or visible_len(txt) > max_chars
                              or span > max_dur):
                break
            if best[i] is None:
                continue
            cost = best[i][0] + 1.0 + split_cost(j) + join_cost(grp)
            if span < TARGET_MIN:
                cost += 3.0 * (TARGET_MIN - span)
            elif span > TARGET_MAX:
                cost += 0.5 * (span - TARGET_MAX)
            if best[j] is None or cost < best[j][0]:
                best[j] = (cost, i)
    groups, j = [], n
    while j > 0:
        i = best[j][1]
        groups.append(words[i:j])
        j = i
    return groups[::-1]


LINGER = 0.08           # a cue may stay at most this long after its speech end (rule: <= 0.1 s)
VAD_TAIL = 0.4          # speech end may follow the VAD region past the last word by this much


def speech_end(last, start, regions):
    """End of the speech of a cue: its (VAD-snapped) last word end, extended to the end of
    the VAD region containing that word when the region ends within VAD_TAIL."""
    end = last
    for r in regions or ():
        if r[0] <= end <= r[1] + 1e-6:
            if r[1] - end <= VAD_TAIL:
                end = r[1]
            break
    return max(end, start + 0.05)


def build_cues(phrases_words, regions=None, end_limit=END_LIMIT, tokenizer=None, omitted=(),
               attach_skip_omitted=False):
    """Cues hug the speech: start at the first word (snapped into VAD speech), end at the
    speech end + LINGER at most. No padding, no minimum duration. attach_skip_omitted: VAD
    speech logged as omitted is never attached to a neighbouring cue (opt-in per job)."""
    words = []
    for pi, pw in enumerate(phrases_words):
        for w in pw:
            words.append(dict(w, phrase=pi))
    words.sort(key=lambda w: w["start"])
    gaps = silence_gaps(regions, PAUSE_BREAK) if regions else ()
    cues = []
    for grp in segment_words(words, tokenizer, gaps=gaps, omitted=[(o["t0"], o["t1"]) for o in omitted]):
        start, end = clamp_to_speech(grp[0], grp[-1], regions)
        se = speech_end(end, start, regions)
        cue = {"text": join_display([w["text"] for w in grp]), "start": start, "end": se,
               "speech_end": se, "speech_start": start,
               "phrases": {w["phrase"] for w in grp}}
        if grp[0].get("split_before"):
            cue["split_before"] = True
        cues.append(cue)
    cues = sorted((c for c in cues if c["start"] < end_limit - 0.2), key=lambda c: c["start"])
    for k, c in enumerate(cues):
        nxt = cues[k + 1]["start"] if k + 1 < len(cues) else end_limit + MIN_GAP
        c["end"] = min(c["speech_end"] + LINGER, c["start"] + MAX_DUR, nxt - MIN_GAP, end_limit)
        c["start"] = round(c["start"], 3)
        c["end"] = round(c["end"], 3)
        c["speech_start"] = c["start"]
    if regions:
        attach_adjacent_speech(cues, regions, end_limit, omitted if attach_skip_omitted else ())
        snap_start_into_speech(cues, regions)
    enforce_floor(cues, end_limit, tokenizer)
    return cues


SNAP_MAX = 0.3          # ASR may time a word up to this much before the VAD speech onset


def snap_start_into_speech(cues, regions, max_shift=SNAP_MAX):
    """A cue starting in VAD silence (> EARLY_TOL before the next speech onset) whose onset
    follows within max_shift starts at that onset instead (ruling R7 measured against VAD:
    Whisper word times run early by ~0.1-0.3 s). Larger offsets are left for curation to
    resolve or justify. If the cue would then be under 0.1 s its end moves later too (never
    into the next cue); the readable floor is applied afterwards."""
    for k, c in enumerate(cues):
        if any(r[0] - EARLY_TOL <= c["start"] < r[1] for r in regions):
            continue
        nxt = [r[0] for r in regions if r[0] > c["start"]]
        if not nxt or nxt[0] - c["start"] > max_shift + 1e-9:
            continue
        limit = cues[k + 1]["start"] - MIN_GAP if k + 1 < len(cues) else c["end"] + max_shift
        end = min(max(c["end"], nxt[0] + 0.1), limit)
        if end - nxt[0] < 0.05:
            continue
        c["start"] = round(nxt[0], 3)
        c["speech_start"] = c["start"]
        if end > c["end"]:
            c["end"] = round(end, 3)
            c["speech_end"] = max(c["speech_end"], c["end"])


READ_FLOOR = 0.35       # ruling R6: no cue shorter than this unless neighbours block it
BORROW_MAX = 0.2        # max delay of a neighbour's start past its first word (floor room)
EARLY_TOL = 0.05        # ruling R7: no cue may start more than this before its speech


def _fits(text, span, tokenizer=None):
    return (count_words(text, tokenizer) <= MAX_WORDS and visible_len(text) <= MAX_CHARS
            and span <= MAX_DUR + 1e-9)


def _end_cap(c, end_limit):
    """Latest end allowed: speech end + LINGER, or start + READ_FLOOR for a floor cue."""
    return min(max(c["speech_end"] + LINGER, c["start"] + READ_FLOOR), c["start"] + MAX_DUR, end_limit)


def _extend_end(cues, j, amt, end_limit, depth=0):
    """Move cue j's end later by up to amt (free gap first, then by delaying the next cue's
    start). Returns the amount gained. A start is never moved earlier (ruling R7)."""
    c = cues[j]
    amt = min(amt, _end_cap(c, end_limit) - c["end"])
    if amt <= 1e-6:
        return 0.0
    nxt = cues[j + 1]["start"] if j + 1 < len(cues) else end_limit + MIN_GAP
    free = nxt - MIN_GAP - c["end"]
    if free < amt and j + 1 < len(cues) and depth < 4:
        _delay_start(cues, j + 1, amt - max(free, 0.0), end_limit, depth + 1)
        free = cues[j + 1]["start"] - MIN_GAP - c["end"]
    take = max(0.0, min(amt, free))
    c["end"] = round(c["end"] + take, 3)
    return take


def _delay_start(cues, j, amt, end_limit, depth=0):
    """Delay cue j's start by up to amt, never more than BORROW_MAX after its first word and
    never leaving it shorter than READ_FLOOR (its end may move later to compensate)."""
    c = cues[j]
    amt = min(amt, c["speech_start"] + BORROW_MAX - c["start"])
    if amt <= 1e-6:
        return 0.0
    slack = (c["end"] - c["start"]) - READ_FLOOR
    if slack < amt:
        _extend_end(cues, j, amt - max(slack, 0.0), end_limit, depth)
        slack = (c["end"] - c["start"]) - READ_FLOOR
    amt = max(0.0, min(amt, slack))
    c["start"] = round(c["start"] + amt, 3)
    return amt


def enforce_floor(cues, end_limit=END_LIMIT, tokenizer=None):
    """Readable floor (ruling R6) under the no-early-start rule (ruling R7). A cue shorter than
    READ_FLOOR is (a) merged with an adjacent cue of the same phrase or across a gap
    < PHRASE_JOIN_GAP when the merged cue still obeys the word/char/duration caps (the
    shorter result wins), else (b) its end is extended to start + READ_FLOOR into the free
    gap, and if the next cue blocks, that cue's start is delayed (<= BORROW_MAX after its
    first word, keeping it >= READ_FLOOR, cascading). No start ever moves earlier; a cue
    still short afterwards is blocked on both sides and stays short. Cues never overlap."""
    k = 0
    while k < len(cues):
        c = cues[k]
        if c["end"] - c["start"] >= READ_FLOOR - 1e-9:
            k += 1
            continue
        opts = []
        for j in (k - 1, k + 1):
            if not 0 <= j < len(cues):
                continue
            a, b = (cues[j], c) if j < k else (c, cues[j])
            gap = b["start"] - a["end"]
            if b.get("split_before"):
                continue         # curator-forced break (phrase "split_before")
            if not (a.get("phrases", set()) & b.get("phrases", set()) or gap < PHRASE_JOIN_GAP):
                continue
            text = join_display([a["text"], b["text"]])
            if _fits(text, b["end"] - a["start"], tokenizer):
                opts.append((b["end"] - a["start"], j, text))
        if opts:
            _, j, text = min(opts)
            a, b = (cues[j], c) if j < k else (c, cues[j])
            merged = {"text": text, "start": a["start"], "end": b["end"],
                      "speech_start": a["speech_start"],
                      "speech_end": max(a["speech_end"], b["speech_end"]),
                      "phrases": a.get("phrases", set()) | b.get("phrases", set())}
            if a.get("split_before"):
                merged["split_before"] = True
            lo = min(j, k)
            cues[lo:lo + 2] = [merged]
            k = max(lo - 1, 0)
            continue
        if _extend_end(cues, k, READ_FLOOR - (c["end"] - c["start"]), end_limit) > 0:
            c["floor"] = True
        if c["end"] - c["start"] < READ_FLOOR - 1e-9:
            c["short_reason"] = short_reason(cues, k, end_limit)
        k += 1


def short_reason(cues, k, end_limit=END_LIMIT):
    """Why cue k could not reach READ_FLOOR (it may not start earlier, ruling R7)."""
    c = cues[k]
    if k + 1 >= len(cues):
        return "timeline end %.2f s" % end_limit
    n = cues[k + 1]
    why = []
    if n["start"] >= n.get("speech_start", n["start"]) + BORROW_MAX - 1e-3:
        why.append("already delayed %.2f s past its first word" % (n["start"] - n["speech_start"]))
    if n["end"] - n["start"] <= READ_FLOOR + 1e-3:
        why.append("a %.2f s cue with no room" % (n["end"] - n["start"]))
    if not why:
        why.append("its end is capped (linger/1.5 s/next cue)")
    return "next cue %r at %.3f is %s" % (n["text"], n["start"], " and ".join(why))


ATTACH_GAP = 0.35       # VAD speech this close to a cue edge belongs to that cue's words
ATTACH_MAX = 1.0        # ... if the uncaptioned piece is at most this long


def attach_adjacent_speech(cues, regions, end_limit=END_LIMIT, omitted=()):
    """Word times from ASR are approximate at phrase edges. An uncaptioned VAD speech piece
    that touches (within ATTACH_GAP) a cue start or end and is <= ATTACH_MAX long is that
    cue's own first/last word: extend the cue edge onto it (start earlier / end later),
    never past the neighbouring cues, MAX_DUR or end_limit. Pieces further away stay
    uncovered and must be logged. A piece mostly inside an `omitted` span is speech the
    curator could not resolve, not the cue's own word, and is left alone."""
    for _ in range(2):
        for x, y, why in uncovered_speech(regions, cues, omitted, min_len=0.05):
            if y - x > ATTACH_MAX or why:
                continue
            for k, c in enumerate(cues):
                prv = cues[k - 1]["end"] + MIN_GAP if k > 0 else 0.0
                nxt = cues[k + 1]["start"] - MIN_GAP if k + 1 < len(cues) else end_limit
                if 0 <= c["start"] - y <= ATTACH_GAP and c["start"] > prv:
                    c["start"] = round(max(x, prv, c["end"] - MAX_DUR), 3)
                    c["speech_start"] = min(c.get("speech_start", c["start"]), c["start"])
                    break
                if 0 <= x - c["end"] <= ATTACH_GAP and c["end"] < nxt:
                    new = round(min(y, nxt, c["start"] + MAX_DUR), 3)
                    c["speech_end"] = max(c["speech_end"], new)
                    c["end"] = new
                    break


def uncovered_speech(regions, cues, omitted=(), min_len=0.3):
    """VAD speech not shown by any cue: [(a, b, logged_reason_or_None)] for pieces >= min_len.
    A piece counts as logged when an omitted span covers at least half of it."""
    out = []
    for a, b in regions or ():
        pieces = [[a, b]]
        for c in cues:
            nxt = []
            for x, y in pieces:
                if c["end"] <= x or c["start"] >= y:
                    nxt.append([x, y])
                    continue
                if c["start"] > x:
                    nxt.append([x, c["start"]])
                if c["end"] < y:
                    nxt.append([c["end"], y])
            pieces = nxt
        for x, y in pieces:
            if y - x < min_len:
                continue
            why = None
            for o in omitted:
                if min(y, o["t1"]) - max(x, o["t0"]) >= 0.5 * (y - x):
                    why = o["reason"]
                    break
            out.append((round(x, 2), round(y, 2), why))
    return out


def cue_speech_checks(cues, regions):
    """Linger, early/late-start and no-speech checks needing word/VAD times (build-time).
    Start: never > EARLY_TOL before the cue's first word/VAD speech (R7), never > BORROW_MAX
    after it.
    Linger is strict (<= 0.1 s after speech) for every cue longer than READ_FLOOR; a cue of
    at most READ_FLOOR may linger (ruling R6: the readable floor beats the linger limit, and
    only floor handling can make such a short cue outlast its speech)."""
    errs = []
    for k, c in enumerate(cues, 1):
        if c["end"] > c["speech_end"] + 0.1 + 1e-6 and c["end"] - c["start"] > READ_FLOOR + 0.002:
            errs.append("cue %d lingers %.2fs after speech" % (k, c["end"] - c["speech_end"]))
        if regions and _overlap(c["start"], c["end"], regions) <= 0:
            errs.append("cue %d %r overlaps no VAD speech" % (k, c["text"]))
        if c["start"] < c["speech_start"] - EARLY_TOL - 1e-6:
            errs.append("cue %d starts %.2fs before its speech" % (k, c["speech_start"] - c["start"]))
        if c["start"] > c["speech_start"] + BORROW_MAX + 1e-6:
            errs.append("cue %d starts %.2fs after its first word" % (k, c["start"] - c["speech_start"]))
    return errs

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


def load_jobs(ws):
    """{job number: job dict} from WORKSPACE/jobs.json ({} when absent)."""
    p = os.path.join(ws, "jobs.json")
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as f:
        return {int(j["job"]): j for j in json.load(f)}


def job_end_limit(ws, n, default=END_LIMIT):
    """A job's last-cue end limit: its duration_s from jobs.json (never a hard-coded 55)."""
    j = load_jobs(ws).get(n)
    return float(j["duration_s"]) if j and j.get("duration_s") else default


def build_job(ws, n, tokenizer=None, end_limit=None):
    with open(os.path.join(ws, "srt", "job%d.curation.json" % n), encoding="utf-8") as f:
        cur = json.load(f)
    if end_limit is None:
        end_limit = job_end_limit(ws, n)
    set_job_rules(*job_rules(ws, n))
    passes, regions = load_passes(ws, n)
    pw = []
    for p in cur["phrases"]:
        segs = passes[p["src"]] if p.get("src") else []
        src = source_chars(segs, p["t0"], p["t1"], p.get("win")) if segs else []
        timed = align_times(p["text"], src, p["t0"], p["t1"])
        words = phrase_words(p["text"], timed, tokenizer)
        if p.get("split_before"):
            words[0]["split_before"] = True
        for bad in lint_phrase(p["text"], tokenizer):
            print("  lint job %d: chunk %r exceeds one cue (split mid-chunk)" % (n, bad))
        p["_start"], p["_end"] = words[0]["start"], words[-1]["end"]
        pw.append(words)
    for a, b in zip(cur["phrases"], cur["phrases"][1:]):
        if b["_start"] < a["_end"] - 0.05:   # words of two phrases would interleave in the cue order
            print("  lint job %d: phrase %r overlaps the previous one by %.2f s (narrow t0/t1)"
                  % (n, b["text"][:20], a["_end"] - b["_start"]))
    use_vad = cur.get("vad_clamp", True)
    cues = build_cues(pw, regions if use_vad else None, end_limit=end_limit, tokenizer=tokenizer,
                      omitted=cur.get("omitted", []),
                      attach_skip_omitted=cur.get("attach_skip_omitted", False))
    # With vad_clamp false the silero map is known to miss this job's speech, so its first
    # onset is no start reference; subtitle_inspect check runs the energy-onset check instead.
    speech_start = regions[0][0] if regions and use_vad else None
    out = os.path.join(ws, "srt", "job%d.srt" % n)
    write_srt(out, cues)
    errs = validate_file(out, speech_start=speech_start, end_limit=end_limit)
    cur["_end_limit"] = end_limit
    ok = {j["text"] for j in cur.get("no_vad_justified", [])}
    errs += [e for e in cue_speech_checks(cues, regions)
             if not ("overlaps no VAD" in e and any(repr(t) in e for t in ok))]
    unc = uncovered_speech(regions, cues, cur.get("omitted", []))
    errs += ["unlogged uncaptioned VAD speech %.2f-%.2f" % (a, b) for a, b, why in unc if not why]
    cur["_uncovered"] = unc
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
    L += ["", "Duration stats: " + fmt_stats(cue_stats(cues))]
    short = [(k, c) for k, c in enumerate(cues, 1) if c.get("short_reason")]
    if short:
        L += ["", "## Cues shorter than %.2f s (blocked)" % READ_FLOOR, ""]
        L += ["- cue %d %s %.3f-%.3f (%.2f s): %s" % (k, c["text"], c["start"], c["end"],
                                                    c["end"] - c["start"], c["short_reason"]) for k, c in short]
    nj = cur.get("no_vad_justified", [])
    if nj:
        L += ["", "## Cues outside VAD speech (justified)", ""]
        L += ["- %s: %s" % (j["text"], j["reason"]) for j in nj]
    unc = cur.get("_uncovered", [])
    L += ["", "## VAD speech not covered by cues (>= 0.3 s)", ""]
    L += ["- [%s-%s] %s" % (_ts(a), _ts(b), ("logged: " + why) if why else "UNLOGGED")
          for a, b, why in unc] or ["- none"]
    L += ["", "VAD speech regions (raw+voice union): " +
          ", ".join("%.2f-%.2f" % (a, b) for a, b in regions), "",
          "End limit (jobs.json duration_s): %.3f s" % cur.get("_end_limit", END_LIMIT),
          "Validator: " + ("PASS" if not errs else "FAIL: " + "; ".join(errs)), ""]
    with open(os.path.join(ws, "srt", "job%d.curation.md" % n), "w", encoding="utf-8") as f:
        f.write("\n".join(L))


def cue_stats(cues):
    import statistics
    d = [c["end"] - c["start"] for c in cues]
    if not d:
        return {"n": 0}
    return {"n": len(d), "mean": statistics.mean(d), "median": statistics.median(d), "min": min(d),
            "max": max(d), "short": sum(1 for x in d if x < READ_FLOOR - 1e-3)}


def fmt_stats(st):
    if not st.get("n"):
        return "no cues"
    return "%d cues, mean %.2f s, median %.2f s, min %.2f s, max %.2f s, %d < %.2f s" % (
        st["n"], st["mean"], st["median"], st["min"], st["max"], st["short"], READ_FLOOR)


def write_summary(ws, built):
    """srt/summary.md: per-job cue stats and every cue under READ_FLOOR with its reason."""
    L = ["# SRT summary", "", "| job | cues | mean | median | min | max | <%.2f s | end limit | validator |"
         % READ_FLOOR, "|---|---|---|---|---|---|---|---|---|"]
    alld = []
    for n, cur, cues, errs in built:
        st = cue_stats(cues)
        alld += cues
        L.append("| %d | %d | %.2f | %.2f | %.2f | %.2f | %d | %.1f | %s |" % (
            n, st["n"], st["mean"], st["median"], st["min"], st["max"], st["short"],
            cur.get("_end_limit", END_LIMIT), "PASS" if not errs else "FAIL"))
    st = cue_stats(alld)
    if st.get("n"):
        L.append("| all | %d | %.2f | %.2f | %.2f | %.2f | %d | | |" % (
            st["n"], st["mean"], st["median"], st["min"], st["max"], st["short"]))
    L += ["", "## Cues shorter than %.2f s" % READ_FLOOR, ""]
    rows = ["- job %d cue %d %s %.3f-%.3f (%.2f s): %s" % (n, k, c["text"], c["start"], c["end"],
                                                         c["end"] - c["start"], c.get("short_reason", "?"))
            for n, _, cues, _ in built for k, c in enumerate(cues, 1)
            if c["end"] - c["start"] < READ_FLOOR - 1e-3]
    L += rows or ["- none"]
    with open(os.path.join(ws, "srt", "summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def write_transcripts(ws, results, title=None):
    title = title or os.path.basename(os.path.normpath(ws))
    L = ["# Clean transcripts (%s, %d jobs)" % (title, len(results)), "",
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
    v.add_argument("--end", type=float, help="end limit s (default: job duration_s, else %.0f)" % END_LIMIT)
    v.add_argument("--workspace", help="read the end limit of --job from WORKSPACE/jobs.json")
    v.add_argument("--job", type=int)
    b.add_argument("--title", help="transcripts.md title (default: workspace folder name)")
    a = ap.parse_args()
    if a.cmd == "validate":
        end = a.end
        if end is None:
            end = job_end_limit(a.workspace, a.job) if a.workspace and a.job else END_LIMIT
        if a.workspace and a.job:   # the job's curated one-word proper nouns count as in build
            set_job_rules(*job_rules(a.workspace, a.job))
        errs = validate_file(a.srt, a.speech_start, end)
        print("PASS" if not errs else "\n".join(errs))
        sys.exit(1 if errs else 0)
    alljobs = sorted(load_jobs(a.workspace)) or list(range(1, 11))
    jobs = alljobs if not a.jobs else [int(x) for x in a.jobs.split(",")]
    results, built, bad = [], [], 0
    for n in jobs:
        cur, cues, errs = build_job(a.workspace, n)
        results.append((n, cur))
        built.append((n, cur, cues, errs))
        bad += bool(errs)
        print("job %d: %s, %s" % (n, fmt_stats(cue_stats(cues)), "PASS" if not errs else "FAIL " + "; ".join(errs)))
    if set(jobs) == set(alljobs):
        write_transcripts(a.workspace, results, a.title)
        write_summary(a.workspace, built)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
