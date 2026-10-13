import os, sys, glob, site
for _sp in [p for p in sys.path if p.endswith("site-packages")]:
    for _d in glob.glob(os.path.join(_sp, "nvidia", "*", "bin")):
        os.add_dll_directory(_d); os.environ["PATH"] = _d + os.pathsep + os.environ["PATH"]
import os, sys, json, re, subprocess, unicodedata, wave
import numpy as np
from faster_whisper import WhisperModel
from pythainlp.tokenize import word_tokenize
W = os.environ["PW"]; FF = os.environ.get("FFMPEG", "ffmpeg")
FPS = 60.0; MAXW = 3; MAXCH = 14; MAXD = 1.5; GAP = 2 / FPS; PAUSE = 0.7
offs = json.load(open(os.path.join(W, "offs.json"), encoding="utf-8"))
only = [int(x) for x in sys.argv[1:]] or [o["i"] for o in offs]
os.makedirs(os.path.join(W, "asr"), exist_ok=True)
model = WhisperModel(os.environ.get("WM", "large-v3"), device=os.environ.get("WD", "cuda"), compute_type=os.environ.get("WC", "float16"))

def keep(segs):
    out = []
    for i, sg in enumerate(segs):
        rep = sum(1 for x in segs if x.text.strip() == sg.text.strip()) >= 3
        if rep or sg.no_speech_prob > 0.6 or sg.avg_logprob < -1.0: continue
        out.append(sg)
    return out

def load(path):
    with wave.open(path) as f: raw = f.readframes(f.getnframes())
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0

def bad_script(c):
    n = unicodedata.name(c, "")
    return any(k in n for k in ("HANGUL", "CJK", "HIRAGANA", "KATAKANA", "CYRILLIC", "ARABIC", "DEVANAGARI"))

def thai(c): return "\u0e00" <= c <= "\u0e7f"
def latin(c): return c.isascii() and c.isalpha()
MARK = re.compile("[\u0e31\u0e34-\u0e3a\u0e47-\u0e4e]")

def build_words(segs, dur):
    chars = []   # (char, t0, t1)
    for sg in segs:
        toks = sg.words or []
        for w in toks:
            txt = w.word; n = len(txt) or 1
            for k, c in enumerate(txt):
                chars.append((c, w.start + (w.end - w.start) * k / n, w.start + (w.end - w.start) * (k + 1) / n))
    chars = [c for c in chars if not bad_script(c[0])]
    text = "".join(c[0] for c in chars)
    words = []; cur = 0
    for tok in word_tokenize(text, engine="newmm", keep_whitespace=True):
        i = text.find(tok, cur)
        if i < 0: continue
        cur = i + len(tok)
        if not tok.strip(): continue
        words.append([tok, chars[i][1], chars[cur - 1][2]])
    merged = []
    for w in words:
        t = w[0]
        punct = all(unicodedata.category(c).startswith("P") for c in t)
        lone = len(t) == 1 and thai(t) and t != "ๆ"
        if merged and (t == "ๆ" or punct or lone or MARK.match(t[0])):
            merged[-1][0] += t; merged[-1][2] = w[2]
        else: merged.append(w)
    return merged

def join(ws):
    out = ""
    for w in ws:
        if out and (latin(out[-1]) != latin(w[0][0]) and (latin(out[-1]) or latin(w[0][0])) and w[0][0] not in ".,!?"): out += " "
        elif out and latin(out[-1]) and latin(w[0][0]): out += " "
        out += w[0]
    return out

def blocks(words, end_t):
    res = []; cur = []
    def flush():
        nonlocal cur
        if cur: res.append(cur); cur = []
    for w in words:
        if cur:
            pause = w[1] - cur[-1][2]
            cand = cur + [w]
            if len(cur) >= MAXW or pause >= PAUSE or len(join(cand).replace(" ", "")) > MAXCH or (w[2] - cur[0][1]) > MAXD + 0.6: flush()
        cur.append(w)
    flush()
    cues = []
    for i, b in enumerate(blocks_ := res):
        s = b[0][1]; e = min(b[-1][2], s + MAXD)
        nxt = blocks_[i + 1][0][1] if i + 1 < len(blocks_) else end_t
        e = min(e, nxt - GAP, end_t - GAP)
        if e - s < 0.25: e = min(s + 0.35, nxt - GAP)
        if e <= s: continue
        cues.append((s, e, join(b)))
    return cues

def ts(t):
    t = max(0.0, t); ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)

report = {}
for o in offs:
    N = o["i"]
    if N not in only: continue
    wav = os.path.join(W, "asr", "T%d.wav" % N); dur = (o["e"] - o["s"]) / FPS
    subprocess.run([FF, "-y", "-v", "error", "-ss", str(o["ss"] / o["src_fps"]), "-t", str(dur), "-i", o["src"], "-vn", "-ac", "1", "-ar", "16000", wav], check=True)
    best = None
    for tag, af in (("raw", None), ("voice", "highpass=f=80,lowpass=f=7000,afftdn=nf=-25,dynaudnorm=f=150:g=15:p=0.7")):
        w2 = wav
        if af:
            w2 = os.path.join(W, "asr", "T%d_v.wav" % N); subprocess.run([FF, "-y", "-v", "error", "-i", wav, "-af", af, w2], check=True)
        segs, info = model.transcribe(load(w2), language="th", word_timestamps=True, beam_size=5, temperature=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0], condition_on_previous_text=False, vad_filter=True, vad_parameters={"min_silence_duration_ms": 400, "speech_pad_ms": 200})
        segs = keep(list(segs)); lp = sum(s.avg_logprob for s in segs) / max(1, len(segs)) if segs else -9.0; txt = "".join(s.text for s in segs)
        th = sum(thai(c) for c in txt); fo = sum(1 for c in txt if c.isalpha() and not thai(c) and not latin(c)); ratio = fo / max(1, th + fo)
        print("T%d %s segs=%d avg_logprob=%.2f thai=%d foreign_ratio=%.2f" % (N, tag, len(segs), lp, th, ratio), flush=True)
        if best is None or len(segs) > len(best[2]): best = (lp, tag, segs, ratio)
        print('   ', ' | '.join(x.text.strip() for x in segs)[:260], flush=True)
        if len(segs) >= 4: break
    lp, tag, segs, ratio = best
    cues = blocks(build_words(segs, dur), dur) if segs else []
    srt = os.path.join(W, "asr", "T%d.srt" % N)
    open(srt, "w", encoding="utf-8").write("\n".join("%d\n%s --> %s\n%s\n" % (i + 1, ts(s), ts(e), t) for i, (s, e, t) in enumerate(cues)))
    report[N] = dict(tag=tag, avg_logprob=round(lp, 2), foreign_ratio=round(ratio, 3), cues=len(cues), first=cues[0][2] if cues else None, kept_segs=len(segs))
    print("T%d -> %d cues via %s" % (N, len(cues), tag), flush=True)
    json.dump(report, open(os.path.join(W, "asr", "report_%s.json" % "_".join(map(str, only))), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
