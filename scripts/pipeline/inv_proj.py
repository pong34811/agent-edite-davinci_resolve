import sys, json, os, time
sys.path.insert(0, os.environ["TMPDIR"])
from rlib import *
PROJ = sys.argv[1]
out = os.path.join(W, "proj", PROJ); os.makedirs(out, exist_ok=True)
st0 = os.path.join(W, "session_start.json")
if not os.path.exists(st0):
    cur = p.GetCurrentTimeline(); json.dump({"project": p.GetName(), "timeline_id": cur.GetUniqueId(), "tc": cur.GetCurrentTimecode(), "page": r.GetCurrentPage()}, open(st0, "w"))
print("save current", pm.SaveProject()); time.sleep(1.2)
if p.GetName() != PROJ:
    ok = pm.LoadProject(PROJ)
    if not ok:
        print("folder", pm.OpenFolder(os.environ.get("PROJECT_FOLDER", ""))); time.sleep(1.5); ok = pm.LoadProject(PROJ)
    print("load", bool(ok)); time.sleep(6)
    p2 = pm.GetCurrentProject(); print("now", p2.GetName())
    assert p2.GetName() == PROJ
else: p2 = p
time.sleep(1.0)
bk = os.path.join(os.environ.get("EXPORT_DIR", os.path.abspath("exports")), "%s_pre-update.drp" % PROJ)
print("export", pm.ExportProject(PROJ, bk, True), os.path.exists(bk) and os.path.getsize(bk))
inv = []
for i in range(1, p2.GetTimelineCount() + 1):
    t = p2.GetTimelineByIndex(i); p2.SetCurrentTimeline(t); time.sleep(1.0)
    row = dict(i=i, name=t.GetName(), id=t.GetUniqueId(), w=t.GetSetting("timelineResolutionWidth"), h=t.GetSetting("timelineResolutionHeight"), fps=t.GetSetting("timelineFrameRate"), start=t.GetStartFrame(), end=t.GetEndFrame(), tracks={})
    for typ in ("video", "audio", "subtitle"):
        row["tracks"][typ] = []
        for k in range(1, t.GetTrackCount(typ) + 1):
            its = t.GetItemListInTrack(typ, k) or []
            row["tracks"][typ].append(dict(n=t.GetTrackName(typ, k), items=len(its), first=[x.GetName()[:30] for x in its[:2]]))
    v1 = t.GetItemListInTrack("video", 1) or []
    row["v1"] = [dict(name=x.GetName(), s=x.GetStart(), e=x.GetEnd(), src=(x.GetMediaPoolItem().GetClipProperty("File Path") if x.GetMediaPoolItem() else None), res=(x.GetMediaPoolItem().GetClipProperty("Resolution") if x.GetMediaPoolItem() else None)) for x in v1]
    row["cues"] = [[x.GetStart(), x.GetEnd(), x.GetName()] for x in (t.GetItemListInTrack("subtitle", 1) or [])]
    inv.append(row)
json.dump(inv, open(os.path.join(out, "inventory.json"), "w", encoding="utf-8"), ensure_ascii=False)
for r_ in inv:
    print(r_["i"], r_["name"][:36], r_["w"], "x", r_["h"], r_["fps"], r_["end"] - r_["start"], "V", [x["items"] for x in r_["tracks"]["video"]], "A", [x["items"] for x in r_["tracks"]["audio"]], "ST", [x["items"] for x in r_["tracks"]["subtitle"]], "| src:", (r_["v1"][0]["src"] or "")[-34:] if r_["v1"] else None, "n_v1", len(r_["v1"]))
