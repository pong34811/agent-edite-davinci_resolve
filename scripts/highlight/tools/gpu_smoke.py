"""60 s Whisper GPU smoke test on the first inventory video: python tools/gpu_smoke.py [start_seconds]

Run from scripts/highlight/ with the venv python. Tries float16, then int8_float16, and prints which works.
Needs inventory.json (python pipeline.py inventory). Fixes cublas DLL lookup via gpu_env.setup().
"""
import pathlib, subprocess, sys, time, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import gpu_env; gpu_env.setup()
import numpy as np
import config

start = sys.argv[1] if len(sys.argv) > 1 else "1500"
inv = json.loads((config.WORK_DIR / "inventory.json").read_text(encoding="utf-8"))
src = inv[0]["file"]
raw = subprocess.run([config.FFMPEG, "-v", "error", "-ss", start, "-t", "60", "-i", src, "-vn", "-ac", "1", "-ar", "16000",
                      "-f", "f32le", "-"], capture_output=True).stdout
audio = np.frombuffer(raw, dtype=np.float32)
print("source", pathlib.Path(src).name, "samples", audio.size, flush=True)
from faster_whisper import WhisperModel
for ct in ("float16", "int8_float16"):
    try:
        t = time.time(); m = WhisperModel("large-v3", device="cuda", compute_type=ct); print("loaded", ct, round(time.time() - t, 1), "s", flush=True)
        t = time.time(); segs, _ = m.transcribe(audio, language=config.LANGUAGE, vad_filter=True, beam_size=1)
        print("OK", ct, round(time.time() - t, 1), "s |", " ".join(s.text for s in segs)[:300]); sys.exit(0)
    except Exception as e:
        print("FAIL", ct, repr(e)[:300], flush=True)
sys.exit(1)
