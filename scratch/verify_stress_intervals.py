import os
import sys
import json
import re
import subprocess

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Ensure Resolve API is importable
os.environ['RESOLVE_SCRIPT_LIB'] = r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
sys.path.append(r'C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\lib\modules')

try:
    import DaVinciResolveScript as dvr
except ImportError as e:
    print(f"Failed to import DaVinciResolveScript: {e}")
    sys.exit(1)

def get_ffprobe_info(filepath):
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=nb_frames,duration,r_frame_rate,avg_frame_rate",
        "-show_entries", "format=duration",
        "-of", "json",
        filepath
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(res.stdout)

def main():
    resolve = dvr.scriptapp('Resolve')
    if not resolve:
        print("[FAIL] Cannot connect to Resolve")
        sys.exit(1)

    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    if not project:
        print("[FAIL] No active project in Resolve")
        sys.exit(1)

    proj_name = project.GetName()
    fps = float(project.GetSetting("timelineFrameRate"))
    print(f"Connected to Project: '{proj_name}' (FPS: {fps})")

    timeline_count = project.GetTimelineCount()
    print(f"Total timelines in project: {timeline_count}")

    timelines_data = []

    for idx in range(1, timeline_count + 1):
        tl = project.GetTimelineByIndex(idx)
        tl_name = tl.GetName()
        tl_start = tl.GetStartFrame()
        tl_end = tl.GetEndFrame()
        tl_dur = tl_end - tl_start
        
        # Get video track items
        v_items = tl.GetItemListInTrack("video", 1) or []
        if not v_items:
            print(f"[WARN] Timeline '{tl_name}' has no video items on track 1")
            continue
        
        v_item = v_items[0]
        src_start = v_item.GetSourceStartFrame()
        src_end = v_item.GetSourceEndFrame()
        item_dur = v_item.GetDuration()
        
        mpi = v_item.GetMediaPoolItem()
        clip_props = mpi.GetClipProperty() if mpi else {}
        clip_path = clip_props.get("File Path", "")
        clip_name = clip_props.get("Clip Name", "")
        
        timelines_data.append({
            "timeline_index": idx,
            "timeline_name": tl_name,
            "timeline_duration_frames": tl_dur,
            "timeline_duration_seconds": tl_dur / fps,
            "item_duration_frames": item_dur,
            "source_start_frame": src_start,
            "source_end_frame": src_end,
            "source_start_second": src_start / fps,
            "source_end_second": src_end / fps,
            "clip_name": clip_name,
            "clip_path": clip_path,
            "file_name": os.path.basename(clip_path) if clip_path else ""
        })

    # Output extracted data
    print(f"Successfully extracted {len(timelines_data)} timelines from Resolve.")
    
    # Save raw extraction to scratch for review
    with open("scratch/extracted_timelines.json", "w", encoding="utf-8") as f:
        json.dump(timelines_data, f, indent=2, ensure_ascii=False)
        
    print("Saved extracted data to scratch/extracted_timelines.json")

if __name__ == "__main__":
    main()
