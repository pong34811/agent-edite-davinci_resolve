import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open(r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\worker_m1\baseline_30_timelines.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"{'Idx':<4} {'FPS':<5} {'Cues':<5} {'V1':<4} {'V2':<4} {'V3':<4} {'A1':<4} {'A2':<4} {'A3':<4} {'Name'}")
print("-" * 90)
for t in data["timelines"]:
    idx = t["timeline_index"]
    name = t["timeline_name"]
    fps = t["frame_rate"]
    cues = t["subtitle_track"]["cue_count"]
    v_map = {tr["track_index"]: tr["item_count"] for tr in t["video_tracks"]}
    a_map = {tr["track_index"]: tr["item_count"] for tr in t["audio_tracks"]}
    v1 = v_map.get(1, 0)
    v2 = v_map.get(2, 0)
    v3 = v_map.get(3, 0)
    a1 = a_map.get(1, 0)
    a2 = a_map.get(2, 0)
    a3 = a_map.get(3, 0)
    print(f"{idx:<4} {fps:<5} {cues:<5} {v1:<4} {v2:<4} {v3:<4} {a1:<4} {a2:<4} {a3:<4} {name}")
