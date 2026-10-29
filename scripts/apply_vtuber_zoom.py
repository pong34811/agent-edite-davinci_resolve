"""Add VTuber Zoom-Focus Adjustment Clips (one new video track) to a COPY of a timeline.

MCP-GAP: davinci-resolve MCP timeline mutators auto-archive a timeline copy on every call, and this build's edit_engine
lists no generator insert; Fusion Transform inputs are set through the scripting API (see fix_focus_black_band.py).
Same operations as focus_apply_p2.py, but N clips on one new track, on a duplicate named `<source>_focus_variant`.

Geometry (Fusion Transform, Pivot 0.5): output u shows composite 0.5 + (u - Center)/Size, so to put a window centred on
composite point (wx, wy_up) at the frame centre: Center = 0.5 - Size * (w - 0.5), per axis (y measured upward).

Usage: python -m scripts.apply_vtuber_zoom --plan plan.json --backup pre.drp [--apply]   (default: dry run)
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
from scripts.backup_drp import verify_drp  # noqa: E402
from scripts.focus_apply_batch import (  # noqa: E402
    SETTLE, check, activate, timecode, normalise, set_transform, get_transform,
)
from scripts.resolve_common import connect_resolve  # noqa: E402

FOCUS_NAME = "Adjustment Clip"


def window_transform(top, bottom, wx):
    """Fusion Transform values for a window spanning source rows [top, bottom] (0 = top) centred at column wx."""
    h = bottom - top
    size = 1.0 / h
    wy_up = 1.0 - (top + bottom) / 2.0
    return {"Size": size,
            "Center": {1: 0.5 - size * (wx - 0.5), 2: 0.5 - size * (wy_up - 0.5), 3: 0.0},
            "Edges": 0.0}


def signature(tl, counts):
    return [(k, i, tl.GetTrackName(k, i),
             [(x.GetUniqueId(), x.GetName(), x.GetStart(), x.GetEnd()) for x in (tl.GetItemListInTrack(k, i) or [])])
            for k in ("video", "audio", "subtitle") for i in range(1, counts[k] + 1)]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--backup", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--in-place", action="store_true", help="edit the plan's timeline itself (explicit user instruction only)")
    a = ap.parse_args()
    plan = json.loads(Path(a.plan).read_text(encoding="utf-8"))
    verify_drp(a.backup)
    want = normalise(window_transform(plan["window_top"], plan["window_bottom"], plan["window_cx"]))
    ranges = [tuple(x) for x in plan["ranges"]]
    for (s, e), (s2, _) in zip(ranges, ranges[1:] + [(10**9, 0)]):
        check(0 <= s < e and e - s >= 90 and e < s2, f"bad/overlapping range {s}-{e}")
    print("transform", want)
    print("ranges", ranges)
    if not a.apply:
        print("DRY RUN")
        return

    r = connect_resolve()
    pm = r.GetProjectManager()
    project = pm.GetCurrentProject()
    check(project.GetName() == plan["project"], "project mismatch")
    check(not project.IsRenderingInProgress(), "render busy")
    src = next(project.GetTimelineByIndex(i) for i in range(1, project.GetTimelineCount() + 1)
               if project.GetTimelineByIndex(i).GetUniqueId() == plan["timeline_id"])
    entry_tl = project.GetCurrentTimeline()
    entry_id, entry_tc, entry_page = entry_tl.GetUniqueId(), entry_tl.GetCurrentTimecode(), r.GetCurrentPage()
    r.OpenPage("edit")
    time.sleep(2)
    check(r.GetCurrentPage() == "edit", "no Edit page")
    activate(project, src)
    if a.in_place:
        tl = src
    else:
        variant = src.DuplicateTimeline(plan["variant_name"])
        check(variant is not None and variant.GetEndFrame() == src.GetEndFrame(), "duplicate failed")
        tl = variant
    activate(project, tl)
    check(float(tl.GetSetting("timelineFrameRate")) in (30, 60) and tl.GetStartFrame() == 0, "fps/start")
    counts = {k: tl.GetTrackCount(k) for k in ("video", "audio", "subtitle")}
    before = signature(tl, counts)
    locks = {(k, i): tl.GetIsTrackLocked(k, i) for k in counts for i in range(1, counts[k] + 1)}
    idx = counts["video"] + 1
    tc = tl.GetCurrentTimecode()
    done = []
    try:
        for k, i in locks:
            if k != "video":
                tl.SetTrackLock(k, i, True)
        time.sleep(SETTLE)
        check(tl.AddTrack("video") and tl.GetTrackCount("video") == idx, "AddTrack failed")
        time.sleep(SETTLE)
        tl.SetTrackName("video", idx, plan["track_name"])
        tl.SetTrackLock("video", idx, False)
        time.sleep(SETTLE)
        for s, e in ranges:
            tl.SetMarkInOut(s, e - 1)
            tl.SetCurrentTimecode(timecode(s, 60))
            time.sleep(SETTLE)
            check(tl.InsertGeneratorIntoTimeline(FOCUS_NAME), f"insert failed {s}-{e}")
            time.sleep(SETTLE)
            items = tl.GetItemListInTrack("video", idx) or []
            check(len(items) == len(done) + 1, f"track has {len(items)} items")
            it = items[-1]
            check((int(it.GetStart()), int(it.GetEnd())) == (s, e), f"range {it.GetStart()}-{it.GetEnd()} != {s}-{e}")
            check(signature(tl, counts) == before, "protected content changed -- STOP, restore backup")
            set_transform(it, want)
            done.append((s, e))
            print("APPLIED", s, e, flush=True)
            tl.ClearMarkInOut()
            time.sleep(SETTLE)
    finally:
        tl.ClearMarkInOut()
        for (k, i), v in locks.items():
            tl.SetTrackLock(k, i, v)
        tl.SetCurrentTimecode(tc)
        time.sleep(0.5)
    check(pm.SaveProject(), "save failed")
    items = tl.GetItemListInTrack("video", idx)
    check([(int(x.GetStart()), int(x.GetEnd())) for x in items] == ranges, "final range readback")
    for x in items:
        check(normalise(get_transform(x)) == want, "saved transform readback")
    check(signature(tl, counts) == before, "protected drift after save")
    print("VERIFIED", len(items), "clips on V%d of %s" % (idx, plan["variant_name"]))
    back = next(project.GetTimelineByIndex(i) for i in range(1, project.GetTimelineCount() + 1)
                if project.GetTimelineByIndex(i).GetUniqueId() == entry_id)
    activate(project, back)
    back.SetCurrentTimecode(entry_tc)
    r.OpenPage(entry_page)


if __name__ == "__main__":
    main()
