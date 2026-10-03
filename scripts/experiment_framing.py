"""Experiment with framing parameters and analyze rendered still frames."""
import os
import sys
import time
from PIL import Image
import numpy as np

sys.path.append(os.path.abspath("scripts"))
import m2_convert_pilot as m2

resolve = m2.get_resolve()
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
tl = m2.find_timeline_by_name(proj, m2.TARGET_NAME)
proj.SetCurrentTimeline(tl)
time.sleep(0.5)

v1_item = tl.GetItemListInTrack("video", 1)[0]
v2_item = tl.GetItemListInTrack("video", 2)[0]
v3_items = tl.GetItemListInTrack("video", 3) or []
v4_items = tl.GetItemListInTrack("video", 4) or []

os.makedirs("test_qc_stills", exist_ok=True)

def analyze_image(path):
    im = Image.open(path)
    arr = np.array(im.convert("L"))
    h, w = arr.shape
    row_means = arr.mean(axis=1)
    black_rows = (row_means < 1.0).sum()
    pct_black = black_rows / h * 100.0
    
    # Check upper half and lower half
    upper_black = (row_means[:h//2] < 1.0).sum() / (h//2) * 100.0
    lower_black = (row_means[h//2:] < 1.0).sum() / (h//2) * 100.0
    
    # Find contiguous black rows (voids)
    max_contiguous_black = 0
    curr_contiguous = 0
    for v in (row_means < 1.0):
        if v:
            curr_contiguous += 1
            if curr_contiguous > max_contiguous_black:
                max_contiguous_black = curr_contiguous
        else:
            curr_contiguous = 0
            
    print(f"[{os.path.basename(path)}]")
    print(f"  Total black rows: {black_rows}/{h} ({pct_black:.1f}%)")
    print(f"  Upper half black: {upper_black:.1f}%, Lower half black: {lower_black:.1f}%")
    print(f"  Max contiguous black rows: {max_contiguous_black}")
    return pct_black, max_contiguous_black, row_means

print("\n--- Testing V1 and V2 framing ---")
# Set V1
v1_item.SetProperty("ZoomX", 1.60)
v1_item.SetProperty("ZoomY", 1.60)
v1_item.SetProperty("Pan", 0.0)
v1_item.SetProperty("Tilt", 480.0)
v1_item.SetProperty("CropBottom", 0.0)

# Test different V2 Tilt values: -50.0, -80.0, -100.0 with Pan -936.0 and -960.0
for pan in [-936.0, -960.0]:
    for tilt in [-50.0, -80.0, -100.0]:
        v2_item.SetProperty("ZoomX", 2.60)
        v2_item.SetProperty("ZoomY", 2.60)
        v2_item.SetProperty("Pan", pan)
        v2_item.SetProperty("Tilt", tilt)
        v2_item.SetProperty("CropTop", 0.0)
        
        tc = m2.frame_to_timecode(216500, 60.0)
        tl.SetCurrentTimecode(tc)
        time.sleep(0.3)
        still_path = os.path.abspath(f"test_qc_stills/split_pan{int(abs(pan))}_tilt{int(abs(tilt))}.png")
        proj.ExportCurrentFrameAsStill(still_path)
        analyze_image(still_path)

print("\nDone testing V1 and V2.")
