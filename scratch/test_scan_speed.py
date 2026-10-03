import os
import sys
import time
import subprocess
import numpy as np

filepath = r"C:\Users\warit\SynologyDrive\Tygarina\2026-09-30\บอสทำไรตอนตี 2？？.mp4"
ffmpeg = r"C:\Users\warit\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe"

t0 = time.time()
cmd = [
    ffmpeg, "-v", "quiet", "-i", filepath,
    "-vn", "-acodec", "pcm_s16le", "-ar", "8000", "-ac", "1", "-f", "s16le", "-"
]
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
raw_audio, _ = p.communicate()
samples = np.frombuffer(raw_audio, dtype=np.int16).astype(np.float32) / 32768.0
t1 = time.time()

total_sec = len(samples) / 8000.0
print(f"File duration: {total_sec:.1f}s ({total_sec/60:.1f} min)")
print(f"Elapsed decode time: {t1 - t0:.2f}s (Speed: {total_sec / (t1 - t0):.1f}x realtime)")
