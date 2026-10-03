import os
import sys
import json
import time
import subprocess
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

torch_lib = r"C:\Users\warit\AppData\Local\Programs\Python\Python312\Lib\site-packages\torch\lib"
if os.path.exists(torch_lib):
    os.add_dll_directory(torch_lib)
    os.environ["PATH"] = torch_lib + os.pathsep + os.environ["PATH"]

from faster_whisper import WhisperModel

ffmpeg = r"C:\Users\warit\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe"
footage_dir = r"C:\Users\warit\SynologyDrive\Tygarina\2026-09-30"

with open("scratch/round4_60_candidates_pre_transcribe.json", "r", encoding="utf-8") as f:
    candidates = json.load(f)

print(f"Loading faster-whisper (small, cuda, float16)...")
t0 = time.time()
model = WhisperModel("small", device="cuda", compute_type="float16")
print(f"Whisper loaded in {time.time()-t0:.2f}s.")

print("Transcribing dialogue samples around peaks for all 60 candidates...")
for idx, c in enumerate(candidates, 1):
    fn = c["source_file"]
    filepath = os.path.join(footage_dir, fn)
    p_ts = c["peak_timestamp_sec"]
    # Sample 18 seconds around peak
    sample_start = max(c["start_sec"], int(p_ts - 4.0))
    sample_dur = 18.0
    
    cmd = [
        ffmpeg, "-y", "-ss", str(sample_start), "-t", str(sample_dur),
        "-i", filepath, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        "-f", "s16le", "-"
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    audio = np.frombuffer(proc.stdout, dtype=np.int16).astype(np.float32) / 32768.0
    
    try:
        segments, _ = model.transcribe(audio, language="th")
        transcript_lines = []
        for s in segments:
            txt = s.text.strip()
            if txt:
                transcript_lines.append(txt)
        snippet = " | ".join(transcript_lines[:3]) if transcript_lines else "บรรยากาศการเล่นเกม/เสียงหัวเราะและรีแอ็กชัน"
    except Exception as e:
        snippet = f"เสียงรีแอ็กชันพลังงานสูง (RMS {c['peak_rms_db']} dBFS)"
        
    c["transcript_snippet"] = snippet
    c["rationale"] = f"ช่วงพลังงานเสียงพีค (RMS {c['peak_rms_db']} dBFS, Max {c['peak_max_db']} dBFS) ณ วินาทีที่ {p_ts:.1f}s — บทสนทนา/รีแอ็กชัน: \"{snippet}\""
    print(f"[{idx:02d}/60] {c['title']} -> {snippet[:60]}...")

out_file = "scratch/round4_60_candidates_complete.json"
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(candidates, f, indent=2, ensure_ascii=False)

print(f"\nAll 60 candidates transcribed and saved to {out_file}!")
