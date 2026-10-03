"""Read-only: compare GIF items (V2 on original vs V4 on _9x16) for one timeline index."""
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import m2_convert_pilot as m2  # noqa: E402


def main():
    idx = int(sys.argv[1])
    proj = m2.get_resolve().GetProjectManager().GetCurrentProject()
    o = proj.GetTimelineByIndex(idx)
    n = m2.find_timeline_by_name(proj, o.GetName() + "_9x16")
    for label, tl, tr in (("ORIG V2", o, 2), ("NEW V4", n, 4)):
        for it in sorted(tl.GetItemListInTrack("video", tr) or [], key=lambda i: i.GetStart()):
            mpi = it.GetMediaPoolItem()
            print(label, it.GetName()[:26], "rec", it.GetStart(), it.GetEnd(), "src", it.GetSourceStartFrame(), it.GetSourceEndFrame(),
                  "L", it.GetLeftOffset(), "R", it.GetRightOffset(), "clip", mpi.GetClipProperty("FPS"), mpi.GetClipProperty("Frames"))


if __name__ == "__main__":
    main()
