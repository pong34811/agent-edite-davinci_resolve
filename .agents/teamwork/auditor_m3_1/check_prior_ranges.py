import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

os.environ['RESOLVE_SCRIPT_LIB'] = r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
sys.path.append(r'C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\lib\modules')

import DaVinciResolveScript as dvr

resolve = dvr.scriptapp('Resolve')
project = resolve.GetProjectManager().GetCurrentProject()

print(f"Active Project: {project.GetName()}")
prior_ranges = []
for i in range(1, 8):
    tl = project.GetTimelineByIndex(i)
    v_items = tl.GetItemListInTrack("video", 1)
    if v_items:
        vi = v_items[0]
        s_start = vi.GetSourceStartFrame()
        s_end = vi.GetSourceEndFrame()
        mpi = vi.GetMediaPoolItem()
        clip_name = mpi.GetClipProperty().get("Clip Name", vi.GetName()) if mpi else vi.GetName()
        prior_ranges.append({
            "name": tl.GetName(),
            "clip": clip_name,
            "start": s_start,
            "end": s_end
        })
        print(f"Prior TL #{i}: '{tl.GetName()}' | Clip: '{clip_name}' | Range: [{s_start}..{s_end}] ({s_end - s_start} frames)")

# Check candidate ranges for overlap
print("\nChecking 21 candidates against prior 7 ranges for zero overlap:")
for i in range(8, 29):
    tl = project.GetTimelineByIndex(i)
    vi = tl.GetItemListInTrack("video", 1)[0]
    c_start = vi.GetSourceStartFrame()
    c_end = vi.GetSourceEndFrame()
    mpi = vi.GetMediaPoolItem()
    clip_name = mpi.GetClipProperty().get("Clip Name", vi.GetName()) if mpi else vi.GetName()
    
    overlap = False
    for pr in prior_ranges:
        if pr["clip"] == clip_name:
            # Overlap check: max(start1, start2) < min(end1, end2)
            if max(c_start, pr["start"]) < min(c_end, pr["end"]):
                print(f"  [OVERLAP DETECTED] TL '{tl.GetName()}' [{c_start}..{c_end}] overlaps with Prior '{pr['name']}' [{pr['start']}..{pr['end']}]")
                overlap = True
    if not overlap:
        print(f"  [PASS] TL #{i:02d} '{tl.GetName()}': No overlap with prior highlights in '{clip_name}'")
