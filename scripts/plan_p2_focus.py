"""Read-only planner: pick a VTuber-visible subtitle beat per p2 timeline and derive Fusion Transform values.

MCP-GAP: davinci-resolve MCP can read each timeline one call at a time (timeline.get_items, subtitle items) but
looping 40+ timelines x 7 sampled frames each is not practical call-by-call -> scripting API, READ ONLY here.

Detection: the VTuber overlay has deep-blue hair; a blue-mask bbox (row/column histograms) is measured in
every sampled frame of a candidate beat. A beat is accepted only if EVERY sample finds the avatar.

Fusion Transform model (verified on the pilot render): out = (src - 0.5) * Size + Center   (point inputs, y up),
so to put the avatar's window centre `w` at the frame centre: Center = 0.5 - (w - 0.5) * Size, and the
window is clamped so no edge goes blank (Edges=0): w in [0.5/Size, 1 - 0.5/Size].

Usage: python -m scripts.plan_p2_focus --out <dir>
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.resolve_common import connect_resolve  # noqa: E402

W, H = 480, 270
SAMPLES = 7
HEADROOM = 0.09          # fraction of output height above the ears
MIN_SIZE, MAX_SIZE = 1.15, 1.8
TARGET_FILL = 0.90       # visible avatar height / output height
SKIP_NAMES = ("_archived", "_MOVE_ERROR")
DONE_TRACK = "VTUBER_FOCUS"


def grab(path, seconds):
    cmd = ["ffmpeg", "-loglevel", "error", "-ss", f"{seconds:.3f}", "-i", path, "-frames:v", "1",
           "-vf", f"scale={W}:{H}", "-f", "image2pipe", "-vcodec", "png", "-"]
    data = subprocess.run(cmd, capture_output=True).stdout
    if not data:
        return None
    import io
    return np.asarray(Image.open(io.BytesIO(data)).convert("RGB")).astype(int)


def _bbox(mask, x_lo, x_hi, y_lo, y_hi):
    sub = mask[int(y_lo * H):int(y_hi * H), int(x_lo * W):int(x_hi * W)]
    if sub.sum() < 0.03 * sub.size:
        return None
    cols = sub.sum(axis=0) >= 0.06 * sub.shape[0]
    rows = sub.sum(axis=1) >= 0.06 * sub.shape[1]
    if not cols.any() or not rows.any():
        return None
    xs, ys = np.where(cols)[0], np.where(rows)[0]
    return (x_lo + xs[0] / W, y_lo + ys[0] / H, x_lo + (xs[-1] + 1) / W, y_lo + (ys[-1] + 1) / H)


def avatar_box(img):
    """Normalised (x0, y0, x1, y1) of the deep-blue-hair avatar overlay, or None.

    The overlay sits in the bottom-left corner (x < 0.40) in gameplay scenes, or large on the right
    (x > 0.40) in the talking layout. Each region is searched on its own so scattered game-blue
    pixels elsewhere in the frame cannot widen the box.
    """
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    mask = (b > 90) & (b > r + 55) & (b > g + 35) & (r < 90) & (g < 120)
    # Left corner overlay: stands on the bottom edge (cut off by the frame), 0.12-0.34 wide, ears above y=0.42.
    box = _bbox(mask, 0.0, 0.40, 0.40, 1.0)
    if box and box[3] >= 0.97 and 0.12 < (box[2] - box[0]) <= 0.34 and box[1] >= 0.40:
        return box
    # Talking layout: large avatar on the right, also standing on the bottom edge.
    box = _bbox(mask, 0.40, 1.0, 0.0, 1.0)
    if box and box[3] >= 0.8 and (box[3] - box[1]) > 0.40 and 0.20 < (box[2] - box[0]) <= 0.45:
        return box
    return None


def beats(subs, gap=24):
    out = []
    for s, e in subs:
        if out and s - out[-1][1] <= gap:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out


def frame_to_src(item, frame, fps):
    return (item.GetSourceStartFrame() + (frame - item.GetStart())) / fps


CANONICAL_LEFT = (0.09, 0.50, 0.31, 1.0)   # fixed bottom-left overlay incl. ear tips (pilot render, ears at ~0.50)


def transform_for(boxes):
    x0 = min(b[0] for b in boxes); y0 = min(b[1] for b in boxes)
    x1 = max(b[2] for b in boxes); y1 = max(b[3] for b in boxes)
    if x1 < 0.45:
        # Left overlay is a fixed layout; a mask box that touches the search-region limits is contaminated
        # by game-blue pixels, so use the calibrated box for every left-corner timeline.
        x0, y0, x1, y1 = CANONICAL_LEFT
    visible_h = min(y1, 1.0) - y0
    size = max(MIN_SIZE, min(MAX_SIZE, TARGET_FILL / max(visible_h, 0.05)))
    if TARGET_FILL / max(visible_h, 0.05) < MIN_SIZE:
        return None, (x0, y0, x1, y1)
    half = 0.5 / size
    wx = min(max((x0 + x1) / 2, half), 1 - half)
    top = y0 - HEADROOM / size
    wy_td = min(max(top + half, half), 1 - half)          # window centre, top-down
    wy = 1 - wy_td                                         # fusion y is up
    cx = 0.5 - (wx - 0.5) * size
    cy = 0.5 - (wy - 0.5) * size
    return {"Size": round(size, 3), "Center": {"1": round(cx, 4), "2": round(cy, 4), "3": 0.0},
            "Edges": 0.0}, (x0, y0, x1, y1)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out); (out / "frames").mkdir(parents=True, exist_ok=True)
    project = connect_resolve().GetProjectManager().GetCurrentProject()
    plan = {"project": project.GetName(), "targets": [], "skipped": []}
    for i in range(1, project.GetTimelineCount() + 1):
        t = project.GetTimelineByIndex(i)
        name = t.GetName()
        rec = {"ordinal": i, "name": name, "timeline_id": t.GetUniqueId()}
        if any(k in name for k in SKIP_NAMES):
            plan["skipped"].append({**rec, "reason": "archive/recovery copy"}); continue
        fps = float(t.GetSetting("timelineFrameRate"))
        vcount = t.GetTrackCount("video")
        have = [n for n in range(1, vcount + 1) if t.GetTrackName("video", n) == DONE_TRACK]
        if have:
            plan["skipped"].append({**rec, "reason": f"{DONE_TRACK} already on V{have[0]} (pilot)"}); continue
        items = t.GetItemListInTrack("video", 1) or []
        subs = [(s.GetStart(), s.GetEnd()) for s in (t.GetItemListInTrack("subtitle", 1) or [])]
        if t.GetStartFrame() != 0 or fps != 60 or not items or not subs:
            plan["skipped"].append({**rec, "reason": f"start={t.GetStartFrame()} fps={fps} items={len(items)} cues={len(subs)}"}); continue
        cands = []
        for min_len in (150, 90):
            for s, e in beats(subs):
                if e - s < min_len or (min_len == 90 and e - s >= 150):
                    continue
                e = min(e, s + 360)
                cands.append((abs((e - s) - 270), s, e))
        # (150+ beats are tried first because their sort key is smaller on average; 90-149 only fill the tail)
        cands.sort(key=lambda c: (c[2] - c[1] < 150, c[0]))
        chosen, tried = None, 0
        for _, s, e in cands[:10]:
            host = [it for it in items if it.GetStart() <= s and e <= it.GetEnd()]
            if len(host) != 1:
                continue
            it = host[0]
            mp = it.GetMediaPoolItem()
            path = mp.GetClipProperty("File Path") if mp else None
            if not path:
                continue
            tried += 1
            boxes, frames = [], []
            for k in range(SAMPLES):
                f = s + round((e - 1 - s) * k / (SAMPLES - 1))
                img = grab(path, frame_to_src(it, f, fps))
                box = avatar_box(img) if img is not None else None
                if box is None:
                    boxes = None
                    break
                boxes.append(box); frames.append((f, img))
            if not boxes:
                continue
            sides = {b[2] < 0.45 for b in boxes}
            ux = max(b[2] for b in boxes) - min(b[0] for b in boxes)
            if len(sides) > 1 or ux > 0.42:      # avatar changed layout/moved during the beat
                continue
            tf, union = transform_for(boxes)
            Image.fromarray(frames[SAMPLES // 2][1].astype("uint8")).save(out / "frames" / f"{i:02d}.jpg")
            chosen = {"cue": [s, e], "union_box": [round(v, 3) for v in union], "transform": tf}
            break
        if not chosen:
            plan["skipped"].append({**rec, "reason": f"no beat with avatar in all {SAMPLES} samples (tried {tried})"})
        elif chosen["transform"] is None:
            plan["skipped"].append({**rec, **chosen, "reason": "avatar already fills the frame; zoom < 1.15x"})
        else:
            plan["targets"].append({**rec, **chosen, "track_name": DONE_TRACK})
        print(i, name[-20:], "ok" if chosen and chosen["transform"] else "skip", flush=True)
    (out / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    print("targets", len(plan["targets"]), "skipped", len(plan["skipped"]))


if __name__ == "__main__":
    main()
