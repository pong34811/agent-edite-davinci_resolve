"""Diagnose exact positioning and geometry of V1."""
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

# Mute tracks 2, 3, 4 so only V1 is visible!
# Or temporarily move V2, V3, V4 items offscreen:
v2 = tl.GetItemListInTrack("video", 2)[0]
v2.SetProperty("Pan", -5000.0) # move V2 completely offscreen

v1 = tl.GetItemListInTrack("video", 1)[0]
v1.SetProperty("CropBottom", 0.0)
v1.SetProperty("CropTop", 0.0)
v1.SetProperty("CropLeft", 0.0)
v1.SetProperty("CropRight", 0.0)
v1.SetProperty("Pan", 0.0)
v1.SetProperty("ZoomX", 1.60)
v1.SetProperty("ZoomY", 1.60)

tc = m2.frame_to_timecode(216500, 60.0)
tl.SetCurrentTimecode(tc)

for tilt in [0.0, 200.0, 480.0, 720.0, -200.0, -480.0]:
    v1.SetProperty("Tilt", tilt)
    time.sleep(0.3)
    p = os.path.abspath(f"test_qc_stills/diag_v1_tilt_{int(tilt)}.png")
    proj.ExportCurrentFrameAsStill(p)
    im = Image.open(p)
    arr = np.array(im.convert("L"))
    means = arr.mean(axis=1)
    active = np.where(means >= 1.0)[0]
    if len(active) > 0:
        print(f"Tilt {tilt:+6.1f}: active rows {active[0]:4d}..{active[-1]:4d} (count {len(active):4d}), center ~{(active[0]+active[-1])/2:.1f}")
    else:
        print(f"Tilt {tilt:+6.1f}: NO ACTIVE ROWS")
