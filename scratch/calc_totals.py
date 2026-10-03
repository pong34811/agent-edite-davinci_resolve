import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\scratch\round4_survey_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

all_footage = data["all_footage"]
processed_files = data["processed_files"]
untouched_files = data["untouched_files"]
timelines = data["timelines"]

total_size_bytes = sum(f["size_bytes"] for f in all_footage)
total_dur_sec = sum(f["duration_sec"] for f in all_footage)
total_frames = sum(f["frames_60fps"] for f in all_footage)

untouched_size = sum(f["size_bytes"] for f in untouched_files)
untouched_dur = sum(f["duration_sec"] for f in untouched_files)

processed_size = sum(f["size_bytes"] for f in processed_files)
processed_dur = sum(f["duration_sec"] for f in processed_files)

print(f"Total files: {len(all_footage)}")
print(f"Total size: {total_size_bytes} bytes ({total_size_bytes / (1024**3):.2f} GiB)")
print(f"Total duration: {total_dur_sec:.2f} s ({total_dur_sec / 3600:.2f} hours)")
print(f"Processed: {len(processed_files)} files, {processed_size / (1024**3):.2f} GiB, {processed_dur / 3600:.2f} hours")
print(f"Untouched: {len(untouched_files)} files, {untouched_size / (1024**3):.2f} GiB, {untouched_dur / 3600:.2f} hours")
