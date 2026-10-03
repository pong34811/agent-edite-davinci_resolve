import os
import sys
import json
import re
import subprocess
from fractions import Fraction

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

PRIOR_TIMELINE_NAMES = {
    "Highlight_Gaming_REPO_Jumpscare",
    "Highlight_Gaming_Climbing_Clutch",
    "Highlight_Gaming_Ib_Horror",
    "Highlight_Fun_DnD_Bard",
    "Highlight_Meme_GarticPhone_Art",
    "Highlight_Meme_FreeTalk_Tiger",
    "Highlight_Fun_Overcooked_KitchenFire"
}

def get_ffprobe_details(filepath):
    """Run ffprobe to get exact duration and frame count."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=nb_frames,duration,r_frame_rate,avg_frame_rate,width,height",
        "-show_entries", "format=duration,size",
        "-of", "json",
        filepath
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(res.stdout)
    
    stream = data.get("streams", [{}])[0]
    format_info = data.get("format", {})
    
    # Duration
    dur_str = stream.get("duration") or format_info.get("duration")
    duration_s = float(dur_str) if dur_str else None
    
    # Frame rate
    r_fps_str = stream.get("r_frame_rate", "60/1")
    fps_val = float(Fraction(r_fps_str))
    
    # Frames
    nb_frames_str = stream.get("nb_frames")
    if nb_frames_str and nb_frames_str != "N/A":
        nb_frames = int(nb_frames_str)
    else:
        # Calculate from duration * fps
        nb_frames = int(round(duration_s * fps_val))
        
    return {
        "file_path": filepath,
        "file_name": os.path.basename(filepath),
        "duration_seconds": duration_s,
        "fps": fps_val,
        "total_frames": nb_frames,
        "width": stream.get("width"),
        "height": stream.get("height"),
        "file_size_bytes": format_info.get("size")
    }

def main():
    with open("scratch/extracted_timelines.json", "r", encoding="utf-8") as f:
        timelines = json.load(f)

    print(f"Loaded {len(timelines)} timelines from extracted JSON.")

    # 1. Catalog unique source media files and probe them
    media_files = {}
    for tl in timelines:
        p = tl["clip_path"]
        if p and p not in media_files:
            if not os.path.exists(p):
                print(f"[FATAL] Source file does not exist: {p}")
                sys.exit(1)
            info = get_ffprobe_details(p)
            media_files[p] = info
            print(f"Probed media: {info['file_name']}")
            print(f"  Duration: {info['duration_seconds']:.2f}s, Total Frames: {info['total_frames']} (FPS: {info['fps']})")

    # Group clips by source file
    grouped_by_file = {}
    for tl in timelines:
        fn = tl["file_name"]
        if fn not in grouped_by_file:
            grouped_by_file[fn] = []
        
        is_prior = tl["timeline_name"] in PRIOR_TIMELINE_NAMES
        tl["is_prior"] = is_prior
        grouped_by_file[fn].append(tl)

    print(f"\nGrouped into {len(grouped_by_file)} unique source video files.")

    # Validation tracking
    all_passed = True
    errors = []
    warnings = []

    # Distribution check: exactly 7 files, each having 1 prior + 3 candidates
    if len(grouped_by_file) != 7:
        errors.append(f"Expected exactly 7 source video files, found {len(grouped_by_file)}")

    report_data = {
        "summary": {},
        "files": []
    }

    total_prior_count = 0
    total_candidate_count = 0

    thai_name_regex = re.compile(r"^([^\x00-\x7F]+)_([A-Za-z0-9]+)-vdo$")

    print("\n" + "="*80)
    print("DETAILED PER-FILE INTERVAL COLLISION & BOUNDARY STRESS TEST")
    print("="*80)

    for fn, clips in sorted(grouped_by_file.items()):
        prior_clips = [c for c in clips if c["is_prior"]]
        candidate_clips = [c for c in clips if not c["is_prior"]]
        
        total_prior_count += len(prior_clips)
        total_candidate_count += len(candidate_clips)

        # File probe info
        sample_path = clips[0]["clip_path"]
        f_info = media_files[sample_path]
        file_max_frames = f_info["total_frames"]
        file_max_seconds = f_info["duration_seconds"]

        file_report = {
            "source_file": fn,
            "file_info": f_info,
            "prior_count": len(prior_clips),
            "candidate_count": len(candidate_clips),
            "clips": clips,
            "pairwise_tests": [],
            "boundary_tests": []
        }

        print(f"\nSource File: {fn}")
        print(f"  File Duration: {file_max_seconds:.3f}s ({file_max_frames} frames)")
        print(f"  Clips Count: Prior={len(prior_clips)}, Candidates={len(candidate_clips)} (Total={len(clips)})")

        if len(prior_clips) != 1:
            err = f"File {fn} has {len(prior_clips)} prior clips (expected exactly 1)"
            errors.append(err)
            print(f"  [FAIL] {err}")

        if len(candidate_clips) != 3:
            err = f"File {fn} has {len(candidate_clips)} candidate clips (expected exactly 3)"
            errors.append(err)
            print(f"  [FAIL] {err}")

        # Check duration and bounds for all clips in this file
        for c in clips:
            c_name = c["timeline_name"]
            sf = c["source_start_frame"]
            ef = c["source_end_frame"]
            df = ef - sf
            ds = df / 60.0
            ss = sf / 60.0
            es = ef / 60.0

            # 1. Duration bounds: [30.0s, 180.0s]
            dur_ok = (30.0 <= ds <= 180.0)
            if not dur_ok:
                err = f"Clip '{c_name}' duration {ds:.2f}s outside [30.0s, 180.0s]"
                errors.append(err)
                print(f"  [FAIL] {err}")

            # 2. Boundary limits: [0, file_max_frames]
            bounds_ok = (0 <= sf < ef <= file_max_frames)
            if not bounds_ok:
                err = f"Clip '{c_name}' bounds [{sf}, {ef}] invalid for file total {file_max_frames} frames"
                errors.append(err)
                print(f"  [FAIL] {err}")

            # 3. Naming check for candidates
            if not c["is_prior"]:
                match = thai_name_regex.match(c_name)
                if not match:
                    err = f"Candidate '{c_name}' fails naming regex"
                    errors.append(err)
                    print(f"  [FAIL] {err}")
                else:
                    thai_p, game_p = match.groups()
                    # Check if any ascii in thai part
                    if re.search(r"[A-Za-z0-9]", thai_p):
                        err = f"Candidate '{c_name}' contains ASCII in Thai part: '{thai_p}'"
                        errors.append(err)
                        print(f"  [FAIL] {err}")

            file_report["boundary_tests"].append({
                "timeline_name": c_name,
                "is_prior": c["is_prior"],
                "start_frame": sf,
                "end_frame": ef,
                "duration_frames": df,
                "start_second": ss,
                "end_second": es,
                "duration_seconds": ds,
                "duration_ok": dur_ok,
                "bounds_ok": bounds_ok
            })

        # Pairwise interval collision stress testing:
        # All pairs among the 4 clips (C(4, 2) = 6 pairs)
        print("  --- Pairwise Interval Collision Matrix ---")
        sorted_clips = sorted(clips, key=lambda x: x["source_start_frame"])
        for i in range(len(sorted_clips)):
            for j in range(i + 1, len(sorted_clips)):
                c1 = sorted_clips[i]
                c2 = sorted_clips[j]
                
                s1, e1 = c1["source_start_frame"], c1["source_end_frame"]
                s2, e2 = c2["source_start_frame"], c2["source_end_frame"]
                
                # Intersection in frames
                # Interval is [s, e)
                overlap_start = max(s1, s2)
                overlap_end = min(e1, e2)
                overlap_frames = max(0, overlap_end - overlap_start)
                overlap_seconds = overlap_frames / 60.0

                # Gap between intervals
                if s2 >= e1:
                    gap_frames = s2 - e1
                elif s1 >= e2:
                    gap_frames = s1 - e2
                else:
                    gap_frames = 0
                gap_seconds = gap_frames / 60.0

                pair_type = ""
                if c1["is_prior"] or c2["is_prior"]:
                    pair_type = "CANDIDATE vs PRIOR"
                else:
                    pair_type = "CANDIDATE vs CANDIDATE"

                collision_passed = (overlap_frames == 0)
                if not collision_passed:
                    err = f"COLLISION DETECTED in file '{fn}' between '{c1['timeline_name']}' and '{c2['timeline_name']}': overlap {overlap_frames} frames ({overlap_seconds:.2f}s)"
                    errors.append(err)
                    print(f"  [COLLISION CRITICAL] {err}")
                else:
                    status_str = f"PASS (overlap=0 frames / 0.0s, gap={gap_frames} frames / {gap_seconds:.2f}s)"
                    print(f"    [{pair_type}] '{c1['timeline_name']}' vs '{c2['timeline_name']}': {status_str}")

                file_report["pairwise_tests"].append({
                    "clip1": c1["timeline_name"],
                    "clip1_prior": c1["is_prior"],
                    "clip1_interval": [s1, e1],
                    "clip2": c2["timeline_name"],
                    "clip2_prior": c2["is_prior"],
                    "clip2_interval": [s2, e2],
                    "pair_type": pair_type,
                    "overlap_frames": overlap_frames,
                    "overlap_seconds": overlap_seconds,
                    "gap_frames": gap_frames,
                    "gap_seconds": gap_seconds,
                    "collision_passed": collision_passed
                })

        report_data["files"].append(file_report)

    # Global summary
    print("\n" + "="*80)
    print("GLOBAL STRESS TEST SUMMARY")
    print("="*80)
    print(f"Total Source Video Files Evaluated: {len(grouped_by_file)}")
    print(f"Total Prior Highlight Timelines: {total_prior_count} (Expected: 7)")
    print(f"Total New Candidate Timelines: {total_candidate_count} (Expected: 21)")
    print(f"Total Timelines in Project: {total_prior_count + total_candidate_count} (Expected: 28)")
    print(f"Total Pairwise Collision Tests Evaluated: {sum(len(f['pairwise_tests']) for f in report_data['files'])}")
    print(f"Total Errors Found: {len(errors)}")

    report_data["summary"] = {
        "total_source_files": len(grouped_by_file),
        "total_prior_timelines": total_prior_count,
        "total_candidate_timelines": total_candidate_count,
        "total_timelines": total_prior_count + total_candidate_count,
        "total_pairwise_tests": sum(len(f['pairwise_tests']) for f in report_data['files']),
        "error_count": len(errors),
        "errors": errors,
        "verdict": "APPROVE" if len(errors) == 0 else "REQUEST_CHANGES"
    }

    with open("scratch/stress_test_report.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    print(f"\nFinal Verdict: {report_data['summary']['verdict']}")
    if len(errors) > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
