import os
import sys
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

os.environ['RESOLVE_SCRIPT_LIB'] = r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
sys.path.append(r'C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\lib\modules')

import DaVinciResolveScript as dvr

resolve = dvr.scriptapp('Resolve')
pm = resolve.GetProjectManager()
project = pm.GetCurrentProject()

timelines = {}
for i in range(1, project.GetTimelineCount() + 1):
    tl = project.GetTimelineByIndex(i)
    timelines[tl.GetName()] = tl

prior_7 = [
    "Highlight_Gaming_REPO_Jumpscare",
    "Highlight_Gaming_Climbing_Clutch",
    "Highlight_Gaming_Ib_Horror",
    "Highlight_Fun_DnD_Bard",
    "Highlight_Meme_GarticPhone_Art",
    "Highlight_Meme_FreeTalk_Tiger",
    "Highlight_Fun_Overcooked_KitchenFire"
]

prior_data = {}
for p in prior_7:
    tl = timelines[p]
    items = tl.GetItemListInTrack("video", 1) or []
    item_infos = []
    for it in items:
        mpi = it.GetMediaPoolItem()
        clip_name = mpi.GetClipProperty().get("Clip Name", "") if mpi else ""
        item_infos.append({
            "name": it.GetName(),
            "clip_name": clip_name,
            "src_start": it.GetSourceStartFrame(),
            "src_end": it.GetSourceEndFrame(),
            "duration": it.GetDuration()
        })
    prior_data[p] = item_infos

print(json.dumps(prior_data, indent=2, ensure_ascii=False))
