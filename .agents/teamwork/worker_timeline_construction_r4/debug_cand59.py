import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

os.environ['RESOLVE_SCRIPT_LIB'] = r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
sys.path.append(r'C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\lib\modules')

import DaVinciResolveScript as dvr

resolve = dvr.scriptapp('Resolve')
resolve.OpenPage("edit")

proj = resolve.GetProjectManager().GetCurrentProject()
mp = proj.GetMediaPool()

title = "จังหวะโดนดักซุ่มพุ่มไม้ร้องเสียงหลง_LoL-vdo"
tl = None
for i in range(1, proj.GetTimelineCount() + 1):
    t = proj.GetTimelineByIndex(i)
    if t.GetName() == title:
        tl = t
        break

print(f"Timeline {title} exists: {tl is not None}")
if tl:
    print(f"Items in V1: {len(tl.GetItemListInTrack('video', 1) or [])}")

# Check clip
root = mp.GetRootFolder()
clip = None
for c in root.GetClipList():
    if c.GetName() == "สอนไทกะเล่น LoL ที.mp4":
        clip = c
        break

print(f"Clip found: {clip.GetName()}, FPS={clip.GetClipProperty('FPS')}")

if not tl:
    tl = mp.CreateEmptyTimeline(title)
    print(f"CreateEmptyTimeline: {tl}")

proj.SetCurrentTimeline(tl)

append_info = {
    "mediaPoolItem": clip,
    "startFrame": 165960,
    "endFrame": 169260,
    "recordFrame": 0,
    "trackIndex": 1
}

res = mp.AppendToTimeline([append_info])
print(f"AppendToTimeline: {res}")
if tl:
    print(f"Timeline start: {tl.GetStartFrame()}, end: {tl.GetEndFrame()}, dur: {tl.GetEndFrame() - tl.GetStartFrame()}")
    v_items = tl.GetItemListInTrack("video", 1) or []
    for v in v_items:
        print(f"  V: dur={v.GetDuration()}, srcStart={v.GetSourceStartFrame()}, srcEnd={v.GetSourceEndFrame()}")
