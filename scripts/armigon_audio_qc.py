"""Read-only loudness QC + hook-frame grab of every armigon-2026-09 horizontal timeline's V1 source range.

ffmpeg is used for read-only analysis only (AGENTS.md exception). Vertical timelines share the same
source range as their horizontal pair, so only 1920x1080 timelines are measured.

Run from repo root after scripts.armigon_source_ranges:
  python -m scripts.armigon_audio_qc
Writes exports/armigon-qc/audio.json and exports/armigon-qc/hook/NN.jpg (frame 1 s into the clip, raw source).
"""
from __future__ import annotations

import json
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "exports" / "armigon-qc"
HOOK = OUT / "hook"
TIMELINE_FPS = 60.0  # every armigon-2026-09 timeline is 60 fps (verified in data.json)


def measure(row):
    it = row["items"][0]
    fps = float(it["fps"] or 60)
    ss = it["src_start"] / fps
    dur = (it["end"] - it["start"]) / TIMELINE_FPS  # record frames are timeline fps, not source fps
    p = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-ss", f"{ss:.3f}", "-t", f"{dur:.3f}", "-i", it["path"],
         "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    txt = p.stderr.split("Summary:")[-1]
    g = lambda pat: (lambda m: float(m.group(1)) if m else None)(re.search(pat, txt))
    res = {"index": row["index"], "name": row["name"], "dur": round(dur, 2),
           "lufs": g(r"I:\s+(-?[\d.]+) LUFS"), "lra": g(r"LRA:\s+([\d.]+) LU"),
           "tp": g(r"Peak:\s+(-?[\d.]+) dBFS")}
    jpg = HOOK / f"{row['index']:02d}.jpg"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{ss + 1:.3f}", "-i", it["path"],
                    "-frames:v", "1", "-vf", "scale=960:-1", str(jpg)], capture_output=True)
    return res


def main():
    HOOK.mkdir(parents=True, exist_ok=True)
    rows = json.loads((OUT / "source_ranges.json").read_text(encoding="utf-8"))
    todo = [r for r in rows if r["items"] and r["name"] != "ARMIGON_FOCUS_MCP_PILOT_TEMP"
            and not r["name"].endswith("_9x16")]
    with ThreadPoolExecutor(4) as ex:
        res = list(ex.map(measure, todo))
    (OUT / "audio.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print("WROTE", len(res))


if __name__ == "__main__":
    main()
