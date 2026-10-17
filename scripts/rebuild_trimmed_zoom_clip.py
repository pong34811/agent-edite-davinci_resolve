"""Rebuild ONE VTuber Zoom Adjustment Clip whose head was trimmed (ripple-deleted timeline start), keeping range + Fusion Transform.

MCP-GAP: davinci-resolve MCP has no generator insert with a mark range and no Fusion Transform write on this build (see
apply_vtuber_zoom.py) -> scripting API through scripts/resolve_common.

Why: a render failed with "The Fusion composition at 00:00:03:38 could not be processed" inside the first Adjustment Clip,
whose start had been cut by 11 frames (240 -> 229). The track is re-built with fresh generators at the wanted ranges and
the same Size/Center/Edges. Other tracks are compared before/after.

NOTE: inserting a generator ripples every later clip on the same track (a single-clip rebuild shifted six zoom clips by 229
frames and stretched the timeline), so the whole track is emptied and re-inserted in time order.

Usage: python -m scripts.rebuild_trimmed_zoom_clip --backup pre.drp --ranges '[[0,229],...]' [--track 2] [--apply]   (dry run default)
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.apply_vtuber_zoom import FOCUS_NAME, signature  # noqa: E402
from scripts.backup_drp import verify_drp  # noqa: E402
from scripts.focus_apply_batch import SETTLE, activate, check, get_transform, normalise, set_transform, timecode  # noqa: E402
from scripts.resolve_common import connect_resolve  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--backup", required=True)
    ap.add_argument("--track", type=int, default=2)
    ap.add_argument("--ranges", required=True, help='JSON [[start,end],...] = the exact Adjustment Clip ranges wanted on the track')
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    verify_drp(a.backup)
    ranges = [tuple(int(v) for v in x) for x in json.loads(a.ranges)]
    check(all(s < e for s, e in ranges) and all(e < s2 for (_, e), (s2, _) in zip(ranges, ranges[1:])), "bad ranges")
    r = connect_resolve()
    pm = r.GetProjectManager()
    project = pm.GetCurrentProject()
    check(not project.IsRenderingInProgress(), "render busy")
    tl = project.GetCurrentTimeline()
    fps = float(tl.GetSetting("timelineFrameRate"))
    clips = tl.GetItemListInTrack("video", a.track) or []
    check(clips and all(c.GetName() == FOCUS_NAME for c in clips), "track is not only Adjustment Clips")
    want = normalise(get_transform(clips[0]))
    print("current", [(int(c.GetStart()), int(c.GetEnd())) for c in clips])
    print("wanted ", ranges, "transform", want)
    if not a.apply:
        print("DRY RUN")
        return
    entry_tc, entry_page = tl.GetCurrentTimecode(), r.GetCurrentPage()
    r.OpenPage("edit")
    time.sleep(2)
    check(r.GetCurrentPage() == "edit", "no Edit page")
    counts = {k: tl.GetTrackCount(k) for k in ("video", "audio", "subtitle")}
    others = lambda: [x for x in signature(tl, counts) if not (x[0] == "video" and x[1] == a.track)]  # noqa: E731
    before = others()
    locks = {(k, i): tl.GetIsTrackLocked(k, i) for k in counts for i in range(1, counts[k] + 1)}
    try:
        for (k, i) in locks:
            tl.SetTrackLock(k, i, True)
        tl.SetTrackLock("video", a.track, False)
        time.sleep(SETTLE)
        # InsertGeneratorIntoTimeline ripples later clips on the track, so empty the track and insert in time order.
        check(tl.DeleteClips(clips, False), "delete failed")
        time.sleep(SETTLE)
        check(not (tl.GetItemListInTrack("video", a.track) or []), "track not empty")
        for s, e in ranges:
            tl.SetMarkInOut(s, e - 1)
            tl.SetCurrentTimecode(timecode(s, fps))
            time.sleep(SETTLE)
            check(tl.InsertGeneratorIntoTimeline(FOCUS_NAME), f"insert failed {s}-{e}")
            time.sleep(SETTLE)
            got = [x for x in tl.GetItemListInTrack("video", a.track) if int(x.GetStart()) == s]
            check(len(got) == 1 and int(got[0].GetEnd()) == e, f"range mismatch {s}-{e}")
            set_transform(got[0], want)
            tl.ClearMarkInOut()
    finally:
        tl.ClearMarkInOut()
        for (k, i), v in locks.items():
            tl.SetTrackLock(k, i, v)
        tl.SetCurrentTimecode(entry_tc)
        time.sleep(0.5)
    check(pm.SaveProject(), "save failed")
    now = tl.GetItemListInTrack("video", a.track)
    check([(int(x.GetStart()), int(x.GetEnd())) for x in now] == ranges, "range readback")
    check(all(normalise(get_transform(x)) == want for x in now), "transform readback")
    check(others() == before, "other tracks changed")
    r.OpenPage(entry_page)
    print("REBUILT", len(now), "clips; others unchanged; timeline end", tl.GetEndFrame())


if __name__ == "__main__":
    main()
