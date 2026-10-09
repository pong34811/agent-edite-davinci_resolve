"""Build the p2 9:16 pilot `<original>_9x16` (structure only; transforms come from p2_9x16_layout).

MCP-GAP: timeline.duplicate / set_setting / add_track / move_clips / delete_clips / insert_generator exist in the
davinci-resolve MCP, but every one is registered in src/utils/destructive_hook.py and triggers version-on-mutate
(timeline_versioning.archive_current_timeline), which adds `<name>_archived_vNN` timeline copies to the project
(for `duplicate`, a copy of the protected original) and moves the Media Pool current folder. That is an unrequested
project change, and the insert needs locks + Edit page + per-step signature checks in one process -> the same
Resolve API calls through scripts/resolve_common (connect_resolve, preserved_state).

Order: duplicate -> raster settings -> AddTrack("video", {"index": 2}) so the duplicate's own Adjustment Clip moves
V2 -> V3 and its GIFs V3 -> V4 untouched -> append the V1 source clip (video only, same ranges) to V2 -> GIF preset
"short" (floats) -> track names -> save -> invariant check. No generator insert (its destination track is the
Edit-page patch panel, not scriptable; a locked destination returned None on this build).

Usage: python -m scripts.p2_9x16_build [--apply]      (default: dry run, read-only)
"""
from __future__ import annotations

import json
import sys
import time

from scripts.p2_9x16_common import (OUT, ORIG_ID, ORIG_NAME, TARGET_NAME, check, find, project_and_timeline)
from scripts.resolve_common import preserved_state

DELAY = 1.25
FOCUS_GEN = "Adjustment Clip"
SHORT = json.loads((OUT.parents[1] / "scripts" / "video_presets.json").read_text(encoding="utf-8"))["short"]["values"]
RASTER = [("useCustomSettings", "1"), ("timelineResolutionWidth", "1080"), ("timelineResolutionHeight", "1920"),
          ("timelineOutputResMatchTimelineRes", "1"), ("timelineOutputResolutionWidth", "1080"),
          ("timelineOutputResolutionHeight", "1920"), ("timelinePixelAspectRatio", "square"),
          ("timelineInputResMismatchBehavior", "scaleToFit"), ("timelineOutputResMismatchBehavior", "scaleToFit")]


# GetProperty() on the ACTIVE timeline adds default-valued keys (DialogueLeveler, VoiceIsolation) that an inactive
# read omits, so compare a fixed key set.
AUDIO_KEYS = ("AudioVolume", "AudioVolumeEnabled", "AudioPan", "AudioPanEnabled", "AudioPitchCents",
              "AudioPitchSemiTones", "AudioPitchEnabled")


def items(tl, kind, n):
    return sorted(tl.GetItemListInTrack(kind, n) or [], key=lambda i: i.GetStart())


def protected(tl):
    """Content that must never change: subtitles, audio (ranges + props), V1, timeline range/fps."""
    sub = [(x.GetName(), x.GetStart(), x.GetEnd()) for i in range(1, tl.GetTrackCount("subtitle") + 1)
           for x in items(tl, "subtitle", i)]
    aud = [(i, x.GetName(), x.GetStart(), x.GetEnd(), x.GetSourceStartFrame(), x.GetSourceEndFrame(),
            json.dumps({k: x.GetProperty(k) for k in AUDIO_KEYS}, sort_keys=True, default=str))
           for i in range(1, tl.GetTrackCount("audio") + 1) for x in items(tl, "audio", i)]
    v1 = [(x.GetName(), x.GetStart(), x.GetEnd(), x.GetSourceStartFrame(), x.GetSourceEndFrame()) for x in items(tl, "video", 1)]
    return {"sub": sub, "audio": aud, "v1": v1, "range": (tl.GetStartFrame(), tl.GetEndFrame()),
            "fps": tl.GetSetting("timelineFrameRate"), "tracks_a_s": (tl.GetTrackCount("audio"), tl.GetTrackCount("subtitle"))}


def activate(p, tl):
    p.SetCurrentTimeline(tl)
    time.sleep(DELAY)
    check(p.GetCurrentTimeline().GetUniqueId() == tl.GetUniqueId(), "activate failed")


def tc(frame, fps=60):
    s, f = divmod(int(frame), fps)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{h:02d}:{m:02d}:{s:02d}:{f:02d}"


def set_float(item, key, value, tol=0.01):
    for _ in range(3):
        item.SetProperty(key, float(value))
        time.sleep(0.3)
        rb = item.GetProperty(key)
        if rb is not None and abs(float(rb) - float(value)) <= tol:
            return float(rb)
        time.sleep(0.9)
    raise RuntimeError(f"{key} did not stick: want {value}, got {rb}")


def main():
    apply = "--apply" in sys.argv
    r, pm, p, orig = project_and_timeline()
    check(orig is not None, "original not found by id+name")
    check(find(p, None, TARGET_NAME) is None, f"target already exists: {TARGET_NAME}")
    check(not p.IsRenderingInProgress(), "render in progress")
    mp = p.GetMediaPool()
    base = protected(orig)
    v1 = items(orig, "video", 1)
    check(len(v1) == 1 and orig.GetTrackName("video", 2) == "VTUBER_FOCUS" and orig.GetTrackName("video", 3) == "ENRICH_GIF",
          "unexpected original track layout")
    focus = [(x.GetStart(), x.GetEnd()) for x in items(orig, "video", 2)]
    check(all(x.GetName() == FOCUS_GEN for x in items(orig, "video", 2)), "V2 is not only Adjustment Clips")
    gifs = []
    for x in items(orig, "video", 3):
        m = x.GetMediaPoolItem()
        gifs.append(dict(mpi=m, name=x.GetName(), rec=x.GetStart(), end=x.GetEnd(), ss=x.GetSourceStartFrame(),
                         se=x.GetSourceEndFrame(), frames=int(float(m.GetClipProperty("Frames")))))
    plan = {"focus": focus, "gifs": [(g["name"], g["rec"], g["end"], g["ss"], g["se"], g["frames"]) for g in gifs],
            "v1": base["v1"], "short": SHORT}
    print("PLAN", json.dumps(plan, ensure_ascii=False))
    if not apply:
        return 0

    log = {"plan": plan, "steps": []}
    with preserved_state(r):
        r.OpenPage("edit")
        time.sleep(2)
        check(r.GetCurrentPage() == "edit", "not on Edit page")
        def sig(n):
            return [(x.GetName(), x.GetStart(), x.GetEnd()) for x in items(new, "video", n)]
        activate(p, orig)
        new = orig.DuplicateTimeline(TARGET_NAME)
        check(new is not None and new.GetName() == TARGET_NAME, "DuplicateTimeline failed")
        time.sleep(DELAY)
        nid = new.GetUniqueId()
        log["new_id"] = nid
        activate(p, new)
        check(protected(new) == base, "duplicate protected content differs from original")
        o = lambda n: [(x.GetName(), x.GetStart(), x.GetEnd()) for x in items(orig, "video", n)]
        orig_v = [o(1), o(2), o(3)]
        check([sig(1), sig(2), sig(3)] == orig_v, "duplicate video tracks differ")

        for k, v in RASTER:
            new.SetSetting(k, v)
            time.sleep(0.3)
        time.sleep(DELAY)
        log["settings"] = {k: new.GetSetting(k) for k, _ in RASTER}
        for k, v in RASTER:
            check(str(log["settings"][k]) == v, f"setting {k} = {log['settings'][k]} (want {v})")
        check(float(new.GetSetting("timelineFrameRate")) == 60.0, "fps changed")
        print("SETTINGS", log["settings"], flush=True)

        # Empty track inserted at index 2: the duplicate's own Adjustment Clip (V2 -> V3) and GIFs (V3 -> V4) shift up
        # with their exact ranges and Fusion comp. (InsertGeneratorIntoTimeline goes to the patch-panel destination
        # track, which the API cannot set; it returned None here.)
        check(new.AddTrack("video", {"index": 2}), "AddTrack index 2 failed")
        time.sleep(DELAY)
        check(new.GetTrackCount("video") == 4 and sig(1) == orig_v[0] and sig(2) == [] and sig(3) == orig_v[1]
              and sig(4) == orig_v[2], "track shift did not produce V1 game / V2 empty / V3 focus / V4 GIFs")
        check(protected(new) == base, "protected drift after AddTrack")

        # V2 = same source clip, same ranges, video only (VTuber panel)
        a = v1[0]
        info = {"mediaPoolItem": a.GetMediaPoolItem(), "startFrame": a.GetSourceStartFrame(),
                "endFrame": a.GetSourceEndFrame(), "mediaType": 1, "trackIndex": 2, "recordFrame": a.GetStart()}
        check(mp.AppendToTimeline([info]), "append V2 panel failed")
        time.sleep(DELAY)
        nv2 = items(new, "video", 2)
        check(len(nv2) == 1 and (nv2[0].GetStart(), nv2[0].GetEnd(), nv2[0].GetSourceStartFrame(), nv2[0].GetSourceEndFrame())
              == (a.GetStart(), a.GetEnd(), a.GetSourceStartFrame(), a.GetSourceEndFrame()), "V2 panel range mismatch")
        check(sig(3) == orig_v[1] and sig(4) == orig_v[2], "V3/V4 drift after V2 append")
        check(protected(new) == base, "protected drift after V2 append")
        v4 = items(new, "video", 4)
        got = [(x.GetName(), x.GetStart(), x.GetEnd(), x.GetSourceStartFrame(), x.GetSourceEndFrame()) for x in v4]
        want = [(g["name"], g["rec"], g["end"], g["ss"], g["se"]) for g in gifs]
        check(got == want, f"GIF ranges mismatch got={got} want={want}")
        for x in v4:
            for k in ("ZoomX", "ZoomY", "Tilt"):
                set_float(x, k, SHORT[k], 0.5 if k == "Tilt" else 0.005)
        log["gifs"] = [{k: x.GetProperty(k) for k in ("ZoomX", "ZoomY", "Pan", "Tilt", "ZoomGang")} for x in v4]
        print("GIFS", log["gifs"], flush=True)

        for n, nm in ((1, "Game Top"), (2, "VTuber Bottom"), (3, "VTUBER_FOCUS"), (4, "ENRICH_GIF")):
            new.SetTrackName("video", n, nm)
            time.sleep(0.3)
        check(protected(new) == base, "protected drift at end of build")
        check(pm.SaveProject(), "SaveProject failed")
        time.sleep(DELAY)
        log["saved"] = True
        log["protected_equal"] = protected(new) == base
        log["tracks"] = {k: new.GetTrackCount(k) for k in ("video", "audio", "subtitle")}
    (OUT / "build_log.json").write_text(json.dumps(log, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("BUILD_OK", log["new_id"], log["tracks"], "protected_equal", log["protected_equal"], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
