"""Test V1 Tilt direction and coverage."""
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

# Disable V2 temporarily to see only V1!
# Or set V2 offscreen / opacity 0 or check V1 alone
# Let's see: we can set V1 Tilt to various values and see where it appears
tc = m2.frame_to_timecode(216500, 60.0)
tl.SetCurrentTimecode(tc)

for tilt in [0.0, 200.0, 480.0, 600.0, -200.0, -480.0]:
    v1_item.SetProperty("ZoomX", 1.60)
    v1_item.SetProperty("ZoomY", 1.60)
    v1_item.SetProperty("Pan", 0.0)
    v1_item.SetProperty("Tilt", tilt)
    v1_item.SetProperty("CropBottom", 0.0)
    v1_item.SetProperty("CropTop", 0.0)
    time.sleep(0.3)
    p = os.path.abspath(f"test_qc_stills/v1_tilt_{int(tilt)}.png")
    proj.ExportCurrentFrameAsStill(p)
    im = Image.open(p)
    arr = np.array(im.convert("L"))
    means = arr.mean(axis=1)
    # find first and last non-black row
    active = np.where(means >= 1.0)[0]
    if len(active) > 0:
        print(f"V1 Tilt {tilt:+6.1f} -> Active rows: {active[0]} to {active[-1]} (span {active[-1]-active[0]+1} rows)")
    else:
        print(f"V1 Tilt {tilt:+6.1f} -> No active rows!")
