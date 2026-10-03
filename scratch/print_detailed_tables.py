import sys
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

with open("scratch/stress_test_report.json", "r", encoding="utf-8") as f:
    report = json.load(f)

print("=== ALL 7 SOURCE FILES DETAILS ===")
for file_data in report["files"]:
    fn = file_data["source_file"]
    finfo = file_data["file_info"]
    print(f"\nSource File: {fn}")
    print(f"Total Duration: {finfo['duration_seconds']:.3f}s | Total Frames: {finfo['total_frames']} | Resolution: {finfo['width']}x{finfo['height']} | Size: {int(finfo['file_size_bytes']):,} bytes")
    print("Clips in chronological order:")
    sorted_clips = sorted(file_data["boundary_tests"], key=lambda x: x["start_frame"])
    for idx, c in enumerate(sorted_clips, 1):
        ptype = "PRIOR" if c["is_prior"] else "CANDIDATE"
        print(f"  {idx}. [{ptype}] {c['timeline_name']}: Frames [{c['start_frame']:,} .. {c['end_frame']:,}] | Seconds [{c['start_second']:.2f}s .. {c['end_second']:.2f}s] | Dur: {c['duration_seconds']:.2f}s ({c['duration_frames']}f) | Bounds OK: {c['bounds_ok']}")
        
    print("Pairwise Intersection Tests (6 pairs):")
    for pt in file_data["pairwise_tests"]:
        print(f"  - [{pt['pair_type']}] '{pt['clip1']}' vs '{pt['clip2']}': Overlap = {pt['overlap_frames']}f ({pt['overlap_seconds']}s) | Gap = {pt['gap_frames']:,}f ({pt['gap_seconds']:.2f}s) | PASS: {pt['collision_passed']}")
