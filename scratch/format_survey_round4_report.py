import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\scratch\round4_survey_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("=== 7 PROCESSED FILES ===")
for p in data["processed_files"]:
    print(f"\nFile: {p['filename']}")
    print(f"  MediaPool Unique ID: {p['media_pool_unique_id']}")
    print(f"  Duration: {p['duration_sec']:.2f}s ({p['frames_60fps']} frames at 60fps) | Size: {p['size_bytes'] / (1024*1024):.2f} MB | Res: {p['resolution']}")
    print(f"  Timelines ({len(p['timelines'])}):")
    # find all timeline details for this file
    matching_tls = [t for t in data["timelines"] if t["source_clip_name"] == p["filename"] or os.path.basename(t["source_file_path"]) == p["filename"]]
    for t in matching_tls:
        print(f"    - #{t['index']}: '{t['name']}' | Frames: [{t['source_start_frame']} .. {t['source_end_frame']}] ({t['duration_frames']} f, {t['duration_sec']:.2f}s)")

print("\n=== 25 UNTOUCHED FILES ===")
for u in data["untouched_files"]:
    print(f"File: {u['filename']}")
    print(f"  Unique ID: {u['media_pool_unique_id']} | Media ID: {u['media_pool_media_id']}")
    print(f"  Duration: {u['duration_sec']:.2f}s ({u['frames_60fps']} frames) | Size: {u['size_bytes'] / (1024*1024):.2f} MB | Res: {u['resolution']} | Codec: {u['video_codec']} | InPool: {u['in_media_pool']}")
