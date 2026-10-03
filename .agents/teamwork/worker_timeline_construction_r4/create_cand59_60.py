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
resolve.OpenPage("edit")
proj = resolve.GetProjectManager().GetCurrentProject()
mp = proj.GetMediaPool()
root = mp.GetRootFolder()

# Ensure clip FPS is 60.0
for c in root.GetClipList():
    if c.GetName() == "สอนไทกะเล่น LoL ที.mp4":
        if float(c.GetClipProperty("FPS")) != 60.0:
            c.SetClipProperty("FPS", "60")
            print("Set FPS to 60.0 on สอนไทกะเล่น LoL ที.mp4")

clips_by_id = {c.GetUniqueId(): c for c in root.GetClipList()}
clips_by_name = {c.GetName(): c for c in root.GetClipList()}

# 1. Candidate 59
title59 = "จังหวะโดนดักซุ่มพุ่มไม้ร้องเสียงหลง_LoL-vdo"
clip59 = clips_by_id.get("35d91ae8-0efc-474b-8034-21b09eb5cc3a") or clips_by_name.get("สอนไทกะเล่น LoL ที.mp4")
tl59 = mp.CreateEmptyTimeline(title59)
print(f"CreateEmptyTimeline 59: {tl59.GetName() if tl59 else None}")
proj.SetCurrentTimeline(tl59)
time.sleep(0.1)

append_info59 = {
    "mediaPoolItem": clip59,
    "startFrame": 165960,
    "endFrame": 169260,
    "recordFrame": 0,
    "trackIndex": 1
}
res59 = mp.AppendToTimeline([append_info59])
print(f"Append 59: {res59}, dur: {tl59.GetEndFrame() - tl59.GetStartFrame()}")

# 2. Candidate 60
title60 = "เพื่อนโดนงาบต่อหน้าต่อตาช่วยไม่ทัน_REPO-vdo"
clip60 = clips_by_id.get("b3fdb6ac-e495-45b7-9bce-5ff92b809fd7") or clips_by_name.get("R.E.P.O @Luche_Sinclair @Kungphaokung @RahhatemPSM @Salika_SaharasCh.mp4")
tl60 = mp.CreateEmptyTimeline(title60)
print(f"CreateEmptyTimeline 60: {tl60.GetName() if tl60 else None}")
proj.SetCurrentTimeline(tl60)
time.sleep(0.1)

append_info60 = {
    "mediaPoolItem": clip60,
    "startFrame": 415200,
    "endFrame": 418500,
    "recordFrame": 0,
    "trackIndex": 1
}
res60 = mp.AppendToTimeline([append_info60])
print(f"Append 60: {res60}, dur: {tl60.GetEndFrame() - tl60.GetStartFrame()}")

# Save Project
pm = resolve.GetProjectManager()
save_res = pm.SaveProject()
print(f"SaveProject result: {save_res}")

# Check total timelines
print(f"New total timeline count: {proj.GetTimelineCount()}")
