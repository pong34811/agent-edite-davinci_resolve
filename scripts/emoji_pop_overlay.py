"""Build pop-in emoji illustration overlays (ProRes 4444 alpha MOV at the timeline raster).

Downloads Noto Emoji 3D PNGs (googlefonts/noto-emoji, `3D/png/512/emoji_u<hex>.png`; README:
image resources Apache-2.0) and renders each as a full-raster transparent clip: the emoji
pops in with a small overshoot, holds, and fades out. Placing a full-raster clip at Zoom 1 /
Pan 0 / Tilt 0 avoids guessing Resolve transform units; the position lives in the render.

Usage: python scripts/emoji_pop_overlay.py plan.json out_dir [--width 1920 --height 1080 --fps 60]
plan.json: [{"id": "01_birthday", "hex": "1f382", "seconds": 2.0}, ...]
           optional per item: "x", "y" (centre px), "size" (px); defaults top-left wall.
Writes out_dir/png/<hex>.png, out_dir/<id>.mov and out_dir/manifest.json. Source files are
never overwritten; existing PNGs are reused.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

URL = "https://raw.githubusercontent.com/googlefonts/noto-emoji/main/3D/png/512/emoji_u{hex}.png"


def scale_expr(size: int) -> str:
    """Pop-in: 0 -> 115% in 0.10 s, settle to 100% by 0.20 s (ffmpeg per-frame expression)."""
    s = "if(lt(t,0.1),1.15*t/0.1,if(lt(t,0.2),1.15-0.15*(t-0.1)/0.1,1))"
    return "max(2,trunc(%d*%s/2)*2)" % (size, s)


def filter_graph(width, height, fps, seconds, x, y, size, fade=0.25):
    e = scale_expr(size)
    return (
        "color=c=black@0.0:s=%dx%d:r=%d:d=%s,format=rgba[bg];"
        "[0:v]format=rgba,scale=w='%s':h='%s':eval=frame,"
        "fade=t=out:st=%s:d=%s:alpha=1[e];"
        "[bg][e]overlay=x='%d-overlay_w/2':y='%d-overlay_h/2':eval=frame:format=auto,format=yuva444p10le[v]"
        % (width, height, fps, seconds, e, e, seconds - fade, fade, x, y)
    )


def fetch(hex_code: str, png_dir: Path) -> Path:
    path = png_dir / ("%s.png" % hex_code)
    if not path.exists():
        png_dir.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(URL.format(hex=hex_code), timeout=30) as r:
            path.write_bytes(r.read())
    return path


def render(png: Path, out: Path, width, height, fps, seconds, x, y, size):
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
           "-loop", "1", "-framerate", str(fps), "-t", str(seconds), "-i", str(png),
           "-filter_complex", filter_graph(width, height, fps, seconds, x, y, size),
           "-map", "[v]", "-t", str(seconds), "-c:v", "prores_ks", "-profile:v", "4444",
           "-pix_fmt", "yuva444p10le", str(out)]
    subprocess.run(cmd, check=True)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("out_dir")
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--fps", type=int, default=60)
    a = ap.parse_args(argv)
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    manifest = []
    for item in json.loads(Path(a.plan).read_text(encoding="utf-8")):
        png = fetch(item["hex"], out / "png")
        mov = out / ("%s.mov" % item["id"])
        x = item.get("x", round(a.width * 0.2))
        y = item.get("y", round(a.height * 0.28))
        size = item.get("size", round(a.height / 3))
        render(png, mov, a.width, a.height, a.fps, item.get("seconds", 2.0), x, y, size)
        manifest.append({**item, "png": str(png), "mov": str(mov), "x": x, "y": y, "size": size,
                         "source": URL.format(hex=item["hex"]), "license": "Apache-2.0 (Noto Emoji README)"})
        print(mov.name)
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
