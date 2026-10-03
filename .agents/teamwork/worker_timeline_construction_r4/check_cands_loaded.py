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
print(f"Current project: {proj.GetName()}")
print(f"Total timelines: {proj.GetTimelineCount()}")

# Check all 60 candidate names
import json
with open("scratch/round4_60_candidates_complete.json", "r", encoding="utf-8") as f:
    cands = json.load(f)

tl_names = {proj.GetTimelineByIndex(i).GetName(): proj.GetTimelineByIndex(i) for i in range(1, proj.GetTimelineCount() + 1)}

for c in cands:
    title = c["title"]
    cid = c["id"]
    if title not in tl_names:
        print(f"MISSING: #{cid} '{title}'")
    else:
        tl = tl_names[title]
        dur = tl.GetEndFrame() - tl.GetStartFrame()
        if dur != 3300:
            print(f"BAD DURATION: #{cid} '{title}' dur={dur}")
