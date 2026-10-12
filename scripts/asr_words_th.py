"""Offline Thai ASR with character-level timing (read-only on media).

Writes <out>.json: segments + per-word spans built per thai-subtitles-resolve §2:
join Whisper tokens, spread time across characters, tokenize with pythainlp newmm,
drop foreign-script glyphs together with their time span.

Usage: python scripts/asr_words_th.py <wav> <out.json> [--model large-v3-turbo]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata


def _register_cuda():
    try:
        import torch
        lib = os.path.join(os.path.dirname(torch.__file__), "lib")
        os.add_dll_directory(lib)
        os.environ["PATH"] = lib + os.pathsep + os.environ["PATH"]
    except Exception:
        pass


FOREIGN = re.compile(r"[぀-ヿ一-鿿가-힯Ѐ-ӿ؀-ۿऀ-ॿ]")


def build_words(segments):
    from pythainlp.tokenize import word_tokenize
    out = []
    for seg in segments:
        chars = []  # (char, start, end)
        for w in seg["words"]:
            tok = w["word"]
            n = max(len(tok), 1)
            span = (w["end"] - w["start"]) / n
            for i, ch in enumerate(tok):
                chars.append((ch, w["start"] + i * span, w["start"] + (i + 1) * span))
        chars = [c for c in chars if not FOREIGN.match(c[0])]
        text = "".join(c[0] for c in chars)
        pos = 0
        for tok in word_tokenize(text, engine="newmm", keep_whitespace=False):
            idx = text.find(tok, pos)
            if idx < 0:
                continue
            pos = idx + len(tok)
            out.append({"w": tok, "s": chars[idx][1], "e": chars[pos - 1][2], "seg": seg["id"]})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("wav")
    ap.add_argument("out")
    ap.add_argument("--model", default="large-v3-turbo")
    args = ap.parse_args(argv)
    _register_cuda()
    from faster_whisper import WhisperModel
    try:
        model = WhisperModel(args.model, device="cuda", compute_type="float16")
    except Exception as exc:  # explicit, measured CPU fallback
        print("CUDA load failed (%s); CPU int8" % exc, file=sys.stderr)
        model = WhisperModel(args.model, device="cpu", compute_type="int8")
    it, info = model.transcribe(
        args.wav, language="th", word_timestamps=True, beam_size=5,
        temperature=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0], condition_on_previous_text=False,
        vad_filter=True, vad_parameters={"min_silence_duration_ms": 400, "speech_pad_ms": 200})
    segs = []
    for i, s in enumerate(it):
        segs.append({"id": i, "start": s.start, "end": s.end, "text": s.text,
                     "avg_logprob": s.avg_logprob,
                     "words": [{"word": w.word, "start": w.start, "end": w.end, "p": w.probability}
                               for w in (s.words or [])]})
    words = build_words(segs)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"model": args.model, "duration": info.duration, "segments": segs, "words": words},
                  f, ensure_ascii=False, indent=1)
    print("%d segments, %d words" % (len(segs), len(words)))
    for s in segs:
        print("[%6.2f-%6.2f lp=%.2f] %s" % (s["start"], s["end"], s["avg_logprob"], s["text"]))


if __name__ == "__main__":
    main()
