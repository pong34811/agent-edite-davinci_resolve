import os
import sys
import re
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Ensure DaVinci Resolve scripting environment
os.environ['RESOLVE_SCRIPT_LIB'] = r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
sys.path.append(r'C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\lib\modules')

import DaVinciResolveScript as dvr

EXPECTED_PRIOR_7 = [
    "Highlight_Gaming_REPO_Jumpscare",
    "Highlight_Gaming_Climbing_Clutch",
    "Highlight_Gaming_Ib_Horror",
    "Highlight_Fun_DnD_Bard",
    "Highlight_Meme_GarticPhone_Art",
    "Highlight_Meme_FreeTalk_Tiger",
    "Highlight_Fun_Overcooked_KitchenFire"
]

CANDIDATES_SPEC = [
    {
        "index": 1,
        "name": "วิ่งหนีปีศาจแทบไม่ทัน_REPO-vdo",
        "clip_id": "4462a5cf-dad7-4499-ab4d-20a999ba2b59",
        "source_file": "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4",
        "game": "REPO",
        "start_s": 4588.0,
        "end_s": 4643.0,
        "start_frame": 275280,
        "end_frame": 278580,
        "duration_frames": 3300
    },
    {
        "index": 2,
        "name": "จังหวะเอาชีวิตรอดเฉียดฉิว_REPO-vdo",
        "clip_id": "4462a5cf-dad7-4499-ab4d-20a999ba2b59",
        "source_file": "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4",
        "game": "REPO",
        "start_s": 9578.0,
        "end_s": 9633.0,
        "start_frame": 574680,
        "end_frame": 577980,
        "duration_frames": 3300
    },
    {
        "index": 3,
        "name": "เปิดตี้แจกความฮากับเพื่อน_REPO-vdo",
        "clip_id": "4462a5cf-dad7-4499-ab4d-20a999ba2b59",
        "source_file": "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4",
        "game": "REPO",
        "start_s": 350.0,
        "end_s": 405.0,
        "start_frame": 21000,
        "end_frame": 24300,
        "duration_frames": 3300
    },
    {
        "index": 4,
        "name": "เหลือสองชีวิตเกาะหน้าผาไว้_Climbing-vdo",
        "clip_id": "3ebbdd92-9aa6-4738-b586-956bf85f35d6",
        "source_file": "ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4",
        "game": "Climbing",
        "start_s": 4296.0,
        "end_s": 4351.0,
        "start_frame": 257760,
        "end_frame": 261060,
        "duration_frames": 3300
    },
    {
        "index": 5,
        "name": "จังหวะกระโดดข้ามหุบเหวสุดเสียว_Climbing-vdo",
        "clip_id": "3ebbdd92-9aa6-4738-b586-956bf85f35d6",
        "source_file": "ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4",
        "game": "Climbing",
        "start_s": 5020.0,
        "end_s": 5075.0,
        "start_frame": 301200,
        "end_frame": 304500,
        "duration_frames": 3300
    },
    {
        "index": 6,
        "name": "แกล้งเพื่อนตั้งแต่จุดสตาร์ท_Climbing-vdo",
        "clip_id": "3ebbdd92-9aa6-4738-b586-956bf85f35d6",
        "source_file": "ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4",
        "game": "Climbing",
        "start_s": 238.0,
        "end_s": 293.0,
        "start_frame": 14280,
        "end_frame": 17580,
        "duration_frames": 3300
    },
    {
        "index": 7,
        "name": "เจอตัวละครใหม่ตกใจจนร้องลั่น_Ib-vdo",
        "clip_id": "7a4e9419-b627-4b4f-87db-9a0d7af59fe2",
        "source_file": "IB - สำรวจโลกภาพวาด P1.mp4",
        "game": "Ib",
        "start_s": 4158.0,
        "end_s": 4213.0,
        "start_frame": 249480,
        "end_frame": 252780,
        "duration_frames": 3300
    },
    {
        "index": 8,
        "name": "ประตูมิติชวนขนหัวลุก_Ib-vdo",
        "clip_id": "7a4e9419-b627-4b4f-87db-9a0d7af59fe2",
        "source_file": "IB - สำรวจโลกภาพวาด P1.mp4",
        "game": "Ib",
        "start_s": 2088.0,
        "end_s": 2143.0,
        "start_frame": 125280,
        "end_frame": 128580,
        "duration_frames": 3300
    },
    {
        "index": 9,
        "name": "ไขปริศนาภาพวาดมรณะ_Ib-vdo",
        "clip_id": "7a4e9419-b627-4b4f-87db-9a0d7af59fe2",
        "source_file": "IB - สำรวจโลกภาพวาด P1.mp4",
        "game": "Ib",
        "start_s": 7614.0,
        "end_s": 7669.0,
        "start_frame": 456840,
        "end_frame": 460140,
        "duration_frames": 3300
    },
    {
        "index": 10,
        "name": "เล่าวินาทีบอสแพ้แบบอนาถ_DnD-vdo",
        "clip_id": "9ae1c0ee-6b90-482e-ac71-a5aac9a6f262",
        "source_file": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4",
        "game": "DnD",
        "start_s": 4382.0,
        "end_s": 4437.0,
        "start_frame": 262920,
        "end_frame": 266220,
        "duration_frames": 3300
    },
    {
        "index": 11,
        "name": "ฉากโรลเพลย์สุดกาวในห้องน้ำ_DnD-vdo",
        "clip_id": "9ae1c0ee-6b90-482e-ac71-a5aac9a6f262",
        "source_file": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4",
        "game": "DnD",
        "start_s": 4780.0,
        "end_s": 4835.0,
        "start_frame": 286800,
        "end_frame": 290100,
        "duration_frames": 3300
    },
    {
        "index": 12,
        "name": "ทอยเต๋าพลาดจนแผนพังยับ_DnD-vdo",
        "clip_id": "9ae1c0ee-6b90-482e-ac71-a5aac9a6f262",
        "source_file": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4",
        "game": "DnD",
        "start_s": 3490.0,
        "end_s": 3545.0,
        "start_frame": 209400,
        "end_frame": 212700,
        "duration_frames": 3300
    },
    {
        "index": 13,
        "name": "เฉลยภาพวาดจนเพื่อนอึ้งทั้งห้อง_GarticPhone-vdo",
        "clip_id": "88c9437b-cf33-48e5-98d5-5faf4844742d",
        "source_file": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4",
        "game": "GarticPhone",
        "start_s": 2630.0,
        "end_s": 2685.0,
        "start_frame": 157800,
        "end_frame": 161100,
        "duration_frames": 3300
    },
    {
        "index": 14,
        "name": "ลืมปิดไมค์วาดรูปไฟลนก้น_GarticPhone-vdo",
        "clip_id": "88c9437b-cf33-48e5-98d5-5faf4844742d",
        "source_file": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4",
        "game": "GarticPhone",
        "start_s": 834.0,
        "end_s": 889.0,
        "start_frame": 50040,
        "end_frame": 53340,
        "duration_frames": 3300
    },
    {
        "index": 15,
        "name": "วาดรูปเพี้ยนจนกลายเป็นมีม_GarticPhone-vdo",
        "clip_id": "88c9437b-cf33-48e5-98d5-5faf4844742d",
        "source_file": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4",
        "game": "GarticPhone",
        "start_s": 2248.0,
        "end_s": 2303.0,
        "start_frame": 134880,
        "end_frame": 138180,
        "duration_frames": 3300
    },
    {
        "index": 16,
        "name": "ตอบแชทเรื่องสู้เสือด้วยมือเปล่า_FreeTalk-vdo",
        "clip_id": "e56002ed-9d9e-4cc4-97c9-fd191a631f5e",
        "source_file": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4",
        "game": "FreeTalk",
        "start_s": 1734.0,
        "end_s": 1789.0,
        "start_frame": 104040,
        "end_frame": 107340,
        "duration_frames": 3300
    },
    {
        "index": 17,
        "name": "จำลองเหตุการณ์ถ้าเจอเสือของจริง_FreeTalk-vdo",
        "clip_id": "e56002ed-9d9e-4cc4-97c9-fd191a631f5e",
        "source_file": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4",
        "game": "FreeTalk",
        "start_s": 1946.0,
        "end_s": 2001.0,
        "start_frame": 116760,
        "end_frame": 120060,
        "duration_frames": 3300
    },
    {
        "index": 18,
        "name": "อ่านคอมเมนต์สุดกาวขำจนตัวโยก_FreeTalk-vdo",
        "clip_id": "e56002ed-9d9e-4cc4-97c9-fd191a631f5e",
        "source_file": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4",
        "game": "FreeTalk",
        "start_s": 1518.0,
        "end_s": 1573.0,
        "start_frame": 91080,
        "end_frame": 94380,
        "duration_frames": 3300
    },
    {
        "index": 19,
        "name": "เปิดครัววันแรกก็วุ่นวายซะแล้ว_Overcooked-vdo",
        "clip_id": "407b877a-89c8-42b1-bc6d-71fbcd5fb6d1",
        "source_file": "เมื่อไทกะคือความชิบหายในครัว!.mp4",
        "game": "Overcooked",
        "start_s": 430.0,
        "end_s": 485.0,
        "start_frame": 25800,
        "end_frame": 29100,
        "duration_frames": 3300
    },
    {
        "index": 20,
        "name": "ออเดอร์ล้นครัวสั่งความวิกฤต_Overcooked-vdo",
        "clip_id": "407b877a-89c8-42b1-bc6d-71fbcd5fb6d1",
        "source_file": "เมื่อไทกะคือความชิบหายในครัว!.mp4",
        "game": "Overcooked",
        "start_s": 3850.0,
        "end_s": 3905.0,
        "start_frame": 231000,
        "end_frame": 234300,
        "duration_frames": 3300
    },
    {
        "index": 21,
        "name": "จานตกน้ำหมดครัวนาทีสุดท้าย_Overcooked-vdo",
        "clip_id": "407b877a-89c8-42b1-bc6d-71fbcd5fb6d1",
        "source_file": "เมื่อไทกะคือความชิบหายในครัว!.mp4",
        "game": "Overcooked",
        "start_s": 9030.0,
        "end_s": 9085.0,
        "start_frame": 541800,
        "end_frame": 545100,
        "duration_frames": 3300
    }
]

def is_strictly_thai(text):
    # Unicode range for Thai is \u0E00-\u0E7F
    # Check if every character in text is in this range
    for ch in text:
        code = ord(ch)
        if not (0x0E00 <= code <= 0x0E7F):
            return False, f"Character '{ch}' (U+{code:04X}) is not in Thai Unicode block (0E00-0E7F)"
    return True, "Strictly Thai"

def run_independent_audit():
    results = {
        "verdict": "APPROVE",
        "checks": {},
        "findings": []
    }
    
    # 1. Connect
    resolve = dvr.scriptapp('Resolve')
    if not resolve:
        results["verdict"] = "REQUEST_CHANGES"
        results["findings"].append({"severity": "Critical", "title": "Connection Failure", "detail": "Could not connect to DaVinci Resolve Studio."})
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return results

    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    if not project:
        results["verdict"] = "REQUEST_CHANGES"
        results["findings"].append({"severity": "Critical", "title": "No Active Project", "detail": "No active project found in Resolve."})
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return results

    proj_name = project.GetName()
    results["checks"]["project_name"] = proj_name
    if proj_name != "tygarina_2026-09-30":
        results["verdict"] = "REQUEST_CHANGES"
        results["findings"].append({"severity": "Critical", "title": "Project Name Mismatch", "detail": f"Expected 'tygarina_2026-09-30', got '{proj_name}'"})

    fps = project.GetSetting("timelineFrameRate")
    results["checks"]["timelineFrameRate"] = fps
    if float(fps) != 60.0:
        results["verdict"] = "REQUEST_CHANGES"
        results["findings"].append({"severity": "Critical", "title": "Frame Rate Mismatch", "detail": f"Expected 60.0 fps, got '{fps}'"})

    tl_count = project.GetTimelineCount()
    results["checks"]["timeline_count"] = tl_count
    if tl_count != 28:
        results["verdict"] = "REQUEST_CHANGES"
        results["findings"].append({"severity": "Critical", "title": "Timeline Count Mismatch", "detail": f"Expected 28 timelines, got {tl_count}"})

    timelines = {}
    for i in range(1, tl_count + 1):
        tl = project.GetTimelineByIndex(i)
        timelines[tl.GetName()] = tl

    results["checks"]["all_timeline_names"] = list(timelines.keys())

    # Check 7 prior timelines
    prior_missing = []
    for p_name in EXPECTED_PRIOR_7:
        if p_name not in timelines:
            prior_missing.append(p_name)
    results["checks"]["prior_7_missing"] = prior_missing
    if prior_missing:
        results["verdict"] = "REQUEST_CHANGES"
        results["findings"].append({"severity": "Critical", "title": "Prior Timeline Missing", "detail": f"Missing prior timelines: {prior_missing}"})

    # Check 21 new timelines
    strict_thai_regex = re.compile(r"^([\u0E00-\u0E7F]+)_([A-Za-z0-9]+)-vdo$")
    
    verified_candidates = []
    for cand in CANDIDATES_SPEC:
        c_idx = cand["index"]
        c_name = cand["name"]
        cand_log = {"index": c_idx, "name": c_name, "issues": []}
        
        if c_name not in timelines:
            cand_log["issues"].append(f"Timeline '{c_name}' not found in project")
            results["findings"].append({"severity": "Critical", "title": f"Candidate {c_idx} Missing", "detail": f"Timeline '{c_name}' not found in Resolve"})
            verified_candidates.append(cand_log)
            continue
            
        tl = timelines[c_name]
        
        # Strict linguistic check
        match = strict_thai_regex.match(c_name)
        if not match:
            cand_log["issues"].append(f"Timeline name '{c_name}' failed strict Thai Unicode regex")
            results["findings"].append({"severity": "Major", "title": f"Candidate {c_idx} Naming Issue", "detail": f"Name '{c_name}' does not match strictly Thai-only prefix format"})
        else:
            thai_part, game_part = match.groups()
            is_thai, reason = is_strictly_thai(thai_part)
            if not is_thai:
                cand_log["issues"].append(f"Thai prefix '{thai_part}' contains non-Thai character: {reason}")
                results["findings"].append({"severity": "Major", "title": f"Candidate {c_idx} Non-Thai Char", "detail": reason})
            if game_part != cand["game"]:
                cand_log["issues"].append(f"Game part '{game_part}' != expected '{cand['game']}'")
                results["findings"].append({"severity": "Major", "title": f"Candidate {c_idx} Game Tag Mismatch", "detail": f"Game part '{game_part}' != expected '{cand['game']}'"})
                
        # Timeline duration & frame boundaries
        start_frame = tl.GetStartFrame()
        end_frame = tl.GetEndFrame()
        tl_duration = end_frame - start_frame
        duration_s = tl_duration / float(fps)
        cand_log["tl_start_frame"] = start_frame
        cand_log["tl_end_frame"] = end_frame
        cand_log["tl_duration"] = tl_duration
        cand_log["tl_duration_s"] = duration_s
        
        if tl_duration != cand["duration_frames"]:
            cand_log["issues"].append(f"Timeline duration {tl_duration} != expected {cand['duration_frames']}")
            results["findings"].append({"severity": "Critical", "title": f"Candidate {c_idx} Duration Mismatch", "detail": f"Duration {tl_duration} != {cand['duration_frames']}"})
            
        if not (30.0 <= duration_s <= 180.0):
            cand_log["issues"].append(f"Timeline duration {duration_s}s outside 30s-180s constraint")
            results["findings"].append({"severity": "Critical", "title": f"Candidate {c_idx} Duration Constraint Violated", "detail": f"{duration_s}s not in [30s, 180s]"})

        # Track analysis
        track_types = ["video", "audio"]
        for t_type in track_types:
            track_count = tl.GetTrackCount(t_type)
            cand_log[f"{t_type}_track_count"] = track_count
            if track_count < 1:
                cand_log["issues"].append(f"Missing {t_type} track 1")
                results["findings"].append({"severity": "Critical", "title": f"Candidate {c_idx} No {t_type.capitalize()} Track", "detail": f"No {t_type} tracks on timeline"})
            else:
                items = tl.GetItemListInTrack(t_type, 1) or []
                cand_log[f"{t_type}_item_count"] = len(items)
                if len(items) != 1:
                    cand_log["issues"].append(f"Expected exactly 1 {t_type} item on track 1, found {len(items)}")
                    results["findings"].append({"severity": "Major", "title": f"Candidate {c_idx} Item Count Unexpected", "detail": f"{len(items)} items on {t_type} 1"})
                else:
                    item = items[0]
                    cand_log[f"{t_type}_item_duration"] = item.GetDuration()
                    cand_log[f"{t_type}_src_start"] = item.GetSourceStartFrame()
                    cand_log[f"{t_type}_src_end"] = item.GetSourceEndFrame()
                    
                    if item.GetDuration() != cand["duration_frames"]:
                        cand_log["issues"].append(f"{t_type} item duration {item.GetDuration()} != {cand['duration_frames']}")
                    if item.GetSourceStartFrame() != cand["start_frame"]:
                        cand_log["issues"].append(f"{t_type} src start {item.GetSourceStartFrame()} != expected {cand['start_frame']}")
                        results["findings"].append({"severity": "Critical", "title": f"Candidate {c_idx} {t_type} Start Mismatch", "detail": f"Source start {item.GetSourceStartFrame()} != {cand['start_frame']}"})
                    if item.GetSourceEndFrame() != cand["end_frame"]:
                        cand_log["issues"].append(f"{t_type} src end {item.GetSourceEndFrame()} != expected {cand['end_frame']}")
                        results["findings"].append({"severity": "Critical", "title": f"Candidate {c_idx} {t_type} End Mismatch", "detail": f"Source end {item.GetSourceEndFrame()} != {cand['end_frame']}"})
                        
                    # MediaPoolItem inspection
                    mpi = item.GetMediaPoolItem()
                    if not mpi:
                        cand_log["issues"].append(f"No MediaPoolItem associated with {t_type} item")
                        results["findings"].append({"severity": "Critical", "title": f"Candidate {c_idx} Missing MPI", "detail": f"No MediaPoolItem for {t_type} item"})
                    else:
                        clip_props = mpi.GetClipProperty()
                        clip_name = clip_props.get("Clip Name", "")
                        file_path = clip_props.get("File Path", "")
                        cand_log[f"{t_type}_clip_name"] = clip_name
                        cand_log[f"{t_type}_file_path"] = file_path
                        
                        # Verify file exists on disk and is non-empty
                        if not os.path.exists(file_path):
                            cand_log["issues"].append(f"Source file missing on disk: {file_path}")
                            results["findings"].append({"severity": "Critical", "title": f"Candidate {c_idx} Media Offline", "detail": f"File does not exist: {file_path}"})
                        elif os.path.getsize(file_path) == 0:
                            cand_log["issues"].append(f"Source file empty: {file_path}")
                            results["findings"].append({"severity": "Critical", "title": f"Candidate {c_idx} Empty Media File", "detail": f"File size 0: {file_path}"})
                            
                        # Verify clip source matches expected file
                        if os.path.basename(file_path) != cand["source_file"]:
                            cand_log["issues"].append(f"Clip file '{os.path.basename(file_path)}' != expected '{cand['source_file']}'")
                            results["findings"].append({"severity": "Critical", "title": f"Candidate {c_idx} Source File Mismatch", "detail": f"File '{os.path.basename(file_path)}' != '{cand['source_file']}'"})
                            
        verified_candidates.append(cand_log)

    results["candidates"] = verified_candidates
    
    # Check for any integrity violations
    if any(f["severity"] == "Critical" for f in results["findings"]):
        results["verdict"] = "REQUEST_CHANGES"

    # Write detailed output
    out_path = r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\reviewer_m3_2\audit_result.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print(f"Audit completed. Total findings: {len(results['findings'])}. Verdict: {results['verdict']}")
    print(f"Results written to: {out_path}")

if __name__ == "__main__":
    run_independent_audit()
