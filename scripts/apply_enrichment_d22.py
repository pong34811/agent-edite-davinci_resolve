"""Add approved BGM + SFX + reaction GIFs to an [ENHANCED] COPY of a timeline (additive only).

MCP-GAP: davinci-resolve MCP mutators auto-archive a timeline copy on every call (clutters the project) and cannot do
the per-item source-frame append + AudioVolume + before/after signature audit used here -> scripting API through
scripts/resolve_common.py (see .agents/skills/resolve-video-enrichment/references/asset-library-and-cues.md).

Usage: python -m scripts.apply_enrichment_d22 --plan plan.json [--apply]   (default: dry run, validates files only)
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.focus_apply_batch import SETTLE, check, activate  # noqa: E402
from scripts.resolve_common import connect_resolve  # noqa: E402
from scripts.backup_drp import verify_drp  # noqa: E402

GAP = 1.2
FPS = 60


def sig(tl, counts):
    return [(k, i, tl.GetTrackName(k, i),
             [(x.GetUniqueId(), x.GetName(), x.GetStart(), x.GetEnd()) for x in (tl.GetItemListInTrack(k, i) or [])])
            for k in ("video", "audio", "subtitle") for i in range(1, counts[k] + 1)]


def dur_of(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def prop(item, name):
    v = item.GetClipProperty(name)
    return v.get(name) if isinstance(v, dict) else v


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--backup", required=True)
    ap.add_argument("--in-place", action="store_true", help="edit the source timeline itself (explicit user instruction only)")
    a = ap.parse_args()
    plan = json.loads(Path(a.plan).read_text(encoding="utf-8"))
    verify_drp(a.backup)
    for k in ("bgm",):
        check(Path(plan[k]["path"]).is_file(), plan[k]["path"])
    for it in plan["sfx"] + plan["gif"]:
        check(Path(it["path"]).is_file(), it["path"])
    last = plan["timeline_end_frame"]
    for it in plan["sfx"] + plan["gif"]:
        check(0 <= it["frame"] < last, f"frame out of range {it}")
    print("files ok; bgm", plan["bgm"]["gain_db"], "dB;", len(plan["sfx"]), "sfx;", len(plan["gif"]), "gif")
    if not a.apply:
        print("DRY RUN")
        return

    r = connect_resolve()
    pm = r.GetProjectManager()
    project = pm.GetCurrentProject()
    check(project.GetName() == plan["project"] and not project.IsRenderingInProgress(), "project/render")
    mp = project.GetMediaPool()
    entry_tl = project.GetCurrentTimeline()
    entry_id, entry_tc, entry_page = entry_tl.GetUniqueId(), entry_tl.GetCurrentTimecode(), r.GetCurrentPage()
    entry_folder = mp.GetCurrentFolder()
    r.OpenPage("edit")
    time.sleep(2)
    src = next(project.GetTimelineByIndex(i) for i in range(1, project.GetTimelineCount() + 1)
               if project.GetTimelineByIndex(i).GetUniqueId() == plan["source_timeline_id"])
    activate(project, src)
    tl = src if a.in_place else src.DuplicateTimeline(plan["enhanced_name"])
    check(tl is not None and tl.GetEndFrame() == src.GetEndFrame(), "duplicate failed")
    activate(project, tl)
    counts = {k: tl.GetTrackCount(k) for k in ("video", "audio", "subtitle")}
    before = sig(tl, counts)
    check(float(tl.GetSetting("timelineFrameRate")) == FPS and tl.GetStartFrame() == 0, "fps/start")

    # --- import only the chosen files into a dedicated bin
    root = mp.GetRootFolder()
    folder = next((f for f in root.GetSubFolderList() if f.GetName() == plan["bin"]), None) or mp.AddSubFolder(root, plan["bin"])
    check(folder is not None and mp.SetCurrentFolder(folder), "bin")
    paths = [plan["bgm"]["path"]] + [x["path"] for x in plan["sfx"]] + [x["path"] for x in plan["gif"]]
    imported = mp.ImportMedia(paths)
    check(imported and len(imported) == len(paths), f"import returned {len(imported or [])}")
    by_path = {str(Path(prop(c, "File Path"))).lower(): c for c in imported}
    pool = {p: by_path[str(Path(p)).lower()] for p in paths}

    # Validate every GIF BEFORE touching the timeline: a too-short GIF found mid-append left a half-built copy.
    for g in plan["gif"]:
        c = pool[g["path"]]
        gfps, frames = float(prop(c, "FPS")), int(float(prop(c, "Frames")))
        check(min(frames, round(2 * gfps)) / gfps >= 1.5, f"GIF too short for a 1.5-2.5 s hold: {g['path']} ({frames} frames @ {gfps})")
    locks = {(k, i): tl.GetIsTrackLocked(k, i) for k in counts for i in range(1, counts[k] + 1)}
    try:
        for k, i in locks:
            tl.SetTrackLock(k, i, True)
        time.sleep(GAP)
        for kind, sub, name in (("audio", "stereo", "SFX"), ("audio", "stereo", "BGM"), ("video", None, "REACTIONS")):
            ok = tl.AddTrack(kind, sub) if sub else tl.AddTrack(kind)
            check(ok, f"AddTrack {name}")
            time.sleep(GAP)
            idx = tl.GetTrackCount(kind)
            tl.SetTrackName(kind, idx, name)
            tl.SetTrackLock(kind, idx, False)
            time.sleep(GAP)
        a_sfx, a_bgm, v_gif = counts["audio"] + 1, counts["audio"] + 2, counts["video"] + 1
        check(tl.GetTrackCount("audio") == a_bgm and tl.GetTrackCount("video") == v_gif, "track counts")

        def append(d, label):
            res = mp.AppendToTimeline([d])
            time.sleep(GAP)
            check(res and len(res) == 1, f"append failed: {label}")
            return res[0]

        placed = {"bgm": None, "sfx": [], "gif": []}
        # BGM: whole timeline
        item = append({"mediaPoolItem": pool[plan["bgm"]["path"]], "startFrame": 0, "endFrame": plan["timeline_end_frame"],
                       "mediaType": 2, "trackIndex": a_bgm, "recordFrame": 0}, "bgm")
        placed["bgm"] = item
        for s in plan["sfx"]:
            secs = min(dur_of(s["path"]), 3.0)
            end = int(secs * FPS) - 1
            placed["sfx"].append((s, append({"mediaPoolItem": pool[s["path"]], "startFrame": 0, "endFrame": end,
                                             "mediaType": 2, "trackIndex": a_sfx, "recordFrame": s["frame"]}, s["path"])))
        for g in plan["gif"]:
            c = pool[g["path"]]
            gfps, frames = float(prop(c, "FPS")), int(float(prop(c, "Frames")))
            n = min(frames, round(2 * gfps))
            g["_n"], g["_fps"] = n, gfps
        for g in plan["gif"]:
            c = pool[g["path"]]
            n, gfps = g["_n"], g["_fps"]
            item = append({"mediaPoolItem": c, "startFrame": 0, "endFrame": n - 1, "mediaType": 1,
                           "trackIndex": v_gif, "recordFrame": g["frame"]}, g["path"])
            rw, rh = (int(x) for x in str(prop(c, "Resolution")).split("x"))
            fit = min(1920 / rw, 1080 / rh)
            fw, fh = rw * fit, rh * fit
            z = min(420 / fw, 300 / fh)
            ow, oh, m = fw * z, fh * z, 40
            item.SetProperty("ZoomX", z)
            item.SetProperty("ZoomY", z)
            item.SetProperty("Pan", (-960 + m + ow / 2) * 1920 / fw)
            item.SetProperty("Tilt", (540 - m - oh / 2) * 1080 / fh)
            placed["gif"].append((g, item))
            print("GIF", g["path"].split("\\")[-1], "zoom %.3f" % z, "frames", n, flush=True)
        # levels
        placed["bgm"].SetProperty("AudioVolume", plan["bgm"]["gain_db"])
        for s, it in placed["sfx"]:
            it.SetProperty("AudioVolume", s["gain_db"])
        time.sleep(GAP)
    finally:
        for (k, i), v in locks.items():
            tl.SetTrackLock(k, i, v)
        time.sleep(0.5)
    check(pm.SaveProject(), "save failed")
    # --- readback
    check(sig(tl, counts) == before, "ORIGINAL TRACKS CHANGED")
    report = {"timeline": tl.GetName(), "tracks": {}, "items": []}
    for kind, idx in (("audio", a_sfx), ("audio", a_bgm), ("video", v_gif)):
        for it in tl.GetItemListInTrack(kind, idx) or []:
            row = {"track": f"{kind}{idx}", "name": it.GetName(), "start": it.GetStart(), "end": it.GetEnd()}
            if kind == "audio":
                row["AudioVolume"] = it.GetProperty("AudioVolume")
            else:
                row.update({k: it.GetProperty(k) for k in ("ZoomX", "Pan", "Tilt")})
            report["items"].append(row)
            print(row, flush=True)
    Path(plan["report"]).write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    # --- restore state
    mp.SetCurrentFolder(entry_folder)
    back = next(project.GetTimelineByIndex(i) for i in range(1, project.GetTimelineCount() + 1)
                if project.GetTimelineByIndex(i).GetUniqueId() == entry_id)
    activate(project, back)
    back.SetCurrentTimecode(entry_tc)
    r.OpenPage(entry_page)
    print("DONE; original tracks identical")


if __name__ == "__main__":
    main()
