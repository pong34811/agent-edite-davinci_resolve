import os
import sys
import json
import subprocess
import glob

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

FOOTAGE_DIR = r"C:\Users\warit\SynologyDrive\Tygarina\2026-09-30"

# 1. Enumerate filesystem files
print(f"=== Scanning Filesystem Directory: {FOOTAGE_DIR} ===")
files = os.listdir(FOOTAGE_DIR)
mp4_files = sorted([f for f in files if f.lower().endswith('.mp4')])
print(f"Total files in folder: {len(files)}, MP4 files: {len(mp4_files)}")

footage_catalog = {}

for idx, fname in enumerate(mp4_files, 1):
    fpath = os.path.join(FOOTAGE_DIR, fname)
    fsize = os.path.getsize(fpath)
    
    # Run ffprobe
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", fpath
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    info = json.loads(res.stdout) if res.stdout else {}
    
    fmt = info.get("format", {})
    dur_sec = float(fmt.get("duration", 0.0))
    bit_rate = int(fmt.get("bit_rate", 0)) if fmt.get("bit_rate") else 0
    
    v_stream = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), {})
    a_stream = next((s for s in info.get("streams", []) if s.get("codec_type") == "audio"), {})
    
    v_codec = v_stream.get("codec_name", "")
    width = v_stream.get("width", 0)
    height = v_stream.get("height", 0)
    r_fps = v_stream.get("r_frame_rate", "")
    avg_fps = v_stream.get("avg_frame_rate", "")
    nb_frames = v_stream.get("nb_frames")
    
    # Calculate frames at 60.0 fps
    calc_frames = round(dur_sec * 60.0)
    exact_frames = int(nb_frames) if nb_frames and nb_frames.isdigit() else calc_frames
    
    a_codec = a_stream.get("codec_name", "")
    a_sample_rate = a_stream.get("sample_rate", "")
    a_channels = a_stream.get("channels", 0)
    
    footage_catalog[fname] = {
        "index": idx,
        "filename": fname,
        "filepath": fpath,
        "size_bytes": fsize,
        "duration_sec": dur_sec,
        "frames_60fps": calc_frames,
        "nb_frames_stream": exact_frames,
        "resolution": f"{width}x{height}",
        "video_codec": v_codec,
        "r_frame_rate": r_fps,
        "avg_frame_rate": avg_fps,
        "audio_codec": a_codec,
        "audio_sample_rate": a_sample_rate,
        "audio_channels": a_channels
    }

print(f"Finished ffprobe catalog for {len(footage_catalog)} files.")

# 2. Connect to DaVinci Resolve
sys.path.append(r'C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules')
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp('Resolve')
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
proj_name = proj.GetName()
print(f"Connected to DaVinci Resolve Project: '{proj_name}'")

# Query Media Pool Master Bin
mp = proj.GetMediaPool()
root = mp.GetRootFolder()
clips = root.GetClipList()
print(f"Total items in Root Folder: {len(clips)}")

mediapool_items = {}
for c in clips:
    c_name = c.GetName()
    c_uid = c.GetUniqueId()
    c_mid = c.GetMediaId()
    props = c.GetClipProperty()
    fpath = props.get("File Path", "")
    clip_type = props.get("Type", "")
    res = props.get("Resolution", "")
    fps = props.get("FPS", "")
    frames = props.get("Frames", "")
    vcodec = props.get("Video Codec", "")
    ach = props.get("Audio Ch", "")
    cformat = props.get("Format", "")
    
    mediapool_items[c_name] = {
        "name": c_name,
        "unique_id": c_uid,
        "media_id": c_mid,
        "file_path": fpath,
        "type": clip_type,
        "resolution": res,
        "fps": fps,
        "frames": frames,
        "video_codec": vcodec,
        "audio_channels": ach,
        "format": cformat
    }

# Query Timelines
tl_count = proj.GetTimelineCount()
print(f"Total timelines in project: {tl_count}")

timelines_data = []
referenced_sources = set()

for i in range(1, tl_count + 1):
    tl = proj.GetTimelineByIndex(i)
    tl_name = tl.GetName()
    s_frame = tl.GetStartFrame()
    e_frame = tl.GetEndFrame()
    dur_frames = e_frame - s_frame
    dur_sec = dur_frames / 60.0
    
    v_items = tl.GetItemListInTrack("video", 1)
    a_items = tl.GetItemListInTrack("audio", 1)
    
    first_v = v_items[0] if v_items else None
    v_mpi = first_v.GetMediaPoolItem() if first_v else None
    v_mpi_name = v_mpi.GetName() if v_mpi else (first_v.GetName() if first_v else "")
    v_mpi_uid = v_mpi.GetUniqueId() if v_mpi else ""
    v_mpi_mid = v_mpi.GetMediaId() if v_mpi else ""
    v_mpi_path = v_mpi.GetClipProperty().get("File Path", "") if v_mpi else ""
    
    src_s = first_v.GetSourceStartFrame() if first_v else None
    src_e = first_v.GetSourceEndFrame() if first_v else None
    
    if v_mpi_name:
        referenced_sources.add(v_mpi_name)
    elif v_mpi_path:
        referenced_sources.add(os.path.basename(v_mpi_path))
    
    timelines_data.append({
        "index": i,
        "name": tl_name,
        "start_frame": s_frame,
        "end_frame": e_frame,
        "duration_frames": dur_frames,
        "duration_sec": dur_sec,
        "source_clip_name": v_mpi_name,
        "source_clip_uid": v_mpi_uid,
        "source_clip_mid": v_mpi_mid,
        "source_file_path": v_mpi_path,
        "source_start_frame": src_s,
        "source_end_frame": src_e
    })

# 3. Classify Processed vs Untouched files
processed_files = []
untouched_files = []

for fname, fdata in sorted(footage_catalog.items()):
    # Check if fname is in referenced_sources
    is_processed = False
    matching_timelines = []
    for tl in timelines_data:
        if tl["source_clip_name"] == fname or os.path.basename(tl["source_file_path"]) == fname:
            is_processed = True
            matching_timelines.append(tl)
            
    # Attach MediaPool info
    mpi_info = mediapool_items.get(fname, {})
    fdata["media_pool_unique_id"] = mpi_info.get("unique_id", "")
    fdata["media_pool_media_id"] = mpi_info.get("media_id", "")
    fdata["in_media_pool"] = fname in mediapool_items
    fdata["timeline_count"] = len(matching_timelines)
    fdata["timelines"] = [t["name"] for t in matching_timelines]
    
    if is_processed:
        processed_files.append(fdata)
    else:
        untouched_files.append(fdata)

print(f"\nClassification Summary:")
print(f"Processed Files: {len(processed_files)}")
print(f"Untouched Files: {len(untouched_files)}")
assert len(processed_files) + len(untouched_files) == 32

output_data = {
    "project_name": proj_name,
    "total_footage_files": len(footage_catalog),
    "total_processed_files": len(processed_files),
    "total_untouched_files": len(untouched_files),
    "total_timelines": len(timelines_data),
    "processed_files": processed_files,
    "untouched_files": untouched_files,
    "all_footage": list(footage_catalog.values()),
    "timelines": timelines_data,
    "mediapool_items": mediapool_items
}

out_json = r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\scratch\round4_survey_data.json"
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print(f"\nSaved survey data to {out_json}")
