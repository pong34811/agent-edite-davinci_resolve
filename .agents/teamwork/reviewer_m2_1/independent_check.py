import os
import sys
import json

sys.stdout.reconfigure(encoding="utf-8")
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
sys.path.append(r"C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\lib\modules")
import DaVinciResolveScript as dvr_script

resolve = dvr_script.scriptapp("Resolve")
if not resolve:
    print("Failed to connect to Resolve")
    sys.exit(1)

pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
count = proj.GetTimelineCount()
target_tl = None
for i in range(1, count + 1):
    tl = proj.GetTimelineByIndex(i)
    if tl.GetName() == "หนีฝ่าความหนาว_Minecraft-vdo_9x16":
        target_tl = tl
        break

if not target_tl:
    print("Target timeline not found")
    sys.exit(1)

print("Target timeline found:", target_tl.GetName())
print("Resolution:", target_tl.GetSetting("timelineResolutionWidth"), "x", target_tl.GetSetting("timelineResolutionHeight"))
print("useCustomSettings:", target_tl.GetSetting("useCustomSettings"))
print("FPS:", target_tl.GetSetting("timelineFrameRate"))
print("Duration:", target_tl.GetEndFrame() - target_tl.GetStartFrame())

v_count = target_tl.GetTrackCount("video")
print("Video track count:", v_count)
for v in range(1, v_count + 1):
    items = target_tl.GetItemListInTrack("video", v) or []
    print(f"V{v} items count: {len(items)}")
    for it in items:
        zx = it.GetProperty("ZoomX")
        zy = it.GetProperty("ZoomY")
        pan = it.GetProperty("Pan")
        tilt = it.GetProperty("Tilt")
        cb = it.GetProperty("CropBottom")
        ct = it.GetProperty("CropTop")
        print(f"  - {it.GetName()} ({it.GetStart()}..{it.GetEnd()}): Zoom=({zx}, {zy}), Pan={pan}, Tilt={tilt}, CropB={cb}, CropT={ct}")
        if v == 3:
            comp = it.GetFusionCompByIndex(1)
            if comp:
                tools = comp.GetToolList()
                for t in tools.values():
                    tname = t.GetAttrs().get("TOOLS_Name")
                    if "Transform" in tname:
                        print(f"    Fusion {tname}: Center={t.GetInput('Center')}, Size={t.GetInput('Size')}")

a_count = target_tl.GetTrackCount("audio")
print("Audio track count:", a_count)
for a in range(1, a_count + 1):
    items = target_tl.GetItemListInTrack("audio", a) or []
    print(f"A{a} items count: {len(items)}")
    for it in items:
        print(f"  - {it.GetName()} ({it.GetStart()}..{it.GetEnd()}) Vol={it.GetProperty('AudioVolume')}")

subs = target_tl.GetItemListInTrack("subtitle", 1) or []
print("Subtitle cue count:", len(subs))
print("First 3 cues:")
for it in subs[:3]:
    print(f"  - {it.GetName()} ({it.GetStart()}..{it.GetEnd()})")
