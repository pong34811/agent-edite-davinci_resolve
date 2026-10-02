"""Curation helpers for Thai subtitle jobs (read-only on the workspace).

    python scripts/subtitle_inspect.py view  WS N [T0 T1]   all passes side by side + VAD
    python scripts/subtitle_inspect.py gap   WS N T0 T1     cues + every pass's word times near a range
    python scripts/subtitle_inspect.py check WS [--jobs 1,2] independent SRT re-check vs VAD
`check` re-parses each srt/job<N>.srt and, from the SRT plus the VAD map alone, counts cues that
start before VAD speech (> 0.05 s), linger > 0.1 s after VAD speech (cues > 0.35 s), uncovered
VAD speech >= 0.3 s (logged / unlogged) and runs the validator with the job's duration_s limit.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import subtitle_srt as S  # noqa: E402


def view(ws, n, t0=0.0, t1=1e9):
    passes, regions = S.load_passes(ws, n)
    print("VAD union:", " ".join("%.2f-%.2f" % tuple(r) for r in regions))
    for name, segs in passes.items():
        print("== %s" % name)
        for sg in segs:
            if sg["end"] < t0 or sg["start"] > t1:
                continue
            w = (" w%g" % sg["window"][0]) if "window" in sg else ""
            fl = (" [%s]" % ",".join(sg["flags"])) if sg["flags"] else ""
            txt = sg["clean_text"].strip()
            print("  %5.2f-%5.2f%s (%.2f) %s%s" % (sg["start"], sg["end"], w, sg["avg_logprob"],
                                                 txt[:200] + ("..." if len(txt) > 200 else ""), fl))


def gap(ws, n, t0, t1):
    p = os.path.join(ws, "srt", "job%d.srt" % n)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            cues = S.parse_srt(f.read())
        print("cues:", " | ".join("%.2f-%.2f %s" % (c["start"], c["end"], c["lines"][0]) for c in cues
                                   if c["end"] > t0 - 1.5 and c["start"] < t1 + 1.5))
    passes, reg = S.load_passes(ws, n)
    print("vad:", [r for r in reg if r[1] > t0 - 1 and r[0] < t1 + 1])
    for name, segs in passes.items():
        for sg in segs:
            ws_ = [w for w in sg["words"] if w["end"] > t0 - 0.3 and w["start"] < t1 + 0.3]
            if ws_:
                print("  %-16s w%s: %s" % (name, sg.get("window", ["-"])[0],
                                          " ".join("%s@%.2f-%.2f" % (w["text"], w["start"], w["end"]) for w in ws_)))


def check_job(ws, n):
    with open(os.path.join(ws, "srt", "job%d.srt" % n), encoding="utf-8") as f:
        cues = S.parse_srt(f.read())
    _, reg = S.load_passes(ws, n)
    end = S.job_end_limit(ws, n)
    errs = S.validate_cues(cues, speech_start=reg[0][0] if reg else None, end_limit=end)
    cp = os.path.join(ws, "srt", "job%d.curation.json" % n)
    cur = json.load(open(cp, encoding="utf-8")) if os.path.exists(cp) else {}
    ok = {j["text"] for j in cur.get("no_vad_justified", [])}
    early, linger = [], []
    for c in cues:
        t = c["lines"][0]
        if t in ok:
            continue
        if not any(r[0] - 0.05 - 1e-6 <= c["start"] < r[1] for r in reg):
            early.append((t, c["start"]))
        last = max([min(c["end"], r[1]) for r in reg if r[0] < c["end"]] or [-9])
        if c["end"] - last > 0.1 + 1e-6 and c["end"] - c["start"] > S.READ_FLOOR + 0.001:
            linger.append((t, c["end"], round(last, 2)))
    cc = [{"start": c["start"], "end": c["end"]} for c in cues]
    unc = S.uncovered_speech(reg, cc, cur.get("omitted", []))
    return {"job": n, "cues": len(cues), "end_limit": end, "errors": errs, "early": early, "linger": linger,
            "uncovered_logged": sum(1 for u in unc if u[2]), "uncovered_unlogged": [u[:2] for u in unc if not u[2]],
            "stats": S.cue_stats([{"start": c["start"], "end": c["end"]} for c in cues])}


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("view")
    v.add_argument("ws")
    v.add_argument("n", type=int)
    v.add_argument("t", nargs="*", type=float)
    g = sub.add_parser("gap")
    g.add_argument("ws")
    g.add_argument("n", type=int)
    g.add_argument("t0", type=float)
    g.add_argument("t1", type=float)
    c = sub.add_parser("check")
    c.add_argument("ws")
    c.add_argument("--jobs")
    a = ap.parse_args()
    if a.cmd == "view":
        view(a.ws, a.n, *(a.t or []))
    elif a.cmd == "gap":
        gap(a.ws, a.n, a.t0, a.t1)
    else:
        jobs = [int(x) for x in a.jobs.split(",")] if a.jobs else sorted(S.load_jobs(a.ws))
        bad = 0
        for n in jobs:
            r = check_job(a.ws, n)
            fail = r["errors"] or r["early"] or r["linger"] or r["uncovered_unlogged"]
            bad += bool(fail)
            print("job %d: %s; end<=%.1f; early %d, linger %d, uncovered logged %d / unlogged %d; %s" % (
                n, S.fmt_stats(r["stats"]), r["end_limit"], len(r["early"]), len(r["linger"]),
                r["uncovered_logged"], len(r["uncovered_unlogged"]),
                "PASS" if not fail else "FAIL %s" % (r["errors"] + r["early"] + r["linger"] + r["uncovered_unlogged"])))
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
