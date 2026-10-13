"""Delete the `<orig>_9x16` timelines of the given original indexes (exact name + id + 1920 raster checked).
Usage: python scripts/delete_9x16.py --project NAME --ids ids.json IDX..."""
import argparse, json, sys, os, time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import convert_talk_9x16 as T
ap = argparse.ArgumentParser(); ap.add_argument("idx", type=int, nargs="+"); ap.add_argument("--project", required=True); ap.add_argument("--ids", required=True)
a = ap.parse_args()
r = T.dvr.scriptapp("Resolve"); proj = r.GetProjectManager().GetCurrentProject(); assert proj.GetName() == a.project
ids = json.load(open(a.ids)); mp = proj.GetMediaPool(); cur = proj.GetCurrentTimeline()
for i in a.idx:
    o = T.find_tl(proj, uid=ids[str(i)]["orig"]); v = T.find_tl(proj, name=o.GetName() + "_9x16")
    if not v: print(i, "none"); continue
    assert v.GetUniqueId() != o.GetUniqueId() and v.GetSetting("timelineResolutionHeight") == "1920"
    proj.SetCurrentTimeline(o); time.sleep(1.2); print(i, "deleted", mp.DeleteTimelines([v])); time.sleep(1.2)
proj.SetCurrentTimeline(cur)
