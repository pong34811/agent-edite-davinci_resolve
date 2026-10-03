import sys
import json
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


with open("scratch/existing_timelines_and_clips.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("=== 28 EXISTING TIMELINES ===")
existing_intervals = {}
for tl in data["timelines"]:
    tl_name = tl["name"]
    for item in tl["video_items"]:
        src_name = item["media_pool_item_name"]
        s_frame = item["source_start_frame"]
        e_frame = item["source_end_frame"]
        dur = item["duration"]
        if src_name not in existing_intervals:
            existing_intervals[src_name] = []
        existing_intervals[src_name].append({
            "timeline": tl_name,
            "start_frame": s_frame,
            "end_frame": e_frame,
            "duration": dur
        })
        print(f"Timeline: {tl_name} | Source: {src_name} | [{s_frame} .. {e_frame}] ({dur}f = {dur/60:.1f}s)")

print("\n=== MEDIA POOL VIDEO CLIPS ===")
video_clips = [c for c in data["clips"] if c["file_path"].endswith(".mp4")]
print(f"Total video clips: {len(video_clips)}")

untouched = []
touched = []
for c in video_clips:
    c_name = c["name"]
    if c_name in existing_intervals:
        touched.append((c_name, c["unique_id"], len(existing_intervals[c_name]), c["frames"]))
    else:
        untouched.append((c_name, c["unique_id"], c["frames"]))

print(f"\nTouched files ({len(touched)}):")
for name, uid, count, frames in touched:
    print(f"  - {name}: {count} timelines, frames: {frames}, id: {uid}")

print(f"\nUntouched files ({len(untouched)}):")
for idx, (name, uid, frames) in enumerate(untouched, 1):
    print(f"  {idx:02d}. {name}: frames: {frames}, id: {uid}")

with open("scratch/untouched_and_touched_inventory.json", "w", encoding="utf-8") as f:
    json.dump({
        "existing_intervals": existing_intervals,
        "touched": touched,
        "untouched": untouched
    }, f, indent=2, ensure_ascii=False)
