"""Calibration 2: does Pan/Tilt scale with Zoom, and is Crop applied pre-zoom? (pilot _9x16 only)."""
import os
import sys
import time

import numpy as np
from PIL import Image

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import m2_convert_pilot as m2  # noqa: E402

FRAME = 216500
PROPS = ["ZoomX", "ZoomY", "Pan", "Tilt", "CropTop", "CropBottom", "CropLeft", "CropRight"]
OUT = os.path.abspath("test_qc_stills")


def bbox(path, thr=14):
    a = np.array(Image.open(path).convert("RGB")).max(axis=2)
    ys, xs = np.where(a > thr)
    return [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if len(xs) else None


def main():
    resolve = m2.get_resolve()
    proj = resolve.GetProjectManager().GetCurrentProject()
    tl = m2.find_timeline_by_name(proj, m2.TARGET_NAME)
    assert tl.GetUniqueId() == "2b0779e3-6b5d-4fd2-91b3-2d55ffaed2a3"
    assert proj.GetCurrentTimeline().GetUniqueId() == tl.GetUniqueId()
    entry_tc = tl.GetCurrentTimecode()
    item = tl.GetItemListInTrack("video", 1)[0]
    saved = {p: float(m2.get_item_property(item, p) or 0.0) for p in PROPS}
    en = {n: tl.GetIsTrackEnabled("video", n) for n in (1, 2, 3, 4)}

    def setp(**kw):
        for k, v in kw.items():
            item.SetProperty(k, float(v))
            time.sleep(0.15)

    def snap(label):
        tl.SetCurrentTimecode(m2.frame_to_timecode(FRAME, 60.0))
        time.sleep(0.5)
        path = os.path.join(OUT, f"cal2_{label}.png")
        ok = proj.ExportCurrentFrameAsStill(path)
        time.sleep(0.3)
        print(f"{label:24s} {bbox(path) if ok else 'EXPORT FAIL'}  rb={ {p: m2.get_item_property(item, p) for p in PROPS} }")

    z = 1.7067
    try:
        for n in (2, 3, 4):
            tl.SetTrackEnable("video", n, False)
            time.sleep(1.2)
        base = dict(ZoomX=z, ZoomY=z, Pan=0.0, Tilt=0.0, CropTop=0.0, CropBottom=0.0, CropLeft=0.0, CropRight=0.0)
        setp(**base); snap("z17_base")
        setp(Pan=100.0); snap("z17_pan100")
        setp(Pan=0.0, Tilt=100.0); snap("z17_tilt100")
        setp(Tilt=1517.0); snap("z17_tilt1517")
        setp(Tilt=0.0, CropTop=100.0); snap("z17_cropT100")
        setp(CropTop=0.0, CropBottom=100.0); snap("z17_cropB100")
        setp(CropBottom=0.0, CropLeft=100.0); snap("z17_cropL100")
    finally:
        setp(ZoomX=1.0, ZoomY=1.0, Pan=0.0, Tilt=0.0, CropTop=0.0, CropBottom=0.0, CropLeft=0.0, CropRight=0.0)
        setp(**saved)
        for n, st in en.items():
            tl.SetTrackEnable("video", n, bool(st))
            time.sleep(1.2)
        tl.SetCurrentTimecode(entry_tc)
        time.sleep(0.5)
        print("restored", {p: m2.get_item_property(item, p) for p in PROPS}, {n: tl.GetIsTrackEnabled("video", n) for n in (1, 2, 3, 4)}, tl.GetCurrentTimecode())


if __name__ == "__main__":
    main()
