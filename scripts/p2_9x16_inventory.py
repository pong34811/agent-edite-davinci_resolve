"""Read-only inventory of p2 timelines for the 9:16 batch: fps, raster, track layout, V1 source, focus clips, GIFs.

MCP-GAP: timeline.list returns names/ids only; per-item reads of non-active timelines through the MCP need
timeline.set_current for every timeline (changes the user's active timeline) -> read-only scripting API via
scripts/resolve_common.connect_resolve. Never switches timeline, page or folder.

Usage: python -m scripts.p2_9x16_inventory 2-15 44      -> exports/9x16-batch/inventory.json (overwritten; read-only data)
"""
from __future__ import annotations

import json
import sys

from scripts.p2_9x16_common import ROOT, check, project_and_timeline

OUT = ROOT / "exports" / "9x16-batch"


def parse_indices(args):
    out = []
    for a in args:
        if "-" in a:
            lo, hi = a.split("-")
            out += list(range(int(lo), int(hi) + 1))
        else:
            out.append(int(a))
    return out


def describe(p, idx):
    tl = p.GetTimelineByIndex(idx)
    check(tl is not None, f"no timeline at index {idx}")
    d = {"index": idx, "name": tl.GetName(), "id": tl.GetUniqueId(), "start": tl.GetStartFrame(), "end": tl.GetEndFrame(),
         "fps": tl.GetSetting("timelineFrameRate"), "playback_fps": tl.GetSetting("timelinePlaybackFrameRate"),
         "raster": [tl.GetSetting("timelineResolutionWidth"), tl.GetSetting("timelineResolutionHeight")],
         "tracks": {k: tl.GetTrackCount(k) for k in ("video", "audio", "subtitle")}, "video": []}
    for n in range(1, tl.GetTrackCount("video") + 1):
        its = []
        for x in sorted(tl.GetItemListInTrack("video", n) or [], key=lambda i: i.GetStart()):
            m = x.GetMediaPoolItem()
            e = {"name": x.GetName(), "start": x.GetStart(), "end": x.GetEnd()}
            if m is not None:
                e.update(src=[x.GetSourceStartFrame(), x.GetSourceEndFrame()], path=m.GetClipProperty("File Path"),
                         res=m.GetClipProperty("Resolution"), src_fps=m.GetClipProperty("FPS"),
                         frames=m.GetClipProperty("Frames"))
            try:
                e["fusion_comps"] = x.GetFusionCompCount()
            except Exception:
                pass
            its.append(e)
        d["video"].append({"track": n, "name": tl.GetTrackName("video", n), "items": its})
    return d


def main():
    idx = parse_indices(sys.argv[1:]) or list(range(2, 16)) + [44]
    _, _, p, _ = project_and_timeline()
    res = [describe(p, i) for i in idx]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "inventory.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    for d in res:
        v = d["video"]
        print(d["index"], d["id"][:8], d["fps"], d["raster"], d["tracks"], [t["name"] for t in v],
              "V1:", [(i["name"][:45], i["start"], i["end"], i.get("res"), i.get("src_fps")) for i in v[0]["items"]] if v else None,
              "counts:", [len(t["items"]) for t in v], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
