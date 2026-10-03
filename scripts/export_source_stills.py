"""Export one clean (no GIF / no adjustment clip) 16:9 still per distinct source video, from original timelines.
Only changes the active timeline + playhead (restored at exit). Output: scratch/src_stills/src_<idx>.png"""
import json
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import m2_convert_pilot as m2  # noqa: E402

IDX = [1, 11, 13, 19, 25, 26, 27]


def main():
    rows = {r["index"]: r for r in json.load(open("scratch/survey_sources.json", encoding="utf-8"))}
    resolve = m2.get_resolve()
    proj = resolve.GetProjectManager().GetCurrentProject()
    cur = proj.GetCurrentTimeline()
    cur_id, cur_tc, page = cur.GetUniqueId(), cur.GetCurrentTimecode(), resolve.GetCurrentPage()
    os.makedirs("scratch/src_stills", exist_ok=True)
    try:
        for i in IDX:
            r = rows[i]
            busy = [(it["s"], it["e"]) for n in ("2", "3") for it in r["tracks"].get(n, [])]
            f = next(f for f in range(r["start"] + 300, r["end"], 120) if not any(s - 30 <= f <= e + 30 for s, e in busy))
            tl = proj.GetTimelineByIndex(i)
            assert tl.GetUniqueId() == r["id"]
            proj.SetCurrentTimeline(tl)
            time.sleep(1.2)
            assert proj.GetCurrentTimeline().GetUniqueId() == r["id"]
            tl.SetCurrentTimecode(m2.frame_to_timecode(f, r["fps"]))
            time.sleep(0.6)
            p = os.path.abspath(f"scratch/src_stills/src_{i}.png")
            print(i, f, proj.ExportCurrentFrameAsStill(p), os.path.exists(p))
            time.sleep(0.3)
    finally:
        for k in range(1, proj.GetTimelineCount() + 1):
            t = proj.GetTimelineByIndex(k)
            if t.GetUniqueId() == cur_id:
                proj.SetCurrentTimeline(t)
                time.sleep(1.2)
                t.SetCurrentTimecode(cur_tc)
                time.sleep(0.5)
                print("restored", t.GetName(), t.GetCurrentTimecode(), "page", resolve.GetCurrentPage(), "was", page)


if __name__ == "__main__":
    main()
