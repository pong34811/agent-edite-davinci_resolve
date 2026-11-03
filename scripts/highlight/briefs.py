"""Render the per-video reviewer brief (templates/reviewer_brief.md) so delegate_task contexts are files, not retyped prose."""
import json, pathlib, string, sys
import config

TEMPLATE = config.CODE_DIR / "templates" / "reviewer_brief.md"

def _fwd(p) -> str:
    return str(p).replace(chr(92), "/")

def render(source_id: str, inventory: list[dict], hint: str = "") -> str:
    row = next(r for r in inventory if r["source_id"] == source_id)
    return string.Template(TEMPLATE.read_text(encoding="utf-8")).substitute(
        VID=source_id, DURATION_S=int(row["duration_s"]), HINT=hint,
        CATEGORIES=", ".join(config.CATEGORIES), CLIP_MIN=config.CLIP_MIN_S, CLIP_MAX=config.CLIP_MAX_S,
        CLIPS_PER_VIDEO=config._job.get("CLIPS_PER_VIDEO", "4-8"),
        WORK=_fwd(config.WORK_DIR.resolve()), JOB_FILE=_fwd(config.JOB_FILE.resolve()), CODE=_fwd(config.CODE_DIR.resolve()),
        PYTHON=_fwd(config._job.get("PYTHON") or sys.executable))  # the interpreter that has the deps, not a guessed .venv

def run_all(hint: str = "") -> None:
    inv = json.loads((config.WORK_DIR / "inventory.json").read_text(encoding="utf-8"))
    out = config.WORK_DIR / "review"; out.mkdir(exist_ok=True)
    for r in inv:
        (out / f"{r['source_id']}.brief.md").write_text(render(r["source_id"], inv, hint), encoding="utf-8")
    print(len(inv), "briefs written to", out, flush=True)

READER = config.CODE_DIR / "templates" / "reader_brief.md"

def _hms(s: float) -> str:
    s = int(s); return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"

def render_reader(pack: dict, source_id: str, duration_s: float, hint: str = "") -> str:
    return string.Template(READER.read_text(encoding="utf-8")).substitute(
        VID=source_id, PACK=pack["pack"], PACK_START=_hms(pack["start_s"]), PACK_END=_hms(pack["end_s"]),
        DURATION_S=int(duration_s), HINT=hint, CATEGORIES=", ".join(config.CATEGORIES),
        CLIP_MIN=config.CLIP_MIN_S, CLIP_MAX=config.CLIP_MAX_S,
        WORK=_fwd(config.WORK_DIR.resolve()), JOB_FILE=_fwd(config.JOB_FILE.resolve()), CODE=_fwd(config.CODE_DIR.resolve()),
        PYTHON=_fwd(config._job.get("PYTHON") or sys.executable))

def run_readers(ids=None, hint: str = "") -> None:
    """review/<pack>.brief.md for every pack in read-plan.json (optionally only the given source ids)."""
    inv = {r["source_id"]: r for r in json.loads((config.WORK_DIR / "inventory.json").read_text(encoding="utf-8"))}
    plan = json.loads((config.WORK_DIR / "review" / "read-plan.json").read_text(encoding="utf-8"))
    n = 0
    for sid, packs in plan.items():
        if ids and sid not in ids:
            continue
        for p in packs:
            (config.WORK_DIR / "review" / f"{p['pack']}.brief.md").write_text(
                render_reader(p, sid, inv[sid]["duration_s"], hint), encoding="utf-8"); n += 1
    print(n, "reader briefs written", flush=True)

if __name__ == "__main__":
    run_all(" ".join(sys.argv[1:]))
