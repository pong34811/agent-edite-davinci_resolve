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

fps_map = {}
for c in root.GetClipList():
    props = c.GetClipProperty()
    fps = props.get("FPS")
    name = c.GetName()
    # only files
    if name.endswith(".mp4"):
        print(f"{name:50s} : FPS={fps}")
        fps_map[name] = fps

non_60 = {k: v for k, v in fps_map.items() if v != 60.0 and v != 60 and v != "60" and v != "60.0"}
print("\nNon-60.0 FPS clips:")
for k, v in non_60.items():
    print(f"  {k}: {v}")
