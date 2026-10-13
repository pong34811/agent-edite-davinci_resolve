import sys, json, os, time
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
os.environ.setdefault("RESOLVE_SCRIPT_LIB", r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll")
import DaVinciResolveScript as dvr
r = dvr.scriptapp("Resolve")
pm = r.GetProjectManager(); p = pm.GetCurrentProject()
print("save:", pm.SaveProject())
bk = os.path.join(os.environ.get("EXPORT_DIR", os.path.abspath("exports")), "%s_pre-enrich.drp" % p.GetName())
print("export:", pm.ExportProject(p.GetName(), bk, True), os.path.exists(bk) and os.path.getsize(bk))
W = os.environ["TMPDIR"]
data = []
for i in range(1, p.GetTimelineCount()+1):
    t = p.GetTimelineByIndex(i)
    fps = float(t.GetSetting("timelineFrameRate"))
    cues = [[it.GetStart(), it.GetEnd(), it.GetName()] for it in (t.GetItemListInTrack("subtitle", 1) or [])]
    v1 = [[it.GetStart(), it.GetEnd()] for it in t.GetItemListInTrack("video", 1)]
    a1 = t.GetItemListInTrack("audio", 1)
    vol = [it.GetProperty("AudioVolume") if hasattr(it, "GetProperty") else None for it in a1]
    data.append({"i": i, "name": t.GetName(), "id": t.GetUniqueId(), "fps": fps, "start": t.GetStartFrame(), "end": t.GetEndFrame(),
                 "v1": v1, "a1vol": vol, "cues": cues})
json.dump(data, open(os.path.join(W, "timelines.json"), "w", encoding="utf-8"), ensure_ascii=False)
for d in data:
    print(d["i"], d["start"], d["end"], round((d["end"]-d["start"])/d["fps"],1), "s", len(d["cues"]), "cues", len(d["v1"]), "v1clips", d["a1vol"])
