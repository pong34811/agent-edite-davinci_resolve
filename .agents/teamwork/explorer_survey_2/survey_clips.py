import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\warit\.gemini\antigravity-cli\brain\52da8985-2a6e-47a3-87f1-774e7d416c05\.system_generated\steps\52\output.txt', encoding='utf-8') as f:
    data = json.load(f)

clips = data.get('clips', [])
print(f"Total clips in Master: {len(clips)}")
for i, c in enumerate(clips):
    print(f"{i+1:2d}. {c['name']} (ID: {c['id']})")

disk_dir = r'C:\Users\warit\SynologyDrive\Tygarina\2026-09-30'
disk_files = set(os.listdir(disk_dir))
pool_names = set(c['name'] for c in clips)

print("\n--- Disk vs Pool Comparison ---")
print(f"Files on disk: {len(disk_files)}")
print(f"Clips in pool: {len(pool_names)}")

missing_in_pool = disk_files - pool_names
extra_in_pool = pool_names - disk_files
print(f"Missing in pool: {len(missing_in_pool)}")
if missing_in_pool:
    for m in missing_in_pool:
        print(f"  Missing: {m}")
print(f"Extra in pool: {len(extra_in_pool)}")
if extra_in_pool:
    for e in extra_in_pool:
        print(f"  Extra: {e}")
