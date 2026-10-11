"""Make a `<name>_150s` variant of a timeline trimmed to 150 s (cut at start+9000 @ 60 fps), originals untouched.

MCP-GAP: no MCP action trims a timeline item's source range or razors (timeline_item has no trim setter,
edit_engine lift_range blocks partial overlaps) -> DuplicateTimeline + DeleteClips + AppendToTimeline with a
reduced endFrame, the same pattern as p2_trim_bad_gif_tail.py. Items fully past the cut are deleted;
subtitle cues starting at/after the cut (or straddling it) are deleted, none are re-timed.
Run from repo root: python -m scripts.p2_trim_tail_150s <timeline index> [...] [--apply] [--seconds 150]
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.backup_drp import export_verified  # noqa: E402
from scripts.resolve_common import connect_resolve, preserved_state  # noqa: E402

GAP = 1.3
VPROPS = ("ZoomX", "ZoomY", "ZoomGang", "Pan", "Tilt", "Opacity", "Pitch", "Yaw", "RotationAngle", "AnchorPointX",
          "AnchorPointY", "FlipX", "FlipY", "CropLeft", "CropRight", "CropTop", "CropBottom", "CropSoftness",
          "CropRetain", "Distortion", "CompositeMode")
APROPS = ("Volume", "Pan")


def props(item, keys):
    out = {}
    for k in keys:
        try:
            v = item.GetProperty(k)
        except Exception:
            v = None
        if v is not None:
            out[k] = v
    return out


def restore(item, before, keys):
    for k, v in before.items():
        if item.GetProperty(k) != v:
            item.SetProperty(k, v)
            time.sleep(0.2)
    after = props(item, keys)
    bad = {k: (before[k], after.get(k)) for k in before if before[k] != after.get(k)}
    assert not bad, f"properties differ after re-append: {bad}"


def find(tl, kind, n, start):
    return [x for x in tl.GetItemListInTrack(kind, n) or [] if x.GetStart() == start]


def trim_timeline(r, p, mp, src, cut_len, apply):
    t0 = src.GetStartFrame()
    cut = t0 + cut_len
    print(f"== {src.GetName()} cut@{cut}", flush=True)
    if not apply:
        return
    dup = src.DuplicateTimeline(src.GetName() + "_150s")
    assert dup, "DuplicateTimeline failed"
    try:
        _trim_dup(p, mp, dup, cut, cut_len)
    except Exception:
        p.SetCurrentTimeline(src)
        time.sleep(GAP)
        mp.DeleteTimelines([dup])
        print("  FAILED -> removed partial variant", flush=True)
        raise


def _trim_dup(p, mp, dup, cut, cut_len):
    time.sleep(GAP)
    p.SetCurrentTimeline(dup)
    time.sleep(GAP)
    assert p.GetCurrentTimeline().GetUniqueId() == dup.GetUniqueId(), "activate failed"
    # 1) whole items past the cut, and subtitle cues touching it
    for kind in ("video", "audio", "subtitle"):
        for n in range(1, dup.GetTrackCount(kind) + 1):
            drop = [x for x in dup.GetItemListInTrack(kind, n) or []
                    if x.GetStart() >= cut or (kind == "subtitle" and x.GetEnd() > cut)]
            if drop:
                assert dup.DeleteClips(drop, False), f"DeleteClips failed {kind}{n}"
                print("  deleted", kind, n, len(drop), flush=True)
                time.sleep(GAP)
    # 2) straddlers: video first (main V1+A1 pair re-appended together so they stay linked)
    jobs = []
    for kind in ("video", "audio"):
        for n in range(1, dup.GetTrackCount(kind) + 1):
            for x in dup.GetItemListInTrack(kind, n) or []:
                if x.GetEnd() > cut:
                    mpi = x.GetMediaPoolItem()
                    assert mpi, f"{x.GetName()} has no media pool item"
                    jobs.append(dict(kind=kind, n=n, s=x.GetStart(), e=x.GetEnd(), ss=x.GetSourceStartFrame(),
                                     se=x.GetSourceEndFrame(), mpi=mpi, name=x.GetName(),
                                     before=props(x, VPROPS if kind == "video" else APROPS)))
    for j in jobs:
        x = find(dup, j["kind"], j["n"], j["s"])[0]
        assert dup.DeleteClips([x], False), "DeleteClips failed (straddler)"
        time.sleep(GAP)
    for j in jobs:
        info = {"mediaPoolItem": j["mpi"], "startFrame": j["ss"], "endFrame": j["se"] - round((j["e"] - cut) * (j["se"] - j["ss"]) / (j["e"] - j["s"])),
                "mediaType": 1 if j["kind"] == "video" else 2, "trackIndex": j["n"], "recordFrame": j["s"]}
        assert mp.AppendToTimeline([info]), f"AppendToTimeline failed {j['name']}"
        time.sleep(GAP)
        new = find(dup, j["kind"], j["n"], j["s"])
        assert len(new) == 1, f"re-appended item not found {j['name']}"
        assert new[0].GetEnd() == cut, f"{j['name']} end {new[0].GetEnd()} != {cut}"
        restore(new[0], j["before"], VPROPS if j["kind"] == "video" else APROPS)
        print("  trimmed", j["kind"], j["n"], j["name"][:30], flush=True)
    dur = (dup.GetEndFrame() - dup.GetStartFrame()) / float(dup.GetSetting("timelineFrameRate"))
    print(f"  RESULT {dup.GetName()} duration {dur:.2f}s", flush=True)
    assert abs(dur - cut_len / 60.0) < 0.05, "duration mismatch"


def main():
    apply = "--apply" in sys.argv
    secs = int(sys.argv[sys.argv.index("--seconds") + 1]) if "--seconds" in sys.argv else 150
    idxs = [int(a) for i, a in enumerate(sys.argv[1:], 1) if a.isdigit() and sys.argv[i - 1] != "--seconds"]
    r = connect_resolve()
    p = r.GetProjectManager().GetCurrentProject()
    mp = p.GetMediaPool()
    if apply:
        out = ROOT / "backups" / "2026-10-10-before-trim-150s.drp"
        if not out.exists():
            print("backup bytes:", export_verified(r.GetProjectManager(), p, out), flush=True)
    with preserved_state(r):
        for i in idxs:
            trim_timeline(r, p, mp, p.GetTimelineByIndex(i), secs * 60, apply)
    if apply:
        assert r.GetProjectManager().SaveProject(), "SaveProject failed"


if __name__ == "__main__":
    main()
