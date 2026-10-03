import json

with open("scratch/stress_test_report.json", "r", encoding="utf-8") as f:
    report = json.load(f)

with open("scratch/all_7_files_summary.txt", "w", encoding="utf-8") as out:
    for idx, file_data in enumerate(report["files"], 1):
        fn = file_data["source_file"]
        finfo = file_data["file_info"]
        out.write(f"\n=======================================================\n")
        out.write(f"FILE {idx}/7: {fn}\n")
        out.write(f"=======================================================\n")
        out.write(f"Total Duration: {finfo['duration_seconds']:.3f}s | Total Frames: {finfo['total_frames']} | Resolution: {finfo['width']}x{finfo['height']}\n")
        out.write("Clips in chronological order:\n")
        sorted_clips = sorted(file_data["boundary_tests"], key=lambda x: x["start_frame"])
        for c_idx, c in enumerate(sorted_clips, 1):
            ptype = "PRIOR" if c["is_prior"] else "CANDIDATE"
            out.write(f"  {c_idx}. [{ptype}] {c['timeline_name']}\n")
            out.write(f"     Frames: [{c['start_frame']:,} .. {c['end_frame']:,}] ({c['duration_frames']} frames)\n")
            out.write(f"     Seconds: [{c['start_second']:.2f}s .. {c['end_second']:.2f}s] ({c['duration_seconds']:.2f}s)\n")
            out.write(f"     Duration in [30s, 180s]: {c['duration_ok']} | Boundary in [0, {finfo['total_frames']}]: {c['bounds_ok']}\n")
            
        out.write("Pairwise Collision Checks (6 pairs):\n")
        for pt in file_data["pairwise_tests"]:
            out.write(f"  * [{pt['pair_type']}]\n")
            out.write(f"    {pt['clip1']} [{pt['clip1_interval'][0]:,}..{pt['clip1_interval'][1]:,}] vs {pt['clip2']} [{pt['clip2_interval'][0]:,}..{pt['clip2_interval'][1]:,}]\n")
            out.write(f"    Overlap: {pt['overlap_frames']} frames ({pt['overlap_seconds']}s) | Gap: {pt['gap_frames']:,} frames ({pt['gap_seconds']:.2f}s) | PASS: {pt['collision_passed']}\n")
