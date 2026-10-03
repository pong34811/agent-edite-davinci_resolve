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
tl = proj.GetCurrentTimeline()

print(f"Current Timeline: {tl.GetName()}")
print(f"Start Frame: {tl.GetStartFrame()}, End Frame: {tl.GetEndFrame()}")
print(f"Duration: {tl.GetEndFrame() - tl.GetStartFrame()}")
print(f"Video tracks: {tl.GetTrackCount('video')}, Audio tracks: {tl.GetTrackCount('audio')}")
v_items = tl.GetItemListInTrack('video', 1)
for it in v_items:
    print(f"  V: {it.GetName()}, dur: {it.GetDuration()}, srcStart: {it.GetSourceStartFrame()}, srcEnd: {it.GetSourceEndFrame()}")
a_items = tl.GetItemListInTrack('audio', 1)
for it in a_items:
    print(f"  A: {it.GetName()}, dur: {it.GetDuration()}, srcStart: {it.GetSourceStartFrame()}, srcEnd: {it.GetSourceEndFrame()}")
