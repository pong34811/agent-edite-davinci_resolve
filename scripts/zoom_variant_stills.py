"""Export Resolve-rendered stills (start/mid/end of each Adjustment range) from a timeline; restores the active timeline."""
import sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.resolve_common import connect_resolve
from scripts.focus_apply_batch import timecode, activate

name, out = sys.argv[1], Path(sys.argv[2]).resolve()
r = connect_resolve(); pm = r.GetProjectManager(); p = pm.GetCurrentProject()
entry = p.GetCurrentTimeline(); etc = entry.GetCurrentTimecode()
tl = next(p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1) if p.GetTimelineByIndex(i).GetName() == name)
activate(p, tl)
n = tl.GetTrackCount("video")
frames = [("pre", 150)]
for k, it in enumerate(tl.GetItemListInTrack("video", n), 1):
    s, e = it.GetStart(), it.GetEnd()
    frames += [(f"c{k}a", s + 6), (f"c{k}b", (s + e) // 2), (f"c{k}c", e - 8)]
for tag, f in frames:
    tl.SetCurrentTimecode(timecode(f + 1, 60)); time.sleep(0.6)
    tl.SetCurrentTimecode(timecode(f, 60)); time.sleep(1.0)
    print(tag, f, p.ExportCurrentFrameAsStill(str(out / f"{tag}.png")), flush=True)
activate(p, entry); entry.SetCurrentTimecode(etc)
