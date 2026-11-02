"""Per-video review packet: shortlist windows + transcript (+-60 s) + contact sheet path, in one markdown file."""
import json, re
import config

CTX_S = 60

def _hms(s: float) -> str:
    s = int(s); return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"

def _clean(t: str, limit: int = 240) -> str:
    t = re.sub(r"(.)\1{3,}", r"\1\1\1", t)
    return t if len(t) <= limit else t[:limit] + "..."

def format_packet(source_id: str, wins, segments, sheets: dict) -> str:
    out = [f"# Review packet {source_id}", ""]
    for i, (s, e, sc) in enumerate(wins):
        out += [f"## {source_id}-w{i + 1:02d}  {_hms(s)}-{_hms(e)}  score={sc:.2f}", f"sheet: {sheets.get(i, 'n/a')}", ""]
        out += [f"[{_hms(g['start'])}] {_clean(g['text'])}" for g in segments if g["end"] >= s - CTX_S and g["start"] <= e + CTX_S]
        out.append("")
    return "\n".join(out)

def run_all() -> None:
    (config.WORK_DIR / "review").mkdir(exist_ok=True)
    for sc in sorted((config.WORK_DIR / "scores").glob("*.top.json")):
        sid = sc.name.split(".")[0]
        wins = [tuple(w) for w in json.loads(sc.read_text(encoding="utf-8"))]
        segs = json.loads((config.WORK_DIR / "transcripts" / f"{sid}.json").read_text(encoding="utf-8"))
        sheets = {i: str(config.WORK_DIR / "frames" / f"{sid}_{int(w[0]):06d}.jpg") for i, w in enumerate(wins)}
        (config.WORK_DIR / "review" / f"{sid}.packet.md").write_text(format_packet(sid, wins, segs, sheets), encoding="utf-8")
    print("packets written", flush=True)
