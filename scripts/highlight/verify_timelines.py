"""Read-only check of EVERY planned highlight timeline in the current Resolve project against timeline_plan.json.

MCP `timeline probe_timeline_structure` / `detect_gaps_overlaps` read only the current timeline, so a batch
read-back would need a set_current per timeline; this reads all of them without switching anything.
usage: python verify_timelines.py   (HIGHLIGHT_JOB set; the job's Resolve project must be current)
Writes WORK_DIR/timeline_verification.json and exits 1 when any timeline does not match."""
import json, pathlib, sys
from collections import Counter

def compare(plan: list[dict], timelines: list[dict], clip_fps: dict, timeline_fps: float) -> list[dict]:
    """plan rows vs read-back {name, video:[{clip_id,start,duration,source_start}], audio:[{clip_id,start,duration}]}."""
    by_name, count = {}, Counter(t["name"] for t in timelines)
    for t in timelines:
        by_name.setdefault(t["name"], t)
    rows = []
    for p in plan:
        ci = p["clip_infos"][0]; problems = []
        t = by_name.get(p["name"])
        if t is None:
            rows.append({"name": p["name"], "candidate": p.get("candidate"), "ok": False, "problems": ["timeline missing"]})
            continue
        if count[p["name"]] > 1:
            problems.append(f"{count[p['name']]} timelines with this name")
        want_dur = round((ci["end_frame"] - ci["start_frame"]) * timeline_fps / clip_fps[ci["clip_id"]])
        if len(t["video"]) != 1:
            problems.append(f"{len(t['video'])} video items, expected 1")
        for v in t["video"][:1]:
            if v["clip_id"] != ci["clip_id"]: problems.append(f"video clip {v['clip_id']} != {ci['clip_id']}")
            if v["source_start"] != ci["start_frame"]: problems.append(f"source_start {v['source_start']} != {ci['start_frame']}")
            if abs(v["duration"] - want_dur) > 1: problems.append(f"video duration {v['duration']} != {want_dur}")
            if v["start"] != 0: problems.append(f"video starts at record {v['start']}, not the timeline start")
        if not t["audio"]:
            problems.append("no audio item")
        for a in t["audio"]:
            if a["clip_id"] != ci["clip_id"] or abs(a["duration"] - want_dur) > 1:
                problems.append(f"audio item {a['clip_id']} dur {a['duration']} != {want_dur}")
        rows.append({"name": p["name"], "candidate": p.get("candidate"), "ok": not problems, "problems": problems,
                     "video_duration": t["video"][0]["duration"] if t["video"] else None, "expected_duration": want_dur})
    return rows

def _read_project(project) -> list[dict]:
    out = []
    for i in range(1, project.GetTimelineCount() + 1):
        tl = project.GetTimelineByIndex(i); t0 = tl.GetStartFrame()
        row = {"name": tl.GetName(), "id": tl.GetUniqueId(), "video": [], "audio": []}
        for kind in ("video", "audio"):
            for n in range(1, tl.GetTrackCount(kind) + 1):
                for it in tl.GetItemListInTrack(kind, n) or []:
                    mpi = it.GetMediaPoolItem()
                    d = {"clip_id": mpi.GetUniqueId() if mpi else None, "start": it.GetStart() - t0,
                         "duration": it.GetDuration(), "source_start": it.GetSourceStartFrame()}
                    row[kind].append(d)
        out.append(row)
    return out

def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import config
    sys.path.insert(0, str(config.CODE_DIR.parent))
    from resolve_common import require_resolve
    project = require_resolve().GetProjectManager().GetCurrentProject()
    plan = json.loads((config.WORK_DIR / "timeline_plan.json").read_text(encoding="utf-8"))
    inv = {r["source_id"]: r for r in json.loads((config.WORK_DIR / "inventory.json").read_text(encoding="utf-8"))}
    clip_ids = json.loads((config.WORK_DIR / "resolve_clips.json").read_text(encoding="utf-8"))
    clip_fps = {clip_ids[sid]: inv[sid]["fps"] for sid in clip_ids}
    tl_fps = float(project.GetSetting("timelineFrameRate"))
    rows = compare(plan, _read_project(project), clip_fps, tl_fps)
    report = {"project": project.GetName(), "timeline_count": project.GetTimelineCount(), "planned": len(plan),
              "ok": sum(r["ok"] for r in rows), "rows": rows}
    (config.WORK_DIR / "timeline_verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(report["project"], "timelines", report["timeline_count"], "planned", report["planned"], "ok", report["ok"])
    for r in rows:
        if not r["ok"]:
            print("FAIL", r["name"], r["problems"])
    return 0 if report["ok"] == len(plan) else 1

if __name__ == "__main__":
    raise SystemExit(main())
