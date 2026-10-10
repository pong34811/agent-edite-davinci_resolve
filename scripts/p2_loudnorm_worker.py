"""Two-pass ffmpeg loudnorm (I=-14, TP=-1.5, LRA=11) for each rendered p2 vertical file listed in done.jsonl.

Offline (no Resolve). Video is stream-copied; only audio is re-encoded (AAC 256k). Verifies each result with
ebur128 + ffprobe and writes exports/render-final/final/<same name>.mp4 and loudnorm_results.json.
Run from repo root: python scripts/p2_loudnorm_worker.py --total 44
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "exports" / "render-final"
FINAL = OUT / "final"
TARGET = dict(I=-14, TP=-1.5, LRA=11)


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def measure(path):
    p = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"])
    t = p.stderr[p.stderr.rfind("Summary:"):]

    def g(pat):
        m = re.search(pat, t)
        return float(m.group(1)) if m else None

    return {"lufs": g(r"I:\s+(-?[\d.]+) LUFS"), "lra": g(r"LRA:\s+([\d.]+) LU"), "peak": g(r"Peak:\s+(-?[\d.]+) dBFS")}


def process(j):
    src = Path(j["file"])
    FINAL.mkdir(exist_ok=True)
    dst = FINAL / src.name
    p1 = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(src), "-vn", "-af",
              f"loudnorm=I={TARGET['I']}:TP={TARGET['TP']}:LRA={TARGET['LRA']}:print_format=json", "-f", "null", "-"])
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", p1.stderr, re.S)
    if not m:
        return {"n": j["n"], "ok": False, "error": "no loudnorm json"}
    d = json.loads(m.group(0))
    af = (f"loudnorm=I={TARGET['I']}:TP={TARGET['TP']}:LRA={TARGET['LRA']}:measured_I={d['input_i']}:"
          f"measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}:measured_thresh={d['input_thresh']}:"
          f"offset={d['target_offset']}:linear=false")
    p2 = run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", str(src), "-map", "0:v:0", "-map", "0:a:0",
              "-c:v", "copy", "-af", af, "-ar", "48000", "-c:a", "aac", "-b:a", "256k", str(dst)])
    if p2.returncode != 0 or not dst.exists():
        return {"n": j["n"], "ok": False, "error": p2.stderr[-300:]}
    pr = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-show_entries", "stream=codec_name,width,height",
              "-of", "json", str(dst)])
    info = json.loads(pr.stdout)
    dur = float(info["format"]["duration"])
    vs = [s for s in info["streams"] if s.get("width")]
    after = measure(dst)
    exp = j["dur_frames"] / 60.0
    ok = (bool(vs) and (vs[0]["width"], vs[0]["height"]) == (1080, 1920) and abs(dur - exp) < 0.5
          and after["lufs"] is not None and abs(after["lufs"] + 14) <= 1.0
          and after["peak"] is not None and after["peak"] <= -1.0)
    return {"n": j["n"], "name": j["name"], "ok": ok, "before": {"lufs": float(d["input_i"]), "tp": float(d["input_tp"])},
            "after": after, "dur": round(dur, 2), "expected_dur": round(exp, 2), "file": str(dst)}


def main():
    total = int(sys.argv[sys.argv.index("--total") + 1])
    done_name = sys.argv[sys.argv.index("--done") + 1] if "--done" in sys.argv else "done.jsonl"
    tp = float(sys.argv[sys.argv.index("--tp") + 1]) if "--tp" in sys.argv else TARGET["TP"]
    TARGET["TP"] = tp
    seen, results = set(), []
    done_path = OUT / done_name
    while len(seen) < total:
        lines = done_path.read_text(encoding="utf-8").splitlines() if done_path.exists() else []
        new = [json.loads(x) for x in lines if x.strip()]
        new = [j for j in new if j["n"] not in seen]
        if not new:
            time.sleep(10)
            continue
        for j in new:
            seen.add(j["n"])
            if j["status"] != "Complete":
                results.append({"n": j["n"], "ok": False, "error": "render " + j["status"]})
            else:
                results.append(process(j))
            print("LOUDNORM", results[-1].get("n"), results[-1].get("ok"), results[-1].get("after"), flush=True)
            (OUT / ("loudnorm_results.json" if done_name == "done.jsonl" else "loudnorm_results_" + done_name.replace(".jsonl", "") + ".json")).write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print("ALL LOUDNORM DONE", sum(1 for r in results if r["ok"]), "/", len(results), flush=True)


if __name__ == "__main__":
    main()
