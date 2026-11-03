"""Where is this job? `python pipeline.py status` prints a per-video stage table and the ONE next step,
so any agent (Claude Code, Codex, Hermes) can resume a job from files alone. Read-only."""
import json, pathlib

# (key, label, what to run when it is missing); order is the funnel order
STEPS = [
    ("features", "audio+features", "python pipeline.py features"),
    ("shortlist", "shortlist", "python pipeline.py shortlist"),
    ("fulltext", "fulltext", "python pipeline.py fulltext   # whole video, word times; run in the background"),
    ("readpacks", "reading packs", "python pipeline.py readpacks && python pipeline.py readbriefs"),
    ("readers", "readers", "spawn one reader subagent per missing pack: \"read review/<pack>.brief.md and follow it\""),
    ("proposals", "proposals", "python pipeline.py proposals"),
    ("sheets", "contact sheets", "python pipeline.py sheets"),
    ("packets", "packets+briefs", "python pipeline.py packets && python pipeline.py briefs <channel hint>"),
    ("review", "final review", "spawn one reviewer subagent per missing video: \"read review/<id>.brief.md and follow it\""),
]

def video_state(w: pathlib.Path, sid: str, plan: dict) -> dict:
    sc, rv = w / "scores", w / "review"
    top = json.loads((sc / f"{sid}.top.json").read_text(encoding="utf-8")) if (sc / f"{sid}.top.json").exists() else None
    packs = plan.get(sid, [])
    missing_readers = [p["pack"] for p in packs if not (rv / f"{p['pack']}.json").exists()]
    return {
        "features": (w / "audio" / f"{sid}.wav").exists() and (sc / f"{sid}.features.npz").exists(),
        "shortlist": top is not None,
        "fulltext": (w / "transcripts" / f"{sid}.sentences.json").exists(),
        "readpacks": bool(packs) and all((rv / p["file"]).exists() and (rv / f"{p['pack']}.brief.md").exists() for p in packs),
        "readers": bool(packs) and not missing_readers,
        "proposals": (rv / f"{sid}.proposals.json").exists(),
        "sheets": top is not None and all((w / "frames" / f"{sid}_{int(t[0]):06d}.jpg").exists() for t in top),
        "packets": (rv / f"{sid}.packet.md").exists() and (rv / f"{sid}.brief.md").exists(),
        "review": (rv / f"{sid}.json").exists(),
        "_missing_readers": missing_readers,
    }

READING = {"fulltext", "readpacks", "readers", "proposals"}   # skipped when job.json READ_WHOLE_STREAM is false

def job_state(w: pathlib.Path, read_whole_stream: bool = True, only=None) -> dict:
    w = pathlib.Path(w)
    if not (w / "inventory.json").exists():
        return {"videos": {}, "next": "python pipeline.py inventory   # then check fps/aspect per file (new-channel-job-setup)"}
    ids = [r["source_id"] for r in json.loads((w / "inventory.json").read_text(encoding="utf-8")) if not only or r["source_id"] in only]
    pf = w / "review" / "read-plan.json"
    plan = json.loads(pf.read_text(encoding="utf-8")) if pf.exists() else {}
    vids = {sid: video_state(w, sid, plan) for sid in ids}
    for key, _, cmd in STEPS:
        if key in READING and not read_whole_stream:
            continue
        todo = [sid for sid, st in vids.items() if not st[key]]
        if todo:
            extra = ""
            if key == "readers":
                extra = "  missing: " + ", ".join(p for sid in todo for p in vids[sid]["_missing_readers"])
            ids_arg = " " + " ".join(todo) if key in ("fulltext", "readpacks", "proposals", "packets") else ""
            redo = [s for s in todo if vids[s]["review"]] if key in READING else []
            warn = (f"\n  NOTE: {', '.join(redo)} already have an approved review/<id>.json; ask before re-reviewing and "
                    "archive it as review/<id>.v1.json first") if redo else ""
            return {"videos": vids, "next": f"{cmd.replace('python pipeline.py ' + key, 'python pipeline.py ' + key + ids_arg, 1)}"
                                            f"   [{', '.join(todo)}]{extra}{warn}"}
    after = [("resolve_clips.json", "python -m pytest -q ../../tests/highlight -k review_files_match_schema   # gate; then MCP "
                                    "media_pool probe_media_pool saved to a file -> python resolve_clips.py <probe.json>"),
             ("timeline_plan.json", "python build_timelines.py   # candidates.json + timeline_plan.json; show the list, APPROVAL gate"),
             ("timeline_verification.json", "create timelines via Resolve MCP (create_timeline_from_clips, if_exists fail), save, "
                                            "then python verify_timelines.py")]
    for f, cmd in after:
        if not (w / f).exists():
            return {"videos": vids, "next": cmd}
    return {"videos": vids, "next": "done: report timelines, low-confidence clips and what was not verified"}

def format_table(state: dict) -> str:
    keys = [k for k, _, _ in STEPS]
    lines = ["video  " + " ".join(f"{k[:9]:>9}" for k in keys)]
    for sid, st in state["videos"].items():
        lines.append(f"{sid:<6} " + " ".join(f"{('yes' if st[k] else '-'):>9}" for k in keys))
    return "\n".join(lines + ["", "NEXT: " + state["next"]])

if __name__ == "__main__":
    import config
    print(format_table(job_state(config.WORK_DIR, config._job.get("READ_WHOLE_STREAM", True))))
