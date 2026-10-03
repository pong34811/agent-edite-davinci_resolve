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
if not resolve:
    print("Error: Could not connect to DaVinci Resolve.")
    sys.exit(1)

pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
if not proj:
    print("Error: No current project open in DaVinci Resolve.")
    sys.exit(1)

print(f"Connected to DaVinci Resolve: Project '{proj.GetName()}'")

mp = proj.GetMediaPool()
root = mp.GetRootFolder()
clips = root.GetClipList()

print(f"Media Pool root folder clips count: {len(clips)}")
clips_info = []
for c in clips:
    clip_id = c.GetUniqueId()
    clip_name = c.GetName()
    props = c.GetClipProperty()
    clips_info.append({
        "unique_id": clip_id,
        "name": clip_name,
        "fps": props.get("FPS", ""),
        "duration": props.get("Duration", ""),
        "frames": props.get("Frames", ""),
        "file_path": props.get("File Path", "")
    })

timeline_count = proj.GetTimelineCount()
print(f"Total timelines in project: {timeline_count}")

timelines_info = []
for i in range(1, timeline_count + 1):
    tl = proj.GetTimelineByIndex(i)
    if not tl:
        continue
    tl_name = tl.GetName()
    tl_id = tl.GetUniqueId()
    tl_start_frame = tl.GetStartFrame()
    tl_end_frame = tl.GetEndFrame()
    tl_track_count = tl.GetTrackCount("video")
    
    # Get items on video track 1
    items = tl.GetItemListInTrack("video", 1)
    items_data = []
    if items:
        for item in items:
            mpi = item.GetMediaPoolItem()
            mpi_name = mpi.GetName() if mpi else "None"
            mpi_id = mpi.GetUniqueId() if mpi else "None"
            items_data.append({
                "item_name": item.GetName(),
                "media_pool_item_name": mpi_name,
                "media_pool_item_id": mpi_id,
                "left_offset": item.GetLeftOffset(),
                "right_offset": item.GetRightOffset(),
                "source_start_frame": item.GetSourceStartFrame(),
                "source_end_frame": item.GetSourceEndFrame(),
                "start": item.GetStart(),
                "end": item.GetEnd(),
                "duration": item.GetDuration()
            })
    
    timelines_info.append({
        "index": i,
        "name": tl_name,
        "id": tl_id,
        "start_frame": tl_start_frame,
        "end_frame": tl_end_frame,
        "duration": tl_end_frame - tl_start_frame,
        "video_items": items_data
    })

data = {
    "project_name": proj.GetName(),
    "timeline_count": timeline_count,
    "clips": clips_info,
    "timelines": timelines_info
}

output_path = r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\scratch\existing_timelines_and_clips.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Saved existing timelines and clips data to {output_path}")
