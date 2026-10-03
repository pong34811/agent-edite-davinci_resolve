import json
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open("scratch/round4_60_candidates_complete.json", "r", encoding="utf-8") as f:
    cands = json.load(f)

with open("scratch/untouched_and_touched_inventory.json", "r", encoding="utf-8") as f:
    inv = json.load(f)

existing = inv["existing_intervals"]
untouched_list = [x[0] for x in inv["untouched"]]

print(f"Total candidates: {len(cands)}")
assert len(cands) == 60, "Candidate count must be exactly 60"

NAMING_REGEX = re.compile(r"^([\u0E00-\u0E7F]+)_([A-Za-z0-9]+)-vdo$")

untouched_counts = {fn: 0 for fn in untouched_list}
processed_counts = {}

# Check each candidate
all_titles = set()
for c in cands:
    cid = c["id"]
    title = c["title"]
    fn = c["source_file"]
    s_f = c["start_frame"]
    e_f = c["end_frame"]
    dur_f = c["duration_frames"]
    dur_s = c["duration_sec"]
    
    # 1. Title format
    m = NAMING_REGEX.match(title)
    if not m:
        print(f"ERROR: Invalid title format: {title}")
        sys.exit(1)
    thai_part, game_part = m.groups()
    if re.search(r"[a-zA-Z]", thai_part):
        print(f"ERROR: English letter in Thai part: {title}")
        sys.exit(1)
    if title in all_titles:
        print(f"ERROR: Duplicate title: {title}")
        sys.exit(1)
    all_titles.add(title)
    
    # 2. Duration check
    if dur_f != 3300 or dur_s != 55.0:
        print(f"ERROR: Duration not 55.0s/3300f: {title} ({dur_s}s, {dur_f}f)")
        sys.exit(1)
        
    # 3. Check against existing timelines
    if fn in existing:
        for ex in existing[fn]:
            ex_s = ex["start_frame"]
            ex_e = ex["end_frame"]
            if not (e_f <= ex_s or s_f >= ex_e):
                print(f"ERROR: Overlap with existing timeline {ex['timeline']} in {fn}: cand [{s_f}..{e_f}] vs exist [{ex_s}..{ex_e}]")
                sys.exit(1)
                
    # Count coverage
    if fn in untouched_counts:
        untouched_counts[fn] += 1
    else:
        processed_counts[fn] = processed_counts.get(fn, 0) + 1

# 4. Check same-file overlap among 60 candidates
for i in range(len(cands)):
    for j in range(i + 1, len(cands)):
        c1 = cands[i]
        c2 = cands[j]
        if c1["source_file"] == c2["source_file"]:
            if not (c1["end_frame"] <= c2["start_frame"] or c1["start_frame"] >= c2["end_frame"]):
                print(f"ERROR: Same-file candidate overlap between #{c1['id']} and #{c2['id']} in {c1['source_file']}")
                sys.exit(1)

print("\n--- COVERAGE SUMMARY ---")
print(f"Untouched files covered: {len(untouched_counts)}/25")
for fn, count in untouched_counts.items():
    print(f"  - {fn[:40]}...: {count} clips")
    assert count >= 2, f"Untouched file {fn} has less than 2 clips!"

print(f"\nProcessed files extra clips: {sum(processed_counts.values())}")
for fn, count in processed_counts.items():
    print(f"  - {fn[:40]}...: {count} clips")

print("\n>>> ALL 60 HIGHLIGHT CANDIDATES FULLY VERIFIED! ZERO OVERLAPS, STRICT THAI NAMING, 100% UNTOUCHED COVERAGE! <<<")
