import sys, json, os, time
sys.path.insert(0, os.environ["TMPDIR"])
from rlib import *
exec(open(os.environ["TMPDIR"] + r"\rlib_apply.py", encoding="utf-8").read())
N = int(sys.argv[1]); which = sys.argv[2]   # which: copy | orig
st = json.load(open(W + r"\state.json")) if os.path.exists(W + r"\state.json") else {}
pl = json.load(open(f"{W}\\final_T{N}.json", encoding="utf-8"))
tid = json.load(open(W + r"\ids.json"))[str(N)][which]
t = tl_by_id(tid); print("target", t.GetName(), tid)
activate(t)
def protected(t):
    d = {"V1": [(it.GetStart(), it.GetEnd(), it.GetSourceStartFrame(), it.GetSourceEndFrame()) for it in t.GetItemListInTrack("video", 1)],
         "A1": [(it.GetStart(), it.GetEnd(), it.GetSourceStartFrame(), it.GetSourceEndFrame(), it.GetProperty("AudioVolume")) for it in t.GetItemListInTrack("audio", 1)],
         "ST": [(it.GetStart(), it.GetEnd(), it.GetName()) for it in (t.GetItemListInTrack("subtitle", 1) or [])]}
    return d
before = protected(t)
apply_plan(t, pl)
time.sleep(D); place_and_mix(t, pl)
time.sleep(D); print("save", pm.SaveProject())
after = protected(t)
print("PROTECTED UNCHANGED:", before == after)
a = audit(t)
json.dump(a, open(f"{W}\\audit_T{N}_{which}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in a.items():
    if k in ("ST1", "names"): print(k, v); continue
    print(k, len(v)); [print("   ", row) for row in v]
