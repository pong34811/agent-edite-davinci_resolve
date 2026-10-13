import sys, json, os, time
sys.path.insert(0, os.environ["TMPDIR"])
from rlib import *
PROJ = sys.argv[1]
assert p.GetName() == PROJ, p.GetName()
inv = json.load(open(os.path.join(W, "proj", p.GetName(), "inventory.json"), encoding="utf-8")); out = []
for d in inv:
    t = tl_by_id(d["id"]); it = t.GetItemListInTrack("video", 1)[0]; m = it.GetMediaPoolItem()
    out.append(dict(i=d["i"], name=d["name"], id=d["id"], src=m.GetClipProperty("File Path"), src_fps=float(m.GetClipProperty("FPS")), ss=it.GetSourceStartFrame(), se=it.GetSourceEndFrame(), s=it.GetStart(), e=it.GetEnd(), lo=it.GetLeftOffset(), speed=it.GetProperty("Speed") if "Speed" in dir(it) else None, subtracks=t.GetTrackCount("subtitle")))
json.dump(out, open(os.path.join(W, "offs.json"), "w", encoding="utf-8"), ensure_ascii=False)
for o in out: print(o["i"], o["src"][-30:], o["src_fps"], o["ss"], o["se"], o["s"], o["e"], o["lo"], o["speed"], o["subtracks"])
