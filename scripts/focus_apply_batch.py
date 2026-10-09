"""Apply / verify VTuber Zoom-Focus Adjustment Clips on aomimama-2026-09-p1.

MCP-GAP: live `davinci-resolve` MCP tools are absent from this session's tool
catalog (tool_search returns nothing for resolve; session.json records
"live MCP tools absent"), so per AGENTS.md the scripting-API fallback is used
through scripts/resolve_common.py:connect_resolve.

Scope: ONLY adds/updates one Adjustment Clip on a NEW video track per target
timeline. Never transforms, trims, moves or deletes underlying footage, audio,
subtitles or unrelated overlays. Original project is written behind a fresh
verified .drp checkpoint passed with --backup.

Usage:
  python -m scripts.focus_apply_batch --plan <plan.json> --backup <pre.drp> [--apply] [--verify]
Default is dry-run (read + report only).
"""
from __future__ import annotations

import argparse
import json
import time
import zipfile
from datetime import datetime
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.resolve_common import connect_resolve  # noqa: E402

ART = Path(".hermes/artifacts/vtuber-focus-review-2026-10-07").resolve()
PROJECT = "aomimama-2026-09-p1"
FOCUS_NAME = "Adjustment Clip"
SETTLE = 1.25


def check(value, message):
    if not value:
        raise RuntimeError(message)


def activate(project, timeline):
    project.SetCurrentTimeline(timeline)
    time.sleep(SETTLE)
    check(project.GetCurrentTimeline().GetUniqueId() == timeline.GetUniqueId(),
          "Active timeline identity mismatch")


def signature(timeline, counts):
    """Identity of every non-task track: names + item name/start/end."""
    return [(kind, i, timeline.GetTrackName(kind, i),
             [(x.GetUniqueId(), x.GetName(), x.GetStart(), x.GetEnd(),
               x.GetProperty()) for x in (timeline.GetItemListInTrack(kind, i) or [])])
            for kind in ("video", "audio", "subtitle")
            for i in range(1, counts[kind] + 1)]


def timecode(frame, fps):
    check(fps == 60, "timecode helper verified only for 60fps")
    seconds, f = divmod(frame, 60)
    h, seconds = divmod(seconds, 3600)
    m, s = divmod(seconds, 60)
    return f"{h:02d}:{m:02d}:{s:02d}:{f:02d}"


def active_comp(item):
    """Return the comp Resolve actually renders.

    A fresh Adjustment Clip already carries its own built-in comp
    (index 1). `AddFusionComp()` appends a NEW comp and makes that one
    active -- on an inserted clip the render comes from the LAST comp, so
    editing index 1 silently produces no visible change. Always resolve the
    highest index.
    """
    count = item.GetFusionCompCount()
    check(count >= 1, "clip has no Fusion comp")
    comp = item.GetFusionCompByIndex(count)
    check(comp is not None, "active comp unreadable")
    return comp


def get_transform(item):
    comp = active_comp(item)
    ts = [t for t in comp.GetToolList().values()
          if t.GetAttrs().get("TOOLS_RegID") == "Transform"]
    check(len(ts) == 1, "expected exactly one Transform node")
    return {k: ts[0].GetInput(k) for k in ("Size", "Center", "Edges")}


def set_transform(item, values):
    comp = item.AddFusionComp()
    check(comp is not None, "could not create Fusion comp")
    nodes = comp.GetToolList().values()
    ins = [x for x in nodes if x.GetAttrs().get("TOOLS_RegID") == "MediaIn"]
    outs = [x for x in nodes if x.GetAttrs().get("TOOLS_RegID") == "MediaOut"]
    check(len(ins) == 1 and len(outs) == 1, "comp IO missing")
    tr = comp.AddTool("Transform", -32768, -32768)
    check(tr and tr.ConnectInput("Input", ins[0]) and outs[0].ConnectInput("Input", tr),
          "graph connection failed")
    for k, v in values.items():
        tr.SetInput(k, v)
    time.sleep(SETTLE)
    check(get_transform(item) == values, "transform readback mismatch")


def set_transform_existing(item, values):
    """Update the Transform node of the comp Resolve actually renders."""
    comp = active_comp(item)
    ts = [t for t in comp.GetToolList().values()
          if t.GetAttrs().get("TOOLS_RegID") == "Transform"]
    check(len(ts) == 1, "expected exactly one Transform node to repair")
    for k, v in values.items():
        ts[0].SetInput(k, v)
    time.sleep(SETTLE)
    check(get_transform(item) == values, "repair readback mismatch")


def normalise(values):
    """Coerce to the exact shapes the Fusion Transform node returns.

    Center is a point input: Resolve's GetInput returns integer keys
    {1: x, 2: y, 3: z}. A JSON round-trip turns those keys into strings and
    SetInput then silently ignores the value, so cast them back.
    """
    return {"Size": float(values["Size"]),
            "Center": {int(k): float(v) for k, v in values["Center"].items()},
            "Edges": float(values["Edges"])}


def find_timeline(project, name, uid):
    for i in range(1, project.GetTimelineCount() + 1):
        t = project.GetTimelineByIndex(i)
        if t.GetName() == name and t.GetUniqueId() == uid:
            return t
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--backup", required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    plan = json.loads(Path(a.plan).read_text(encoding="utf-8"))
    backup = Path(a.backup)
    check(backup.is_file() and backup.stat().st_size > 0, "backup missing or empty")
    with zipfile.ZipFile(backup) as z:
        check(z.testzip() is None, "backup is not a valid archive")

    targets = plan["targets"]
    ids = [t["timeline_id"] for t in targets]
    check(len(ids) == len(set(ids)), "duplicate timeline_id in plan")
    for t in targets:
        s, e = t["cue"]
        check(0 <= s < e, f"bad cue range for T{t['ordinal']:02d}")
        check(e - s >= 120, f"cue shorter than 2s for T{t['ordinal']:02d}")

    r = connect_resolve()
    check(r is not None, "Resolve unavailable")
    pm = r.GetProjectManager()
    entry = pm.GetCurrentProject()
    entry_name = entry.GetName()
    entry_tl = entry.GetCurrentTimeline()
    entry_name_tl = entry_tl.GetName() if entry_tl else None
    entry_tc = entry_tl.GetCurrentTimecode() if entry_tl else None
    entry_page = r.GetCurrentPage()
    check(not entry.IsRenderingInProgress(), "render busy at entry")

    out = ART / "focus-batch" / datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    out.mkdir(parents=True, exist_ok=False)
    report = {"project": PROJECT, "apply": bool(a.apply), "plan": str(a.plan),
              "backup": str(backup), "started": datetime.now().isoformat(),
              "records": []}
    try:
        project = entry if entry_name == PROJECT else pm.LoadProject(PROJECT)
        check(project is not None, "target project unavailable")
        for t in targets:
            n = t["ordinal"]
            tl = find_timeline(project, t["name"], t["timeline_id"])
            check(tl is not None, f"T{n:02d} timeline not found by name+id")
            activate(project, tl)
            check(float(tl.GetSetting("timelineFrameRate")) == 60, f"T{n:02d} fps drift")
            counts = {k: tl.GetTrackCount(k) for k in ("video", "audio", "subtitle")}
            before = signature(tl, counts)
            track_name = t["track_name"]
            want = normalise(t["transform"])
            s, e = t["cue"]
            rec = {"ordinal": n, "timeline_id": tl.GetUniqueId(), "name": tl.GetName(),
                   "cue": [s, e], "track_name": track_name, "transform": want,
                   "video_tracks_before": counts["video"]}

            existing = [i for i in range(1, counts["video"] + 1)
                        if tl.GetTrackName("video", i) == track_name]
            check(len(existing) <= 1, f"T{n:02d} duplicate focus tracks")
            if existing:
                idx = existing[0]
                items = tl.GetItemListInTrack("video", idx) or []
                check(len(items) == 1, f"T{n:02d} focus track holds {len(items)} items")
                it = items[0]
                got = normalise(get_transform(it))
                if (int(it.GetStart()) == s and int(it.GetEnd()) == e
                        and got == want):
                    rec.update(status="already_matching", track=idx,
                               clip_id=it.GetUniqueId())
                    rec["protected_content_verified"] = signature(tl, counts) == before
                    report["records"].append(rec)
                    print(f"ALREADY_MATCHING T{n:02d}", flush=True)
                    continue
                if got["Center"] == {1: 0.5, 2: 0.5, 3: 0.0}:
                    # Interrupted run left the freshly inserted clip un-framed
                    # (Center still at the Transform default). Repair it in
                    # place rather than adding a second clip.
                    set_transform_existing(it, want)
                    rec.update(status="repaired", track=idx, clip_id=it.GetUniqueId(),
                               previous_transform=got)
                    rec["protected_content_verified"] = signature(tl, counts) == before
                    report["records"].append(rec)
                    print(f"REPAIRED T{n:02d} track={idx}", flush=True)
                    continue
                rec.update(status="existing_differs", track=idx,
                           clip_id=it.GetUniqueId(),
                           existing_range=[int(it.GetStart()), int(it.GetEnd())],
                           existing_transform=got)
                rec["protected_content_verified"] = signature(tl, counts) == before
                report["records"].append(rec)
                print(f"EXISTING_DIFFERS T{n:02d}", flush=True)
                continue

            if not a.apply:
                rec.update(status="planned", track=counts["video"] + 1)
                rec["protected_content_verified"] = True
                report["records"].append(rec)
                print(f"PLANNED T{n:02d}", flush=True)
                continue

            locks = {(k, i): tl.GetIsTrackLocked(k, i)
                     for k in counts for i in range(1, counts[k] + 1)}
            tc = tl.GetCurrentTimecode()
            idx = counts["video"] + 1
            try:
                for k, i in locks:
                    tl.SetTrackLock(k, i, True)
                time.sleep(SETTLE)
                check(tl.AddTrack("video"), f"T{n:02d} AddTrack failed")
                time.sleep(SETTLE)
                check(tl.GetTrackCount("video") == idx, f"T{n:02d} track count mismatch")
                tl.SetTrackName("video", idx, track_name)
                tl.SetTrackLock("video", idx, False)
                time.sleep(SETTLE)
                tl.SetMarkInOut(s, e - 1)
                tl.SetCurrentTimecode(timecode(s, 60))
                time.sleep(SETTLE)
                check(tl.InsertGeneratorIntoTimeline(FOCUS_NAME),
                      f"T{n:02d} generator insert failed")
                time.sleep(SETTLE)
                items = tl.GetItemListInTrack("video", idx) or []
                check(len(items) == 1, f"T{n:02d} inserted {len(items)} items")
                it = items[0]
                check(int(it.GetStart()) == s and int(it.GetEnd()) == e,
                      f"T{n:02d} inserted range {it.GetStart()}-{it.GetEnd()} != {s}-{e}")
                set_transform(it, want)
                check(signature(tl, counts) == before,
                      f"T{n:02d} protected content changed -- STOP and restore backup")
                rec.update(status="applied", track=idx, clip_id=it.GetUniqueId())
            finally:
                tl.ClearMarkInOut()
                for (k, i), v in locks.items():
                    tl.SetTrackLock(k, i, v)
                tl.SetCurrentTimecode(tc)
                time.sleep(0.5)
            check(pm.SaveProject(), f"T{n:02d} save failed")
            check(normalise(get_transform(it)) == want, f"T{n:02d} saved readback failed")
            rec["protected_content_verified"] = signature(tl, counts) == before
            report["records"].append(rec)
            print(f"APPLIED T{n:02d} track={idx} cue={s}-{e}", flush=True)
            (out / "report.json").write_text(
                json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    finally:
        o = pm.LoadProject(entry_name)
        check(o is not None, "entry project restore failed")
        t0 = None
        for i in range(1, o.GetTimelineCount() + 1):
            if o.GetTimelineByIndex(i).GetName() == entry_name_tl:
                t0 = o.GetTimelineByIndex(i)
                break
        if t0 is not None:
            activate(o, t0)
            if entry_tc:
                t0.SetCurrentTimecode(entry_tc)
            time.sleep(0.5)
        r.OpenPage(entry_page)
        time.sleep(0.5)
        report["working_state_restored"] = bool(
            t0 is not None and t0.GetCurrentTimecode() == entry_tc
            and r.GetCurrentPage() == entry_page)
        report["finished"] = datetime.now().isoformat()
        (out / "report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("REPORT", str(out / "report.json"), flush=True)
    print("RESTORED", report.get("working_state_restored"), flush=True)


if __name__ == "__main__":
    main()
