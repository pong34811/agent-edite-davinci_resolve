import os
import sys
import json
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# 1. Load files
with open(r".agents/teamwork/explorer_survey_r4_3/highlight_titles_catalog.json", "r", encoding="utf-8") as f:
    titles_data = json.load(f)

with open(r"scratch/untouched_audio_peaks.json", "r", encoding="utf-8") as f:
    untouched_peaks = json.load(f)

with open(r"scratch/untouched_and_touched_inventory.json", "r", encoding="utf-8") as f:
    inventory = json.load(f)

with open(r".agents/teamwork/explorer_survey_r3_3/peaks.json", "r", encoding="utf-8") as f:
    r3_peaks = json.load(f)

existing_intervals = inventory["existing_intervals"]
primary_60 = titles_data["primary_60_titles"]
file_mapping = {x["filename"]: x for x in titles_data["file_mapping"]}

print(f"Loaded {len(primary_60)} primary titles.")

# Check mapping
for item in primary_60:
    fn = item["file"]
    if fn not in file_mapping:
        print(f"Error: {fn} not in file mapping!")

print("All filenames match file mapping.")
