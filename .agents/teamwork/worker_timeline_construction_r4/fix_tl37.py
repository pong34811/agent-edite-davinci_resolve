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

target_tl = None
for i in range(1, proj.GetTimelineCount() + 1):
    tl = proj.GetTimelineByIndex(i)
    if "โดนโค้ชบ่นเรื่องลืมซื้อของตอนเริ่มเกม_LoL-vdo" in tl.GetName():
        target_tl = tl
        break

print(f"Target timeline: {target_tl.GetName()}")
proj.SetCurrentTimeline(target_tl)

v_items = target_tl.GetItemListInTrack("video", 1) or []
a_items = target_tl.GetItemListInTrack("audio", 1) or []
all_items = v_items + a_items
print(f"Deleting {len(all_items)} items from timeline...")
res = target_tl.DeleteClips(all_items, False)
print(f"DeleteClips result: {res}")

# Check items
v_rem = target_tl.GetItemListInTrack("video", 1) or []
a_rem = target_tl.GetItemListInTrack("audio", 1) or []
print(f"Remaining: {len(v_rem)} V items, {len(a_rem)} A items")

# Re-append clip with 60 fps
root = mp.GetRootFolder()
target_clip = None
for c in root.GetClipList():
    if c.GetName() == "สอนไทกะเล่น LoL ที.mp4":
        target_clip = c
        break

append_info = {
    "mediaPoolItem": target_clip,
    "startFrame": 350160,
    "endFrame": 353460,
    "recordFrame": 0,
    "trackIndex": 1
}

app_res = mp.AppendToTimeline([append_info])
print(f"AppendToTimeline result: {app_res}")

print(f"Start Frame: {target_tl.GetStartFrame()}, End Frame: {target_tl.GetEndFrame()}")
dur = target_tl.GetEndFrame() - target_tl.GetStartFrame()
print(f"Duration: {dur} (expected 3300)")

v_new = target_tl.GetItemListInTrack("video", 1) or []
a_new = target_tl.GetItemListInTrack("audio", 1) or []
for v in v_new:
    print(f"  V: dur={v.GetDuration()}, srcStart={v.GetSourceStartFrame()}, srcEnd={v.GetSourceEndFrame()}")
for a in a_new:
    print(f"  A: dur={a.GetDuration()}, srcStart={a.GetSourceStartFrame()}, srcEnd={a.GetSourceEndFrame()}")
