import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

os.environ['RESOLVE_SCRIPT_LIB'] = r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
sys.path.append(r'C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\lib\modules')

import DaVinciResolveScript as dvr

resolve = dvr.scriptapp('Resolve')
proj = resolve.GetProjectManager().GetCurrentProject()
root = proj.GetMediaPool().GetRootFolder()

target_clip = None
for c in root.GetClipList():
    if c.GetName() == "สอนไทกะเล่น LoL ที.mp4":
        target_clip = c
        break

print(f"Target clip: {target_clip.GetName()}")
print(f"Current FPS property: {target_clip.GetClipProperty('FPS')}")

# Try setting FPS
for val in ["60", "60.0", 60, 60.0]:
    res = target_clip.SetClipProperty("FPS", val)
    print(f"SetClipProperty('FPS', {val!r}) -> {res}")
    readback = target_clip.GetClipProperty("FPS")
    print(f"  Readback: {readback}")
    if float(readback) == 60.0:
        print("SUCCESS! FPS is now 60.0!")
        break
