"""Read-only: list V1 source file + mid-timeline source time per timeline, extract one frame each.
MCP-GAP: no MCP action lists per-timeline items without activating each timeline -> scripting API (read only)."""
import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.resolve_common import connect_resolve
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
p = connect_resolve().GetProjectManager().GetCurrentProject()
rows = []
for i in range(1, p.GetTimelineCount() + 1):
    t = p.GetTimelineByIndex(i)
    items = t.GetItemListInTrack("video", 1) or []
    subs = t.GetItemListInTrack("subtitle", 1) or []
    if not items:
        rows.append({"i": i, "name": t.GetName(), "err": "no V1"}); continue
    it = items[0]
    mp = it.GetMediaPoolItem()
    path = mp.GetClipProperty("File Path") if mp else None
    fps = float(t.GetSetting("timelineFrameRate"))
    # frame at the middle of the first subtitle cue (else timeline middle)
    f = (subs[0].GetStart() + subs[0].GetEnd()) // 2 if subs else (it.GetStart() + it.GetEnd()) // 2
    src = (it.GetSourceStartFrame() + (f - it.GetStart())) / fps
    img = out / f"{i:02d}.jpg"
    subprocess.run(["ffmpeg","-y","-loglevel","error","-ss",f"{src:.3f}","-i",path,"-frames:v","1","-vf","scale=480:-1",str(img)])
    rows.append({"i": i, "name": t.GetName(), "path": path, "frame": f, "v1_items": len(items), "vtracks": t.GetTrackCount("video"), "cues": len(subs)})
(out / "scan.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(rows))
