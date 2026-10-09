"""Read-only scene-cut scan over a timeline's whole V1 source range (ffmpeg decode at 192x108, every frame).

Reports record frames where the mean abs frame difference jumps (> THR) plus a contact sheet of the frame after each
jump, so short scene switches (chat/room/outro) that a 12-frame sample misses are seen before building.
Usage: python -m scripts.p2_9x16_cutscan <index> [...]   (needs exports/9x16-batch/inventory.json)
"""
from __future__ import annotations

import json
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

from scripts.p2_9x16_inventory import OUT

THR = 12.0


def scan(index):
    inv = {d["index"]: d for d in json.loads((OUT / "inventory.json").read_text(encoding="utf-8"))}
    cuts, thumbs, facecam_runs = [], [], []
    for it in inv[index]["video"][0]["items"]:
        fps = float(it["src_fps"])
        s0, s1 = it["src"]
        cmd = ["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{s0 / fps:.4f}", "-i", it["path"], "-frames:v", str(s1 - s0),
               "-vf", "scale=192:108", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        raw = subprocess.run(cmd, capture_output=True, check=True, timeout=1800).stdout
        a = np.frombuffer(raw, np.uint8).reshape(-1, 108, 192, 3)
        d = np.abs(np.diff(a.astype(np.int16), axis=0)).mean(axis=(1, 2, 3))
        rec_per_src = 60.0 / fps
        # facecam presence: deep-blue avatar hair in the bottom-left facecam box (source x<660, y 500..1080)
        b = a[:, 50:, :66].astype(np.int16)
        hair = ((b[..., 2] > 110) & (b[..., 0] < 70) & (b[..., 1] < 70) & (b[..., 2] > b[..., 0] + 60)).sum(axis=(1, 2))
        med = float(np.median(hair))
        low = hair < 0.3 * med
        runs, start = [], None
        for i, v in enumerate(list(low) + [False]):
            if v and start is None:
                start = i
            elif not v and start is not None:
                runs.append([int(it["start"] + start * rec_per_src), int(it["start"] + i * rec_per_src)])
                start = None
        facecam_runs.append({"median_hair_px": med, "absent_runs_rec": runs})
        for i in np.where(d > THR)[0]:
            rec = int(it["start"] + (i + 1) * rec_per_src)
            cuts.append({"rec": rec, "diff": round(float(d[i]), 1)})
            thumbs.append((rec, a[i + 1]))
    sheet = Image.new("RGB", (192 * 8, 108 * max(1, (len(thumbs) + 7) // 8)))
    for k, (rec, im) in enumerate(thumbs[:96]):
        t = Image.fromarray(im)
        ImageDraw.Draw(t).text((2, 2), str(rec), fill=(255, 255, 0))
        sheet.paste(t, ((k % 8) * 192, (k // 8) * 108))
    sheet.save(OUT / f"cutscan_{index}.png")
    return {"cuts": cuts, "facecam": facecam_runs}


def main():
    out = {}
    for i in [int(x) for x in sys.argv[1:]]:
        out[i] = scan(i)
        print(i, "cuts", len(out[i]["cuts"]), "facecam", out[i]["facecam"], flush=True)
    p = OUT / "cutscan.json"
    old = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    old.update({str(k): v for k, v in out.items()})
    p.write_text(json.dumps(old, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
