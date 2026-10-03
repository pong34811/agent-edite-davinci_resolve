import sys
import os
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules')
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp('Resolve')
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()

print(f"Project: {proj.GetName()}")
timeline_count = proj.GetTimelineCount()
print(f"Timeline Count: {timeline_count}")

for i in range(1, timeline_count + 1):
    tl = proj.GetTimelineByIndex(i)
    print(f"\n--- Timeline {i}: {tl.GetName()} ---")
    print(f"  StartFrame: {tl.GetStartFrame()}")
    print(f"  EndFrame: {tl.GetEndFrame()}")
    print(f"  Duration: {tl.GetEndFrame() - tl.GetStartFrame()} frames ({(tl.GetEndFrame() - tl.GetStartFrame())/60.0:.2f}s)")
    
    # Video Tracks
    v_track_count = tl.GetTrackCount("video")
    a_track_count = tl.GetTrackCount("audio")
    print(f"  Video tracks: {v_track_count}, Audio tracks: {a_track_count}")
    
    for vt in range(1, v_track_count + 1):
        items = tl.GetItemListInTrack("video", vt)
        print(f"  Video Track {vt} item count: {len(items) if items else 0}")
        if items:
            for idx, it in enumerate(items):
                mpi = it.GetMediaPoolItem()
                print(f"    Item {idx}: Name='{it.GetName()}', Start={it.GetStart()}, End={it.GetEnd()}, Duration={it.GetDuration()}")
                print(f"      SourceStart={it.GetSourceStartFrame()}, SourceEnd={it.GetSourceEndFrame()}")
                print(f"      LeftOffset={it.GetLeftOffset()}, RightOffset={it.GetRightOffset()}")
                if mpi:
                    print(f"      MediaPoolItem: Name='{mpi.GetName()}', ClipProperties:")
                    props = mpi.GetClipProperty()
                    for k in ["File Path", "FPS", "Resolution", "Drop frame", "Format"]:
                        print(f"        {k}: {props.get(k)}")
                else:
                    print("      MediaPoolItem: None")

    for at in range(1, a_track_count + 1):
        items = tl.GetItemListInTrack("audio", at)
        print(f"  Audio Track {at} item count: {len(items) if items else 0}")
        if items:
            for idx, it in enumerate(items):
                mpi = it.GetMediaPoolItem()
                print(f"    Item {idx}: Name='{it.GetName()}', Start={it.GetStart()}, End={it.GetEnd()}, Duration={it.GetDuration()}")
                print(f"      SourceStart={it.GetSourceStartFrame()}, SourceEnd={it.GetSourceEndFrame()}")
                print(f"      LeftOffset={it.GetLeftOffset()}, RightOffset={it.GetRightOffset()}")
                print(f"      MediaPoolItem Name: {mpi.GetName() if mpi else None}")
