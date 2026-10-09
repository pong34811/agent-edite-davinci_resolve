"""Apply planned VTuber Zoom-Focus Adjustment Clips to aomimama-2026-09-p2 (one new top video track per timeline).

MCP-GAP: every step was proven through the davinci-resolve MCP on the pilot (timeline.add_track / insert_generator /
set_mark_in_out, fusion_comp.*), but a 40-timeline loop with a full before/after signature audit per timeline is not
practical call-by-call -> same operations through the scripting API via scripts/resolve_common.py.

Scope: ONLY adds one Adjustment Clip on a NEW video track. All original video/audio/subtitle tracks are locked during
the insert and audited before/after; any drift aborts the run (restore from the verified .drp).

Usage: python -m scripts.focus_apply_p2 --plan <plan.json> --backup <.drp> [--apply] [--only 5,6]
Default is a dry run.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.backup_drp import verify_drp  # noqa: E402
from scripts.focus_apply_batch import (  # noqa: E402
    SETTLE, check, activate, signature, timecode, normalise, set_transform, get_transform,
)
from scripts.resolve_common import connect_resolve  # noqa: E402

FOCUS_NAME = "Adjustment Clip"


def find_timeline(project, name, uid):
    for i in range(1, project.GetTimelineCount() + 1):
        t = project.GetTimelineByIndex(i)
        if t.GetUniqueId() == uid and t.GetName() == name:
            return t
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--backup", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--report", required=True)
    a = ap.parse_args()

    plan = json.loads(Path(a.plan).read_text(encoding="utf-8"))
    verify_drp(a.backup)
    only = {int(x) for x in a.only.split(",") if x}
    targets = [t for t in plan["targets"] if not only or t["ordinal"] in only]
    for t in targets:
        s, e = t["cue"]
        check(0 <= s < e and e - s >= 90, f"bad cue T{t['ordinal']:02d}")

    r = connect_resolve()
    check(r is not None, "Resolve unavailable")
    pm = r.GetProjectManager()
    project = pm.GetCurrentProject()
    check(project.GetName() == plan["project"], "project mismatch")
    check(not project.IsRenderingInProgress(), "render busy")
    entry_tl = project.GetCurrentTimeline()
    entry_id, entry_tc, entry_page = entry_tl.GetUniqueId(), entry_tl.GetCurrentTimecode(), r.GetCurrentPage()

    if a.apply:
        # InsertGeneratorIntoTimeline only lands on the new track from the Edit page (it overwrote V1 from Deliver).
        r.OpenPage("edit")
        time.sleep(2)
        check(r.GetCurrentPage() == "edit", "could not switch to the Edit page")

    report = {"apply": a.apply, "backup": a.backup, "started": datetime.now().isoformat(), "records": []}
    rp = Path(a.report)
    rp.parent.mkdir(parents=True, exist_ok=True)
    try:
        for t in targets:
            n = t["ordinal"]
            tl = find_timeline(project, t["name"], t["timeline_id"])
            check(tl is not None, f"T{n:02d} not found by name+id")
            activate(project, tl)
            check(r.GetCurrentPage() == "edit", f"T{n:02d} not on Edit page")
            check(float(tl.GetSetting("timelineFrameRate")) == 60 and tl.GetStartFrame() == 0, f"T{n:02d} fps/start")
            counts = {k: tl.GetTrackCount(k) for k in ("video", "audio", "subtitle")}
            before = signature(tl, counts)
            s, e = t["cue"]
            want = normalise(t["transform"])
            rec = {"ordinal": n, "name": t["name"], "cue": [s, e], "transform": want}
            if any(tl.GetTrackName("video", i) == t["track_name"] for i in range(1, counts["video"] + 1)):
                rec["status"] = "already_present"
                report["records"].append(rec)
                print(f"SKIP T{n:02d} already present", flush=True)
                continue
            if not a.apply:
                rec["status"] = "planned"
                report["records"].append(rec)
                print(f"PLANNED T{n:02d} {s}-{e} {want['Size']}", flush=True)
                continue
            # Rollback copy: if anything below fails the damaged timeline is renamed aside and this copy takes
            # its name back. (The first live attempt put the clip on V1 and shifted the whole timeline.)
            bk = tl.DuplicateTimeline(t["name"] + "_prefocus_bak")
            check(bk is not None and bk.GetEndFrame() == tl.GetEndFrame(), f"T{n:02d} backup copy failed")
            rec["backup_timeline"] = bk.GetUniqueId()
            activate(project, tl)
            locks = {(k, i): tl.GetIsTrackLocked(k, i) for k in counts for i in range(1, counts[k] + 1)}
            tc = tl.GetCurrentTimecode()
            idx = counts["video"] + 1
            try:
                for k, i in locks:
                    tl.SetTrackLock(k, i, True)
                time.sleep(SETTLE)
                check(tl.AddTrack("video"), f"T{n:02d} AddTrack failed")
                time.sleep(SETTLE)
                check(tl.GetTrackCount("video") == idx, f"T{n:02d} track count")
                tl.SetTrackName("video", idx, t["track_name"])
                tl.SetTrackLock("video", idx, False)
                time.sleep(SETTLE)
                tl.SetMarkInOut(s, e - 1)
                tl.SetCurrentTimecode(timecode(s, 60))
                time.sleep(SETTLE)
                check(tl.InsertGeneratorIntoTimeline(FOCUS_NAME), f"T{n:02d} generator insert failed")
                time.sleep(SETTLE)
                items = tl.GetItemListInTrack("video", idx) or []
                check(len(items) == 1, f"T{n:02d} inserted {len(items)} items")
                it = items[0]
                check(int(it.GetStart()) == s and int(it.GetEnd()) == e,
                      f"T{n:02d} range {it.GetStart()}-{it.GetEnd()} != {s}-{e}")
                check(signature(tl, counts) == before, f"T{n:02d} protected content changed -- STOP, restore backup")
                set_transform(it, want)
                rec.update(status="applied", track=idx, clip_id=it.GetUniqueId())
            except Exception:
                tl.ClearMarkInOut()
                for (k, i), v in locks.items():
                    tl.SetTrackLock(k, i, v)
                tl.SetName(t["name"] + "_FAILED_FOCUS_RETAINED")
                bk.SetName(t["name"])
                pm.SaveProject()
                rec["status"] = "rolled_back"
                report["records"].append(rec)
                print(f"ROLLED_BACK T{n:02d}", flush=True)
                raise
            finally:
                tl.ClearMarkInOut()
                for (k, i), v in locks.items():
                    tl.SetTrackLock(k, i, v)
                tl.SetCurrentTimecode(tc)
                time.sleep(0.5)
            check(pm.SaveProject(), f"T{n:02d} save failed")
            check(normalise(get_transform(it)) == want, f"T{n:02d} saved readback failed")
            rec["protected_content_verified"] = signature(tl, counts) == before
            check(rec["protected_content_verified"], f"T{n:02d} protected drift after save")
            report["records"].append(rec)
            print(f"APPLIED T{n:02d} V{idx} {s}-{e}", flush=True)
            rp.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    finally:
        back = find_timeline(project, entry_tl.GetName(), entry_id)
        if back is not None:
            activate(project, back)
            back.SetCurrentTimecode(entry_tc)
            time.sleep(0.5)
        r.OpenPage(entry_page)
        report["finished"] = datetime.now().isoformat()
        report["restored"] = bool(back is not None and project.GetCurrentTimeline().GetUniqueId() == entry_id)
        rp.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
        print("REPORT", rp, "restored", report["restored"], flush=True)


if __name__ == "__main__":
    main()
