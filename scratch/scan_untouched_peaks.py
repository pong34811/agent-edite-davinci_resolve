import os
import sys
import time
import json
import subprocess
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

ffmpeg = r"C:\Users\warit\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe"
footage_dir = r"C:\Users\warit\SynologyDrive\Tygarina\2026-09-30"

with open(r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\scratch\untouched_and_touched_inventory.json", "r", encoding="utf-8") as f:
    inv = json.load(f)

untouched_files = [x[0] for x in inv["untouched"]]

def scan_single_file(filename, top_n=6):
    filepath = os.path.join(footage_dir, filename)
    cmd = [
        ffmpeg, "-v", "quiet", "-i", filepath,
        "-vn", "-acodec", "pcm_s16le", "-ar", "8000", "-ac", "1", "-f", "s16le", "-"
    ]
    t0 = time.time()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    raw_audio, _ = p.communicate()
    samples = np.frombuffer(raw_audio, dtype=np.int16).astype(np.float32) / 32768.0
    total_sec = len(samples) / 8000.0
    
    # 10s windows every 2s
    win_len = 10 * 8000
    hop_len = 2 * 8000
    num_windows = (len(samples) - win_len) // hop_len
    
    peaks = []
    for i in range(num_windows):
        start_sec = (i * hop_len) / 8000.0
        end_sec = start_sec + 10.0
        
        # Skip intro (first 180s) and outro (last 120s)
        if start_sec < 180 or end_sec > total_sec - 120:
            continue
            
        w_samples = samples[i * hop_len : i * hop_len + win_len]
        rms = np.sqrt(np.mean(w_samples ** 2))
        max_val = np.max(np.abs(w_samples))
        peaks.append((rms, max_val, start_sec, end_sec))
        
    peaks.sort(key=lambda x: x[0], reverse=True)
    
    # Select non-overlapping top peaks (separated by at least 150s)
    selected = []
    for rms, max_val, s, e in peaks:
        clash = False
        for _, _, sel_s, sel_e in selected:
            if abs(s - sel_s) < 150:
                clash = True
                break
        if not clash:
            selected.append((rms, max_val, s, e))
            if len(selected) >= top_n:
                break
                
    elapsed = time.time() - t0
    formatted_peaks = []
    for rms, max_val, s, e in selected:
        rms_db = 20 * np.log10(rms + 1e-9)
        peak_db = 20 * np.log10(max_val + 1e-9)
        formatted_peaks.append({
            "rms": float(rms),
            "rms_db": float(rms_db),
            "peak": float(max_val),
            "peak_db": float(peak_db),
            "start_sec": float(s),
            "end_sec": float(e)
        })
        
    return filename, total_sec, elapsed, formatted_peaks

def main():
    print(f"Starting audio peak scan for all {len(untouched_files)} untouched files...")
    start_time = time.time()
    results = {}
    
    # Run with 4 parallel worker processes
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(scan_single_file, fn): fn for fn in untouched_files}
        count = 0
        for future in as_completed(futures):
            fn = futures[future]
            try:
                filename, total_sec, elapsed, peaks = future.result()
                count += 1
                results[filename] = {
                    "total_sec": total_sec,
                    "total_frames": int(total_sec * 60),
                    "peaks": peaks
                }
                print(f"[{count:02d}/{len(untouched_files)}] Scanned '{filename}' ({total_sec:.1f}s) in {elapsed:.1f}s — Found {len(peaks)} peaks")
                for idx, p in enumerate(peaks[:3], 1):
                    m = int(p['start_sec'] // 60)
                    s = int(p['start_sec'] % 60)
                    print(f"    Peak #{idx}: {m:02d}:{s:02d} ({p['start_sec']:.1f}s) | RMS: {p['rms_db']:.1f} dBFS | Max: {p['peak_db']:.1f} dBFS")
            except Exception as e:
                print(f"Error scanning '{fn}': {e}")
                
    total_time = time.time() - start_time
    print(f"\nAll {len(untouched_files)} files scanned in {total_time:.1f}s ({total_time/60:.2f} min).")
    
    out_path = r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\scratch\untouched_audio_peaks.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Saved peak data to {out_path}")

if __name__ == "__main__":
    main()
