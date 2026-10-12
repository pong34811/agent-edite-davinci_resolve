"""Retune the Fusion Transform of every Adjustment Clip on a focus track (only those clips are touched).

Usage: python -m scripts.retune_vtuber_zoom <timeline name> <track name> <window_top> <window_bottom> <window_cx>
"""
import sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.resolve_common import connect_resolve
from scripts.focus_apply_batch import normalise, get_transform, set_transform_existing, activate, check
from scripts.apply_vtuber_zoom import window_transform, signature

name, track, top, bot, cx = sys.argv[1], sys.argv[2], *map(float, sys.argv[3:6])
r = connect_resolve(); pm = r.GetProjectManager(); p = pm.GetCurrentProject()
entry = p.GetCurrentTimeline(); etc = entry.GetCurrentTimecode()
tl = next(p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1) if p.GetTimelineByIndex(i).GetName() == name)
activate(p, tl)
idx = next(i for i in range(1, tl.GetTrackCount("video") + 1) if tl.GetTrackName("video", i) == track)
counts = {"video": idx - 1, "audio": tl.GetTrackCount("audio"), "subtitle": tl.GetTrackCount("subtitle")}
before = signature(tl, counts)
want = normalise(window_transform(top, bot, cx))
items = tl.GetItemListInTrack("video", idx)
for it in items:
    set_transform_existing(it, want)
    print("RETUNED", it.GetStart(), it.GetEnd(), flush=True)
check(pm.SaveProject(), "save failed")
check(all(normalise(get_transform(x)) == want for x in tl.GetItemListInTrack("video", idx)), "readback")
check(signature(tl, counts) == before, "protected drift")
print("OK", want)
activate(p, entry); entry.SetCurrentTimecode(etc)
