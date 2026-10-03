"""Read-only: GIF item source/record range semantics, original vs pilot _9x16."""
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import m2_convert_pilot as m2  # noqa: E402


def dump(tl, track, label):
    for it in tl.GetItemListInTrack("video", track) or []:
        mpi = it.GetMediaPoolItem()
        print(label, track, it.GetName()[:24], "rec", it.GetStart(), it.GetEnd(), "dur", it.GetDuration(),
              "srcS", it.GetSourceStartFrame(), "srcE", it.GetSourceEndFrame(),
              "L", it.GetLeftOffset(), "R", it.GetRightOffset(),
              "clipfps", mpi.GetClipProperty("FPS") if mpi else None, "frames", mpi.GetClipProperty("Frames") if mpi else None)


def main():
    proj = m2.get_resolve().GetProjectManager().GetCurrentProject()
    o = m2.find_timeline_by_name(proj, m2.PILOT_NAME)
    n = m2.find_timeline_by_name(proj, m2.TARGET_NAME)
    dump(o, 2, "ORIG")
    dump(n, 4, "PILOT")
    dump(o, 1, "ORIG")
    dump(n, 1, "PILOT")
    dump(n, 2, "PILOT")
    for name in ("ต้องพายเรือ หรือหิ้วเรือขึ้นเขา_Minecraft-vdo", "ลืมเสบียง จนต้องกินเนื้อซอมบี้_Minecraft-vdo"):
        t = m2.find_timeline_by_name(proj, name)
        dump(t, 2, "ORIG:" + name[:6])


if __name__ == "__main__":
    main()
