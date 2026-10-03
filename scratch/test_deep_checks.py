import sys
import os
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules')
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp('Resolve')
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()

print("Project settings:")
for s in ["timelineFrameRate", "timelinePlaybackFrameRate", "timelineResolutionWidth", "timelineResolutionHeight"]:
    print(f"  {s}: {proj.GetSetting(s)}")

timeline_count = proj.GetTimelineCount()
for i in range(1, timeline_count + 1):
    tl = proj.GetTimelineByIndex(i)
    print(f"\nTimeline {i}: {tl.GetName()}")
    print(f"  StartTimecode: {tl.GetStartTimecode()}")
    print(f"  Subtitle tracks: {tl.GetTrackCount('subtitle')}")
    print(f"  Markers on timeline: {tl.GetMarkers()}")
    
    # Check video items
    v_items = tl.GetItemListInTrack("video", 1)
    a_items = tl.GetItemListInTrack("audio", 1)
    
    if v_items:
        v0 = v_items[0]
        print(f"  Video item 0 markers: {v0.GetMarkers()}")
        print(f"  Video item 0 fusion comp count: {v0.GetFusionCompCount()}")
    
    if a_items:
        a0 = a_items[0]
        print(f"  Audio item 0 markers: {a0.GetMarkers()}")
        # Check alignment between audio and video
        if v_items:
            align_start = (v0.GetStart() == a0.GetStart())
            align_end = (v0.GetEnd() == a0.GetEnd())
            align_duration = (v0.GetDuration() == a0.GetDuration())
            align_source_start = (v0.GetSourceStartFrame() == a0.GetSourceStartFrame())
            align_source_end = (v0.GetSourceEndFrame() == a0.GetSourceEndFrame())
            print(f"  AV Alignment: Start={align_start}, End={align_end}, Dur={align_duration}, SrcStart={align_source_start}, SrcEnd={align_source_end}")

print("\nFinished deep check.")
