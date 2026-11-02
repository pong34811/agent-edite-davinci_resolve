"""Pass A: demux each video ONCE to a level-untouched 16 kHz mono wav, then per-second RMS/peak dB."""
import pathlib, subprocess, wave, json
import numpy as np
import config

SR = 16000

def wav_path(source_id: str) -> pathlib.Path:
    return config.WORK_DIR / "audio" / f"{source_id}.wav"

def _inventory() -> dict:
    rows = json.loads((config.WORK_DIR / "inventory.json").read_text(encoding="utf-8"))
    return {r["source_id"]: r for r in rows}

def extract_wav(source_id: str) -> pathlib.Path:
    row = _inventory()[source_id]; src = pathlib.Path(row["file"]); out = wav_path(source_id)
    if out.exists() and out.stat().st_mtime >= src.stat().st_mtime:
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([config.FFMPEG, "-y", "-v", "error", "-i", str(src), "-vn", "-ac", "1", "-ar", str(SR),
                    "-c:a", "pcm_s16le", str(out)], check=True)
    with wave.open(str(out)) as w:
        dur = w.getnframes() / w.getframerate()
    assert abs(dur - row["duration_s"]) < 1.5, f"{source_id}: wav {dur:.1f}s vs source {row['duration_s']:.1f}s"
    return out

def per_second_db(x: np.ndarray, sr: int = SR):
    n = len(x) // sr
    f = x[: n * sr].astype(np.float32).reshape(n, sr) / 32768.0
    rms = 20 * np.log10(np.sqrt((f ** 2).mean(axis=1)) + 1e-9)
    peak = 20 * np.log10(np.abs(f).max(axis=1) + 1e-9)
    return rms, peak

def extract(source_id: str) -> pathlib.Path:
    wav = extract_wav(source_id)
    out = config.WORK_DIR / "scores" / f"{source_id}.features.npz"
    if out.exists() and out.stat().st_mtime >= wav.stat().st_mtime:
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    rs, ps = [], []
    with wave.open(str(wav)) as w:
        while True:
            raw = w.readframes(SR * 600)
            if not raw: break
            r, p = per_second_db(np.frombuffer(raw, dtype=np.int16))
            rs.append(r); ps.append(p)
    np.savez(out, rms=np.concatenate(rs), peak=np.concatenate(ps))
    return out
