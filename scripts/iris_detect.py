"""Locate the VTuber's golden irises in an image (RGB). Returns centroid + count of iris-like pixels.

Iris colour ~ gold (R>170,G>130,B<110, R-B>90). Restrict to a region to avoid HUD/torch yellows.
"""
import numpy as np
from PIL import Image


def iris(path, region=None):
    a = np.array(Image.open(path).convert("RGB")).astype(int)
    x0, y0, x1, y1 = region or (0, 0, a.shape[1], a.shape[0])
    sub = a[y0:y1, x0:x1]
    r, g, b = sub[..., 0], sub[..., 1], sub[..., 2]
    m = (r > 150) & (g > 110) & (b < 120) & ((r - b) > 70) & ((r - g) < 70) & ((r - g) > 5)
    ys, xs = np.nonzero(m)
    if len(xs) < 20:
        return None
    # keep the densest cluster: median-based trimming
    mx, my = np.median(xs), np.median(ys)
    keep = (abs(xs - mx) < 150) & (abs(ys - my) < 60)
    xs, ys = xs[keep], ys[keep]
    return {"x": float(xs.mean() + x0), "y": float(ys.mean() + y0), "n": int(len(xs)),
            "xspan": [int(xs.min() + x0), int(xs.max() + x0)]}


if __name__ == "__main__":
    import sys
    reg = tuple(int(v) for v in sys.argv[2:6]) if len(sys.argv) >= 6 else None
    print(iris(sys.argv[1], reg))
