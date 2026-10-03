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
mp = proj.GetMediaPool()

title = "จังหวะโดนดักซุ่มพุ่มไม้ร้องเสียงหลง_LoL-vdo"
tl = None
for i in range(1, proj.GetTimelineCount() + 1):
    t = proj.GetTimelineByIndex(i)
    if t.GetName() == title:
        tl = t
        break

print("Wanted tl ID:", tl.GetUniqueId())
print("Current tl ID before:", proj.GetCurrentTimeline().GetUniqueId() if proj.GetCurrentTimeline() else None)
ret = proj.SetCurrentTimeline(tl)
print("SetCurrentTimeline returned:", ret)
print("Current tl ID after:", proj.GetCurrentTimeline().GetUniqueId() if proj.GetCurrentTimeline() else None)
print("Current tl Name after:", proj.GetCurrentTimeline().GetName() if proj.GetCurrentTimeline() else None)

# What are tracks on current tl?
ctl = proj.GetCurrentTimeline()
print("ctl video tracks:", ctl.GetTrackCount("video"))
print("ctl audio tracks:", ctl.GetTrackCount("audio"))

# Let's inspect tracks
v1_items = ctl.GetItemListInTrack("video", 1)
print("v1_items:", v1_items)
a1_items = ctl.GetItemListInTrack("audio", 1)
print("a1_items:", a1_items)

# Check clip
root = mp.GetRootFolder()
clip = None
for c in root.GetClipList():
    if c.GetName() == "สอนไทกะเล่น LoL ที.mp4":
        clip = c
        break
print("Clip:", clip.GetName(), clip.GetUniqueId())
