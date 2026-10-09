"""Render each focus cue (burn-in subtitles) per timeline and save the mid frame + a contact sheet.
MCP-GAP: timeline_frame.capture -> RENDER_START_FAILED on this build; render via scripting API. Read-only for timelines."""
import json, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from scripts.resolve_common import connect_resolve
plan = json.load(open(sys.argv[1], encoding="utf-8")); out = Path(sys.argv[2]).resolve(); out.mkdir(parents=True, exist_ok=True)
rows = plan["targets"] + [{"ordinal": 4, "name": "บ่นทำไมชอบสู้ในทางแคบ-strinova-vdo", "cue": [1995, 2272]}]
r = connect_resolve(); pm = r.GetProjectManager(); p = pm.GetCurrentProject()
entry = p.GetCurrentTimeline(); page = r.GetCurrentPage(); r.OpenPage("edit"); time.sleep(1)
preset = f"qc-all-{int(time.time())}"; assert p.SaveAsNewRenderPreset(preset)
byname = {p.GetTimelineByIndex(i).GetName(): p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1)}
done = {}
try:
    for t in sorted(rows, key=lambda x: x["ordinal"]):
        n = t["ordinal"]; s, e = t["cue"]; tl = byname[t["name"]]
        p.SetCurrentTimeline(tl); time.sleep(1.5)
        p.LoadRenderPreset("H.264 Master"); p.SetCurrentRenderFormatAndCodec("mp4", "H264_NVIDIA"); p.SetCurrentRenderMode(1)
        p.SetRenderSettings({"TargetDir": str(out), "CustomName": f"T{n:02d}", "SelectAllFrames": False, "ExportVideo": True,
            "ExportAudio": False, "FormatWidth": 1280, "FormatHeight": 720, "FrameRate": 60.0, "MarkIn": s, "MarkOut": e - 1,
            "ExportSubtitle": True, "SubtitleFormat": "BurnIn"})
        job = p.AddRenderJob(); ok = job and p.StartRendering([job], False)
        while ok and p.IsRenderingInProgress(): time.sleep(1)
        st = p.GetRenderJobStatus(job).get("JobStatus") if job else None
        v = out / f"T{n:02d}.mp4"
        if st == "Complete" and v.is_file():
            subprocess.run(["ffmpeg", "-y", "-i", str(v), "-vf", f"select=eq(n\\,{(e - s) // 2})", "-frames:v", "1", str(out / f"T{n:02d}.jpg"), "-hide_banner", "-loglevel", "error"])
        done[n] = st; print(n, st, flush=True)
finally:
    p.LoadRenderPreset(preset)
    for i in range(1, p.GetTimelineCount() + 1):
        if p.GetTimelineByIndex(i).GetUniqueId() == entry.GetUniqueId(): p.SetCurrentTimeline(p.GetTimelineByIndex(i))
    r.OpenPage(page); json.dump(done, open(out / "qc.json", "w"))
