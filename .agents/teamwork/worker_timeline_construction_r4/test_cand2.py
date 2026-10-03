import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

os.environ['RESOLVE_SCRIPT_LIB'] = r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
sys.path.append(r'C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\lib\modules')

import DaVinciResolveScript as dvr

resolve = dvr.scriptapp('Resolve')
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
mp = proj.GetMediaPool()
root = mp.GetRootFolder()

# Find item
cid = "33bd05cc-6238-469a-acf1-74e6bac5270e"
mp_item = None
for c in root.GetClipList():
    if c.GetUniqueId() == cid:
        mp_item = c
        break

if not mp_item:
    print(f"Error: clip {cid} not found")
    sys.exit(1)

name = "สารภาพความในใจสุดเขินกลางตี้_DnD-vdo"
tl = mp.CreateEmptyTimeline(name)
if not tl:
    print("Error: CreateEmptyTimeline failed")
    sys.exit(1)

proj.SetCurrentTimeline(tl)

append_info = {
    "mediaPoolItem": mp_item,
    "startFrame": 140520,
    "endFrame": 143820,
    "recordFrame": 0,
    "trackIndex": 1
}

res = mp.AppendToTimeline([append_info])
print(f"AppendToTimeline result: {res}")

print(f"Created timeline: {tl.GetName()}")
print(f"Start Frame: {tl.GetStartFrame()}, End Frame: {tl.GetEndFrame()}")
print(f"Duration: {tl.GetEndFrame() - tl.GetStartFrame()}")
print(f"Video tracks: {tl.GetTrackCount('video')}, Audio tracks: {tl.GetTrackCount('audio')}")
v_items = tl.GetItemListInTrack('video', 1)
for it in v_items:
    print(f"  V: {it.GetName()}, dur: {it.GetDuration()}, srcStart: {it.GetSourceStartFrame()}, srcEnd: {it.GetSourceEndFrame()}")
a_items = tl.GetItemListInTrack('audio', 1)
for it in a_items:
    print(f"  A: {it.GetName()}, dur: {it.GetDuration()}, srcStart: {it.GetSourceStartFrame()}, srcEnd: {it.GetSourceEndFrame()}")
