"""Read-only source stills for per-stream facecam calibration (ffmpeg decode -> new PNGs; sources untouched).

No Resolve call: reads exports/9x16-batch/inventory.json (from p2_9x16_inventory) and decodes one clean full-res
frame per timeline from its V1 source file at the given fractions of the V1 source range, plus a gridded crop of
the facecam search region (100 px red grid, 50 px green) for reading eye x/y, head top and facecam extent.

Usage: python -m scripts.p2_9x16_sources [fractions...]     (default 0.5)
"""
from __future__ import annotations

import json
import subprocess
import sys

from PIL import Image, ImageDraw

from scripts.p2_9x16_inventory import OUT

SRC = OUT / "sources"


def grab(path, seconds, dst):
    if dst.exists():
        return dst
    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{seconds:.3f}", "-i", path, "-frames:v", "1", "-y", str(dst)]
    subprocess.run(cmd, check=True, timeout=120)
    return dst


def grid(src, dst, box=(0, 300, 1920, 1080)):
    im = Image.open(src).convert("RGB").crop(box)
    d = ImageDraw.Draw(im)
    for x in range(0, im.width, 50):
        d.line([(x, 0), (x, im.height)], fill=(255, 0, 0) if (x + box[0]) % 100 == 0 else (0, 255, 0))
    for y in range(0, im.height, 50):
        yy = y + box[1] - box[1] % 50
        d.line([(0, yy - box[1]), (im.width, yy - box[1])], fill=(255, 0, 0) if yy % 100 == 0 else (0, 255, 0))
    im.save(dst)
    return dst


def range_sheet(index, n=12):
    """Decode n frames evenly across one timeline's V1 source range -> exports/9x16-batch/<index>/range/ + contact sheet
    (scene-switch check before building)."""
    inv = {d["index"]: d for d in json.loads((OUT / "inventory.json").read_text(encoding="utf-8"))}
    v1 = inv[index]["video"][0]["items"][0]
    s0, s1 = v1["src"]
    d = OUT / str(index) / "range"
    d.mkdir(parents=True, exist_ok=True)
    W, H = 480, 270
    sheet = Image.new("RGB", (W * 4, H * ((n + 3) // 4)))
    for k in range(n):
        f = s0 + int((s1 - 2 - s0) * k / (n - 1))
        p = grab(v1["path"], f / float(v1["src_fps"]), d / f"src_{f}.png")
        im = Image.open(p).convert("RGB").resize((W, H))
        ImageDraw.Draw(im).text((4, 4), f"rec {f - s0 + v1['start']} src {f}", fill=(255, 255, 0))
        sheet.paste(im, ((k % 4) * W, (k // 4) * H))
    sheet.save(OUT / f"contact_{index}_range.png")
    return OUT / f"contact_{index}_range.png"


def main():
    if sys.argv[1:2] == ["range"]:
        for i in sys.argv[2:]:
            print(range_sheet(int(i)), flush=True)
        return 0
    fr = [float(a) for a in sys.argv[1:]] or [0.5]
    SRC.mkdir(parents=True, exist_ok=True)
    inv = json.loads((OUT / "inventory.json").read_text(encoding="utf-8"))
    for d in inv:
        v1 = d["video"][0]["items"][0]
        fps = float(v1["src_fps"])
        for f in fr:
            s = (v1["src"][0] + f * (v1["src"][1] - v1["src"][0])) / fps
            dst = SRC / f"{d['index']:02d}_{int(s)}s.png"
            grab(v1["path"], s, dst)
            print(d["index"], dst.name, flush=True)


if __name__ == "__main__":
    sys.exit(main())
