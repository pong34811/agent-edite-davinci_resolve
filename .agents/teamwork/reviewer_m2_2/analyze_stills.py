import sys, os
from PIL import Image
import numpy as np

qc_dir = r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\worker_m2\qc_stills"
stills = [
    "split_screen_normal_216500.png",
    "reaction_gif_safe_218650.png",
    "vtuber_focus_zoom_219300.png"
]

print("=== QC STILLS PIXEL & FRAMING ANALYSIS ===")
for s in stills:
    path = os.path.join(qc_dir, s)
    if not os.path.exists(path):
        print(f"File not found: {path}")
        continue
    img = Image.open(path)
    arr = np.array(img)
    h, w, c = arr.shape
    print(f"\nImage: {s} | Shape: {w}x{h}x{c}")
    
    # Calculate black / near-black pixels (threshold < 15)
    # Convert to grayscale
    gray = np.mean(arr[:, :, :3], axis=2)
    black_mask = gray < 10
    black_pct = np.mean(black_mask) * 100.0
    print(f"  Overall black / empty canvas percentage: {black_pct:.1f}%")
    
    # Analyze row by row brightness
    row_means = np.mean(gray, axis=1)
    
    # Split into 3 sections:
    # Upper canvas: rows 0 to 960 (in 1080x1920, height is 1920, so upper is 0 to 960)
    # Lower canvas: rows 960 to 1920
    upper_gray = gray[:960, :]
    lower_gray = gray[960:, :]
    
    upper_black_pct = np.mean(upper_gray < 10) * 100.0
    lower_black_pct = np.mean(lower_gray < 10) * 100.0
    print(f"  Upper half (0..960) black percentage: {upper_black_pct:.1f}%")
    print(f"  Lower half (960..1920) black percentage: {lower_black_pct:.1f}%")
    
    # Find active vertical content ranges (rows with mean brightness > 10)
    active_rows = np.where(row_means > 10)[0]
    if len(active_rows) > 0:
        print(f"  Active content Y-range: row {active_rows[0]} to row {active_rows[-1]} (out of 1920)")
        
        # Check gaps (runs of black rows in the middle)
        diffs = np.diff(active_rows)
        large_gaps = np.where(diffs > 20)[0]
        for g in large_gaps:
            gap_start = active_rows[g]
            gap_end = active_rows[g+1]
            print(f"  !! BLACK GAP DETECTED: row {gap_start} to row {gap_end} (height {gap_end - gap_start} pixels) !!")
    else:
        print("  !! ENTIRE IMAGE IS VIRTUALLY BLACK !!")
