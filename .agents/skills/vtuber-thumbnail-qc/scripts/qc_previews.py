#!/usr/bin/env python3
"""Generate QC previews for YouTube thumbnails so tests are SEEN, not imagined.

Outputs per input: <stem>_mobile.png (10% and 20% side by side), <stem>_gray.png,
<stem>_squint.png, <stem>_badge.png (duration badge / Shorts danger overlay).
Also feed_sheet.png (all inputs at feed size, for A/B/C) and tech_report.json.

Usage: python qc_previews.py thumb.jpg [more.jpg ...] --out DIR
Requires Pillow.
"""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps


def tech(path: Path, im: Image.Image) -> dict:
    w, h = im.size
    ratio = w / h
    if abs(ratio - 16 / 9) < 0.01:
        kind = "landscape-16:9"
    elif abs(ratio - 9 / 16) < 0.01:
        kind = "shorts-9:16"
    else:
        kind = "non-standard"
    issues = []
    if kind == "non-standard":
        issues.append(f"aspect ratio {ratio:.3f} is not 16:9 or 9:16")
    if kind == "landscape-16:9" and w < 1280:
        issues.append("below recommended 1280x720")
    size = path.stat().st_size
    if size > 2 * 1024 * 1024:
        issues.append("file > 2MB (YouTube thumbnail limit)")
    if im.mode not in ("RGB", "L"):
        issues.append(f"mode {im.mode} (export as RGB)")
    return {"file": str(path), "width": w, "height": h, "ratio": round(ratio, 4),
            "kind": kind, "bytes": size, "mode": im.mode, "format": im.format,
            "icc_profile": bool(im.info.get("icc_profile")), "issues": issues}


def label(im: Image.Image, text: str) -> Image.Image:
    canvas = Image.new("RGB", (max(im.width, 8 * len(text) + 8), im.height + 18), "white")
    canvas.paste(im, (0, 18))
    ImageDraw.Draw(canvas).text((4, 3), text, fill="black")
    return canvas


def hstack(images, gap=12, bg="white") -> Image.Image:
    w = sum(i.width for i in images) + gap * (len(images) - 1)
    h = max(i.height for i in images)
    out = Image.new("RGB", (w, h), bg)
    x = 0
    for i in images:
        out.paste(i, (x, 0))
        x += i.width + gap
    return out


def scaled(im: Image.Image, frac: float) -> Image.Image:
    return im.resize((max(1, round(im.width * frac)), max(1, round(im.height * frac))), Image.LANCZOS)


def badge_overlay(im: Image.Image, kind: str) -> Image.Image:
    out = im.copy().convert("RGBA")
    layer = Image.new("RGBA", out.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    w, h = out.size
    if kind == "shorts-9:16":
        d.rectangle([0, int(h * 0.75), w, h], fill=(255, 0, 0, 90))      # bottom 25% UI
        d.rectangle([int(w * 0.85), 0, w, h], fill=(255, 0, 0, 90))      # right 15% buttons
        # 4:5 channel-grid crop window (centered)
        ch = int(w * 5 / 4)
        top = (h - ch) // 2
        d.rectangle([0, top, w - 1, top + ch], outline=(0, 255, 255, 255), width=max(2, w // 200))
    else:
        # approximate duration badge: ~7% x 6% of frame, small margin from bottom-right
        bw, bh, m = int(w * 0.075), int(h * 0.065), int(w * 0.006)
        d.rounded_rectangle([w - m - bw, h - m - bh, w - m, h - m], radius=bh // 5, fill=(0, 0, 0, 200))
        d.text((w - m - bw + bw // 5, h - m - bh + bh // 3), "12:34", fill=(255, 255, 255, 255))
        # caution zone around it + progress scrubber strip
        d.rectangle([int(w * 0.80), int(h * 0.82), w, h], outline=(255, 0, 0, 255), width=max(2, w // 400))
        d.rectangle([0, int(h * 0.975), w, h], fill=(255, 0, 0, 120))
    return Image.alpha_composite(out, layer).convert("RGB")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="+", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    report, feed, written = [], [], []
    for path in args.images:
        with Image.open(path) as raw:
            info = tech(path, raw)
            im = ImageOps.exif_transpose(raw).convert("RGB")
        report.append(info)
        stem = path.stem

        mobile = hstack([label(scaled(im, 0.10), "10%"), label(scaled(im, 0.20), "20%")])
        gray = ImageOps.grayscale(scaled(im, 0.33)).convert("RGB")
        small = scaled(im, 320 / im.width)
        squint = small.filter(ImageFilter.GaussianBlur(radius=max(3, small.width // 50)))
        badge = scaled(badge_overlay(im, info["kind"]), 0.5)

        for suffix, img in (("mobile", mobile), ("gray", gray), ("squint", squint), ("badge", badge)):
            p = args.out / f"{stem}_{suffix}.png"
            img.save(p)
            written.append(str(p))
        target_w = 246 if info["kind"] != "shorts-9:16" else 140  # ~mobile feed tile width
        feed.append(label(scaled(im, target_w / im.width), stem[:30]))

    sheet = hstack(feed, gap=16, bg="#0f0f0f")
    sheet_path = args.out / "feed_sheet.png"
    sheet.save(sheet_path)
    written.append(str(sheet_path))

    rep_path = args.out / "tech_report.json"
    rep_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("previews:")
    for p in written:
        print("  " + p)


if __name__ == "__main__":
    main()
