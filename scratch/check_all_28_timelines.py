import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\scratch\round4_survey_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total timelines: {len(data['timelines'])}")
for t in data["timelines"]:
    print(f"Index {t['index']:2d}: {t['name']}")
    print(f"   Source Clip: {t['source_clip_name']}")
    print(f"   Source Start: {t['source_start_frame']} | Source End: {t['source_end_frame']}")
    print(f"   Duration: {t['duration_frames']} frames ({t['duration_sec']:.2f}s)")
    print(f"   Timeline Start/End: [{t['start_frame']} .. {t['end_frame']}]")
    print(f"   Source UID: {t['source_clip_uid']}")
