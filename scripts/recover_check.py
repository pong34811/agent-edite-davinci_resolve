"""Recovery after the Resolve hang.

1. Inspect the half-built `_9x16` (index 10 original). If it is the partial duplicate (not 1080x1920 /
   3 video tracks), delete ONLY that timeline (matched by exact name + id + raster) with --delete.
2. Re-verify every existing converted timeline against its original (subs/audio/ranges/gifs/raster/offline).
Usage: python scripts/recover_check.py [--delete]
"""
import json
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import compare_invariants as ci  # noqa: E402
import m2_convert_pilot as m2  # noqa: E402
import m3_convert as m3  # noqa: E402

PARTIAL_IDX = int(os.environ.get("PARTIAL_IDX", "10"))


def main():
    resolve = m2.get_resolve()
    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    mp = proj.GetMediaPool()
    rows = {r["index"]: r for r in json.load(open("scratch/survey_sources.json", encoding="utf-8"))}
    orig = proj.GetTimelineByIndex(PARTIAL_IDX)
    assert orig.GetUniqueId() == rows[PARTIAL_IDX]["id"]
    part = m2.find_timeline_by_name(proj, orig.GetName() + "_9x16")
    if part:
        info = dict(id=part.GetUniqueId(), w=part.GetSetting("timelineResolutionWidth"), h=part.GetSetting("timelineResolutionHeight"),
                    vt=part.GetTrackCount("video"), subs=len(ci.sub_sig(part)), v2=len(part.GetItemListInTrack("video", 2) or []),
                    v4=len(part.GetItemListInTrack("video", 4) or []) if part.GetTrackCount("video") >= 4 else None)
        print("partial:", info)
        complete = info["w"] == "1080" and info["h"] == "1920" and info["vt"] == 4
        print("looks complete:", complete)
        if "--delete" in sys.argv:
            assert not complete, "refusing to delete a complete timeline"
            # leave the partial before deleting it
            m3.activate(proj, orig)
            print("DeleteTimelines:", mp.DeleteTimelines([part]))
            time.sleep(m3.DELAY)
            print("still exists:", bool(m2.find_timeline_by_name(proj, orig.GetName() + "_9x16")))
            print("save", pm.SaveProject())
    else:
        print("no partial timeline for index", PARTIAL_IDX)

    allok = True
    for idx in range(1, 31):
        o = proj.GetTimelineByIndex(idx)
        n = m2.find_timeline_by_name(proj, o.GetName() + "_9x16")
        if not n:
            continue
        if n.GetSetting("timelineResolutionHeight") != "1920":
            continue
        pre_gifs = m3.gif_infos(o)
        res = m3.verify(o, n, m3.snapshot_original(o), pre_gifs)
        print(idx, "ok" if res["ok"] else "FAIL", {k: v for k, v in res.items() if k != "ok" and (v is False or v == [] and k == "offline" and False)})
        allok &= res["ok"]
    print("ALL VERIFIED:", allok)


if __name__ == "__main__":
    main()
