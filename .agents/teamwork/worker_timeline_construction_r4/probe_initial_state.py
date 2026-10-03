import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

os.environ['RESOLVE_SCRIPT_LIB'] = r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
sys.path.append(r'C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\lib\modules')

import DaVinciResolveScript as dvr

resolve = dvr.scriptapp('Resolve')
if not resolve:
    print("[ERROR] Cannot connect to DaVinci Resolve")
    sys.exit(1)

pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
if not proj:
    print("[ERROR] No current project open")
    sys.exit(1)

print(f"Project Name: {proj.GetName()}")
print(f"Project ID: {proj.GetUniqueId()}")
fps = proj.GetSetting('timelineFrameRate')
print(f"Timeline Frame Rate: {fps}")
tl_count = proj.GetTimelineCount()
print(f"Current Timeline Count: {tl_count}")

mp = proj.GetMediaPool()
root = mp.GetRootFolder()
clips = root.GetClipList()
print(f"Media Pool Clip Count in Root Folder: {len(clips)}")

timelines = []
for i in range(1, tl_count + 1):
    tl = proj.GetTimelineByIndex(i)
    if tl:
        timelines.append(tl.GetName())

print("Timelines currently in project:")
for idx, name in enumerate(timelines, 1):
    print(f"  {idx:2d}: {name}")
