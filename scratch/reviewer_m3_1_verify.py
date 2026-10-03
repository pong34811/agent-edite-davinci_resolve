import os
import sys
import re
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

os.environ['RESOLVE_SCRIPT_LIB'] = r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
sys.path.append(r'C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\lib\modules')

import DaVinciResolveScript as dvr

EXPECTED_PRIOR_TIMELINES = [
    "Highlight_Gaming_REPO_Jumpscare",
    "Highlight_Gaming_Climbing_Clutch",
    "Highlight_Gaming_Ib_Horror",
    "Highlight_Fun_DnD_Bard",
    "Highlight_Meme_GarticPhone_Art",
    "Highlight_Meme_FreeTalk_Tiger",
    "Highlight_Fun_Overcooked_KitchenFire"
]

EXPECTED_CANDIDATES = [
    {
        "index": 1,
        "name": "วิ่งหนีปีศาจแทบไม่ทัน_REPO-vdo",
        "clip_id": "4462a5cf-dad7-4499-ab4d-20a999ba2b59",
        "source_file": "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4",
        "game_tag": "REPO",
        "start_frame": 275280,
        "end_frame": 278580,
        "expected_duration": 3300
    },
    {
        "index": 2,
        "name": "จังหวะเอาชีวิตรอดเฉียดฉิว_REPO-vdo",
        "clip_id": "4462a5cf-dad7-4499-ab4d-20a999ba2b59",
        "source_file": "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4",
        "game_tag": "REPO",
        "start_frame": 574680,
        "end_frame": 577980,
        "expected_duration": 3300
    },
    {
        "index": 3,
        "name": "เปิดตี้แจกความฮากับเพื่อน_REPO-vdo",
        "clip_id": "4462a5cf-dad7-4499-ab4d-20a999ba2b59",
        "source_file": "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4",
        "game_tag": "REPO",
        "start_frame": 21000,
        "end_frame": 24300,
        "expected_duration": 3300
    },
    {
        "index": 4,
        "name": "เหลือสองชีวิตเกาะหน้าผาไว้_Climbing-vdo",
        "clip_id": "3ebbdd92-9aa6-4738-b586-956bf85f35d6",
        "source_file": "ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4",
        "game_tag": "Climbing",
        "start_frame": 257760,
        "end_frame": 261060,
        "expected_duration": 3300
    },
    {
        "index": 5,
        "name": "จังหวะกระโดดข้ามหุบเหวสุดเสียว_Climbing-vdo",
        "clip_id": "3ebbdd92-9aa6-4738-b586-956bf85f35d6",
        "source_file": "ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4",
        "game_tag": "Climbing",
        "start_frame": 301200,
        "end_frame": 304500,
        "expected_duration": 3300
    },
    {
        "index": 6,
        "name": "แกล้งเพื่อนตั้งแต่จุดสตาร์ท_Climbing-vdo",
        "clip_id": "3ebbdd92-9aa6-4738-b586-956bf85f35d6",
        "source_file": "ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4",
        "game_tag": "Climbing",
        "start_frame": 14280,
        "end_frame": 17580,
        "expected_duration": 3300
    },
    {
        "index": 7,
        "name": "เจอตัวละครใหม่ตกใจจนร้องลั่น_Ib-vdo",
        "clip_id": "7a4e9419-b627-4b4f-87db-9a0d7af59fe2",
        "source_file": "IB - สำรวจโลกภาพวาด P1.mp4",
        "game_tag": "Ib",
        "start_frame": 249480,
        "end_frame": 252780,
        "expected_duration": 3300
    },
    {
        "index": 8,
        "name": "ประตูมิติชวนขนหัวลุก_Ib-vdo",
        "clip_id": "7a4e9419-b627-4b4f-87db-9a0d7af59fe2",
        "source_file": "IB - สำรวจโลกภาพวาด P1.mp4",
        "game_tag": "Ib",
        "start_frame": 125280,
        "end_frame": 128580,
        "expected_duration": 3300
    },
    {
        "index": 9,
        "name": "ไขปริศนาภาพวาดมรณะ_Ib-vdo",
        "clip_id": "7a4e9419-b627-4b4f-87db-9a0d7af59fe2",
        "source_file": "IB - สำรวจโลกภาพวาด P1.mp4",
        "game_tag": "Ib",
        "start_frame": 456840,
        "end_frame": 460140,
        "expected_duration": 3300
    },
    {
        "index": 10,
        "name": "เล่าวินาทีบอสแพ้แบบอนาถ_DnD-vdo",
        "clip_id": "9ae1c0ee-6b90-482e-ac71-a5aac9a6f262",
        "source_file": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4",
        "game_tag": "DnD",
        "start_frame": 262920,
        "end_frame": 266220,
        "expected_duration": 3300
    },
    {
        "index": 11,
        "name": "ฉากโรลเพลย์สุดกาวในห้องน้ำ_DnD-vdo",
        "clip_id": "9ae1c0ee-6b90-482e-ac71-a5aac9a6f262",
        "source_file": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4",
        "game_tag": "DnD",
        "start_frame": 286800,
        "end_frame": 290100,
        "expected_duration": 3300
    },
    {
        "index": 12,
        "name": "ทอยเต๋าพลาดจนแผนพังยับ_DnD-vdo",
        "clip_id": "9ae1c0ee-6b90-482e-ac71-a5aac9a6f262",
        "source_file": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4",
        "game_tag": "DnD",
        "start_frame": 209400,
        "end_frame": 212700,
        "expected_duration": 3300
    },
    {
        "index": 13,
        "name": "เฉลยภาพวาดจนเพื่อนอึ้งทั้งห้อง_GarticPhone-vdo",
        "clip_id": "88c9437b-cf33-48e5-98d5-5faf4844742d",
        "source_file": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4",
        "game_tag": "GarticPhone",
        "start_frame": 157800,
        "end_frame": 161100,
        "expected_duration": 3300
    },
    {
        "index": 14,
        "name": "ลืมปิดไมค์วาดรูปไฟลนก้น_GarticPhone-vdo",
        "clip_id": "88c9437b-cf33-48e5-98d5-5faf4844742d",
        "source_file": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4",
        "game_tag": "GarticPhone",
        "start_frame": 50040,
        "end_frame": 53340,
        "expected_duration": 3300
    },
    {
        "index": 15,
        "name": "วาดรูปเพี้ยนจนกลายเป็นมีม_GarticPhone-vdo",
        "clip_id": "88c9437b-cf33-48e5-98d5-5faf4844742d",
        "source_file": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4",
        "game_tag": "GarticPhone",
        "start_frame": 134880,
        "end_frame": 138180,
        "expected_duration": 3300
    },
    {
        "index": 16,
        "name": "ตอบแชทเรื่องสู้เสือด้วยมือเปล่า_FreeTalk-vdo",
        "clip_id": "e56002ed-9d9e-4cc4-97c9-fd191a631f5e",
        "source_file": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4",
        "game_tag": "FreeTalk",
        "start_frame": 104040,
        "end_frame": 107340,
        "expected_duration": 3300
    },
    {
        "index": 17,
        "name": "จำลองเหตุการณ์ถ้าเจอเสือของจริง_FreeTalk-vdo",
        "clip_id": "e56002ed-9d9e-4cc4-97c9-fd191a631f5e",
        "source_file": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4",
        "game_tag": "FreeTalk",
        "start_frame": 116760,
        "end_frame": 120060,
        "expected_duration": 3300
    },
    {
        "index": 18,
        "name": "อ่านคอมเมนต์สุดกาวขำจนตัวโยก_FreeTalk-vdo",
        "clip_id": "e56002ed-9d9e-4cc4-97c9-fd191a631f5e",
        "source_file": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4",
        "game_tag": "FreeTalk",
        "start_frame": 91080,
        "end_frame": 94380,
        "expected_duration": 3300
    },
    {
        "index": 19,
        "name": "เปิดครัววันแรกก็วุ่นวายซะแล้ว_Overcooked-vdo",
        "clip_id": "407b877a-89c8-42b1-bc6d-71fbcd5fb6d1",
        "source_file": "เมื่อไทกะคือความชิบหายในครัว!.mp4",
        "game_tag": "Overcooked",
        "start_frame": 25800,
        "end_frame": 29100,
        "expected_duration": 3300
    },
    {
        "index": 20,
        "name": "ออเดอร์ล้นครัวสั่งความวิกฤต_Overcooked-vdo",
        "clip_id": "407b877a-89c8-42b1-bc6d-71fbcd5fb6d1",
        "source_file": "เมื่อไทกะคือความชิบหายในครัว!.mp4",
        "game_tag": "Overcooked",
        "start_frame": 231000,
        "end_frame": 234300,
        "expected_duration": 3300
    },
    {
        "index": 21,
        "name": "จานตกน้ำหมดครัวนาทีสุดท้าย_Overcooked-vdo",
        "clip_id": "407b877a-89c8-42b1-bc6d-71fbcd5fb6d1",
        "source_file": "เมื่อไทกะคือความชิบหายในครัว!.mp4",
        "game_tag": "Overcooked",
        "start_frame": 541800,
        "end_frame": 545100,
        "expected_duration": 3300
    }
]

PRIOR_CLIPS_INTERVALS = {
    "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4": {"name": "Highlight_Gaming_REPO_Jumpscare", "start": 403200, "end": 407100},
    "ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4": {"name": "Highlight_Gaming_Climbing_Clutch", "start": 351300, "end": 354900},
    "IB - สำรวจโลกภาพวาด P1.mp4": {"name": "Highlight_Gaming_Ib_Horror", "start": 268500, "end": 271800},
    "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4": {"name": "Highlight_Fun_DnD_Bard", "start": 58800, "end": 62100},
    "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4": {"name": "Highlight_Meme_GarticPhone_Art", "start": 150600, "end": 154500},
    "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4": {"name": "Highlight_Meme_FreeTalk_Tiger", "start": 134100, "end": 137700},
    "เมื่อไทกะคือความชิบหายในครัว!.mp4": {"name": "Highlight_Fun_Overcooked_KitchenFire", "start": 458400, "end": 462300}
}

def run_adversarial_review():
    report = {
        "connected": False,
        "project_name": None,
        "fps": None,
        "timeline_count": 0,
        "prior_timelines_found": [],
        "prior_timelines_missing": [],
        "new_timelines_found": [],
        "new_timelines_missing": [],
        "naming_checks": [],
        "duration_checks": [],
        "track_item_checks": [],
        "overlap_checks": [],
        "media_pool_checks": [],
        "non_destructive_storage": {},
        "failures": [],
        "warnings": []
    }

    resolve = dvr.scriptapp('Resolve')
    if not resolve:
        report["failures"].append("Cannot connect to DaVinci Resolve")
        return report
    
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    if not project:
        report["failures"].append("No active project in DaVinci Resolve")
        return report

    report["connected"] = True
    proj_name = project.GetName()
    report["project_name"] = proj_name
    fps_val = project.GetSetting("timelineFrameRate")
    report["fps"] = float(fps_val)
    total_tl_count = project.GetTimelineCount()
    report["timeline_count"] = total_tl_count

    print(f"Connected to project: {proj_name}, FPS: {report['fps']}, Total timelines: {total_tl_count}")

    if proj_name != "tygarina_2026-09-30":
        report["failures"].append(f"Unexpected project name '{proj_name}' (expected 'tygarina_2026-09-30')")
    if report["fps"] != 60.0:
        report["failures"].append(f"Unexpected FPS {report['fps']} (expected 60.0)")
    if total_tl_count != 28:
        report["failures"].append(f"Unexpected timeline count {total_tl_count} (expected 28)")

    # Read all timelines
    timelines_by_name = {}
    for idx in range(1, total_tl_count + 1):
        tl = project.GetTimelineByIndex(idx)
        timelines_by_name[tl.GetName()] = tl

    # 1. Prior timelines check
    for p_name in EXPECTED_PRIOR_TIMELINES:
        if p_name in timelines_by_name:
            report["prior_timelines_found"].append(p_name)
        else:
            report["prior_timelines_missing"].append(p_name)
            report["failures"].append(f"Prior timeline '{p_name}' missing!")

    # 2. Strict Naming Regex: ^([^\x00-\x7F]+)_([A-Za-z0-9]+)-vdo$
    strict_regex = re.compile(r"^([^\x00-\x7F]+)_([A-Za-z0-9]+)-vdo$")

    # 3. Check each candidate timeline
    file_to_candidates = {}
    for c in EXPECTED_CANDIDATES:
        c_name = c["name"]
        src_file = c["source_file"]
        if src_file not in file_to_candidates:
            file_to_candidates[src_file] = []
        file_to_candidates[src_file].append(c)

        if c_name not in timelines_by_name:
            report["new_timelines_missing"].append(c_name)
            report["failures"].append(f"Candidate timeline '{c_name}' not found!")
            continue

        report["new_timelines_found"].append(c_name)
        tl = timelines_by_name[c_name]

        # Naming check
        match = strict_regex.match(c_name)
        naming_issue = None
        if not match:
            naming_issue = f"Name '{c_name}' does not match strict regex ^([^\\x00-\\x7F]+)_([A-Za-z0-9]+)-vdo$"
            report["failures"].append(naming_issue)
        else:
            thai_part, game_part = match.groups()
            # Double check for ANY ascii character in thai part
            ascii_in_thai = [ch for ch in thai_part if ord(ch) <= 127]
            if ascii_in_thai:
                naming_issue = f"ASCII characters {ascii_in_thai} found in Thai portion of '{c_name}'"
                report["failures"].append(naming_issue)
            # Check game tag matches candidate
            if game_part != c["game_tag"]:
                naming_issue = f"Game tag '{game_part}' does not match expected '{c['game_tag']}'"
                report["failures"].append(naming_issue)

        report["naming_checks"].append({
            "name": c_name,
            "passed": naming_issue is None,
            "issue": naming_issue
        })

        # Duration check
        start_frame = tl.GetStartFrame()
        end_frame = tl.GetEndFrame()
        tl_dur_frames = end_frame - start_frame
        tl_dur_secs = tl_dur_frames / 60.0

        dur_issue = None
        if tl_dur_frames != c["expected_duration"]:
            dur_issue = f"Duration {tl_dur_frames} frames != expected {c['expected_duration']}"
            report["failures"].append(f"{c_name}: {dur_issue}")
        if not (30.0 <= tl_dur_secs <= 180.0):
            dur_issue = f"Duration {tl_dur_secs:.2f}s outside required 30s-180s range"
            report["failures"].append(f"{c_name}: {dur_issue}")

        report["duration_checks"].append({
            "name": c_name,
            "start_frame": start_frame,
            "end_frame": end_frame,
            "duration_frames": tl_dur_frames,
            "duration_seconds": tl_dur_secs,
            "passed": dur_issue is None,
            "issue": dur_issue
        })

        # Track item & Source checks
        v_items = tl.GetItemListInTrack("video", 1)
        a_items = tl.GetItemListInTrack("audio", 1)

        item_issue = None
        if not v_items or len(v_items) == 0:
            item_issue = "No video item on Video Track 1"
            report["failures"].append(f"{c_name}: {item_issue}")
        else:
            v_item = v_items[0]
            v_dur = v_item.GetDuration()
            src_start = v_item.GetSourceStartFrame()
            src_end = v_item.GetSourceEndFrame()
            
            if v_dur != c["expected_duration"]:
                item_issue = f"Video item duration {v_dur} != expected {c['expected_duration']}"
                report["failures"].append(f"{c_name}: {item_issue}")
            if src_start != c["start_frame"]:
                item_issue = f"Source start {src_start} != expected {c['start_frame']}"
                report["failures"].append(f"{c_name}: {item_issue}")
            if src_end != c["end_frame"]:
                item_issue = f"Source end {src_end} != expected {c['end_frame']}"
                report["failures"].append(f"{c_name}: {item_issue}")
            if (src_end - src_start) != c["expected_duration"]:
                item_issue = f"Source frame delta ({src_end - src_start}) != {c['expected_duration']}"
                report["failures"].append(f"{c_name}: {item_issue}")

            mpi = v_item.GetMediaPoolItem()
            mpi_path = ""
            mpi_name = ""
            if mpi:
                props = mpi.GetClipProperty()
                mpi_name = props.get("Clip Name", "")
                mpi_path = props.get("File Path", "")
                if not os.path.exists(mpi_path):
                    report["failures"].append(f"{c_name}: Source file offline at {mpi_path}")
            else:
                report["warnings"].append(f"{c_name}: GetMediaPoolItem returned None")

            report["track_item_checks"].append({
                "name": c_name,
                "video_item_duration": v_dur,
                "source_start": src_start,
                "source_end": src_end,
                "media_pool_name": mpi_name,
                "media_pool_path": mpi_path,
                "passed": item_issue is None,
                "issue": item_issue
            })

    # 4. Rigorous Non-Overlap Checks
    for src_file, c_list in file_to_candidates.items():
        prior_info = PRIOR_CLIPS_INTERVALS.get(src_file)
        intervals = []
        if prior_info:
            intervals.append({
                "label": f"Prior: {prior_info['name']}",
                "start": prior_info["start"],
                "end": prior_info["end"]
            })
        for c in c_list:
            intervals.append({
                "label": f"Cand {c['index']}: {c['name']}",
                "start": c["start_frame"],
                "end": c["end_frame"]
            })

        # Pairwise check for overlap: max(s1, s2) < min(e1, e2)
        overlaps_detected = []
        for i in range(len(intervals)):
            for j in range(i + 1, len(intervals)):
                i1 = intervals[i]
                i2 = intervals[j]
                overlap_start = max(i1["start"], i2["start"])
                overlap_end = min(i1["end"], i2["end"])
                if overlap_start < overlap_end:
                    overlap_len = overlap_end - overlap_start
                    err = f"OVERLAP DETECTED between '{i1['label']}' [{i1['start']}, {i1['end']}] and '{i2['label']}' [{i2['start']}, {i2['end']}]! Overlap length: {overlap_len} frames."
                    overlaps_detected.append(err)
                    report["failures"].append(err)

        # Sort intervals by start frame and compute gaps
        sorted_intervals = sorted(intervals, key=lambda x: x["start"])
        gaps = []
        for idx in range(len(sorted_intervals) - 1):
            gap_frames = sorted_intervals[idx+1]["start"] - sorted_intervals[idx]["end"]
            gap_secs = gap_frames / 60.0
            gaps.append({
                "between": f"{sorted_intervals[idx]['label']} and {sorted_intervals[idx+1]['label']}",
                "gap_frames": gap_frames,
                "gap_seconds": gap_secs
            })

        report["overlap_checks"].append({
            "source_file": src_file,
            "total_clips_checked": len(intervals),
            "overlaps": overlaps_detected,
            "passed": len(overlaps_detected) == 0,
            "gaps": gaps
        })

    # 5. Non-destructive file storage check
    storage_dir = r"C:\Users\warit\SynologyDrive\Tygarina\2026-09-30"
    if os.path.exists(storage_dir):
        files_on_disk = [f for f in os.listdir(storage_dir) if f.endswith(".mp4")]
        report["non_destructive_storage"]["total_mp4_files"] = len(files_on_disk)
        # Check that all 7 target source files exist
        missing_sources = [c["source_file"] for c in EXPECTED_CANDIDATES if not os.path.exists(os.path.join(storage_dir, c["source_file"]))]
        report["non_destructive_storage"]["missing_sources"] = missing_sources
        if missing_sources:
            report["failures"].append(f"Source files missing on disk: {missing_sources}")
    else:
        report["failures"].append(f"Storage dir {storage_dir} not accessible")

    return report

if __name__ == "__main__":
    rep = run_adversarial_review()
    out_path = r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\scratch\reviewer_m3_1_report.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=2)
    print("\n--- INDEPENDENT REVIEW SUMMARY ---")
    print(f"Failures count: {len(rep['failures'])}")
    if rep['failures']:
        for fl in rep['failures']:
            print(f" [FAIL] {fl}")
    else:
        print(" [PASS] ZERO failures detected across all independent checks!")
    print(f"Prior timelines: {len(rep['prior_timelines_found'])}/7 found")
    print(f"New candidate timelines: {len(rep['new_timelines_found'])}/21 found")
    print(f"Total timelines: {rep['timeline_count']}/28")
    print(f"Detailed JSON report written to: {out_path}")
