import os
import sys
import subprocess
import json
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

torch_lib = r"C:\Users\warit\AppData\Local\Programs\Python\Python312\Lib\site-packages\torch\lib"
if os.path.exists(torch_lib):
    os.add_dll_directory(torch_lib)
    os.environ["PATH"] = torch_lib + os.pathsep + os.environ["PATH"]

from faster_whisper import WhisperModel

folder = r"C:\Users\warit\SynologyDrive\Tygarina\2026-09-30"
ffmpeg = r"C:\Users\warit\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe"

files_map = {
    "REPO": "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4",
    "Climbing": "ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4",
    "Ib": "IB - สำรวจโลกภาพวาด P1.mp4",
    "DnD": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4",
    "GarticPhone": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4",
    "FreeTalk": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4",
    "Overcooked": "เมื่อไทกะคือความชิบหายในครัว!.mp4"
}

with open(".agents/teamwork/explorer_survey_r3_3/peaks.json", "r", encoding="utf-8") as f:
    peaks_data = json.load(f)

print("Loading Whisper model (small) on CUDA...")
model = WhisperModel("small", device="cuda", compute_type="float16")
print("Whisper model loaded successfully.")

results = {}

for tag, peaks in peaks_data.items():
    filename = files_map[tag]
    filepath = os.path.join(folder, filename)
    print(f"\n==========================================")
    print(f"Transcribing Top 3 Peaks for {tag}: {filename}")
    print(f"==========================================")
    results[tag] = []
    
    # Process top 3 peaks
    for idx, p in enumerate(peaks[:3]):
        peak_center = p["start"] + 5.0 # center of 10s peak window
        # Target a 50s-60s window: start ~25s before peak, end ~30s after peak
        # Snap start to integer
        start_sec = max(0, int(peak_center - 25.0))
        duration = 55.0
        end_sec = start_sec + duration
        
        cmd = [
            ffmpeg, "-y", "-ss", str(start_sec), "-t", str(duration),
            "-i", filepath, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            "-f", "s16le", "-"
        ]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        audio = np.frombuffer(proc.stdout, dtype=np.int16).astype(np.float32) / 32768.0
        
        segments, info = model.transcribe(audio, language="th")
        transcript_lines = []
        full_text = []
        for s in segments:
            t_start = start_sec + s.start
            t_end = start_sec + s.end
            line = f"[{t_start:.1f}s - {t_end:.1f}s] {s.text.strip()}"
            transcript_lines.append(line)
            full_text.append(s.text.strip())
            
        res_item = {
            "candidate_idx": idx + 1,
            "peak_rms_db": 20 * np.log10(p["rms"] + 1e-9),
            "peak_max_db": 20 * np.log10(p["peak"] + 1e-9),
            "start_sec": start_sec,
            "end_sec": end_sec,
            "duration": duration,
            "start_frame": int(start_sec * 60),
            "end_frame": int(end_sec * 60),
            "duration_frames": int(duration * 60),
            "transcript": transcript_lines,
            "summary_text": " ".join(full_text)
        }
        results[tag].append(res_item)
        print(f"\n--- Candidate #{idx+1} for {tag} [{start_sec}s..{end_sec}s] ({duration}s) ---")
        print(f"Audio: RMS {res_item['peak_rms_db']:.1f} dBFS, Peak {res_item['peak_max_db']:.1f} dBFS")
        for line in transcript_lines[:6]:
            print(f"  {line}")
        if len(transcript_lines) > 6:
            print(f"  ... ({len(transcript_lines)-6} more lines)")

with open(".agents/teamwork/explorer_survey_r3_3/transcripts.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\nAll candidate transcriptions finished and saved to transcripts.json")
