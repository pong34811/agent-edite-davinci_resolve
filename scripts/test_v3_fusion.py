"""Test V3 Fusion Transform settings and inspect rendered still at frame 219300."""
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

v3_items = tl.GetItemListInTrack("video", 3) or []
print(f"V3 items count: {len(v3_items)}")

# Test Option A: Pivot (0.5, 0.25), Center (0.5, 0.5), Size 2.0
for idx, adj in enumerate(v3_items):
    comp = adj.GetFusionCompByIndex(1)
    tools = comp.GetToolList()
    for t in tools.values():
        if "Transform" in t.GetAttrs().get("TOOLS_Name", ""):
            res_p = t.SetInput("Pivot", {1: 0.50, 2: 0.25, 3: 0.0})
            res_c = t.SetInput("Center", {1: 0.50, 2: 0.50, 3: 0.0})
            res_s = t.SetInput("Size", 2.0)
            print(f"Adj {idx+1} Transform inputs set: Pivot={res_p}, Center={res_c}, Size={res_s}")
            print(f"  Readback Pivot: {t.GetInput('Pivot')}")
            print(f"  Readback Center: {t.GetInput('Center')}")
            print(f"  Readback Size: {t.GetInput('Size')}")

tc = m2.frame_to_timecode(219300, 60.0)
tl.SetCurrentTimecode(tc)
time.sleep(0.5)

out_p = os.path.abspath("test_qc_stills/vtuber_focus_zoom_test.png")
proj.ExportCurrentFrameAsStill(out_p)

im = Image.open(out_p)
arr = np.array(im)
means = arr.mean(axis=(1, 2))
black_rows = (means < 1.0).sum()
pct_black = black_rows / len(means) * 100.0
print(f"\n[vtuber_focus_zoom_test.png]")
print(f"  Total black rows: {black_rows}/1920 ({pct_black:.1f}%)")

# Check skin presence in full screen close up
skin_mask = (arr[:, :, 0] > 180) & (arr[:, :, 1] > 140) & (arr[:, :, 2] > 130) & (arr[:, :, 0] > arr[:, :, 1]) & (arr[:, :, 1] > arr[:, :, 2])
rows, cols = np.where(skin_mask)
if len(rows) > 0:
    print(f"  [Skin/Face] Detected {len(rows)} pixels! Row range: {rows.min()}..{rows.max()}, Col range: {cols.min()}..{cols.max()}")
    print(f"  Center: row {rows.mean():.1f}, col {cols.mean():.1f}")
else:
    print("  [Skin/Face] NO SKIN PIXELS DETECTED!")

# Check purple controller
purple_mask = (arr[:, :, 2] > 100) & (arr[:, :, 0] > 80) & (arr[:, :, 2] > arr[:, :, 1] * 1.3) & (arr[:, :, 0] > arr[:, :, 1] * 1.1)
rows_p, cols_p = np.where(purple_mask)
if len(rows_p) > 0:
    print(f"  [Purple Controller] Detected {len(rows_p)} pixels! Row range: {rows_p.min()}..{rows_p.max()}, Col range: {cols_p.min()}..{cols_p.max()}")
