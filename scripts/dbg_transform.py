import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import compare_invariants as ci
import layout9x16 as L
import m2_convert_pilot as m2

proj = m2.get_resolve().GetProjectManager().GetCurrentProject()
for idx in [int(a) for a in sys.argv[1:]]:
    o = proj.GetTimelineByIndex(idx)
    n = m2.find_timeline_by_name(proj, o.GetName() + "_9x16")
    spec = L.avatar_spec_for(ci.items(o, "video", 1)[0].GetName())
    print(idx, o.GetName()[:20], "spec", spec)
    for label, item, want in (("V1", ci.items(n, "video", 1)[0], L.game_params()), ("V2", ci.items(n, "video", 2)[0], L.avatar_params(*spec))):
        for k, w in want.items():
            print("  ", label, k, "want", round(float(w), 3), "got", m2.get_item_property(item, k))
