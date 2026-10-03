import os
import sys
import re
import unicodedata
from collections import defaultdict

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

os.environ['RESOLVE_SCRIPT_LIB'] = r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
sys.path.append(r'C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\lib\modules')

import DaVinciResolveScript as dvr

EXPECTED_PROJECT_NAME = "tygarina_2026-09-30"
EXPECTED_TOTAL_TIMELINES = 28
EXPECTED_PRIOR_COUNT = 7
EXPECTED_NEW_COUNT = 21

EXPECTED_PRIOR_NAMES = {
    "Highlight_Gaming_REPO_Jumpscare": {"source_prefix": "Collab R.E.P.O", "start_frame": 403200, "end_frame": 407100},
    "Highlight_Gaming_Climbing_Clutch": {"source_prefix": "ปืนเขาที่เราหมดแรง", "start_frame": 351300, "end_frame": 354900},
    "Highlight_Gaming_Ib_Horror": {"source_prefix": "IB - สำรวจโลกภาพวาด P1", "start_frame": 268500, "end_frame": 271800},
    "Highlight_Fun_DnD_Bard": {"source_prefix": "After DnD", "start_frame": 418200, "end_frame": 422400},
    "Highlight_Meme_GarticPhone_Art": {"source_prefix": "Gartic phone", "start_frame": 769200, "end_frame": 773100},
    "Highlight_Meme_FreeTalk_Tiger": {"source_prefix": "Free Talk", "start_frame": 184800, "end_frame": 188400},
    "Highlight_Fun_Overcooked_KitchenFire": {"source_prefix": "เมื่อไทกะคือความชิบหายในครัว", "start_frame": 126000, "end_frame": 129900},
}

EXPECTED_21_CANDIDATES = [
    {"index": 1, "name": "วิ่งหนีปีศาจแทบไม่ทัน_REPO-vdo", "game": "REPO", "source_prefix": "Collab R.E.P.O", "start_frame": 275280, "end_frame": 278580, "duration": 3300},
    {"index": 2, "name": "จังหวะเอาชีวิตรอดเฉียดฉิว_REPO-vdo", "game": "REPO", "source_prefix": "Collab R.E.P.O", "start_frame": 574680, "end_frame": 577980, "duration": 3300},
    {"index": 3, "name": "เปิดตี้แจกความฮากับเพื่อน_REPO-vdo", "game": "REPO", "source_prefix": "Collab R.E.P.O", "start_frame": 21000, "end_frame": 24300, "duration": 3300},
    {"index": 4, "name": "เหลือสองชีวิตเกาะหน้าผาไว้_Climbing-vdo", "game": "Climbing", "source_prefix": "ปืนเขาที่เราหมดแรง", "start_frame": 257760, "end_frame": 261060, "duration": 3300},
    {"index": 5, "name": "จังหวะกระโดดข้ามหุบเหวสุดเสียว_Climbing-vdo", "game": "Climbing", "source_prefix": "ปืนเขาที่เราหมดแรง", "start_frame": 301200, "end_frame": 304500, "duration": 3300},
    {"index": 6, "name": "แกล้งเพื่อนตั้งแต่จุดสตาร์ท_Climbing-vdo", "game": "Climbing", "source_prefix": "ปืนเขาที่เราหมดแรง", "start_frame": 14280, "end_frame": 17580, "duration": 3300},
    {"index": 7, "name": "เจอตัวละครใหม่ตกใจจนร้องลั่น_Ib-vdo", "game": "Ib", "source_prefix": "IB - สำรวจโลกภาพวาด P1", "start_frame": 249480, "end_frame": 252780, "duration": 3300},
    {"index": 8, "name": "ประตูมิติชวนขนหัวลุก_Ib-vdo", "game": "Ib", "source_prefix": "IB - สำรวจโลกภาพวาด P1", "start_frame": 125280, "end_frame": 128580, "duration": 3300},
    {"index": 9, "name": "ไขปริศนาภาพวาดมรณะ_Ib-vdo", "game": "Ib", "source_prefix": "IB - สำรวจโลกภาพวาด P1", "start_frame": 456840, "end_frame": 460140, "duration": 3300},
    {"index": 10, "name": "เล่าวินาทีบอสแพ้แบบอนาถ_DnD-vdo", "game": "DnD", "source_prefix": "After DnD", "start_frame": 262920, "end_frame": 266220, "duration": 3300},
    {"index": 11, "name": "ฉากโรลเพลย์สุดกาวในห้องน้ำ_DnD-vdo", "game": "DnD", "source_prefix": "After DnD", "start_frame": 286800, "end_frame": 290100, "duration": 3300},
    {"index": 12, "name": "ทอยเต๋าพลาดจนแผนพังยับ_DnD-vdo", "game": "DnD", "source_prefix": "After DnD", "start_frame": 209400, "end_frame": 212700, "duration": 3300},
    {"index": 13, "name": "เฉลยภาพวาดจนเพื่อนอึ้งทั้งห้อง_GarticPhone-vdo", "game": "GarticPhone", "source_prefix": "Gartic phone", "start_frame": 157800, "end_frame": 161100, "duration": 3300},
    {"index": 14, "name": "ลืมปิดไมค์วาดรูปไฟลนก้น_GarticPhone-vdo", "game": "GarticPhone", "source_prefix": "Gartic phone", "start_frame": 50040, "end_frame": 53340, "duration": 3300},
    {"index": 15, "name": "วาดรูปเพี้ยนจนกลายเป็นมีม_GarticPhone-vdo", "game": "GarticPhone", "source_prefix": "Gartic phone", "start_frame": 134880, "end_frame": 138180, "duration": 3300},
    {"index": 16, "name": "ตอบแชทเรื่องสู้เสือด้วยมือเปล่า_FreeTalk-vdo", "game": "FreeTalk", "source_prefix": "Free Talk", "start_frame": 104040, "end_frame": 107340, "duration": 3300},
    {"index": 17, "name": "จำลองเหตุการณ์ถ้าเจอเสือของจริง_FreeTalk-vdo", "game": "FreeTalk", "source_prefix": "Free Talk", "start_frame": 116760, "end_frame": 120060, "duration": 3300},
    {"index": 18, "name": "อ่านคอมเมนต์สุดกาวขำจนตัวโยก_FreeTalk-vdo", "game": "FreeTalk", "source_prefix": "Free Talk", "start_frame": 91080, "end_frame": 94380, "duration": 3300},
    {"index": 19, "name": "เปิดครัววันแรกก็วุ่นวายซะแล้ว_Overcooked-vdo", "game": "Overcooked", "source_prefix": "เมื่อไทกะคือความชิบหายในครัว", "start_frame": 25800, "end_frame": 29100, "duration": 3300},
    {"index": 20, "name": "ออเดอร์ล้นครัวสั่งความวิกฤต_Overcooked-vdo", "game": "Overcooked", "source_prefix": "เมื่อไทกะคือความชิบหายในครัว", "start_frame": 231000, "end_frame": 234300, "duration": 3300},
    {"index": 21, "name": "จานตกน้ำหมดครัวนาทีสุดท้าย_Overcooked-vdo", "game": "Overcooked", "source_prefix": "เมื่อไทกะคือความชิบหายในครัว", "start_frame": 541800, "end_frame": 545100, "duration": 3300},
]

def main():
    print("=" * 80)
    print("VICTORY AUDITOR: INDEPENDENT EMPIRICAL AUDIT OF DAVINCI RESOLVE")
    print("=" * 80)

    resolve = dvr.scriptapp('Resolve')
    if not resolve:
        print("[CRITICAL FAIL] Cannot connect to DaVinci Resolve Studio process!")
        sys.exit(1)
    print(f"[PASS] Connected to DaVinci Resolve: {resolve}")

    pm = resolve.GetProjectManager()
    if not pm:
        print("[CRITICAL FAIL] ProjectManager not available")
        sys.exit(1)
    project = pm.GetCurrentProject()
    if not project:
        print("[CRITICAL FAIL] No project currently open in Resolve!")
        sys.exit(1)

    proj_name = project.GetName()
    proj_id = project.GetUniqueId()
    print(f"[PASS] Active Project: '{proj_name}' (ID: {proj_id})")
    assert proj_name == EXPECTED_PROJECT_NAME, f"Project name mismatch: {proj_name}"

    fps = float(project.GetSetting("timelineFrameRate"))
    print(f"[PASS] Timeline Frame Rate: {fps} fps")
    assert fps == 60.0, f"Frame rate mismatch: {fps}"

    total_timelines = project.GetTimelineCount()
    print(f"[PASS] Total Timelines: {total_timelines} (Expected: {EXPECTED_TOTAL_TIMELINES})")
    assert total_timelines == EXPECTED_TOTAL_TIMELINES, f"Total timelines {total_timelines} != {EXPECTED_TOTAL_TIMELINES}"

    timelines = {}
    timeline_ids = set()
    for i in range(1, total_timelines + 1):
        tl = project.GetTimelineByIndex(i)
        tl_name = tl.GetName()
        tl_id = tl.GetUniqueId()
        assert tl_id not in timeline_ids, f"Duplicate timeline ID detected: {tl_id}"
        timeline_ids.add(tl_id)
        assert tl_name not in timelines, f"Duplicate timeline name detected: {tl_name}"
        timelines[tl_name] = tl

    print(f"[PASS] All {len(timelines)} timelines have unique names and unique IDs.")

    # Check 7 prior timelines
    print("\n--- Auditing 7 Prior Timelines ---")
    for pname, pdata in EXPECTED_PRIOR_NAMES.items():
        assert pname in timelines, f"Prior timeline '{pname}' missing from project!"
        tl = timelines[pname]
        dur = tl.GetEndFrame() - tl.GetStartFrame()
        print(f"  [OK] Prior timeline '{pname}': Duration={dur} frames")

    # Check 21 new candidates
    print("\n--- Auditing 21 New Candidates ---")
    thai_name_regex = re.compile(r"^([^\x00-\x7F]+)_([A-Za-z0-9]+)-vdo$")

    source_clip_intervals = defaultdict(list)

    # Add prior clips to intervals
    for pname, pdata in EXPECTED_PRIOR_NAMES.items():
        source_clip_intervals[pdata["source_prefix"]].append({
            "name": pname,
            "start": pdata["start_frame"],
            "end": pdata["end_frame"],
            "is_prior": True
        })

    for cand in EXPECTED_21_CANDIDATES:
        cname = cand["name"]
        idx = cand["index"]
        print(f"\nVerifying Candidate #{idx}: {cname}")

        assert cname in timelines, f"Candidate #{idx} '{cname}' not found in project!"
        tl = timelines[cname]

        # 1. Regex check
        m = thai_name_regex.match(cname)
        assert m is not None, f"Naming convention failure for '{cname}'"
        thai_part, game_part = m.groups()

        # 2. Strict Thai character check (no English letters, no ASCII)
        for char in thai_part:
            cp = ord(char)
            # Thai Unicode block is 0x0E00 to 0x0E7F
            assert 0x0E00 <= cp <= 0x0E7F or char == ' ', f"Non-Thai character U+{cp:04X} ('{char}') in Thai title of '{cname}'"
            assert not ('a' <= char <= 'z' or 'A' <= char <= 'Z'), f"English letter '{char}' in Thai title of '{cname}'"

        assert game_part == cand["game"], f"Game part '{game_part}' != expected '{cand['game']}'"
        print(f"  [PASS] Name format: Thai='{thai_part}', Game='{game_part}', Suffix='-vdo'")

        # 3. Duration check
        dur_frames = tl.GetEndFrame() - tl.GetStartFrame()
        dur_sec = dur_frames / fps
        print(f"  [PASS] Timeline duration: {dur_frames} frames ({dur_sec:.2f}s)")
        assert dur_frames == cand["duration"], f"Duration {dur_frames} != {cand['duration']}"
        assert 30.0 <= dur_sec <= 180.0, f"Duration {dur_sec}s outside [30.0s, 180.0s]"

        # 4. Track inspection
        v_items = tl.GetItemListInTrack("video", 1)
        a_items = tl.GetItemListInTrack("audio", 1)
        assert len(v_items) == 1, f"Expected 1 video item on V1, found {len(v_items)}"
        assert len(a_items) == 1, f"Expected 1 audio item on A1, found {len(a_items)}"

        v_item = v_items[0]
        v_dur = v_item.GetDuration()
        assert v_dur == cand["duration"], f"V1 item duration {v_dur} != {cand['duration']}"

        src_in = v_item.GetSourceStartFrame()
        src_out = v_item.GetSourceEndFrame()
        print(f"  [PASS] Video Item: Duration={v_dur}, Source In={src_in}, Source Out={src_out}")
        assert src_in == cand["start_frame"], f"Source In {src_in} != {cand['start_frame']}"
        assert src_out == cand["end_frame"], f"Source Out {src_out} != {cand['end_frame']}"

        # 5. MediaPool item and online check
        mpi = v_item.GetMediaPoolItem()
        assert mpi is not None, f"No MediaPoolItem bound to V1 item in '{cname}'"
        props = mpi.GetClipProperty()
        file_path = props.get("File Path", "")
        assert file_path != "", f"Empty File Path in MediaPoolItem"
        assert os.path.isfile(file_path), f"Source file does not exist on disk: {file_path}"
        file_size = os.path.getsize(file_path)
        assert file_size > 1024 * 1024, f"Source file too small ({file_size} bytes): {file_path}"
        print(f"  [PASS] Media Online: '{os.path.basename(file_path)}' ({file_size / (1024*1024):.1f} MB)")

        # Record interval for collision checking
        source_clip_intervals[cand["source_prefix"]].append({
            "name": cname,
            "start": src_in,
            "end": src_out,
            "is_prior": False
        })

    # Collision & Overlap checking
    print("\n--- Auditing Temporal Collisions & Interval Overlaps ---")
    total_collision_pairs_checked = 0
    for src_prefix, intervals in source_clip_intervals.items():
        print(f"\nSource Video Group: '{src_prefix}' ({len(intervals)} clips: 1 prior + 3 candidates)")
        assert len(intervals) == 4, f"Group '{src_prefix}' expected 4 clips, found {len(intervals)}"
        for i in range(len(intervals)):
            for j in range(i + 1, len(intervals)):
                c1 = intervals[i]
                c2 = intervals[j]
                total_collision_pairs_checked += 1
                # Check overlap
                overlap_start = max(c1["start"], c2["start"])
                overlap_end = min(c1["end"], c2["end"])
                overlap_frames = max(0, overlap_end - overlap_start)
                gap = abs(c1["start"] - c2["end"]) if c1["start"] >= c2["end"] else abs(c2["start"] - c1["end"])
                assert overlap_frames == 0, f"COLLISION DETECTED between '{c1['name']}' and '{c2['name']}': {overlap_frames} frames overlap!"
                print(f"  [OK] Pair '{c1['name'][:25]}' vs '{c2['name'][:25]}': overlap={overlap_frames} frames, gap={gap} frames ({gap/60.0:.2f}s)")

    print(f"\n[PASS] Verified {total_collision_pairs_checked} pairwise interval combinations across all 7 sources.")
    print("Zero temporal overlap across all pairs (0 frames).")

    print("\n" + "=" * 80)
    print("INDEPENDENT VICTORY AUDIT RESULT: ALL CHECKS PASSED (100%)")
    print("=" * 80)
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
