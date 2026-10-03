import os
import sys
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

os.environ['RESOLVE_SCRIPT_LIB'] = r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
sys.path.append(r'C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\lib\modules')

import DaVinciResolveScript as dvr

with open("scratch/round4_60_candidates_complete.json", "r", encoding="utf-8") as f:
    cands = json.load(f)

resolve = dvr.scriptapp('Resolve')
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
mp = proj.GetMediaPool()
root = mp.GetRootFolder()
clips = root.GetClipList()

print(f"Total clips/items in root folder: {len(clips)}")
clips_by_id = {}
clips_by_name = {}
for c in clips:
    cid = c.GetUniqueId()
    cname = c.GetName()
    clips_by_id[cid] = c
    clips_by_name[cname] = c

print(f"Unique IDs indexed: {len(clips_by_id)}")

missing_ids = []
missing_names = []
for c in cands:
    cid = c["mediapool_id"]
    sfile = c["source_file"]
    if cid not in clips_by_id:
        missing_ids.append((c["id"], cid, sfile))
    if sfile not in clips_by_name:
        missing_names.append((c["id"], sfile))

print(f"Missing IDs: {len(missing_ids)}")
if missing_ids:
    for m in missing_ids[:5]:
        print(f"  Missing ID: cand {m[0]}, id {m[1]}, file {m[2]}")

print(f"Missing Names: {len(missing_names)}")
if missing_names:
    for m in missing_names[:5]:
        print(f"  Missing Name: cand {m[0]}, file {m[1]}")

if not missing_ids and not missing_names:
    print(">>> 100% of 60 candidates match existing MediaPool clips by ID and Name! <<<")
