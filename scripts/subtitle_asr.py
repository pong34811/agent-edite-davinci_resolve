"""Draft Thai ASR for subtitle jobs: ffmpeg decode -> faster-whisper -> char-time index.

Usage: python scripts/subtitle_asr.py WORKSPACE [--jobs 1,2] [--model large-v3]
Source media is only read; all outputs are new files under WORKSPACE.
"""
import argparse
import json
import os
import re
import subprocess
import unicodedata

VOICE_FILTER = "highpass=f=80,lowpass=f=7000,afftdn=nf=-25,dynaudnorm=f=150:g=15:p=0.7"
FOREIGN_RE = re.compile(
    "[ᄀ-ᇿ㄰-㆏가-힯"      # Hangul
    "぀-ヿㇰ-ㇿ"                    # Kana
    "⺀-⿟㐀-䶿一-鿿豈-﫿"  # Han
    "Ѐ-ԯ"                                 # Cyrillic
    "؀-ۿݐ-ݿ"                    # Arabic
    "ऀ-ॿ]")                               # Devanagari
THAI_RE = re.compile("[฀-๿]")
COMBINING_RE = re.compile("^[ัิ-ฺ็-๎]")
REPEAT_RE = re.compile(r"(.{1,6}?)\1{5,}")
CHUNK_S = 15
LOW_P = 0.05
LOW_SEG_LOGPROB = -1.0


def is_foreign(ch):
    return bool(FOREIGN_RE.match(ch))


def register_cuda():
    import torch
    lib = os.path.join(os.path.dirname(torch.__file__), "lib")
    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(lib)
    os.environ["PATH"] = lib + os.pathsep + os.environ.get("PATH", "")


def ffmpeg_wav(src, start_s, dur_s, out, voice=False):
    cmd = ["ffmpeg", "-y", "-v", "error", "-ss", str(start_s), "-t", str(dur_s), "-i", src,
           "-vn", "-ac", "1", "-ar", "16000"]
    if voice:
        cmd += ["-af", VOICE_FILTER]
    cmd += ["-c:a", "pcm_s16le", out]
    subprocess.run(cmd, check=True)


def char_index(tokens):
    """tokens: [{word,start,end,probability}] -> per-char dicts with interpolated time."""
    out = []
    for t in tokens:
        w = t["word"]
        if not w:
            continue
        n = len(w)
        dur = max(t["end"] - t["start"], 0.0)
        for i, ch in enumerate(w):
            out.append({"ch": ch,
                        "start": t["start"] + dur * i / n,
                        "end": t["start"] + dur * (i + 1) / n,
                        "p": t.get("probability")})
    return out


def clean_chars(chars):
    """Drop foreign-script chars together with their time spans."""
    return [c for c in chars if not is_foreign(c["ch"])]


def _is_punct_only(s):
    return bool(s) and all(unicodedata.category(c).startswith("P") or c.isspace() for c in s)


def words_from_chars(chars, tokenizer=None):
    text = "".join(c["ch"] for c in chars)
    if tokenizer is None:
        from pythainlp.tokenize import word_tokenize

        def tokenizer(s):
            return word_tokenize(s, engine="newmm")
    words, pos = [], 0
    for tok in tokenizer(text):
        if not tok:
            continue
        seg = chars[pos:pos + len(tok)]
        pos += len(tok)
        if not seg:
            continue
        rec = {"text": tok, "start": seg[0]["start"], "end": seg[-1]["end"]}
        if tok.strip() == "":
            if words:
                words[-1]["text"] += tok
                words[-1]["end"] = rec["end"]
            continue
        lone_thai = len(tok) == 1 and THAI_RE.match(tok)
        if words and (lone_thai or COMBINING_RE.match(tok) or _is_punct_only(tok) or tok == "ๆ"):
            words[-1]["text"] += tok
            words[-1]["end"] = rec["end"]
        else:
            words.append(rec)
    return words


def foreign_ratio(text):
    thai = len(THAI_RE.findall(text))
    other = len([c for c in text if c.isalpha() and not THAI_RE.match(c)])
    return other / (thai + other) if (thai + other) else 0.0


def segment_record(seg):
    toks = [{"word": w.word, "start": round(w.start, 3), "end": round(w.end, 3),
             "probability": round(float(w.probability), 4)} for w in (seg.words or [])]
    chars = char_index(toks)
    foreign = [c for c in chars if is_foreign(c["ch"])]
    cleaned = clean_chars(chars)
    words = words_from_chars(cleaned)
    low = [{"text": t["word"], "start": t["start"], "end": t["end"], "p": t["probability"]}
           for t in toks if t["probability"] < LOW_P and not any(is_foreign(c) for c in t["word"])]
    fr = foreign_ratio(seg.text)
    flags = []
    if seg.avg_logprob < LOW_SEG_LOGPROB:
        flags.append("low_logprob")
    if foreign:
        flags.append("foreign_glyph")
    if fr > 0.12:
        flags.append("foreign_ratio")
    if seg.no_speech_prob > 0.6:
        flags.append("high_no_speech")
    if seg.compression_ratio > 2.4 or REPEAT_RE.search(re.sub(r"\s+", "", seg.text)):
        flags.append("repetition")
    return {
        "start": round(seg.start, 3), "end": round(seg.end, 3), "text": seg.text,
        "clean_text": "".join(c["ch"] for c in cleaned),
        "avg_logprob": round(seg.avg_logprob, 4), "no_speech_prob": round(seg.no_speech_prob, 4),
        "compression_ratio": round(seg.compression_ratio, 3),
        "tokens": toks,
        "words": [{"text": w["text"], "start": round(w["start"], 3), "end": round(w["end"], 3)} for w in words],
        "foreign_glyphs": [{"ch": c["ch"], "start": round(c["start"], 3), "end": round(c["end"], 3)} for c in foreign],
        "foreign_ratio": round(fr, 3),
        "low_prob_tokens": low,
        "flags": flags,
    }


def pass_stats(segs):
    if not segs:
        return {"n_segments": 0, "n_words": 0, "mean_avg_logprob": None, "foreign_glyphs": 0, "flagged": 0, "repetition": 0}
    return {"n_segments": len(segs),
            "repetition": sum(1 for s in segs if "repetition" in s["flags"]),
            "n_words": sum(len(s["words"]) for s in segs),
            "mean_avg_logprob": round(sum(s["avg_logprob"] for s in segs) / len(segs), 4),
            "foreign_glyphs": sum(len(s["foreign_glyphs"]) for s in segs),
            "flagged": sum(1 for s in segs if s["flags"])}


def pass_score(st):
    return (st["mean_avg_logprob"] - 0.05 * st["foreign_glyphs"]
            - 0.5 * st.get("repetition", 0))


def choose_pass(passes):
    """passes: {name: {stats}}. Highest avg_logprob wins (skill rule), penalised for foreign
    glyphs and repetition loops (hallucination loops score a deceptively high logprob), and a
    pass that lost most of the speech is ineligible."""
    live = {k: v for k, v in passes.items() if v["stats"]["mean_avg_logprob"] is not None}
    if not live:
        return None, "no pass produced segments"
    top = max(v["stats"]["n_words"] for v in live.values())
    ok = {k: v for k, v in live.items() if v["stats"]["n_words"] >= 0.6 * top} or live
    best = max(ok, key=lambda k: pass_score(ok[k]["stats"]))
    detail = ", ".join("%s=%.3f(w%d,rep%d,fg%d)" % (
        k, pass_score(v["stats"]), v["stats"]["n_words"], v["stats"].get("repetition", 0),
        v["stats"]["foreign_glyphs"]) for k, v in live.items())
    dropped = [k for k in live if k not in ok]
    return best, "best penalised avg_logprob among %s%s" % (
        detail, "; ineligible (speech loss): " + ",".join(dropped) if dropped else "")


def fmt_ts(t):
    m, s = divmod(t, 60)
    return "%02d:%05.2f" % (int(m), s)


def write_txt(path, job, rec):
    chosen = rec["passes"][rec["chosen_pass"]]
    lines = ["# job %s source_start_s=%s chosen=%s (%s)" % (
        job["job"], job["source_start_s"], rec["chosen_pass"], rec["chosen_reason"]),
        "# WAV t=0 == source t=%ss; timestamps are WAV-relative" % job["source_start_s"], ""]
    for s in chosen["segments"]:
        mark = "  [FLAG %s]" % ",".join(s["flags"]) if s["flags"] else ""
        lines.append("[%s-%s] (%.2f) %s%s" % (fmt_ts(s["start"]), fmt_ts(s["end"]),
                                              s["avg_logprob"], s["clean_text"].strip(), mark))
        for g in s["foreign_glyphs"]:
            lines.append("    foreign glyph %r @ %.2fs (dropped from clean text)" % (g["ch"], g["start"]))
    lines += ["", "# flagged spans (chosen pass)"]
    fl = [s for s in chosen["segments"] if s["flags"] or s["low_prob_tokens"]]
    if not fl:
        lines.append("(none)")
    for s in fl:
        lines.append("- %s-%s flags=%s low_p_tokens=%s" % (
            fmt_ts(s["start"]), fmt_ts(s["end"]), s["flags"],
            [(t["text"], float(t["p"])) for t in s["low_prob_tokens"]][:8]))
    for name, ps in rec["passes"].items():
        if name == rec["chosen_pass"]:
            continue
        lines += ["", "# other pass (%s) %s for cross-check" % (name, ps["stats"])]
        for s in ps["segments"]:
            fl_ = " [FLAG %s]" % ",".join(s["flags"]) if s["flags"] else ""
            lines.append("[%s-%s] (%.2f) %s%s" % (fmt_ts(s["start"]), fmt_ts(s["end"]),
                                                  s["avg_logprob"], s["clean_text"].strip(), fl_))
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


TRANSCRIBE_KW = dict(
    language="th", word_timestamps=True, beam_size=5,
    temperature=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0], condition_on_previous_text=False,
    vad_filter=True, vad_parameters={"min_silence_duration_ms": 400, "speech_pad_ms": 200})


class _Shift:
    """View of a faster-whisper segment with all times shifted by an offset."""

    def __init__(self, seg, off):
        self.start, self.end = seg.start + off, seg.end + off
        self.text, self.avg_logprob = seg.text, seg.avg_logprob
        self.no_speech_prob, self.compression_ratio = seg.no_speech_prob, seg.compression_ratio
        self.words = [type("W", (), {"word": w.word, "start": w.start + off, "end": w.end + off,
                                     "probability": w.probability})() for w in (seg.words or [])]


def transcribe(model, wav, chunk_s=None):
    """Whole-file pass, or (chunk_s) independent windows with no overlap, times shifted back.

    Chunking breaks the long-segment hallucination loops seen on whole 55 s files.
    """
    if not chunk_s:
        segs, info = model.transcribe(wav, **TRANSCRIBE_KW)
        recs = [segment_record(s) for s in segs]
        dur = info.duration
    else:
        from faster_whisper.audio import decode_audio
        audio = decode_audio(wav, sampling_rate=16000)
        dur = len(audio) / 16000
        recs = []
        for st in range(0, int(dur) + 1, chunk_s):
            piece = audio[st * 16000:(st + chunk_s) * 16000]
            if len(piece) < 16000 // 2:
                continue
            segs, _ = model.transcribe(piece, **TRANSCRIBE_KW)
            recs += [segment_record(_Shift(s, st)) for s in segs]
    return {"segments": recs, "stats": pass_stats(recs), "duration": round(dur, 3),
            "chunk_s": chunk_s}


def load_model(name):
    register_cuda()
    from faster_whisper import WhisperModel
    errs = []
    for n, ct in [(name, "float16"), (name, "int8_float16"), ("large-v3-turbo", "float16")]:
        try:
            return WhisperModel(n, device="cuda", compute_type=ct), n, ct
        except Exception as e:  # noqa: BLE001
            errs.append("%s/%s: %s" % (n, ct, e))
    raise RuntimeError("no model loaded: " + " | ".join(errs))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("workspace")
    ap.add_argument("--jobs")
    ap.add_argument("--model", default="large-v3")
    a = ap.parse_args()
    ws = a.workspace
    with open(os.path.join(ws, "jobs.json"), encoding="utf-8") as f:
        jobs = json.load(f)
    if a.jobs:
        want = {int(x) for x in a.jobs.split(",")}
        jobs = [j for j in jobs if j["job"] in want]
    for j in jobs:
        n = j["job"]
        for voice in (False, True):
            out = os.path.join(ws, "audio", "job%d%s.wav" % (n, "_voice" if voice else ""))
            if not os.path.exists(out):
                ffmpeg_wav(j["source"], j["source_start_s"], j["duration_s"], out, voice)
    model, mname, ctype = load_model(a.model)
    print("model", mname, ctype, flush=True)
    for j in jobs:
        n = j["job"]
        passes = {}
        for name, sfx, ck in (("raw", "", None), ("voice", "_voice", None),
                              ("raw_chunk", "", CHUNK_S), ("voice_chunk", "_voice", CHUNK_S)):
            passes[name] = transcribe(model, os.path.join(ws, "audio", "job%d%s.wav" % (n, sfx)), ck)
            print(n, name, passes[name]["stats"], flush=True)
        ch, why = choose_pass(passes)
        rec = {"job": n, "source": j["source"], "source_start_s": j["source_start_s"],
               "duration_s": j["duration_s"], "model": mname, "compute_type": ctype,
               "passes": passes, "chosen_pass": ch, "chosen_reason": why}
        with open(os.path.join(ws, "asr", "job%d.json" % n), "w", encoding="utf-8") as f:
            json.dump(rec, f, ensure_ascii=False, indent=1)
        write_txt(os.path.join(ws, "asr", "job%d.txt" % n), j, rec)
        print(n, "CHOSEN", ch, why, flush=True)


if __name__ == "__main__":
    main()
