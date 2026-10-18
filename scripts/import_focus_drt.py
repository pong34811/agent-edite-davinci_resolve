"""Import a patched focus .drt as a `_focus_variant` timeline and give each Adjustment Clip its Fusion Transform.

Usage: python -m scripts.import_focus_drt --plan plan.json --drt patched.drt [--apply]   (default: dry run)

The plan is the apply_vtuber_zoom plan (project, timeline_id, variant_name, track_name, window_*, ranges). The source
timeline is never modified; every original track of the import is compared against the source before any transform is set.
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
from scripts.apply_vtuber_zoom import window_transform  # noqa: E402
from scripts.focus_apply_batch import SETTLE, activate, check, get_transform, normalise, set_transform  # noqa: E402
from scripts.resolve_common import connect_resolve  # noqa: E402


def track_sig(tl, kind, i):
    return [(x.GetName(), int(x.GetStart()), int(x.GetEnd())) for x in (tl.GetItemListInTrack(kind, i) or [])]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--drt", required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    plan = json.loads(Path(a.plan).read_text(encoding="utf-8"))
    want = normalise(window_transform(plan["window_top"], plan["window_bottom"], plan["window_cx"]))
    ranges = [tuple(x) for x in plan["ranges"]]
    print("transform", want, "clips", len(ranges))
    if not a.apply:
        print("DRY RUN")
        return
    r = connect_resolve()
    pm = r.GetProjectManager()
    project = pm.GetCurrentProject()
    check(project.GetName() == plan["project"], "project mismatch")
    tls = {project.GetTimelineByIndex(i).GetName(): project.GetTimelineByIndex(i)
           for i in range(1, project.GetTimelineCount() + 1)}
    check(plan["variant_name"] not in tls, "variant already exists")
    src = next(t for t in tls.values() if t.GetUniqueId() == plan["timeline_id"])
    entry = project.GetCurrentTimeline()
    entry_id, entry_tc = entry.GetUniqueId(), entry.GetCurrentTimecode()
    counts = {k: src.GetTrackCount(k) for k in ("video", "audio", "subtitle")}
    before = {(k, i): track_sig(src, k, i) for k in counts for i in range(1, counts[k] + 1)}
    mp = project.GetMediaPool()
    tl = mp.ImportTimelineFromFile(str(Path(a.drt).resolve()))
    check(tl is not None, "import failed")
    tl.SetName(plan["variant_name"])
    time.sleep(SETTLE)
    activate(project, tl)
    check(tl.GetTrackCount("video") == counts["video"] + 1, "video track count")
    idx = counts["video"] + 1
    check(tl.GetTrackName("video", idx) == plan["track_name"], "track name")
    for k in counts:
        check(tl.GetTrackCount(k) == counts[k] + (k == "video"), f"{k} track count")
    for (k, i), sig in before.items():
        check(track_sig(tl, k, i) == sig, f"original {k}{i} differs from source")
    items = tl.GetItemListInTrack("video", idx) or []
    check([(int(x.GetStart()), int(x.GetEnd())) for x in items] == ranges, "range readback")
    for n, x in enumerate(items, 1):
        set_transform(x, want)
        print("TRANSFORM", n, flush=True)
    check(pm.SaveProject(), "save failed")
    for x in tl.GetItemListInTrack("video", idx):
        check(normalise(get_transform(x)) == want, "saved transform readback")
    for (k, i), sig in before.items():
        check(track_sig(tl, k, i) == sig, f"original {k}{i} drift after save")
    print("VERIFIED", len(items), "clips on V%d of %s" % (idx, plan["variant_name"]))
    back = next(project.GetTimelineByIndex(i) for i in range(1, project.GetTimelineCount() + 1)
                if project.GetTimelineByIndex(i).GetUniqueId() == entry_id)
    activate(project, back)
    back.SetCurrentTimecode(entry_tc)


if __name__ == "__main__":
    main()
