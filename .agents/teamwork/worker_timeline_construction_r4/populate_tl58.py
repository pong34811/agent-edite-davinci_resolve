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
root = mp.GetRootFolder()

# Clip for 58
clip58 = None
for c in root.GetClipList():
    if c.GetName() == "ไลฟ์นี้จะเล่น Fallout 4 Nuka-world P1.mp4":
        clip58 = c
        break

print("Found clip 58:", clip58.GetName(), clip58.GetUniqueId())

# Timeline 58
title58 = "หลงทางในแดนรกร้างเดินวนอยู่ที่เดิม_Fallout4-vdo"
tl58 = None
for i in range(1, proj.GetTimelineCount() + 1):
    t = proj.GetTimelineByIndex(i)
    if t.GetName() == title58:
        tl58 = t
        break

print("Found tl 58:", tl58.GetName(), "dur:", tl58.GetEndFrame() - tl58.GetStartFrame())
proj.SetCurrentTimeline(tl58)

append_info58 = {
    "mediaPoolItem": clip58,
    "startFrame": 306360,
    "endFrame": 309660,
    "recordFrame": 0,
    "trackIndex": 1
}

res58 = mp.AppendToTimeline([append_info58])
print("Append 58 result:", res58)
print("TL 58 new dur:", tl58.GetEndFrame() - tl58.GetStartFrame())
