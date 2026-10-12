"""Build `<name>_9x16` from a 16:9 original (Mobile-Legends / Roblox streams with the avatar baked at the bottom right).

MCP-GAP: timeline.duplicate / add_track / delete_clips exist in the davinci-resolve MCP, but each is a registered
destructive action that auto-archives (`<name>_archived_vNN` copies, Media Pool folder moves) -- an unrequested project
change; appending video-only source ranges onto a chosen track and exporting verification stills have no MCP action ->
scripting API through scripts/resolve_common (same reason as p2_9x16_build).

Layout (approved 2026-10-11): V1 "Game Top" (game window -> rows 0..960), V2 "REACTIONS" (empty), V3 "VTuber Bottom"
(avatar window -> rows 960..1920), V4 "VTuber Full" (full-screen avatar over the ORIGINAL VTuber-Focus ranges, merged when
they touch). The duplicate's own Adjustment Clips are deleted (they exist only on the new timeline). Subtitles, audio and
V1 source range are checked identical to the original before and after; the original is never touched.

Source geometry: 1280x720 with the game inside rows 72..648 (phone letterbox) and the avatar at x ~1048..1219. Per-source
avatar vertical position is one of three measured variants (VARIANT_BY_FILE; centre y A=491 B=540 C=555).

Usage: python -m scripts.build_9x16_batch "<original name>" [--apply]      (default: dry run, read-only)
       python -m scripts.build_9x16_batch --verify "<target name>"         (stills + black-row measurement)
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from scripts.fix_vtuber2d_9x16 import CH, CW, S0, SRC_H, SRC_W, apply_props, place, read_props, window_crop
from scripts.p2_9x16_build import DELAY, RASTER, activate, items, protected, tc
from scripts.p2_9x16_common import check, find
from scripts.resolve_common import connect_resolve, preserved_state

OUT = Path(__file__).resolve().parents[1] / "exports" / "9x16-batch2"
FPS = 30
VARIANT_BY_FILE = {
    "_doGDuFZ6V4": "A", "BpAJgs0jxcs": "A", "Dx8EllYHlwA": "A", "Gj6sJz743jo": "B", "gPFWQRDiaN4": "C",
    "JvGMNSNawgg": "B", "jYSutB1hEC4": "B", "K3d3txSjKv0": "A", "MKpTF3pRKzI": "A", "nRHnqYlHTCc": "A",
    "P1TqW5M1pJ8": "B", "PEPGEieTGcU": "C", "rD9Mb90U_lc": "A", "SoHKKvCxSBc": "A", "urEeOHj42G0": "B",
    "xWi5lr-D0QY": "A",
}
AV_CY = {"A": 491.0, "B": 540.0, "C": 555.0}
AV_CX = {"A": 1133.5, "B": 1133.5, "C": 1131.0}   # avatar bbox centre x (measured)
GAME_Y = {"A": (72.0, 648.0), "B": (36.0, 612.0), "C": (36.0, 612.0)}  # A has a phone letterbox; B/C are full height
GAME_X = {"A": (316.0, 964.0), "B": (330.0, 978.0), "C": (250.0, 898.0)}  # 648 px wide -> 1080; B skips the house inset sliver, C the leaderboard
GAME_BOTTOM = 646.0       # PRISM Live logo starts ~y 646: never include it in an avatar window
K_STACK = 3.6
K_FULL = {"A": 5.73, "B": 5.6, "C": 5.6}   # window 188-193 px wide x 335-343 px tall, y ends at GAME_BOTTOM


def layouts(variant):
    cy, cx = AV_CY[variant], AV_CX[variant]
    x0, x1 = GAME_X[variant]
    y0, y1 = GAME_Y[variant]
    k_game = 960.0 / (y1 - y0)
    v1 = place(((x0 + x1) / 2, (y0 + y1) / 2), k_game, (540.0, 480.0))
    v1.update(window_crop(0, y0, SRC_W, y1))
    w, h = CW / K_STACK, 960.0 / K_STACK
    sx = min(cx, SRC_W - w / 2)
    sy = min(cy, GAME_BOTTOM - h / 2)
    v3 = place((sx, sy), K_STACK, (540.0, 1440.0))
    v3.update(window_crop(sx - w / 2, sy - h / 2, sx + w / 2, sy + h / 2))
    k = K_FULL[variant]
    fy = GAME_BOTTOM - (CH / k) / 2
    full = place((cx, fy), k, (540.0, 960.0))
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


def variant_of(item):
    m = item.GetMediaPoolItem()
    base = str(m.GetClipProperty("File Path")).replace("\\", "/").split("/")[-1][:11]
    check(base in VARIANT_BY_FILE, f"source {base!r} has no measured layout variant")
    return VARIANT_BY_FILE[base]


def build(orig_name, apply):
    r = connect_resolve()
    check(r is not None, "Resolve unavailable")
    pm = r.GetProjectManager()
    p = pm.GetCurrentProject()
    check(p is not None and p.GetName() == "sakuyako-2026-09", "wrong project")
    check(not p.IsRenderingInProgress(), "render in progress")
    target_name = orig_name + "_9x16"
    orig = find(p, name=orig_name)
    check(orig is not None, f"original not found: {orig_name}")
    existing = find(p, name=target_name)
    if existing is not None and "--update" not in sys.argv:
        raise RuntimeError(f"target already exists: {target_name}")
    check(float(orig.GetSetting("timelineFrameRate")) == FPS, "fps")
    check(orig.GetTrackCount("video") == 2, f"original has {orig.GetTrackCount('video')} video tracks")
    v1 = items(orig, "video", 1)
    v2 = items(orig, "video", 2)
    check(len(v1) == 1 and all(x.GetName() == "Adjustment Clip" for x in v2), "unexpected original V1/V2 content")
    variant = variant_of(v1[0])
    focus = merge([(x.GetStart(), x.GetEnd()) for x in v2])
    lay = layouts(variant)
    plan = {"target": target_name, "variant": variant, "focus_merged": focus, "orig_focus_n": len(v2), "layouts": lay}
    print("PLAN", json.dumps(plan, ensure_ascii=False))
    if not apply:
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    if existing is not None:
        return update(r, pm, p, existing, orig, lay, plan)
    mp = p.GetMediaPool()
    log = {"plan": plan, "steps": []}
    with preserved_state(r):
        r.OpenPage("edit")
        time.sleep(2)
        check(r.GetCurrentPage() == "edit", "not on Edit page")
        activate(p, orig)
        base = protected(orig)
        new = orig.DuplicateTimeline(target_name)
        check(new is not None and new.GetName() == target_name, "DuplicateTimeline failed")
        time.sleep(DELAY)
        activate(p, new)
        check(protected(new) == base, "duplicate protected content differs from original")
        for k, v in RASTER:
            new.SetSetting(k, v)
            time.sleep(0.3)
        time.sleep(DELAY)
        for k, v in RASTER:
            check(str(new.GetSetting(k)) == v, f"setting {k}={new.GetSetting(k)} (want {v})")
        check(float(new.GetSetting("timelineFrameRate")) == FPS, "fps changed")
        locks = {n: new.GetIsTrackLocked("video", n) for n in (1, 2)}
        for n in (1, 2):
            if locks[n]:
                check(new.SetTrackLock("video", n, False), f"unlock V{n}")
        try:
            # focus adjustment clips of the duplicate are replaced by V4 full-screen segments
            adj = items(new, "video", 2)
            check(len(adj) == len(v2), "duplicate V2 count differs")
            check(new.DeleteClips(adj, False), "DeleteClips adjustment clips failed")
            time.sleep(DELAY)
            check(items(new, "video", 2) == [], "V2 not empty after delete")
            for _ in (3, 4):
                check(new.AddTrack("video"), "AddTrack failed")
                time.sleep(DELAY)
            check(new.GetTrackCount("video") == 4, "expected 4 video tracks")
            a = items(new, "video", 1)[0]
            src0, mpi = a.GetSourceStartFrame(), a.GetMediaPoolItem()

            def sig(x):
                return (x.GetStart(), x.GetEnd(), x.GetSourceStartFrame(), x.GetSourceEndFrame())

            def append(track, rec0, rec1):
                info = {"mediaPoolItem": mpi, "startFrame": src0 + (rec0 - a.GetStart()), "endFrame": src0 + (rec1 - a.GetStart()),
                        "mediaType": 1, "trackIndex": track, "recordFrame": rec0}
                check(mp.AppendToTimeline([info]), f"append V{track} {rec0}-{rec1} failed")
                time.sleep(DELAY)
                got = [x for x in items(new, "video", track) if x.GetStart() == rec0]
                check(len(got) == 1 and got[0].GetEnd() == rec1, f"V{track} item {rec0}-{rec1} mismatch: "
                      f"{[sig(x) for x in items(new, 'video', track)]}")
                return got[0]

            apply_props(a, lay["V1"])
            v3 = append(3, a.GetStart(), a.GetEnd())
            apply_props(v3, lay["V3"])
            for f0, f1 in focus:
                apply_props(append(4, f0, f1), lay["FULL"])
            for n, nm in ((1, "Game Top"), (2, "REACTIONS"), (3, "VTuber Bottom"), (4, "VTuber Full")):
                new.SetTrackName("video", n, nm)
                time.sleep(0.3)
            check(protected(new) == base, "protected drift")
            check(pm.SaveProject(), "SaveProject failed")
            time.sleep(DELAY)
            log["after"] = {f"V{n}": [(x.GetStart(), x.GetEnd(), read_props(x)) for x in items(new, "video", n)] for n in (1, 2, 3, 4)}
            log["protected_equal"] = protected(new) == base
            check(log["protected_equal"], "protected drift at end")
        finally:
            for n in (1, 2):
                if locks.get(n):
                    new.SetTrackLock("video", n, True)
    safe = target_name[:20].replace(" ", "_")
    (OUT / f"build_{safe}.json").write_text(json.dumps(log, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("BUILD_OK", target_name, "protected_equal", log["protected_equal"])
    return 0


def update(r, pm, p, tl, orig, lay, plan):
    """Re-apply the layout values on an already built target (structure unchanged)."""
    with preserved_state(r):
        r.OpenPage("edit")
        time.sleep(2)
        activate(p, tl)
        base = protected(tl)
        check(protected(orig) == base, "target protected content differs from original")
        locks = {n: tl.GetIsTrackLocked("video", n) for n in (1, 2, 3, 4)}
        for n, v in locks.items():
            if v:
                check(tl.SetTrackLock("video", n, False), f"unlock V{n}")
        try:
            check(tl.GetTrackCount("video") == 4, "target is not a 4-track build")
            for key, trk in (("V1", 1), ("V3", 3)):
                xs = items(tl, "video", trk)
                check(len(xs) == 1, f"V{trk} items")
                apply_props(xs[0], lay[key])
            v4 = items(tl, "video", 4)
            check([(x.GetStart(), x.GetEnd()) for x in v4] == [tuple(f) for f in plan["focus_merged"]], "V4 ranges differ from plan")
            for x in v4:
                apply_props(x, lay["FULL"])
            check(protected(tl) == base, "protected drift")
            check(pm.SaveProject(), "SaveProject failed")
            time.sleep(DELAY)
        finally:
            for n, v in locks.items():
                if v:
                    tl.SetTrackLock("video", n, True)
    print("UPDATE_OK", plan["target"])
    return 0


def verify(target_name):
    import numpy as np
    r = connect_resolve()
    p = r.GetProjectManager().GetCurrentProject()
    tl = find(p, name=target_name)
    check(tl is not None, "target not found")
    check((tl.GetSetting("timelineResolutionWidth"), tl.GetSetting("timelineResolutionHeight")) == ("1080", "1920"), "raster")
    full = [(x.GetStart(), x.GetEnd()) for x in items(tl, "video", 4)]
    end = tl.GetEndFrame()
    stacked = next((f for f in (3, 40, 90, 200, 400) if f < end and not any(a <= f < b for a, b in full)), None)
    frames = ([("stacked", stacked)] if stacked is not None else []) + ([("full", (full[0][0] + full[0][1]) // 2)] if full else [])
    d = OUT / "verify"
    d.mkdir(parents=True, exist_ok=True)
    res = []
    with preserved_state(r):
        r.OpenPage("edit")
        time.sleep(2)
        activate(p, tl)
        for kind, f in frames:
            path = d / f"{target_name[:14].replace(' ', '_')}_{kind}_{f}.png"
            tl.SetCurrentTimecode(tc(f + 1, FPS))
            time.sleep(0.5)
            tl.SetCurrentTimecode(tc(f, FPS))
            time.sleep(1.0)
            ok = p.ExportCurrentFrameAsStill(str(path))
            time.sleep(0.5)
            check(ok and path.exists(), f"still export failed {f}")
            from PIL import Image
            a = np.asarray(Image.open(path).convert("L")).astype(float).mean(axis=1)
            runs, s = [], None
            for y in range(len(a)):
                if a[y] < 8:
                    s = y if s is None else s
                elif s is not None:
                    runs.append((s, y - 1))
                    s = None
            if s is not None:
                runs.append((s, len(a) - 1))
            res.append({"kind": kind, "frame": f, "png": str(path), "dark_row_runs": runs})
            print(res[-1], flush=True)
    return res


if __name__ == "__main__":
    if "--verify" in sys.argv:
        verify([a for a in sys.argv[1:] if not a.startswith("--")][0])
    else:
        sys.exit(build([a for a in sys.argv[1:] if not a.startswith("--")][0], "--apply" in sys.argv))
