import os
import sys
import time

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

# Ensure current folder is root/Master
mp.SetCurrentFolder(root)
print("Current folder:", mp.GetCurrentFolder().GetName())

title = "จังหวะโดนดักซุ่มพุ่มไม้ร้องเสียงหลง_LoL-vdo"
tl = None
for i in range(1, proj.GetTimelineCount() + 1):
    t = proj.GetTimelineByIndex(i)
    if t.GetName() == title:
        tl = t
        break

proj.SetCurrentTimeline(tl)
time.sleep(0.2)

clip = None
for c in root.GetClipList():
    if c.GetName() == "สอนไทกะเล่น LoL ที.mp4":
        clip = c
        break

print("Testing variation 1: standard clipInfo")
ci1 = {
    "mediaPoolItem": clip,
    "startFrame": 165960,
    "endFrame": 169260,
    "recordFrame": 0,
    "trackIndex": 1
}
res1 = mp.AppendToTimeline([ci1])
print("Res 1:", res1)

if not res1:
    print("Testing variation 2: without trackIndex")
    ci2 = {
        "mediaPoolItem": clip,
        "startFrame": 165960,
        "endFrame": 169260,
        "recordFrame": 0
    }
    res2 = mp.AppendToTimeline([ci2])
    print("Res 2:", res2)

if not res1 and not res2:
    print("Testing variation 3: float frames")
    ci3 = {
        "mediaPoolItem": clip,
        "startFrame": float(165960),
        "endFrame": float(169260),
        "recordFrame": 0.0,
        "trackIndex": 1
    }
    res3 = mp.AppendToTimeline([ci3])
    print("Res 3:", res3)

if not res1 and not res2 and not res3:
    print("Testing variation 4: check if track 1 exists on tl")
    print("Video tracks on tl:", tl.GetTrackCount("video"))
    print("Audio tracks on tl:", tl.GetTrackCount("audio"))
