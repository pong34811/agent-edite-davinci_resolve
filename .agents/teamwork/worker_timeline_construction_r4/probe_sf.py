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
root = mp.GetRootFolder()

clip = None
for c in root.GetClipList():
    if c.GetName() == "สอนไทกะเล่น LoL ที.mp4":
        clip = c
        break

title = "จังหวะโดนดักซุ่มพุ่มไม้ร้องเสียงหลง_LoL-vdo"
tl = None
for i in range(1, proj.GetTimelineCount() + 1):
    t = proj.GetTimelineByIndex(i)
    if t.GetName() == title:
        tl = t
        break

proj.SetCurrentTimeline(tl)

# Try appending different ranges
for sf in [0, 1000, 10000, 100000, 165960, 200000, 330120, 350160]:
    ci = {
        "mediaPoolItem": clip,
        "startFrame": sf,
        "endFrame": sf + 3300,
        "recordFrame": 0,
        "trackIndex": 1
    }
    res = mp.AppendToTimeline([ci])
    print(f"sf={sf}..{sf+3300}: res={res}")
    if res:
        # delete to clean up for next test
        items = (tl.GetItemListInTrack("video", 1) or []) + (tl.GetItemListInTrack("audio", 1) or [])
        tl.DeleteClips(items, False)
