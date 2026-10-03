import os
import sys
import subprocess
import json
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

torch_lib = os.path.join(os.path.dirname(sys.executable), 'Lib', 'site-packages', 'torch', 'lib')
if os.path.exists(torch_lib):
    os.add_dll_directory(torch_lib)

from faster_whisper import WhisperModel

folder = r"C:\Users\warit\SynologyDrive\Tygarina\2026-09-30"
files_map = {
    "REPO": {
        "file": "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4",
        "exclude": [(6720, 6785)]
    },
    "Climbing": {
        "file": "ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4",
        "exclude": [(5855, 5915)]
    },
    "Ib": {
        "file": "IB - สำรวจโลกภาพวาด P1.mp4",
        "exclude": [(4475, 4530)]
    },
    "DnD": {
        "file": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4",
        "exclude": [(980, 1035)]
    },
    "GarticPhone": {
        "file": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4",
        "exclude": [(2510, 2575)]
    },
    "FreeTalk": {
        "file": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4",
        "exclude": [(2235, 2295)]
    },
    "Overcooked": {
        "file": "เมื่อไทกะคือความชิบหายในครัว!.mp4",
        "exclude": [(7640, 7705)]
    }
}

ffmpeg = r"C:\Users\warit\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe"

def scan_file_peaks(filepath, exclude_ranges, top_n=10):
    # Pipe 8000 Hz 16-bit mono PCM
    cmd = [
        ffmpeg, "-v", "quiet", "-i", filepath,
        "-vn", "-acodec", "pcm_s16le", "-ar", "8000", "-ac", "1", "-f", "s16le", "-"
    ]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    raw_audio, _ = p.communicate()
    samples = np.frombuffer(raw_audio, dtype=np.int16).astype(np.float32) / 32768.0
    total_sec = len(samples) / 8000.0
    
    # Calculate RMS in 10s windows every 2s
    win_len = 10 * 8000
    hop_len = 2 * 8000
    num_windows = (len(samples) - win_len) // hop_len
    
    peaks = []
    for i in range(num_windows):
        start_sec = (i * hop_len) / 8000.0
        end_sec = start_sec + 10.0
        
        # Check start/end margins (skip first 3 minutes, skip last 2 minutes)
        if start_sec < 180 or end_sec > total_sec - 120:
            continue
            
        # Check excluded intervals
        overlap = False
        for ex_s, ex_e in exclude_ranges:
            if not (end_sec < ex_s - 30 or start_sec > ex_e + 30):
                overlap = True
                break
        if overlap:
            continue
            
        w_samples = samples[i * hop_len : i * hop_len + win_len]
        rms = np.sqrt(np.mean(w_samples ** 2))
        max_val = np.max(np.abs(w_samples))
        peaks.append((rms, max_val, start_sec, end_sec))
        
    peaks.sort(key=lambda x: x[0], reverse=True)
    
    # Select non-overlapping top peaks (separated by at least 180s)
    selected = []
    for rms, max_val, s, e in peaks:
        clash = False
        for _, _, sel_s, sel_e in selected:
            if abs(s - sel_s) < 180:
                clash = True
                break
        if not clash:
            selected.append((rms, max_val, s, e))
            if len(selected) >= top_n:
                break
                
    return total_sec, selected

print("Scanning files for top peaks...")
top_candidates = {}
for tag, info in files_map.items():
    fp = os.path.join(folder, info["file"])
    print(f"\nScanning {tag} ({info['file']})...")
    dur, peaks = scan_file_peaks(fp, info["exclude"], top_n=6)
    top_candidates[tag] = peaks
    for rank, (rms, max_val, s, e) in enumerate(peaks):
        rms_db = 20 * np.log10(rms + 1e-9)
        peak_db = 20 * np.log10(max_val + 1e-9)
        m = int(s // 60)
        sec = int(s % 60)
        print(f"  #{rank+1}: {m:02d}:{sec:02d} ({s:.1f}s) | RMS: {rms:.4f} ({rms_db:.1f} dBFS), Peak: {peak_db:.1f} dBFS")

# Save peaks to json
with open(".agents/teamwork/explorer_survey_r3_3/peaks.json", "w", encoding="utf-8") as f:
    json.dump({k: [{"rms": float(p[0]), "peak": float(p[1]), "start": float(p[2]), "end": float(p[3])} for p in v] for k, v in top_candidates.items()}, f, indent=2)

print("\nDone scanning. peaks.json saved.")
