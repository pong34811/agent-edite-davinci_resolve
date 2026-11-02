"""Create the planned timelines for ONE Resolve project from timeline_plan.json via the Resolve scripting API.
usage: python make_timelines.py <project-name>   (that project must already be the current project)
Skips plan entries whose timeline name already exists. Writes verification rows to stdout (JSON)."""
import sys, json, os, pathlib
sys.path.insert(0, r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ.setdefault("RESOLVE_SCRIPT_LIB", r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll")
import DaVinciResolveScript as dvr

proj_name = sys.argv[1]
job = pathlib.Path(os.environ["HIGHLIGHT_JOB"]).parent
TL_FPS = json.loads((job / "job.json").read_text(encoding="utf-8"))["TIMELINE_FPS"]
inv = {r["source_id"]: r for r in json.loads((job / "inventory.json").read_text(encoding="utf-8"))}
plan = [x for x in json.loads((job / "timeline_plan.json").read_text(encoding="utf-8")) if x["project"] == proj_name]

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
project = pm.GetCurrentProject()
assert project.GetName() == proj_name, f"current project is {project.GetName()!r}, expected {proj_name!r}"
mp = project.GetMediaPool()
folder = mp.GetCurrentFolder()
assert folder.GetName() == "2026-09-aomimama", f"current folder is {folder.GetName()!r}"
clips = {c.GetUniqueId(): c for c in folder.GetClipList()}
existing = {project.GetTimelineByIndex(i).GetName() for i in range(1, project.GetTimelineCount() + 1)}

rows = []
for x in plan:
    if x["name"] in existing:
        rows.append({"name": x["name"], "status": "skipped-exists"}); continue
    ci = x["clip_infos"][0]
    item = clips[ci["clip_id"]]
    tl = mp.CreateTimelineFromClips(x["name"], [{"mediaPoolItem": item, "startFrame": ci["start_frame"],
                                                  "endFrame": ci["end_frame"], "recordFrame": 0}])
    row = {"name": x["name"], "status": "created" if tl else "FAILED"}
    if tl:
        src_fps = inv[x["candidate"].split("-")[0]]["fps"]
        expected = round((ci["end_frame"] - ci["start_frame"]) * TL_FPS / src_fps)
        row["frames"] = tl.GetEndFrame() - tl.GetStartFrame()
        row["expected"] = expected
        row["items"] = len(tl.GetItemListInTrack("video", 1))
        row["ok"] = row["frames"] == expected and row["items"] == 1
    rows.append(row)
print(json.dumps(rows, ensure_ascii=False))
