import sys
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

with open("scratch/stress_test_report.json", "r", encoding="utf-8") as f:
    report = json.load(f)

for idx, file_data in enumerate(report["files"], 1):
    fn = file_data["source_file"]
    finfo = file_data["file_info"]
    print(f"\n=======================================================")
    print(f"FILE {idx}/7: {fn}")
    print(f"=======================================================")
    print(f"Total Duration: {finfo['duration_seconds']:.3f}s | Total Frames: {finfo['total_frames']} | Resolution: {finfo['width']}x{finfo['height']}")
    print("Clips in chronological order:")
    sorted_clips = sorted(file_data["boundary_tests"], key=lambda x: x["start_frame"])
    for c_idx, c in enumerate(sorted_clips, 1):
        ptype = "PRIOR" if c["is_prior"] else "CANDIDATE"
        print(f"  {c_idx}. [{ptype}] {c['timeline_name']}")
        print(f"     Frames: [{c['start_frame']:,} .. {c['end_frame']:,}] ({c['duration_frames']} frames)")
        print(f"     Seconds: [{c['start_second']:.2f}s .. {c['end_second']:.2f}s] ({c['duration_seconds']:.2f}s)")
        print(f"     Duration in [30s, 180s]: {c['duration_ok']} | Boundary in [0, {finfo['total_frames']}]: {c['bounds_ok']}")
        
    print("Pairwise Collision Checks (6 pairs):")
    for pt in file_data["pairwise_tests"]:
        c1_type = "PRIOR" if pt['clip1_prior'] else "CANDIDATE"
        c2_type = "PRIOR" if pt['clip2_prior'] else "CANDIDATE"
        print(f"  * [{pt['pair_type']}]")
        print(f"    {pt['clip1']} [{pt['clip1_interval'][0]:,}..{pt['clip1_interval'][1]:,}] vs {pt['clip2']} [{pt['clip2_interval'][0]:,}..{pt['clip2_interval'][1]:,}]")
        print(f"    Overlap: {pt['overlap_frames']} frames ({pt['overlap_seconds']}s) | Gap: {pt['gap_frames']:,} frames ({pt['gap_seconds']:.2f}s) | PASS: {pt['collision_passed']}")
