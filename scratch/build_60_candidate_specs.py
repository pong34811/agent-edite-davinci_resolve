import os
import sys
import json
import subprocess
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

torch_lib = r"C:\Users\warit\AppData\Local\Programs\Python\Python312\Lib\site-packages\torch\lib"
if os.path.exists(torch_lib):
    os.add_dll_directory(torch_lib)
    os.environ["PATH"] = torch_lib + os.pathsep + os.environ["PATH"]

from faster_whisper import WhisperModel

ffmpeg = r"C:\Users\warit\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe"
footage_dir = r"C:\Users\warit\SynologyDrive\Tygarina\2026-09-30"

# 1. Load data
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

tag_to_r3_tag = {
    "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4": "REPO",
    "ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4": "Climbing",
    "IB - สำรวจโลกภาพวาด P1.mp4": "Ib",
    "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4": "DnD",
    "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4": "GarticPhone",
    "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4": "FreeTalk",
    "เมื่อไทกะคือความชิบหายในครัว!.mp4": "Overcooked"
}

# Determine candidate intervals
candidates = []
selected_per_file = {}

def is_overlapping_any(fn, s_frame, e_frame, existing_dict, current_selected):
    # Check against 28 existing timelines
    if fn in existing_dict:
        for ex in existing_dict[fn]:
            if not (e_frame <= ex["start_frame"] or s_frame >= ex["end_frame"]):
                return True, f"Existing timeline: {ex['timeline']}"
    # Check against already selected in current run for this file
    if fn in current_selected:
        for c in current_selected[fn]:
            if not (e_frame <= c["start_frame"] or s_frame >= c["end_frame"]):
                return True, f"Same-run candidate: {c['title']}"
    return False, None

print("Assigning candidate intervals...")
for item in primary_60:
    cid = item["id"]
    fn = item["file"]
    title = item["title"]
    ctype = item["type"]
    gtag = item["game"]
    f_info = file_mapping[fn]
    mp_id = f_info["mediapool_id"]
    tot_frames = f_info["frames_60fps"]
    tot_sec = f_info["duration_sec"]
    
    if fn not in selected_per_file:
        selected_per_file[fn] = []
        
    chosen_peak = None
    if cid <= 50:
        # Untouched files: 2 clips each
        file_peaks = untouched_peaks[fn]["peaks"]
        # Find first non-overlapping peak
        for p in file_peaks:
            p_center = p["start_sec"] + 5.0
            start_sec = max(0, int(p_center - 25.0))
            duration = 55.0
            end_sec = start_sec + duration
            s_frame = int(start_sec * 60)
            e_frame = int(end_sec * 60)
            
            overlap, reason = is_overlapping_any(fn, s_frame, e_frame, existing_intervals, selected_per_file)
            if not overlap and e_frame < tot_frames:
                chosen_peak = {
                    "peak_info": p,
                    "start_sec": start_sec,
                    "end_sec": end_sec,
                    "start_frame": s_frame,
                    "end_frame": e_frame,
                    "duration": duration,
                    "duration_frames": int(duration * 60)
                }
                break
    elif 51 <= cid <= 57:
        # Processed files: find unused peak from r3_peaks
        r3_key = tag_to_r3_tag[fn]
        file_peaks = r3_peaks[r3_key]
        for p in file_peaks:
            p_center = p["start"] + 5.0
            start_sec = max(0, int(p_center - 25.0))
            duration = 55.0
            end_sec = start_sec + duration
            s_frame = int(start_sec * 60)
            e_frame = int(end_sec * 60)
            
            overlap, reason = is_overlapping_any(fn, s_frame, e_frame, existing_intervals, selected_per_file)
            if not overlap and e_frame < tot_frames:
                rms_val = p["rms"]
                peak_val = p["peak"]
                p_dict = {
                    "rms": rms_val,
                    "rms_db": 20 * np.log10(rms_val + 1e-9),
                    "peak": peak_val,
                    "peak_db": 20 * np.log10(peak_val + 1e-9),
                    "start_sec": p["start"],
                    "end_sec": p["end"]
                }
                chosen_peak = {
                    "peak_info": p_dict,
                    "start_sec": start_sec,
                    "end_sec": end_sec,
                    "start_frame": s_frame,
                    "end_frame": e_frame,
                    "duration": duration,
                    "duration_frames": int(duration * 60)
                }
                break
    else:
        # cid 58, 59, 60: 3rd peak from large untouched files
        file_peaks = untouched_peaks[fn]["peaks"]
        for p in file_peaks:
            p_center = p["start_sec"] + 5.0
            start_sec = max(0, int(p_center - 25.0))
            duration = 55.0
            end_sec = start_sec + duration
            s_frame = int(start_sec * 60)
            e_frame = int(end_sec * 60)
            
            overlap, reason = is_overlapping_any(fn, s_frame, e_frame, existing_intervals, selected_per_file)
            if not overlap and e_frame < tot_frames:
                chosen_peak = {
                    "peak_info": p,
                    "start_sec": start_sec,
                    "end_sec": end_sec,
                    "start_frame": s_frame,
                    "end_frame": e_frame,
                    "duration": duration,
                    "duration_frames": int(duration * 60)
                }
                break

    if not chosen_peak:
        print(f"FAILED to find candidate for ID {cid} ({title}) in {fn}!")
        sys.exit(1)
        
    cand_obj = {
        "id": cid,
        "title": title,
        "source_file": fn,
        "game_tag": gtag,
        "mediapool_id": mp_id,
        "type": ctype,
        "start_sec": chosen_peak["start_sec"],
        "end_sec": chosen_peak["end_sec"],
        "duration_sec": chosen_peak["duration"],
        "start_frame": chosen_peak["start_frame"],
        "end_frame": chosen_peak["end_frame"],
        "duration_frames": chosen_peak["duration_frames"],
        "peak_rms_db": round(chosen_peak["peak_info"]["rms_db"], 1),
        "peak_max_db": round(chosen_peak["peak_info"]["peak_db"], 1),
        "peak_timestamp_sec": chosen_peak["peak_info"]["start_sec"]
    }
    candidates.append(cand_obj)
    selected_per_file[fn].append(cand_obj)
    print(f"[{cid:02d}/60] {title} | {fn[:30]}... | Frame: [{cand_obj['start_frame']}..{cand_obj['end_frame']}] ({cand_obj['duration_sec']}s) | RMS: {cand_obj['peak_rms_db']} dBFS")

# Save initial candidates before transcription
with open("scratch/round4_60_candidates_pre_transcribe.json", "w", encoding="utf-8") as f:
    json.dump(candidates, f, indent=2, ensure_ascii=False)

print("\nCandidate interval assignment 100% SUCCESSFUL with 0 overlaps.")
