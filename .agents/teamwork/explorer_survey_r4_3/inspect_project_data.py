import sys
import os
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules')
import DaVinciResolveScript as dvr

def main():
    resolve = dvr.scriptapp('Resolve')
    if not resolve:
        print("ERROR: Cannot connect to DaVinci Resolve")
        sys.exit(1)
        
    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    print(f"Project: {proj.GetName()} (ID: {proj.GetUniqueId()})")
    
    tl_count = proj.GetTimelineCount()
    print(f"Total existing timelines: {tl_count}")
    
    timelines = []
    for i in range(1, tl_count + 1):
        tl = proj.GetTimelineByIndex(i)
        timelines.append({
            "index": i,
            "name": tl.GetName(),
            "id": tl.GetUniqueId(),
            "start_frame": tl.GetStartFrame(),
            "end_frame": tl.GetEndFrame(),
            "track_count_video": tl.GetTrackCount("video"),
            "track_count_audio": tl.GetTrackCount("audio")
        })
        print(f"  [{i:02d}] {tl.GetName()} (Frames: {tl.GetStartFrame()} - {tl.GetEndFrame()})")

    # Media pool clips
    mp = proj.GetMediaPool()
    root = mp.GetRootFolder()
    clips = root.GetClipList() or []
    print(f"\nMedia Pool Clips: {len(clips)}")
    pool_clips = []
    for c in clips:
        props = c.GetClipProperty()
        name = c.GetName()
        path = props.get("File Path")
        uid = c.GetUniqueId()
        if path: # filter out timeline items in root if any
            pool_clips.append({
                "name": name,
                "file_path": path,
                "id": uid,
                "fps": props.get("FPS"),
                "duration": props.get("Duration"),
                "resolution": props.get("Resolution")
            })
            print(f"  Clip: {name} | Path: {path}")

    # Files on disk
    footage_dir = r"C:\Users\warit\SynologyDrive\Tygarina\2026-09-30"
    disk_files = [f for f in os.listdir(footage_dir) if f.endswith(".mp4")]
    print(f"\nDisk Files: {len(disk_files)}")
    for f in disk_files:
        print(f"  Disk: {f}")

    data = {
        "timelines": timelines,
        "media_pool_clips": pool_clips,
        "disk_files": disk_files
    }
    
    out_path = r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\explorer_survey_r4_3\current_state.json"
    with open(out_path, "w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=2)
    print(f"\nWrote current state to {out_path}")

if __name__ == "__main__":
    main()
