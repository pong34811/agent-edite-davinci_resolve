"""Pass B: transcribe ONLY shortlist spans (padded) on GPU, from a boosted copy of the audio."""
import json, pathlib, subprocess, wave
import numpy as np
import config, gpu_env
from features import wav_path, SR
from windows import merge_windows

PAD_S = 60
BOOST_AF = "highpass=f=80,loudnorm=I=-16:TP=-1.5:LRA=11"

def boost(x: np.ndarray, sr: int = SR) -> np.ndarray:
    p = subprocess.run([config.FFMPEG, "-v", "error", "-f", "f32le", "-ar", str(sr), "-ac", "1", "-i", "-",
                        "-af", BOOST_AF, "-f", "f32le", "-ar", str(sr), "-ac", "1", "-"],
                       input=x.astype(np.float32).tobytes(), capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype=np.float32)

def spans(wins, duration_s: float, pad: float = PAD_S):
    padded = [(max(0.0, s - pad), min(duration_s, e + pad), sc) for s, e, sc in wins]
    return [(s, e) for s, e, _ in merge_windows(padded, gap_s=0)]

def segments_for_span(model, audio: np.ndarray, offset: float):
    segs, _ = model.transcribe(audio, language=config.LANGUAGE, beam_size=1, batch_size=16)
    return [{"start": round(s.start + offset, 2), "end": round(s.end + offset, 2), "text": s.text.strip()} for s in segs]

def read_span(wav: pathlib.Path, s: float, e: float) -> np.ndarray:
    with wave.open(str(wav)) as w:
        w.setpos(int(s * w.getframerate()))
        raw = w.readframes(int((e - s) * w.getframerate()))
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0

_model = None
def _get_model():
    global _model
    if _model is None:
        gpu_env.setup()
        from faster_whisper import WhisperModel, BatchedInferencePipeline
        _model = BatchedInferencePipeline(model=WhisperModel("large-v3", device="cuda", compute_type="float16"))
    return _model

def run(source_id: str) -> pathlib.Path:
    out = config.WORK_DIR / "transcripts" / f"{source_id}.json"
    part = out.with_suffix(".partial.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        return out
    inv = {r["source_id"]: r for r in json.loads((config.WORK_DIR / "inventory.json").read_text(encoding="utf-8"))}
    top = json.loads((config.WORK_DIR / "scores" / f"{source_id}.top.json").read_text(encoding="utf-8"))
    todo = spans([tuple(w) for w in top], inv[source_id]["duration_s"])
    state = json.loads(part.read_text(encoding="utf-8")) if part.exists() else {"done": [], "segments": []}
    model = _get_model()
    for s, e in todo:
        if [s, e] in state["done"]:
            continue
        audio = boost(read_span(wav_path(source_id), s, e))
        state["segments"] += segments_for_span(model, audio, s)
        state["done"].append([s, e])
        part.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
        print(f"{source_id} span {s:.0f}-{e:.0f} done ({len(state['done'])}/{len(todo)})", flush=True)
    segs = sorted(state["segments"], key=lambda x: x["start"])
    out.write_text(json.dumps(segs, ensure_ascii=False), encoding="utf-8")
    part.unlink(missing_ok=True)
    return out
