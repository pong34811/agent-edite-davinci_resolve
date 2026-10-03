import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\scratch\round4_survey_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for p in data["processed_files"]:
    fname = p["filename"]
    matching_tls = [t for t in data["timelines"] if t["source_clip_name"] == fname or os.path.basename(t["source_file_path"]) == fname]
    matching_tls.sort(key=lambda x: x["source_start_frame"])
    print(f"\n==========================================")
    print(f"FILE: {fname}")
    print(f"Duration: {p['duration_sec']:.2f}s ({p['frames_60fps']} frames)")
    print(f"Existing Timelines ({len(matching_tls)}):")
    
    # Check pairwise overlap
    for idx, t in enumerate(matching_tls):
        print(f"  {idx+1}. [{t['source_start_frame']} .. {t['source_end_frame']}] ({t['duration_frames']}f / {t['duration_sec']:.1f}s) -> '{t['name']}'")
        
    for i in range(len(matching_tls)):
        for j in range(i + 1, len(matching_tls)):
            t1 = matching_tls[i]
            t2 = matching_tls[j]
            overlap = max(0, min(t1["source_end_frame"], t2["source_end_frame"]) - max(t1["source_start_frame"], t2["source_start_frame"]))
            assert overlap == 0, f"OVERLAP DETECTED between {t1['name']} and {t2['name']}!"
    print("  -> Overlap check: 0 frames overlap (PASS)")
