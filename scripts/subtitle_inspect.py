"""Curation helpers for Thai subtitle jobs (read-only on the workspace).

    python scripts/subtitle_inspect.py view  WS N [T0 T1]   all passes side by side + VAD
    python scripts/subtitle_inspect.py gap   WS N T0 T1     cues + every pass's word times near a range
    python scripts/subtitle_inspect.py check WS [--jobs 1,2] independent SRT re-check vs VAD
`check` re-parses each srt/job<N>.srt and, from the SRT plus the VAD map alone, counts cues that
start before VAD speech (> 0.05 s), linger > 0.1 s after VAD speech (cues > 0.35 s), uncovered
VAD speech >= 0.3 s (logged / unlogged) and runs the validator with the job's duration_s limit.
For a job whose curation sets "vad_clamp": false (silero misses its speech), the early/linger
checks use voice-band energy bursts instead (energy_checks), so they are not vacuous.
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


ENERGY_HOP = 0.05      # s per frame
ENERGY_REL_DB = 10.0   # a speech frame has voice-band energy >= job median + this ...
VOICED_MIN = 0.6       # ... and periodicity (normalised autocorrelation, F0 90-500 Hz) >= this
EDGE_FRAMES = 2        # unvoiced consonant frames (energy only) allowed before/after the voicing


def energy_envelope(ws, n):
    """Per ENERGY_HOP frame of the RAW audio/job<N>.wav (the _voice WAV is not used: its
    denoise/normaliser filters delay it by ~50 ms): (voice-band 300-3000 Hz energy in dB,
    periodicity 0..1 of the band-limited frame). Frame k covers [k*hop, (k+1)*hop).
    Periodicity separates voiced speech from game noise / gunfire of the same level."""
    import wave
    import numpy as np
    w = wave.open(os.path.join(ws, "audio", "job%d.wav" % n))
    sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
    if w.getnchannels() > 1:
        x = x.reshape(-1, w.getnchannels()).mean(axis=1)
    hop = int(sr * ENERGY_HOP)
    win = np.hanning(hop)
    f = np.fft.rfftfreq(hop, 1.0 / sr)
    band = (f >= 300) & (f <= 3000)
    lo, hi = int(sr / 500), int(sr / 90)
    en, per = [], []
    for i in range(0, len(x) - hop + 1, hop):
        X = np.fft.rfft(x[i:i + hop] * win) * band
        en.append(10 * np.log10((np.abs(X) ** 2).sum() + 1e-12))
        ac = np.fft.irfft(np.abs(np.fft.rfft(np.fft.irfft(X, hop), 2 * hop)) ** 2)[:hop]
        per.append(float(ac[lo:hi].max() / ac[0]) if ac[0] > 0 else 0.0)
    return np.array(en), np.array(per)


def energy_checks(cues, env, hop=ENERGY_HOP, rel_db=ENERGY_REL_DB, voiced=VOICED_MIN):
    """Independent start/linger check against voiced energy bursts, for jobs where silero
    VAD is known to miss the speech (curation vad_clamp false). cues: [{start,end,text}];
    env: (energy dB, periodicity) from energy_envelope. A speech frame has energy >= job
    median + rel_db and periodicity >= voiced; up to EDGE_FRAMES loud unvoiced frames
    directly before / after a run of speech frames (consonants) also count.
    Early: the first speech frame in [start - 0.3, end) begins more than EARLY_TOL after the
    cue start. Linger (cues > READ_FLOOR): the cue ends more than 0.1 s after the end of its
    last speech frame. No burst: no speech frame at all in the cue."""
    import numpy as np
    en, per = env
    thr = float(np.median(en)) + rel_db
    sp = [bool(en[k] >= thr and per[k] >= voiced) for k in range(len(en))]
    ext = list(sp)
    for k in range(len(en)):
        if sp[k]:
            for d in range(1, EDGE_FRAMES + 1):
                for j in (k - d, k + d):
                    if 0 <= j < len(en) and not sp[j] and en[j] >= thr and all(
                            en[m] >= thr for m in range(min(j, k), max(j, k) + 1)):
                        ext[j] = True
    early, linger, none = [], [], []
    for c in cues:
        s, e, t = c["start"], c["end"], c["text"]
        ks = [k for k in range(max(0, int((s - 0.3) / hop)), min(len(en), int(np.ceil(e / hop))))
              if ext[k] and k * hop < e]
        if not ks:
            none.append((t, s))
            continue
        onset = ks[0] * hop
        if onset - s > S.EARLY_TOL + 1e-6:
            early.append((t, s, round(onset, 2)))
        last = (ks[-1] + 1) * hop
        if e - last > 0.1 + 1e-6 and e - s > S.READ_FLOOR + 0.001:
            linger.append((t, e, round(last, 2)))
    return {"early": early, "linger": linger, "no_burst": none}


def check_job(ws, n):
    with open(os.path.join(ws, "srt", "job%d.srt" % n), encoding="utf-8") as f:
        cues = S.parse_srt(f.read())
    _, reg = S.load_passes(ws, n)
    end = S.job_end_limit(ws, n)
    cp = os.path.join(ws, "srt", "job%d.curation.json" % n)
    cur = json.load(open(cp, encoding="utf-8")) if os.path.exists(cp) else {}
    use_vad = cur.get("vad_clamp", True)
    errs = S.validate_cues(cues, speech_start=reg[0][0] if reg and use_vad else None, end_limit=end)
    ok = {j["text"] for j in cur.get("no_vad_justified", [])}
    early, linger = [], []
    energy = None
    if not use_vad:   # silero misses this job's speech: energy bursts are the independent reference
        energy = energy_checks([{"start": c["start"], "end": c["end"], "text": c["lines"][0]} for c in cues],
                               energy_envelope(ws, n))
        early, linger = energy["early"], energy["linger"]
    for c in cues:
        t = c["lines"][0]
        if t in ok or energy is not None:
            continue
        if not any(r[0] - 0.05 - 1e-6 <= c["start"] < r[1] for r in reg):
            early.append((t, c["start"]))
        last = max([min(c["end"], r[1]) for r in reg if r[0] < c["end"]] or [-9])
        if c["end"] - last > 0.1 + 1e-6 and c["end"] - c["start"] > S.READ_FLOOR + 0.001:
            linger.append((t, c["end"], round(last, 2)))
    cc = [{"start": c["start"], "end": c["end"]} for c in cues]
    unc = S.uncovered_speech(reg, cc, cur.get("omitted", []))
    return {"job": n, "cues": len(cues), "end_limit": end, "errors": errs, "early": early, "linger": linger,
            "energy": energy,
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
            nb = r["energy"]["no_burst"] if r["energy"] else []
            fail = r["errors"] or r["early"] or r["linger"] or r["uncovered_unlogged"] or nb
            bad += bool(fail)
            print("job %d: %s; end<=%.1f; %searly %d, linger %d, %suncovered logged %d / unlogged %d; %s" % (
                n, S.fmt_stats(r["stats"]), r["end_limit"], "energy-based (vad_clamp false) " if r["energy"] else "",
                len(r["early"]), len(r["linger"]), "no burst %d, " % len(nb) if r["energy"] else "",
                r["uncovered_logged"], len(r["uncovered_unlogged"]),
                "PASS" if not fail else "FAIL %s" % (r["errors"] + r["early"] + r["linger"] + r["uncovered_unlogged"] + nb)))
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
