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
        WORK=_fwd(config.WORK_DIR.resolve()), CODE=_fwd(config.CODE_DIR.resolve()),
        PYTHON=".venv/Scripts/python.exe")

def run_all(hint: str = "") -> None:
    inv = json.loads((config.WORK_DIR / "inventory.json").read_text(encoding="utf-8"))
    out = config.WORK_DIR / "review"; out.mkdir(exist_ok=True)
    for r in inv:
        (out / f"{r['source_id']}.brief.md").write_text(render(r["source_id"], inv, hint), encoding="utf-8")
    print(len(inv), "briefs written to", out, flush=True)

if __name__ == "__main__":
    run_all(" ".join(sys.argv[1:]))
