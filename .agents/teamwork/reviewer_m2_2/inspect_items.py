import sys, os
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

os.environ['RESOLVE_SCRIPT_LIB'] = r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
sys.path.append(r'C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\lib\modules')
import DaVinciResolveScript as dvr

r = dvr.scriptapp('Resolve')
p = r.GetProjectManager().GetCurrentProject()

target_tl = None
for i in range(1, p.GetTimelineCount()+1):
    tl = p.GetTimelineByIndex(i)
    if tl.GetName() == 'หนีฝ่าความหนาว_Minecraft-vdo_9x16':
        target_tl = tl
        break

if target_tl:
    print("=== Target Timeline Video Tracks & Clip Properties ===")
    for v in range(1, target_tl.GetTrackCount("video") + 1):
        items = target_tl.GetItemListInTrack("video", v) or []
        print(f"\n--- Track V{v} ({len(items)} items) ---")
        for idx, it in enumerate(items):
            print(f"Item {idx}: Name='{it.GetName()}', Start={it.GetStart()}, End={it.GetEnd()}, Dur={it.GetDuration()}")
            props = [
                "ZoomX", "ZoomY", "Pan", "Tilt",
                "CropLeft", "CropRight", "CropTop", "CropBottom",
                "CropSoftness", "CropRetain"
            ]
            prop_vals = {}
            for pr in props:
                val = it.GetProperty(pr)
                if val is not None and val is not False:
                    prop_vals[pr] = val
            print(f"  Transforms: {prop_vals}")
