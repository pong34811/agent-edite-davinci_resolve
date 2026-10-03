import json
import sys

# Configure UTF-8 stdout
sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\worker_m1\baseline_30_timelines.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("Checking subtitle cues with \\ufffd...")
ufffd_count = 0
for t in data["timelines"]:
    for cue in t["subtitle_track"]["cues"]:
        if "\ufffd" in cue["text"]:
            ufffd_count += 1
            print(f"Timeline {t['timeline_index']} ({t['timeline_name']}) Cue {cue['cue_index']}: {repr(cue['text'])} timecode={cue.get('start_tc')}")

print(f"Total cues with \\ufffd: {ufffd_count}")

pilot = [t for t in data["timelines"] if "หนีฝ่าความหนาว" in t["timeline_name"]][0]
v3 = [tr for tr in pilot["video_tracks"] if tr["track_index"] == 3][0]
print("\nPilot V3 items:")
for item in v3["items"]:
    print(item)
