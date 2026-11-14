"""Measure a full-canvas alpha overlay and compute Resolve Zoom/Pan/Tilt for a 9:16 slot.

Invoke through the `terminal` tool:
  python overlay_place.py OVERLAY.mov --target-cy 1180 --target-h 620
  python overlay_place.py OVERLAY.mov --target-cy 1180 --target-w 1040
Needs ffmpeg/ffprobe on PATH and Pillow. Read-only: writes frames to a temp dir only.
Timeline defaults: 1080x1920, scaleToFit (a 16:9 clip at Zoom 1 is fitted to the width).
Pan/Tilt are timeline pixels; positive Tilt moves up, positive Pan moves right.
"""
import argparse, glob, json, os, subprocess, tempfile

from PIL import Image


def probe(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=width,height", "-of", "csv=p=0", path], text=True)
    w, h = out.strip().splitlines()[0].split(",")[:2]
    return int(w), int(h)


def alpha_bbox(path, fps=2.0, threshold=40):
    """Union of the alpha bounding boxes over the whole clip, in source pixels."""
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", path, "-vf", f"fps={fps},alphaextract",
                               os.path.join(tmp, "a_%04d.png")])
        boxes = []
        for p in sorted(glob.glob(os.path.join(tmp, "a_*.png"))):
            with Image.open(p) as im:
                b = im.convert("L").point(lambda v: 255 if v > threshold else 0).getbbox()
            if b:
                boxes.append(b)
    if not boxes:
        raise SystemExit("no opaque pixels found (no alpha channel?)")
    return [min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes)]


def place(src_wh, bbox, tl_wh, target_cx, target_cy, target_w=None, target_h=None):
    W, H = src_wh
    TW, TH = tl_wh
    fit = min(TW / W, TH / H)
    x0, y0, x1, y1 = bbox
    if target_h:
        zoom = target_h / ((y1 - y0) * fit)
    else:
        zoom = target_w / ((x1 - x0) * fit)
    k = fit * zoom
    dx = (x0 + x1) / 2 - W / 2          # right of source centre
    dy_up = H / 2 - (y0 + y1) / 2       # above source centre
    pan = (target_cx - TW / 2) - dx * k
    tilt = (TH / 2 - target_cy) - dy_up * k
    return {"ZoomX": round(zoom, 3), "ZoomY": round(zoom, 3), "Pan": round(pan, 1), "Tilt": round(tilt, 1),
            "result_px": [round((x1 - x0) * k), round((y1 - y0) * k)]}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("overlay")
    ap.add_argument("--timeline", default="1080x1920")
    ap.add_argument("--target-cx", type=float, help="slot centre x from left (default: frame centre)")
    ap.add_argument("--target-cy", type=float, required=True, help="slot centre y from top")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--target-w", type=float)
    g.add_argument("--target-h", type=float)
    a = ap.parse_args()
    TW, TH = (int(v) for v in a.timeline.lower().split("x"))
    src = probe(a.overlay)
    bbox = alpha_bbox(a.overlay)
    cx = a.target_cx if a.target_cx is not None else TW / 2
    print(json.dumps({"source": src, "alpha_bbox": bbox,
                      "props": place(src, bbox, (TW, TH), cx, a.target_cy, a.target_w, a.target_h)}))


if __name__ == "__main__":
    main()
