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

for i in range(1, proj.GetTimelineCount() + 1):
    tl = proj.GetTimelineByIndex(i)
    if "โดนโค้ชบ่นเรื่องลืมซื้อของตอนเริ่มเกม_LoL-vdo" in tl.GetName():
        print(f"Timeline: {tl.GetName()}")
        print(f"Start Frame: {tl.GetStartFrame()}, End Frame: {tl.GetEndFrame()}")
        v_items = tl.GetItemListInTrack("video", 1) or []
        print(f"Video items count: {len(v_items)}")
        for v in v_items:
            print(f"  v: {v.GetName()}, dur={v.GetDuration()}, srcStart={v.GetSourceStartFrame()}, srcEnd={v.GetSourceEndFrame()}")
        a_items = tl.GetItemListInTrack("audio", 1) or []
        print(f"Audio items count: {len(a_items)}")
        for a in a_items:
            print(f"  a: {a.GetName()}, dur={a.GetDuration()}, srcStart={a.GetSourceStartFrame()}, srcEnd={a.GetSourceEndFrame()}")
        
        # Check source clip properties
        if v_items:
            mpi = v_items[0].GetMediaPoolItem()
            print("MediaPoolItem properties:", mpi.GetClipProperty())
