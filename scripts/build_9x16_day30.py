"""Build `<name>_9x16` for Katy404 Minecraft "day 30" project (1920x1080 @ 60 fps, avatar baked bottom-right).

MCP-GAP: timeline.duplicate / add_track / delete_clips exist in the davinci-resolve MCP but each auto-archives the
timeline (unrequested project change); appending a source range onto a chosen track and exporting verification stills
have no MCP action -> scripting API through scripts/resolve_common (same reason as build_9x16_day29).

Geometry is expressed in 1280x720 "preview" coordinates of the fitted source (the 2560x1440 file shown in a 16:9
timeline); the fit raster is 16:9 so fix_vtuber2d_9x16.place/window_crop apply directly.
Source content has no black letterbox bars (full 1440 height), avatar bbox x ~935..1200, y ~420..720.

Layout: V1 "Game Top" (rows 0..960), V2 "REACTIONS" (empty track, reserved for GIFs/popups), V3 "VTuber Bottom"
(rows 960..1920), V4 "VTuber Full" (full-screen avatar over the merged original VTuber-Focus ranges).
Subtitle 1 has the vertical preset "Mitr-short-001" applied.
Audio, subtitles and the V1 source range are checked identical before and after; the original is never touched.

Usage: python -m scripts.build_9x16_day30 [--apply]      (default: dry run, read-only)
       python -m scripts.build_9x16_day30 verify         (exports stills for visual QC)
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from scripts.drt_set_subtitle_preset import patch_drt
from scripts.fix_vtuber2d_9x16 import CH, CW, S0, SRC_H, SRC_W, apply_props, place, read_props, window_crop
from scripts.load_subtitle_preset import find_user_db, library_roots, read_presets
from scripts.p2_9x16_build import DELAY, RASTER, activate, items, protected, set_float
from scripts.p2_9x16_common import check, find
from scripts.resolve_common import connect_resolve, preserved_state

OUT = Path(__file__).resolve().parents[1] / "exports" / "9x16-day30"
ORIG_NAME = "Timeline 1"
TARGET_NAME = "Timeline 1_9x16"
FPS = 60
GAME_WIN = (300.0, 90.0, 930.0, 650.0)   # 630x560 (1.125 = 1080:960); keeps the avatar's shoulder out of the panel
AV_CENTRE = (1065.0, 540.0)              # avatar window centre
K_STACK = 3.0                            # window 360x320 -> y 380..700: ahoge tip with headroom
K_FULL = 3.6                             # canvas width covers 300 src px; avatar ~265 px wide -> ~88%
SRC_BOTTOM = 720.0                       # no letterbox bar at bottom


def layouts():
    x0, y0, x1, y1 = GAME_WIN
    k_game = 960.0 / (y1 - y0)
    v1 = place(((x0 + x1) / 2, (y0 + y1) / 2), k_game, (540.0, 480.0))
    v1.update(window_crop(x0, y0, x1, y1))
    w, h = CW / K_STACK, 960.0 / K_STACK
    cx, cy = AV_CENTRE
    v3 = place((cx, cy), K_STACK, (540.0, 1440.0))
    v3.update(window_crop(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))
    fy = SRC_BOTTOM - (CH / K_FULL) / 2
    full = place((cx, fy), K_FULL, (540.0, 960.0))
    full.update(window_crop(0, 0, SRC_W, SRC_H))
    return {"V1": v1, "V3": v3, "FULL": full}


def merge(ranges):
    out = []
    for a, b in sorted(ranges):
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return [tuple(x) for x in out]


def apply_subtitle_preset_drt(resolve, project, mp, timeline, preset_name="Mitr-short-001"):
    """Export timeline to DRT, patch Subtitle track style, and re-import."""
    pm = resolve.GetProjectManager()
    db = pm.GetCurrentDatabase() or {}
    root = library_roots()[db["DbName"]]
    user_db = find_user_db(root, "guest")
    presets = read_presets(user_db)
    check(preset_name in presets, f"preset {preset_name!r} not in {user_db}")
    style = presets[preset_name]

    tmp_export = OUT / "tmp_export.drt"
    tmp_patched = OUT / "tmp_patched.drt"
    if tmp_export.exists(): tmp_export.unlink()
    if tmp_patched.exists(): tmp_patched.unlink()

    check(timeline.Export(str(tmp_export.resolve()), resolve.EXPORT_DRT, resolve.EXPORT_NONE), "Export DRT failed")
    time.sleep(1.0)

    report = patch_drt(tmp_export, tmp_patched, style, [1])
    print(f"Patched DRT subtitle preset {preset_name!r}: {report}")
    time.sleep(1.0)

    # Set to orig before deleting and reimporting
    orig_tl = find(project, name=ORIG_NAME)
    project.SetCurrentTimeline(orig_tl)
    time.sleep(1.0)
    check(mp.DeleteTimelines([timeline]), "Delete interim target failed")
    time.sleep(1.0)

    imported = mp.ImportTimelineFromFile(str(tmp_patched.resolve()))
    check(imported is not None, "Import patched DRT failed")
    imported.SetName(TARGET_NAME)
    time.sleep(1.0)
    project.SetCurrentTimeline(imported)
    time.sleep(1.0)
    return imported


def build(apply):
    r = connect_resolve()
    check(r is not None, "Resolve unavailable")
    pm = r.GetProjectManager()
    p = pm.GetCurrentProject()
    check(p is not None, "no project")
    check(not p.IsRenderingInProgress(), "render in progress")
    orig = find(p, name=ORIG_NAME)
    check(orig is not None, f"original not found: {ORIG_NAME}")
    existing_target = find(p, name=TARGET_NAME)
    if existing_target and not apply:
        print(f"Target {TARGET_NAME} already exists (will be replaced with --apply)")
    check(float(orig.GetSetting("timelineFrameRate")) == FPS, "fps mismatch")

    v1 = items(orig, "video", 1)
    v2 = items(orig, "video", 2)
    check(len(v1) == 1 and v2 and all(x.GetName() == "Adjustment Clip" for x in v2), "unexpected V1/V2")
    focus = merge([(x.GetStart(), x.GetEnd()) for x in v2])

    lay = layouts()
    plan = {
        "target": TARGET_NAME,
        "focus_merged": focus,
        "layouts": lay,
        "orig_tracks": [orig.GetTrackName("video", n) for n in range(1, orig.GetTrackCount("video") + 1)],
    }
    print("PLAN", json.dumps(plan, ensure_ascii=False, indent=2))
    if not apply:
        return 0

    OUT.mkdir(parents=True, exist_ok=True)
    mp = p.GetMediaPool()
    if existing_target:
        p.SetCurrentTimeline(orig)
        time.sleep(1.0)
        mp.DeleteTimelines([existing_target])
        time.sleep(1.0)

    log = {"plan": plan}
    with preserved_state(r):
        r.OpenPage("edit")
        time.sleep(2)
        check(r.GetCurrentPage() == "edit", "not on Edit page")
        activate(p, orig)
        base = protected(orig)
        new = orig.DuplicateTimeline(TARGET_NAME)
        check(new is not None and new.GetName() == TARGET_NAME, "DuplicateTimeline failed")
        time.sleep(DELAY)
        activate(p, new)
        check(protected(new) == base, "duplicate protected content differs from original")

        # Apply raster
        for k, v in RASTER:
            new.SetSetting(k, v)
            time.sleep(0.3)
        time.sleep(DELAY)
        for k, v in RASTER:
            check(str(new.GetSetting(k)) == v, f"setting {k}={new.GetSetting(k)} (want {v})")
        check(float(new.GetSetting("timelineFrameRate")) == FPS, "fps changed")

        locks = {n: new.GetIsTrackLocked("video", n) for n in range(1, new.GetTrackCount("video") + 1)}
        for n in locks:
            if locks[n]:
                check(new.SetTrackLock("video", n, False), f"unlock V{n}")

        try:
            # Delete Adjustment Clips from V2
            old_v2 = items(new, "video", 2)
            check(len(old_v2) == len(v2), "duplicate V2 count differs")
            check(new.DeleteClips(old_v2, False), "DeleteClips failed")
            time.sleep(DELAY)
            check(items(new, "video", 2) == [], "V2 not empty after delete")

            # Add Track V3 and V4
            check(new.AddTrack("video"), "AddTrack V3 failed")
            time.sleep(DELAY)
            check(new.AddTrack("video"), "AddTrack V4 failed")
            time.sleep(DELAY)
            check(new.GetTrackCount("video") == 4, f"expected 4 video tracks, got {new.GetTrackCount('video')}")

            a = items(new, "video", 1)[0]
            src0, mpi = a.GetSourceStartFrame(), a.GetMediaPoolItem()

            def append(track, rec0, rec1):
                base0, end0 = src0 + (rec0 - a.GetStart()), src0 + (rec1 - a.GetStart())
                info = {
                    "mediaPoolItem": mpi,
                    "startFrame": base0,
                    "endFrame": end0,
                    "mediaType": 1,
                    "trackIndex": track,
                    "recordFrame": rec0,
                }
                check(mp.AppendToTimeline([info]), f"append V{track} {rec0}-{rec1} failed")
                time.sleep(DELAY)
                got = [x for x in items(new, "video", track) if x.GetStart() == rec0]
                check(len(got) == 1 and abs(got[0].GetEnd() - rec1) <= 3, f"V{track} item {rec0}-{rec1} mismatch")
                return got[0]

            # V1: Game Top
            apply_props(a, lay["V1"])

            # V3: VTuber Bottom
            av = append(3, a.GetStart(), a.GetEnd())
            apply_props(av, lay["V3"])

            # V4: VTuber Full (for each focus range)
            for f0, f1 in focus:
                af = append(4, f0, f1)
                apply_props(af, lay["FULL"])

            # Track names
            for n, nm in ((1, "Game Top"), (2, "REACTIONS"), (3, "VTuber Bottom"), (4, "VTuber Full")):
                new.SetTrackName("video", n, nm)
                time.sleep(0.3)

            # Apply Mitr-short-001 subtitle preset
            new = apply_subtitle_preset_drt(r, p, mp, new, "Mitr-short-001")
            for n, nm in ((1, "Game Top"), (2, "REACTIONS"), (3, "VTuber Bottom"), (4, "VTuber Full")):
                new.SetTrackName("video", n, nm)
                time.sleep(0.2)
            for n, nm in ((1, "Dialogue 1"), (2, "SFX"), (3, "BGM")):
                new.SetTrackName("audio", n, nm)
                time.sleep(0.2)

            check(protected(new) == base, "protected drift after build")
            check(pm.SaveProject(), "SaveProject failed")
            time.sleep(DELAY)

            log["after"] = {
                f"V{n}": [(x.GetName(), x.GetStart(), x.GetEnd(), read_props(x)) for x in items(new, "video", n)]
                for n in (1, 2, 3, 4)
            }
            log["protected_equal"] = protected(new) == base
            check(log["protected_equal"], "protected drift at end")
        finally:
            for n, locked in locks.items():
                if locked:
                    new.SetTrackLock("video", n, True)

    (OUT / "build_day30_9x16.json").write_text(json.dumps(log, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("BUILD_OK", TARGET_NAME, "protected_equal", log["protected_equal"])
    return 0


def verify():
    """Export still frames from the built 9:16 timeline for visual QC."""
    r = connect_resolve()
    check(r is not None, "Resolve unavailable")
    pm = r.GetProjectManager()
    p = pm.GetCurrentProject()
    tl = find(p, name=TARGET_NAME)
    check(tl is not None, f"target not found: {TARGET_NAME}")

    d = OUT / "verify"
    d.mkdir(parents=True, exist_ok=True)
    frames = [100, 600, 1400, 2200, 3800, 5000, 5600]
    results = []

    with preserved_state(r):
        r.OpenPage("edit")
        time.sleep(2)
        activate(p, tl)
        for f in frames:
            still = d / f"still_{f}.png"
            from scripts.fix_vtuber2d_9x16 import tc
            tl.SetCurrentTimecode(tc(f + 1, FPS))
            time.sleep(0.5)
            tl.SetCurrentTimecode(tc(f, FPS))
            time.sleep(1.0)
            ok = p.ExportCurrentFrameAsStill(str(still.resolve()))
            time.sleep(0.5)
            check(ok and still.exists(), f"still export failed at frame {f}")
            results.append({"frame": f, "path": str(still.resolve()), "size": still.stat().st_size})
            print(f"Exported frame {f}: {still.resolve()} ({still.stat().st_size} bytes)")

    print("VERIFY_OK", len(results), "frames")
    return 0


if __name__ == "__main__":
    if "verify" in sys.argv:
        sys.exit(verify())
    else:
        sys.exit(build("--apply" in sys.argv))
