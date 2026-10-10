"""Trim the last frames of GIF timeline items whose tail Resolve cannot decode at render time.

Why: render jobs for `Anime - Shocked Reaction.gif` failed with "Error decoding full resolution media ... at the last
timeline frame of the item" (Resolve counts 111 frames, the file really has 58; ffmpeg reads it fine).
Fix: delete the item and re-append the same media pool item on the same track/record frame with the source end
reduced by TRIM frames, then copy every item property back and verify.
MCP-GAP: no MCP action trims a timeline item's source range in place (timeline_item has no trim setter); this uses
DeleteClips + AppendToTimeline like the other p2 scripts.
Run from repo root: python -m scripts.p2_trim_bad_gif_tail <timeline index> [...] [--apply] [--trim 3]
A verified .drp backup must exist before --apply.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.resolve_common import connect_resolve, preserved_state  # noqa: E402

BAD = "Anime - Shocked Reaction.gif"
GAP = 1.3


def props(item):
    out = {}
    for k in ("ZoomX", "ZoomY", "ZoomGang", "Pan", "Tilt", "Opacity", "Pitch", "Yaw", "RotationAngle", "AnchorPointX",
              "AnchorPointY", "FlipX", "FlipY", "CropLeft", "CropRight", "CropTop", "CropBottom", "CropSoftness",
              "CropRetain", "Distortion", "CompositeMode"):
        try:
            out[k] = item.GetProperty(k)
        except Exception:
            pass
    return {k: v for k, v in out.items() if v is not None}


def main():
    apply = "--apply" in sys.argv
    trim = int(sys.argv[sys.argv.index("--trim") + 1]) if "--trim" in sys.argv else 3
    idxs = [int(a) for a in sys.argv[1:] if a.isdigit() and sys.argv[sys.argv.index(a) - 1] != "--trim"]
    r = connect_resolve()
    p = r.GetProjectManager().GetCurrentProject()
    mp = p.GetMediaPool()
    with preserved_state(r):
        for idx in idxs:
            tl = p.GetTimelineByIndex(idx)
            p.SetCurrentTimeline(tl)
            time.sleep(GAP)
            assert p.GetCurrentTimeline().GetUniqueId() == tl.GetUniqueId(), "activate failed"
            hit = [(n, x) for n in range(1, tl.GetTrackCount("video") + 1) for x in tl.GetItemListInTrack("video", n) or []
                   if x.GetName() == BAD]
            assert len(hit) == 1, f"{tl.GetName()}: expected one {BAD}, found {len(hit)}"
            n, x = hit[0]
            s, e, ss, se = x.GetStart(), x.GetEnd(), x.GetSourceStartFrame(), x.GetSourceEndFrame()
            before = props(x)
            allv = {k: [(y.GetName(), y.GetStart(), y.GetEnd()) for y in tl.GetItemListInTrack("video", k) or []]
                    for k in range(1, tl.GetTrackCount("video") + 1)}
            print(idx, tl.GetName()[:30], "track", n, "rec", s, e, "src", ss, se, flush=True)
            if not apply:
                continue
            pool = x.GetMediaPoolItem()
            assert tl.DeleteClips([x], False), "DeleteClips failed"
            time.sleep(GAP)
            info = {"mediaPoolItem": pool, "startFrame": ss, "endFrame": se - trim, "mediaType": 1,
                    "trackIndex": n, "recordFrame": s}
            assert mp.AppendToTimeline([info]), "AppendToTimeline failed"
            time.sleep(GAP)
            new = [y for y in tl.GetItemListInTrack("video", n) or [] if y.GetName() == BAD]
            assert len(new) == 1, "re-appended item not found"
            y = new[0]
            for k, v in before.items():
                if y.GetProperty(k) != v:
                    y.SetProperty(k, v)
                    time.sleep(0.2)
            after = props(y)
            bad = {k: (before[k], after.get(k)) for k in before if before[k] != after.get(k)}
            assert not bad, f"properties differ after re-append: {bad}"
            assert y.GetStart() == s and y.GetEnd() < e and e - y.GetEnd() <= int(trim * 1.2) + 2, \
                f"range {y.GetStart()}-{y.GetEnd()} vs {s}-{e}"
            now = {k: [(z.GetName(), z.GetStart(), z.GetEnd()) for z in tl.GetItemListInTrack("video", k) or []]
                   for k in range(1, tl.GetTrackCount("video") + 1)}
            for k in allv:
                if k != n:
                    assert now[k] == allv[k], f"track {k} changed"
            print(idx, "OK new range", y.GetStart(), y.GetEnd(), "src", y.GetSourceStartFrame(), y.GetSourceEndFrame(), flush=True)
        if apply:
            p.GetMediaPool()
            r.GetProjectManager().SaveProject()


if __name__ == "__main__":
    main()
