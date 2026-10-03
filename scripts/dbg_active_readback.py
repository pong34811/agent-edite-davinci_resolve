"""Does GetProperty readback depend on the timeline being active? Activate target, re-read, restore."""
import os, sys, time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import compare_invariants as ci
import layout9x16 as L
import m2_convert_pilot as m2
import m3_convert as m3

resolve = m2.get_resolve()
proj = resolve.GetProjectManager().GetCurrentProject()
cur = proj.GetCurrentTimeline()
cur_id, cur_tc = cur.GetUniqueId(), cur.GetCurrentTimecode()
idx = int(sys.argv[1])
o = proj.GetTimelineByIndex(idx)
n = m2.find_timeline_by_name(proj, o.GetName() + "_9x16")
v1 = ci.items(n, "video", 1)[0]
print("INACTIVE  V1 Pan/Tilt/CropB:", [m2.get_item_property(v1, k) for k in ("Pan", "Tilt", "CropBottom")])
m3.activate(proj, n)
v1 = ci.items(n, "video", 1)[0]
print("ACTIVE    V1 Pan/Tilt/CropB:", [m2.get_item_property(v1, k) for k in ("Pan", "Tilt", "CropBottom")], "want", [round(L.game_params()[k], 2) for k in ("Pan", "Tilt", "CropBottom")])
print("raster", n.GetSetting("timelineResolutionWidth"), n.GetSetting("timelineResolutionHeight"))
for t in (proj.GetTimelineByIndex(i) for i in range(1, proj.GetTimelineCount() + 1)):
    if t.GetUniqueId() == cur_id:
        m3.activate(proj, t)
        t.SetCurrentTimecode(cur_tc)
        time.sleep(0.5)
        print("restored", t.GetName(), t.GetCurrentTimecode())
