"""Pass A2: transcribe the WHOLE video with word timestamps, so agents can read every minute and cuts can land
on sentence edges. Writes transcripts/<id>.words.json (segments + words), <id>.sentences.json and <id>.fulltext.txt.

Model and beam come from job.json FULL_ASR_MODEL (default large-v3-turbo) and FULL_ASR_BEAM (default 5).
Audio is read from the level-untouched wav and boosted per chunk, like transcribe.py."""
import json, pathlib, re
import config
from features import wav_path, SR
from transcribe import boost, read_span

CHUNK_S = 600
GAP_S = 0.6        # a pause this long between words ends a sentence (Thai ASR gives no punctuation)
MAX_SENT_S = 12.0  # split longer runs at their largest pause so `[ends]` stays useful

def _hms(s: float) -> str:
    s = int(s); return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"

def clean(t: str, limit: int = 240) -> str:
    """collapse Whisper's repeated-character loops and cap the line."""
    t = re.sub(r"(.{1,6}?)\1{3,}", r"\1\1\1", t.strip())
    return t if len(t) <= limit else t[:limit] + "..."

def _split_long(words):
    if len(words) < 2 or words[-1][2] - words[0][1] <= MAX_SENT_S:
        return [words]
    i = max(range(1, len(words)), key=lambda k: words[k][1] - words[k - 1][2])
    return _split_long(words[:i]) + _split_long(words[i:])

def sentences(segments, gap: float = GAP_S):
    """segments [{words: [[text, start, end, prob], ...]}] -> [{start, end, text}] split at word pauses only:
    batched Whisper segment edges can fall mid-word in Thai ("ต|อนนี้"), so they are not boundaries."""
    out, run = [], []
    for w in sorted((w for seg in segments for w in seg.get("words") or []), key=lambda w: w[1]):
        if run and w[1] - run[-1][2] >= gap:
            out += _split_long(run); run = []
        run.append(w)
    if run:
        out += _split_long(run)
    res = []
    for ws in out:
        text = clean("".join(w[0] for w in ws))
        if text:
            res.append({"start": round(ws[0][1], 2), "end": round(ws[-1][2], 2), "text": text})
    return res

def format_text(source_id: str, sents) -> str:
    lines = [f"# Full transcript {source_id} (unverified ASR; [ends s] = when the sentence's last word ends)", ""]
    return "\n".join(lines + [f"[{_hms(s['start'])}] {s['text']}   [ends {s['end']:.1f}]" for s in sents]) + "\n"

def _segments(model_out, offset: float):
    segs = []
    for s in model_out:
        words = [[w.word, round(w.start + offset, 2), round(w.end + offset, 2), round(w.probability, 3)] for w in (s.words or [])]
        segs.append({"start": round(s.start + offset, 2), "end": round(s.end + offset, 2), "text": s.text.strip(), "words": words})
    return segs

_model = None
def _get_model():
    global _model
    if _model is None:
        import gpu_env; gpu_env.setup()
        from faster_whisper import WhisperModel, BatchedInferencePipeline
        name = config._job.get("FULL_ASR_MODEL", "large-v3-turbo")
        _model = BatchedInferencePipeline(model=WhisperModel(name, device="cuda", compute_type="float16"))
    return _model

def run(source_id: str) -> pathlib.Path:
    d = config.WORK_DIR / "transcripts"; d.mkdir(parents=True, exist_ok=True)
    out = d / f"{source_id}.words.json"
    if not out.exists():
        part = d / f"{source_id}.words.partial.json"
        inv = {r["source_id"]: r for r in json.loads((config.WORK_DIR / "inventory.json").read_text(encoding="utf-8"))}
        dur = inv[source_id]["duration_s"]
        state = json.loads(part.read_text(encoding="utf-8")) if part.exists() else {"done": [], "segments": []}
        model, beam = _get_model(), int(config._job.get("FULL_ASR_BEAM", 5))
        t = 0.0
        while t < dur - 0.05:
            e = min(t + CHUNK_S, dur)
            if [t, e] not in state["done"]:
                res, _ = model.transcribe(boost(read_span(wav_path(source_id), t, e)), language=config.LANGUAGE,
                                          beam_size=beam, batch_size=8, word_timestamps=True)
                state["segments"] += _segments(res, t)
                state["done"].append([t, e])
                part.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
                print(f"{source_id} {_hms(t)}-{_hms(e)} done", flush=True)
            t = e
        segs = sorted(state["segments"], key=lambda x: x["start"])
        out.write_text(json.dumps({"source_id": source_id, "model": config._job.get("FULL_ASR_MODEL", "large-v3-turbo"),
                                   "segments": segs}, ensure_ascii=False), encoding="utf-8")
        part.unlink(missing_ok=True)
    sents = sentences(json.loads(out.read_text(encoding="utf-8"))["segments"])
    (d / f"{source_id}.sentences.json").write_text(json.dumps(sents, ensure_ascii=False), encoding="utf-8")
    (d / f"{source_id}.fulltext.txt").write_text(format_text(source_id, sents), encoding="utf-8")
    return out

def load_sentences(source_id: str):
    p = config.WORK_DIR / "transcripts" / f"{source_id}.sentences.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    for sid in sys.argv[1:]:
        print(sid, run(sid), flush=True)
