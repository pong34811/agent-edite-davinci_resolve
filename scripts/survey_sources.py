"""Read-only survey of the 30 original timelines: V1/V2/V3 structure, source rasters, GIFs, adjustment clips.
Writes scratch/survey_sources.json. No Resolve writes (does not even switch the active timeline)."""
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import m2_convert_pilot as m2  # noqa: E402


def main():
    resolve = m2.get_resolve()
    proj = resolve.GetProjectManager().GetCurrentProject()
    rows = []
    for i in range(1, proj.GetTimelineCount() + 1):
        tl = proj.GetTimelineByIndex(i)
        name = tl.GetName()
        if name.endswith("_9x16"):
            continue
        row = {"index": i, "name": name, "id": tl.GetUniqueId(), "fps": tl.GetSetting("timelineFrameRate"),
               "start": tl.GetStartFrame(), "end": tl.GetEndFrame(), "tracks": {}}
        for n in range(1, tl.GetTrackCount("video") + 1):
            its = []
            for it in tl.GetItemListInTrack("video", n) or []:
                d = {"name": it.GetName(), "s": it.GetStart(), "e": it.GetEnd()}
                mpi = it.GetMediaPoolItem()
                if mpi:
                    d["res"] = mpi.GetClipProperty("Resolution")
                    d["clipfps"] = mpi.GetClipProperty("FPS")
                    d["frames"] = mpi.GetClipProperty("Frames")
                else:
                    d["res"] = None
                for p in ("ZoomX", "Pan", "Tilt", "CropTop", "CropBottom", "CropLeft", "CropRight"):
                    d[p] = m2.get_item_property(it, p)
                its.append(d)
            row["tracks"][n] = its
        rows.append(row)
    json.dump(rows, open("scratch/survey_sources.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print(len(rows), "timelines surveyed")


if __name__ == "__main__":
    main()
