import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open(r".agents/teamwork/worker_m1/baseline_30_timelines.json", encoding="utf-8") as f:
    data = json.load(f)

print("Top level keys:", list(data.keys()))
print("Total timelines:", len(data["timelines"]))

# Timeline 1
tl1 = data["timelines"][0]
print("\n--- Timeline 1 ---")
print("Name:", tl1["timeline_name"])
print("ID:", tl1["timeline_id"])
print("FPS:", tl1["frame_rate"], "Resolution:", f"{tl1['resolution_width']}x{tl1['resolution_height']}")
print("Duration:", tl1["duration_frames"], "frames,", tl1["duration_tc"])
print("Subtitle count:", tl1["subtitle_track"]["cue_count"])
if tl1["subtitle_track"]["cues"]:
    print("Sample subtitle cue 1:", tl1["subtitle_track"]["cues"][0])
print("Audio tracks:", len(tl1["audio_tracks"]))
for a in tl1["audio_tracks"]:
    print(f"  A{a['track_index']}: {a['track_name']} ({a['track_type']}) items={a['item_count']}")
print("Video tracks:", len(tl1["video_tracks"]))
for v in tl1["video_tracks"]:
    adj_items = [i for i in v["items"] if i.get("is_adjustment_clip")]
    print(f"  V{v['track_index']}: {v['track_name']} items={v['item_count']} (adj={len(adj_items)})")

# Timeline 26
tl26 = [t for t in data["timelines"] if "หนีฝ่าความหนาว" in t["timeline_name"]][0]
print("\n--- Timeline 26 (Pilot timeline: หนีฝ่าความหนาว) ---")
print("Name:", tl26["timeline_name"])
print("ID:", tl26["timeline_id"])
print("FPS:", tl26["frame_rate"])
print("Duration:", tl26["duration_frames"], "frames,", tl26["duration_tc"])
print("Subtitle count:", tl26["subtitle_track"]["cue_count"])
print("First 2 subtitle cues:")
for c in tl26["subtitle_track"]["cues"][:2]:
    print(" ", c)
print("Video track 3 items (Adjustment Clips / VTuber focus):")
for it in tl26["video_tracks"][2]["items"]:
    print("  Item:", it["name"], "start:", it["start_frame"], "end:", it["end_frame"], "dur:", it["duration_frames"])
    if it.get("fusion_comp"):
        print("    Fusion tools:", [t["name"] for t in it["fusion_comp"].get("tools", [])])

# Timeline 30fps
tl30 = [t for t in data["timelines"] if t["frame_rate"] == 30.0][0]
print("\n--- 30 FPS Timeline ---")
print("Name:", tl30["timeline_name"])
print("ID:", tl30["timeline_id"])
print("FPS:", tl30["frame_rate"])
print("Duration:", tl30["duration_frames"], "frames,", tl30["duration_tc"])
print("Subtitle count:", tl30["subtitle_track"]["cue_count"])
