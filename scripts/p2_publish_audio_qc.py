"""Read-only source-audio loudness/silence QC for each horizontal p2 timeline (ffmpeg on the source range).

Measures only the SOURCE audio of V1 (voice + game). BGM/SFX layers are not in this number: a true
delivered-mix reading needs a render, which this script does not do.
Input: exports/publish-qc/sources.json   Output: exports/publish-qc/audio.json
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "exports" / "publish-qc"


def measure(path, start_s, dur_s):
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-ss", f"{start_s:.3f}", "-t", f"{dur_s:.3f}", "-i", path,
           "-vn", "-af", "ebur128=peak=true,silencedetect=n=-45dB:d=3", "-f", "null", "-"]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    err = p.stderr
    tail = err[err.rfind("Summary:"):] if "Summary:" in err else ""
    g = lambda pat: (lambda m: float(m.group(1)) if m else None)(re.search(pat, tail))
    sil = [float(x) for x in re.findall(r"silence_duration: ([\d.]+)", err)]
    return {"lufs": g(r"I:\s+(-?[\d.]+) LUFS"), "lra": g(r"LRA:\s+([\d.]+) LU"), "tp": g(r"Peak:\s+(-?[\d.]+) dBFS"),
            "silence_s": round(sum(sil), 1), "rc": p.returncode}


def main():
    rows = json.loads((OUT / "sources.json").read_text(encoding="utf-8"))
    res = []
    for r in rows:
        segs = []
        for s in r["segs"]:
            m = measure(s["path"], s["s"] / s["fps"], (s["e"] - s["s"]) / s["fps"])
            segs.append({**m, "dur": round((s["e"] - s["s"]) / s["fps"], 1)})
        res.append({"index": r["index"], "name": r["name"], "segs": segs})
        print(r["index"], r["name"][:30], segs, flush=True)
    (OUT / "audio.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
