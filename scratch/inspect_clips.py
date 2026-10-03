import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules')
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp('Resolve')
proj = resolve.GetProjectManager().GetCurrentProject()
mp = proj.GetMediaPool()
root = mp.GetRootFolder()
clips = root.GetClipList()

print(f"Total clips in root folder: {len(clips)}")
timelines_in_pool = []
video_clips = []
other_clips = []

for i, c in enumerate(clips):
    props = c.GetClipProperty()
    name = c.GetName()
    path = props.get('File Path', '')
    clip_type = props.get('Type', '')
    clip_format = props.get('Format', '')
    
    if not path:
        timelines_in_pool.append((i+1, name, clip_type))
    elif path.endswith('.mp4'):
        video_clips.append((i+1, name, path))
    else:
        other_clips.append((i+1, name, path))

print(f"\nVideo clips with file paths: {len(video_clips)}")
for idx, name, path in video_clips:
    print(f"  [{idx}] {name} -> {path} (exists: {os.path.exists(path)})")

print(f"\nItems without file paths (e.g. Timelines in pool): {len(timelines_in_pool)}")
for idx, name, ctype in timelines_in_pool:
    print(f"  [{idx}] {name} (type: {ctype})")

print(f"\nOther clips: {len(other_clips)}")
for idx, name, path in other_clips:
    print(f"  [{idx}] {name} -> {path}")
