"""Character-free cover background from a source video.

Two commands:

  scan  — near a reference frame, find the frame where the in-stream model leaves
          the most room, and report the model-free widths (writes JSON)
  crop  — extract ONE frame and cut the model-free room region out of it

The model bbox is always measured on the frame that is actually extracted: a
coarse `fps=1/N` scan does not land on the same frame as an `ffmpeg -ss` seek, so
a crop planned from a scan-grid bbox lands on the wrong pixels.

Run through the `terminal` tool. Reads the source read-only.

  python scripts/character_free_bg.py scan --source "src.mp4" --around-frame 31272 --out scan.json
  python scripts/character_free_bg.py crop --source "src.mp4" --frame 33162 --side LR --out bg.png
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

HAIR_D_R = 70
HAIR_D_G = 70
MIN_MODEL_HEIGHT = 400
MAX_MODEL_TOP = 200


def hair_mask(a: np.ndarray) -> np.ndarray:
    r, g, b = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
    return (b > r + HAIR_D_R) & (b > g + HAIR_D_G)


def model_bbox(a: np.ndarray) -> tuple[int, int, int, int] | None:
    """Bounding box of the model's hair, or None when this is not the centre-frame model."""
    ys, xs = np.nonzero(hair_mask(a))
    if len(xs) < 500:
        return None
    x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())
    if (y1 - y0) < MIN_MODEL_HEIGHT or y0 > MAX_MODEL_TOP:
        return None
    return x0, y0, x1, y1


def extract_frame(source: str, frame: int, dest: Path, fps: float = 30.0) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{frame / fps:.4f}",
                    "-i", source, "-frames:v", "1", str(dest)], check=True)
    return dest


def room_crop(im: Image.Image, bb: tuple[int, int, int, int], side: str, pad: int) -> Image.Image:
    x0, _, x1, _ = bb
    left = im.crop((0, 0, x0 - pad, im.height))
    right = im.crop((x1 + pad, 0, im.width, im.height))
    if side == "L":
        return left
    if side == "R":
        return right
    if side == "LR":
        both = Image.new("RGB", (left.width + right.width, im.height))
        both.paste(left, (0, 0))
        both.paste(right, (left.width, 0))
        return both
    raise SystemExit(f"unknown side {side!r} (want L, R or LR)")


def cmd_scan(args: argparse.Namespace) -> int:
    start = args.around_frame / args.fps - args.window
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{start:.3f}", "-i", args.source,
                        "-t", str(2 * args.window), "-vf", f"fps=1/{args.step}",
                        "-q:v", "3", str(d / "f_%04d.jpg")], check=True)
        rows = []
        for i, p in enumerate(sorted(d.glob("f_*.jpg"))):
            frame = round((start + i * args.step) * args.fps)
            a = np.asarray(Image.open(p).convert("RGB"))
            bb = model_bbox(a)
            if bb is None:
                continue
            rows.append({"frame": frame, "bbox": list(bb), "left": int(bb[0]),
                         "right": int(a.shape[1] - bb[2]),
                         "both": int(a.shape[1] - (bb[2] - bb[0]))})
    rows.sort(key=lambda r: r["both"], reverse=True)
    Path(args.out).write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in rows[:6]:
        print(r)
    print(f"{len(rows)} model frames -> {args.out}")
    return 0


def cmd_crop(args: argparse.Namespace) -> int:
    with tempfile.TemporaryDirectory() as tmp:
        src = extract_frame(args.source, args.frame, Path(tmp) / "f.png", args.fps)
        im = Image.open(src).convert("RGB")
        a = np.asarray(im)
        bb = model_bbox(a)
        if bb is None:
            raise SystemExit("no centre-frame model found on this frame")
        out = room_crop(im, bb, args.side, args.pad)
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        out.save(args.out)
        region = np.asarray(out)
        print(f"frame {args.frame} bbox {bb} side {args.side} pad {args.pad} "
              f"-> {out.size} hair={int(hair_mask(region).sum())}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", required=True)
    ap.add_argument("--fps", type=float, default=30.0)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan")
    s.add_argument("--around-frame", type=int, required=True)
    s.add_argument("--window", type=float, default=120.0)
    s.add_argument("--step", type=float, default=3.0)
    s.add_argument("--out", required=True)
    c = sub.add_parser("crop")
    c.add_argument("--frame", type=int, required=True)
    c.add_argument("--side", choices=("L", "R", "LR"), required=True)
    c.add_argument("--pad", type=int, default=10)
    c.add_argument("--out", required=True)
    args = ap.parse_args()
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")
    return cmd_scan(args) if args.cmd == "scan" else cmd_crop(args)


if __name__ == "__main__":
    raise SystemExit(main())
