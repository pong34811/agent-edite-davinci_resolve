"""Pass C: reading packs so subagents read the WHOLE stream, not just the loudness shortlist.
Each pack is ~30 min of `fulltext` sentences with a per-minute signal line between minutes, overlapping its
neighbour by 2 min so a story at the seam is seen whole. Writes review/<id>-read-NN.md (+ index in read-plan.json).
Needs `features`, `shortlist` and `fulltext` done."""
import json
import numpy as np
import config, fulltext
from shortlist import _jump

PACK_S = 1800
OVERLAP_S = 120

def _hms(s: float) -> str:
    s = int(s); return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"

def minute_signals(rms, top_windows, sentences):
    """-> one dict per minute: loud (z of the minute's mean dB vs the whole video), jump (max dB rise over the
    recent median), talk (share of seconds inside a sentence), short (minute overlaps a shortlist window),
    hot (loud z >= 1.5 or jump in the stream's top 10% of minutes; a fixed dB bar flagged nearly every minute)."""
    rms = np.asarray(rms, dtype=float)
    n = int(np.ceil(len(rms) / 60))
    means = np.array([rms[m * 60:(m + 1) * 60].mean() for m in range(n)])
    z = (means - means.mean()) / (means.std() or 1.0)
    jump = _jump(rms)
    talk = np.zeros(n * 60)
    for s in sentences:
        talk[int(s["start"]):int(np.ceil(s["end"]))] = 1
    jmax = np.array([jump[m * 60:(m + 1) * 60].max() for m in range(n)])
    jhot = np.percentile(jmax, 90)
    out = []
    for m in range(n):
        a, b = m * 60, (m + 1) * 60
        out.append({"t": a, "loud": round(float(z[m]), 1), "jump": round(float(jmax[m]), 1),
                    "talk": round(float(talk[a:b].mean()), 2), "short": any(s < b and e > a for s, e, *_ in top_windows),
                    "hot": bool(z[m] >= 1.5 or (jmax[m] >= jhot and jmax[m] > 0))})
    return out

def signal_line(sig) -> str:
    flags = [f"loud {sig['loud']:+.1f}", f"jump {sig['jump']:.0f}dB", f"talk {int(sig['talk'] * 100)}%"]
    if sig["hot"]:
        flags.append("!!")
    if sig["short"]:
        flags.append("shortlist")
    return f"── {_hms(sig['t'])}  " + "  ".join(flags)

def packs(duration_s: float, size: float = PACK_S, overlap: float = OVERLAP_S):
    out, s = [], 0.0
    while s < duration_s:
        e = min(s + size, duration_s)
        if out and e - s < size / 3:          # fold a short tail into the previous pack
            out[-1] = (out[-1][0], e); break
        out.append((s, e)); s = e - overlap if e < duration_s else e
    return out

def format_pack(source_id: str, n: int, total: int, span, sentences, sigs) -> str:
    s, e = span
    head = [f"# Reading pack {source_id}-read-{n:02d} ({n}/{total})  {_hms(s)}-{_hms(e)}",
            "Lines: `[H:MM:SS] text   [ends seconds]` (unverified ASR). `──` lines are per-minute audio signals: "
            "loud = minute loudness vs the whole stream (z), jump = sudden rise in dB, talk = share of the minute with speech, "
            "!! = strong spike, shortlist = picked by the loudness funnel.", ""]
    body, items = [], [(g["t"], 0, g) for g in sigs if s <= g["t"] < e] + [(x["start"], 1, x) for x in sentences if s <= x["start"] < e]
    for _, kind, x in sorted(items, key=lambda i: (i[0], i[1])):
        body.append(signal_line(x) if kind == 0 else f"[{_hms(x['start'])}] {x['text']}   [ends {x['end']:.1f}]")
    return "\n".join(head + body) + "\n"

def run(source_id: str) -> list:
    w = config.WORK_DIR
    sents = fulltext.load_sentences(source_id)
    if sents is None:
        raise FileNotFoundError(f"run `pipeline.py fulltext` first: no transcripts/{source_id}.sentences.json")
    d = np.load(w / "scores" / f"{source_id}.features.npz")
    top = json.loads((w / "scores" / f"{source_id}.top.json").read_text(encoding="utf-8"))
    sigs = minute_signals(d["rms"], top, sents)
    spans = packs(float(len(d["rms"])))
    (w / "review").mkdir(exist_ok=True)
    files = []
    for i, sp in enumerate(spans, 1):
        p = w / "review" / f"{source_id}-read-{i:02d}.md"   # same stem as the pack id the brief names
        p.write_text(format_pack(source_id, i, len(spans), sp, sents, sigs), encoding="utf-8")
        files.append({"pack": f"{source_id}-read-{i:02d}", "file": p.name, "start_s": sp[0], "end_s": sp[1]})
    return files

def run_all(ids=None) -> None:
    inv = json.loads((config.WORK_DIR / "inventory.json").read_text(encoding="utf-8"))
    pf = config.WORK_DIR / "review" / "read-plan.json"
    plan = json.loads(pf.read_text(encoding="utf-8")) if pf.exists() else {}
    plan.update({r["source_id"]: run(r["source_id"]) for r in inv if not ids or r["source_id"] in ids})
    pf.write_text(json.dumps(plan, indent=1), encoding="utf-8")
    print(sum(map(len, plan.values())), "reading packs for", len(plan), "videos", flush=True)
