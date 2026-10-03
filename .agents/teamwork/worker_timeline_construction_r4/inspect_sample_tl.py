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

tl_count = proj.GetTimelineCount()
for i in range(1, tl_count + 1):
    tl = proj.GetTimelineByIndex(i)
    if tl.GetName() == "วิ่งหนีปีศาจแทบไม่ทัน_REPO-vdo":
        print(f"Found timeline: {tl.GetName()}")
        print(f"Start Frame: {tl.GetStartFrame()}, End Frame: {tl.GetEndFrame()}")
        print(f"Video track count: {tl.GetTrackCount('video')}")
        print(f"Audio track count: {tl.GetTrackCount('audio')}")
        
        v_items = tl.GetItemListInTrack('video', 1)
        print(f"Video track 1 items: {len(v_items)}")
        for it in v_items:
            print(f"  V item: {it.GetName()}, dur: {it.GetDuration()}, srcStart: {it.GetSourceStartFrame()}, srcEnd: {it.GetSourceEndFrame()}")
            
        a_items = tl.GetItemListInTrack('audio', 1)
        print(f"Audio track 1 items: {len(a_items)}")
        for it in a_items:
            print(f"  A item: {it.GetName()}, dur: {it.GetDuration()}, srcStart: {it.GetSourceStartFrame()}, srcEnd: {it.GetSourceEndFrame()}")
        break
