"""Merge reader output review/<pack>.json -> review/<id>.proposals.json/.md for the final reviewer.
Checks each item (keys, order, length, quote really in the pack), drops duplicates from overlapping packs,
and marks `quiet` items the loudness shortlist never reached."""
import json, re
import config

KEYS = {"id", "source_id", "pack", "start_s", "end_s", "setup_s", "payoff_s", "category", "title_th", "quote", "reason", "confidence"}

def _hms(s: float) -> str:
    s = int(s); return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"

def _norm(t: str) -> str:
    return re.sub(r"\s+", "", t)

def problems(item: dict, pack_text: str, duration_s: float) -> list[str]:
    if not KEYS <= set(item):
        return [f"missing keys {sorted(KEYS - set(item))}"]
    out = []
    if not item["start_s"] <= item["setup_s"] < item["payoff_s"] < item["end_s"]:
        out.append("needs start <= setup < payoff < end")
    if not config.CLIP_MIN_S <= item["end_s"] - item["start_s"] <= config.CLIP_MAX_S:
        out.append(f"length {item['end_s'] - item['start_s']:.0f}s")
    if item["start_s"] < 0 or item["end_s"] > duration_s:
        out.append("outside the video")
    if item["category"] not in config.CATEGORIES:
        out.append(f"category {item['category']}")
    if not 0 <= item["confidence"] <= 1:
        out.append("confidence")
    if not _norm(item["quote"]) or _norm(item["quote"]) not in _norm(pack_text):
        out.append("quote not in pack")
    return out

def overlap(a, b) -> float:
    inter = min(a["end_s"], b["end_s"]) - max(a["start_s"], b["start_s"])
    return max(0.0, inter) / min(a["end_s"] - a["start_s"], b["end_s"] - b["start_s"])

def merge(items, min_overlap: float = 0.5):
    """keep the most confident of items that overlap by >= min_overlap of the shorter one."""
    kept = []
    for it in sorted(items, key=lambda x: -x["confidence"]):
        if all(overlap(it, k) < min_overlap for k in kept):
            kept.append(it)
    return sorted(kept, key=lambda x: x["start_s"])

def format_md(source_id: str, items) -> str:
    out = [f"# Reader proposals {source_id} ({len(items)} after merge; quote = payoff line from the unverified transcript)", ""]
    for it in items:
        tag = "quiet" if it["quiet"] else "shortlist"
        out += [f"## {it['id']}  {_hms(it['start_s'])}-{_hms(it['end_s'])} ({it['end_s'] - it['start_s']:.0f}s)  "
                f"{it['category']}  conf={it['confidence']:.2f}  {tag}",
                f"start_s={it['start_s']} end_s={it['end_s']} payoff at {_hms(it['payoff_s'])}",
                f"title: {it['title_th']}", f"quote: {it['quote']}", f"why: {it['reason']}", ""]
    return "\n".join(out)

def run(source_id: str, packs: list, duration_s: float, top_windows) -> dict:
    rv = config.WORK_DIR / "review"
    items, bad, missing = [], [], []
    for p in packs:
        f = rv / f"{p['pack']}.json"
        if not f.exists():
            missing.append(p["pack"]); continue
        text = (rv / p["file"]).read_text(encoding="utf-8")
        for it in json.loads(f.read_text(encoding="utf-8")):
            pr = problems(it, text, duration_s)
            (bad.append((it.get("id"), pr)) if pr else items.append(it))
    merged = merge(items)
    for it in merged:
        it["quiet"] = not any(s < it["end_s"] and e > it["start_s"] for s, e, *_ in top_windows)
    (rv / f"{source_id}.proposals.json").write_text(json.dumps(merged, ensure_ascii=False, indent=1), encoding="utf-8")
    (rv / f"{source_id}.proposals.md").write_text(format_md(source_id, merged), encoding="utf-8")
    return {"kept": len(merged), "read": len(items), "rejected": bad, "missing_packs": missing}

def run_all() -> None:
    w = config.WORK_DIR
    inv = {r["source_id"]: r for r in json.loads((w / "inventory.json").read_text(encoding="utf-8"))}
    plan = json.loads((w / "review" / "read-plan.json").read_text(encoding="utf-8"))
    for sid, packs in plan.items():
        top = json.loads((w / "scores" / f"{sid}.top.json").read_text(encoding="utf-8"))
        r = run(sid, packs, inv[sid]["duration_s"], top)
        print(sid, f"{r['kept']} kept of {r['read']} valid;", f"rejected {r['rejected']};" if r["rejected"] else "",
              f"MISSING reader output {r['missing_packs']}" if r["missing_packs"] else "", flush=True)
