"""Build pop-in overlays from the user's own still images (cards, posters) as full-raster alpha MOVs.

Each overlay holds one or more images at fixed centres and heights (aspect kept). Every image pops in
(0 -> 115% in 0.10 s, settles to 100% by 0.20 s), later images start `stagger` seconds after the
previous one, everything fades out over the last `fade` seconds, and each image gets a soft drop
shadow so it separates from a busy background. The render is ProRes 4444 with alpha at the timeline
raster, so it is placed at Zoom 1 / Pan 0 / Tilt 0 in Resolve; position lives in the pixels.

Usage: python scripts/card_pop_overlay.py plan.json out_dir [--width 1920 --height 1080 --fps 30]
plan.json: [{"id": "01_goddess", "seconds": 7.5, "stagger": 0.12,
             "cards": [{"path": "C:/.../card.png", "cx": 1560, "cy": 470, "h": 860}, ...]}, ...]
Writes out_dir/<id>.mov and out_dir/manifest.json. Source images are only read.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageFilter

SHADOW_BLUR = 14
SHADOW_OFFSET = (0, 10)
SHADOW_ALPHA = 150


def pop_scale(t: float) -> float:
    """Scale factor at `t` seconds after the image's own start; 0 before it."""
    if t < 0:
        return 0.0
    if t < 0.10:
        return 1.15 * t / 0.10
    if t < 0.20:
        return 1.15 - 0.15 * (t - 0.10) / 0.10
    return 1.0


def fade_alpha(t: float, seconds: float, fade: float) -> float:
    """Global opacity: 1 until the last `fade` seconds, then linear to 0 at `seconds`."""
    if fade <= 0 or t <= seconds - fade:
        return 1.0
    return max(0.0, (seconds - t) / fade)


def card_box(img_w: int, img_h: int, cx: float, cy: float, h: float, scale: float):
    """Pixel box (left, top, width, height) of an image of height h*scale centred on (cx, cy), aspect kept."""
    hh = max(2, round(h * scale))
    ww = max(2, round(img_w * hh / img_h))
    return round(cx - ww / 2), round(cy - hh / 2), ww, hh


def shadowed(img: Image.Image) -> Image.Image:
    """Image on a transparent canvas with a soft drop shadow; returns (canvas, pad)."""
    pad = SHADOW_BLUR * 3
    w, h = img.size
    canvas = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, SHADOW_ALPHA))
    canvas.paste(shadow, (pad + SHADOW_OFFSET[0], pad + SHADOW_OFFSET[1]))
    canvas = canvas.filter(ImageFilter.GaussianBlur(SHADOW_BLUR))
    canvas.alpha_composite(img, (pad, pad))
    return canvas, pad


def frame(cards, t, seconds, stagger, fade, width, height):
    out = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    for i, (img, c) in enumerate(cards):
        s = pop_scale(t - i * stagger)
        if s <= 0:
            continue
        left, top, w, h = card_box(img.width, img.height, c["cx"], c["cy"], c["h"], s)
        layer, pad = shadowed(img.resize((w, h), Image.LANCZOS))
        tmp = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        tmp.paste(layer, (left - pad, top - pad))  # raw copy; clips at the frame edge
        out = Image.alpha_composite(out, tmp)  # later cards stack over earlier ones
    a = fade_alpha(t, seconds, fade)
    if a < 1.0:
        alpha = out.getchannel("A").point(lambda v: round(v * a))
        out.putalpha(alpha)
    return out


def render(item, out: Path, width, height, fps):
    seconds = float(item["seconds"])
    stagger = float(item.get("stagger", 0.12))
    fade = float(item.get("fade", 0.25))
    cards = [(Image.open(c["path"]).convert("RGBA"), c) for c in item["cards"]]
    n = round(seconds * fps)
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
           "-f", "rawvideo", "-pix_fmt", "rgba", "-s", "%dx%d" % (width, height), "-r", str(fps), "-i", "-",
           "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    still = None
    for k in range(n):
        t = k / fps
        settled = t >= (len(cards) - 1) * stagger + 0.2 and fade_alpha(t, seconds, fade) == 1.0
        if settled and still is not None:
            img = still
        else:
            img = frame(cards, t, seconds, stagger, fade, width, height)
            if settled:
                still = img
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg failed for %s" % out)
    return n


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("out_dir")
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--fps", type=int, default=30)
    a = ap.parse_args(argv)
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    manifest = []
    for item in json.loads(Path(a.plan).read_text(encoding="utf-8")):
        mov = out / ("%s.mov" % item["id"])
        frames = render(item, mov, a.width, a.height, a.fps)
        manifest.append({**item, "mov": str(mov), "frames": frames, "fps": a.fps})
        print(mov.name, frames)
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
