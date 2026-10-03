"""Inspect V4 Reaction GIF at frame 218650."""
import os
import sys
import time
from PIL import Image
import numpy as np

sys.path.append(os.path.abspath("scripts"))
import m2_convert_pilot as m2

resolve = m2.get_resolve()
proj = resolve.GetProjectManager().GetCurrentProject()
tl = m2.find_timeline_by_name(proj, m2.TARGET_NAME)
proj.SetCurrentTimeline(tl)
time.sleep(0.5)

v4_items = tl.GetItemListInTrack("video", 4) or []
v4 = v4_items[0] if v4_items else None
if v4:
    print("V4 properties:")
    for p in ["ZoomX", "ZoomY", "Pan", "Tilt", "CropTop", "CropBottom", "CropLeft", "CropRight"]:
        print(f"  {p}:", v4.GetProperty(p))

tc = m2.frame_to_timecode(218650, 60.0)
tl.SetCurrentTimecode(tc)
time.sleep(0.5)

out_p = os.path.abspath("test_qc_stills/reaction_gif_test.png")
proj.ExportCurrentFrameAsStill(out_p)

im = Image.open(out_p)
arr = np.array(im)
means = arr.mean(axis=(1, 2))
black_rows = (means < 1.0).sum()
pct_black = black_rows / len(means) * 100.0
print(f"\n[reaction_gif_test.png]")
print(f"  Total black rows: {black_rows}/1920 ({pct_black:.1f}%)")

# Let's find contiguous black blocks
in_black = False
start = 0
for i, m in enumerate(means):
    if m < 1.0 and not in_black:
        start = i
        in_black = True
    elif m >= 1.0 and in_black:
        print(f"  Black rows {start}..{i-1} ({i-start} rows)")
        in_black = False
if in_black:
    print(f"  Black rows {start}..{len(means)-1} ({len(means)-start} rows)")
