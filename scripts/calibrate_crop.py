"""Calibration probe: measure Resolve Crop/Zoom/Pan/Tilt semantics on the pilot _9x16 timeline.

WRITES only to the pilot _9x16 timeline (never originals). Disables V2-V4 while probing V1,
then restores track-enable states and the item property values it found on entry.
Stills are scratch analysis only (test_qc_stills/cal_*.png).
"""
import json
import os
import sys
import time

import numpy as np
from PIL import Image

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import m2_convert_pilot as m2  # noqa: E402

FRAME = 216500  # normal period: no V3 adjustment / V4 gif active
PROPS = ["ZoomX", "ZoomY", "Pan", "Tilt", "CropTop", "CropBottom", "CropLeft", "CropRight"]
OUT = os.path.abspath("test_qc_stills")
os.makedirs(OUT, exist_ok=True)


def bbox(path, thr=14):
    a = np.array(Image.open(path).convert("RGB")).max(axis=2)
    ys, xs = np.where(a > thr)
    if len(xs) == 0:
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]


def main():
    resolve = m2.get_resolve()
    proj = resolve.GetProjectManager().GetCurrentProject()
    tl = m2.find_timeline_by_name(proj, m2.TARGET_NAME)
    assert tl and tl.GetUniqueId() == "2b0779e3-6b5d-4fd2-91b3-2d55ffaed2a3", "wrong timeline"
    if proj.GetCurrentTimeline().GetUniqueId() != tl.GetUniqueId():
        proj.SetCurrentTimeline(tl)
        time.sleep(1.2)
    assert proj.GetCurrentTimeline().GetUniqueId() == tl.GetUniqueId()
    entry_tc = tl.GetCurrentTimecode()
    v = {n: tl.GetItemListInTrack("video", n)[0] for n in (1, 2)}
    saved = {n: {p: float(m2.get_item_property(v[n], p) or 0.0) for p in PROPS} for n in v}
    en = {n: tl.GetIsTrackEnabled("video", n) for n in (1, 2, 3, 4)}
    print("entry", entry_tc, saved, en)

    def setp(item, **kw):
        for k, val in kw.items():
            item.SetProperty(k, float(val))
            time.sleep(0.15)

    def reset(item):
        setp(item, ZoomX=1.0, ZoomY=1.0, Pan=0.0, Tilt=0.0, CropTop=0.0, CropBottom=0.0, CropLeft=0.0, CropRight=0.0)

    def snap(label, item):
        rb = {p: m2.get_item_property(item, p) for p in PROPS}
        tl.SetCurrentTimecode(m2.frame_to_timecode(FRAME, 60.0))
        time.sleep(0.5)
        path = os.path.join(OUT, f"cal_{label}.png")
        ok = proj.ExportCurrentFrameAsStill(path)
        time.sleep(0.3)
        bb = bbox(path) if ok and os.path.exists(path) else None
        print(f"{label:28s} export={ok} bbox(x0,y0,x1,y1)={bb} readback={rb}")
        return bb

    results = {}
    try:
        for n in (2, 3, 4):
            tl.SetTrackEnable("video", n, False)
            time.sleep(1.2)
        item = v[1]
        reset(item)
        results["z1_base"] = snap("v1_z1_base", item)
        setp(item, CropLeft=480.0)
        results["z1_cropL480"] = snap("v1_z1_cropL480", item)
        reset(item); setp(item, CropRight=480.0)
        results["z1_cropR480"] = snap("v1_z1_cropR480", item)
        reset(item); setp(item, CropTop=270.0)
        results["z1_cropT270"] = snap("v1_z1_cropT270", item)
        reset(item); setp(item, CropBottom=270.0)
        results["z1_cropB270"] = snap("v1_z1_cropB270", item)
        reset(item); setp(item, ZoomX=2.0, ZoomY=2.0)
        results["z2_base"] = snap("v1_z2_base", item)
        setp(item, CropLeft=480.0)
        results["z2_cropL480"] = snap("v1_z2_cropL480", item)
        reset(item); setp(item, Tilt=300.0)
        results["z1_tilt300"] = snap("v1_z1_tilt300", item)
        reset(item); setp(item, Pan=300.0)
        results["z1_pan300"] = snap("v1_z1_pan300", item)
    finally:
        reset(v[1])
        setp(v[1], **saved[1])
        for n, st in en.items():
            tl.SetTrackEnable("video", n, bool(st))
            time.sleep(1.2)
        tl.SetCurrentTimecode(entry_tc)
        time.sleep(0.5)
        print("restored V1", {p: m2.get_item_property(v[1], p) for p in PROPS})
        print("restored enables", {n: tl.GetIsTrackEnabled("video", n) for n in (1, 2, 3, 4)}, "tc", tl.GetCurrentTimecode())
    json.dump(results, open("scratch/calibration_v1.json", "w"), indent=1)


if __name__ == "__main__":
    main()
