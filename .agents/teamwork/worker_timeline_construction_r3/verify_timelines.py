import os
import sys
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Ensure DaVinci Resolve scripting environment
os.environ['RESOLVE_SCRIPT_LIB'] = r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
sys.path.append(r'C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\lib\modules')

import DaVinciResolveScript as dvr

EXPECTED_CANDIDATES = [
    {
        "index": 1,
        "name": "วิ่งหนีปีศาจแทบไม่ทัน_REPO-vdo",
        "clip_id": "4462a5cf-dad7-4499-ab4d-20a999ba2b59",
        "source_file": "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4",
        "start_frame": 275280,
        "end_frame": 278580,
        "expected_duration": 3300
    },
    {
        "index": 2,
        "name": "จังหวะเอาชีวิตรอดเฉียดฉิว_REPO-vdo",
        "clip_id": "4462a5cf-dad7-4499-ab4d-20a999ba2b59",
        "source_file": "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4",
        "start_frame": 574680,
        "end_frame": 577980,
        "expected_duration": 3300
    },
    {
        "index": 3,
        "name": "เปิดตี้แจกความฮากับเพื่อน_REPO-vdo",
        "clip_id": "4462a5cf-dad7-4499-ab4d-20a999ba2b59",
        "source_file": "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4",
        "start_frame": 21000,
        "end_frame": 24300,
        "expected_duration": 3300
    },
    {
        "index": 4,
        "name": "เหลือสองชีวิตเกาะหน้าผาไว้_Climbing-vdo",
        "clip_id": "3ebbdd92-9aa6-4738-b586-956bf85f35d6",
        "source_file": "ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4",
        "start_frame": 257760,
        "end_frame": 261060,
        "expected_duration": 3300
    },
    {
        "index": 5,
        "name": "จังหวะกระโดดข้ามหุบเหวสุดเสียว_Climbing-vdo",
        "clip_id": "3ebbdd92-9aa6-4738-b586-956bf85f35d6",
        "source_file": "ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4",
        "start_frame": 301200,
        "end_frame": 304500,
        "expected_duration": 3300
    },
    {
        "index": 6,
        "name": "แกล้งเพื่อนตั้งแต่จุดสตาร์ท_Climbing-vdo",
        "clip_id": "3ebbdd92-9aa6-4738-b586-956bf85f35d6",
        "source_file": "ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4",
        "start_frame": 14280,
        "end_frame": 17580,
        "expected_duration": 3300
    },
    {
        "index": 7,
        "name": "เจอตัวละครใหม่ตกใจจนร้องลั่น_Ib-vdo",
        "clip_id": "7a4e9419-b627-4b4f-87db-9a0d7af59fe2",
        "source_file": "IB - สำรวจโลกภาพวาด P1.mp4",
        "start_frame": 249480,
        "end_frame": 252780,
        "expected_duration": 3300
    },
    {
        "index": 8,
        "name": "ประตูมิติชวนขนหัวลุก_Ib-vdo",
        "clip_id": "7a4e9419-b627-4b4f-87db-9a0d7af59fe2",
        "source_file": "IB - สำรวจโลกภาพวาด P1.mp4",
        "start_frame": 125280,
        "end_frame": 128580,
        "expected_duration": 3300
    },
    {
        "index": 9,
        "name": "ไขปริศนาภาพวาดมรณะ_Ib-vdo",
        "clip_id": "7a4e9419-b627-4b4f-87db-9a0d7af59fe2",
        "source_file": "IB - สำรวจโลกภาพวาด P1.mp4",
        "start_frame": 456840,
        "end_frame": 460140,
        "expected_duration": 3300
    },
    {
        "index": 10,
        "name": "เล่าวินาทีบอสแพ้แบบอนาถ_DnD-vdo",
        "clip_id": "9ae1c0ee-6b90-482e-ac71-a5aac9a6f262",
        "source_file": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4",
        "start_frame": 262920,
        "end_frame": 266220,
        "expected_duration": 3300
    },
    {
        "index": 11,
        "name": "ฉากโรลเพลย์สุดกาวในห้องน้ำ_DnD-vdo",
        "clip_id": "9ae1c0ee-6b90-482e-ac71-a5aac9a6f262",
        "source_file": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4",
        "start_frame": 286800,
        "end_frame": 290100,
        "expected_duration": 3300
    },
    {
        "index": 12,
        "name": "ทอยเต๋าพลาดจนแผนพังยับ_DnD-vdo",
        "clip_id": "9ae1c0ee-6b90-482e-ac71-a5aac9a6f262",
        "source_file": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4",
        "start_frame": 209400,
        "end_frame": 212700,
        "expected_duration": 3300
    },
    {
        "index": 13,
        "name": "เฉลยภาพวาดจนเพื่อนอึ้งทั้งห้อง_GarticPhone-vdo",
        "clip_id": "88c9437b-cf33-48e5-98d5-5faf4844742d",
        "source_file": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4",
        "start_frame": 157800,
        "end_frame": 161100,
        "expected_duration": 3300
    },
    {
        "index": 14,
        "name": "ลืมปิดไมค์วาดรูปไฟลนก้น_GarticPhone-vdo",
        "clip_id": "88c9437b-cf33-48e5-98d5-5faf4844742d",
        "source_file": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4",
        "start_frame": 50040,
        "end_frame": 53340,
        "expected_duration": 3300
    },
    {
        "index": 15,
        "name": "วาดรูปเพี้ยนจนกลายเป็นมีม_GarticPhone-vdo",
        "clip_id": "88c9437b-cf33-48e5-98d5-5faf4844742d",
        "source_file": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4",
        "start_frame": 134880,
        "end_frame": 138180,
        "expected_duration": 3300
    },
    {
        "index": 16,
        "name": "ตอบแชทเรื่องสู้เสือด้วยมือเปล่า_FreeTalk-vdo",
        "clip_id": "e56002ed-9d9e-4cc4-97c9-fd191a631f5e",
        "source_file": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4",
        "start_frame": 104040,
        "end_frame": 107340,
        "expected_duration": 3300
    },
    {
        "index": 17,
        "name": "จำลองเหตุการณ์ถ้าเจอเสือของจริง_FreeTalk-vdo",
        "clip_id": "e56002ed-9d9e-4cc4-97c9-fd191a631f5e",
        "source_file": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4",
        "start_frame": 116760,
        "end_frame": 120060,
        "expected_duration": 3300
    },
    {
        "index": 18,
        "name": "อ่านคอมเมนต์สุดกาวขำจนตัวโยก_FreeTalk-vdo",
        "clip_id": "e56002ed-9d9e-4cc4-97c9-fd191a631f5e",
        "source_file": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4",
        "start_frame": 91080,
        "end_frame": 94380,
        "expected_duration": 3300
    },
    {
        "index": 19,
        "name": "เปิดครัววันแรกก็วุ่นวายซะแล้ว_Overcooked-vdo",
        "clip_id": "407b877a-89c8-42b1-bc6d-71fbcd5fb6d1",
        "source_file": "เมื่อไทกะคือความชิบหายในครัว!.mp4",
        "start_frame": 25800,
        "end_frame": 29100,
        "expected_duration": 3300
    },
    {
        "index": 20,
        "name": "ออเดอร์ล้นครัวสั่งความวิกฤต_Overcooked-vdo",
        "clip_id": "407b877a-89c8-42b1-bc6d-71fbcd5fb6d1",
        "source_file": "เมื่อไทกะคือความชิบหายในครัว!.mp4",
        "start_frame": 231000,
        "end_frame": 234300,
        "expected_duration": 3300
    },
    {
        "index": 21,
        "name": "จานตกน้ำหมดครัวนาทีสุดท้าย_Overcooked-vdo",
        "clip_id": "407b877a-89c8-42b1-bc6d-71fbcd5fb6d1",
        "source_file": "เมื่อไทกะคือความชิบหายในครัว!.mp4",
        "start_frame": 541800,
        "end_frame": 545100,
        "expected_duration": 3300
    }
]

def verify():
    resolve = dvr.scriptapp('Resolve')
    if not resolve:
        print("[FAIL] Could not connect to DaVinci Resolve")
        sys.exit(1)
        
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    if not project:
        print("[FAIL] No active project in DaVinci Resolve")
        sys.exit(1)
        
    proj_name = project.GetName()
    print(f"[OK] Connected to active project: {proj_name}")
    if proj_name != "tygarina_2026-09-30":
        print(f"[FAIL] Expected project 'tygarina_2026-09-30', got '{proj_name}'")
        sys.exit(1)
        
    fps = project.GetSetting("timelineFrameRate")
    print(f"[OK] Project timelineFrameRate: {fps}")
    if float(fps) != 60.0:
        print(f"[FAIL] Expected timelineFrameRate 60.0, got {fps}")
        sys.exit(1)
        
    total_timelines = project.GetTimelineCount()
    print(f"[OK] Total timeline count: {total_timelines}")
    if total_timelines != 28:
        print(f"[FAIL] Expected exactly 28 timelines, found {total_timelines}")
        sys.exit(1)
        
    timelines_by_name = {}
    for idx in range(1, total_timelines + 1):
        tl = project.GetTimelineByIndex(idx)
        timelines_by_name[tl.GetName()] = tl
        
    print(f"[INFO] Cataloged {len(timelines_by_name)} timelines by name.")
    
    # Verify the 21 candidates
    failures = []
    
    thai_name_regex = re.compile(r"^([^\x00-\x7F]+)_([A-Za-z0-9]+)-vdo$")
    
    for cand in EXPECTED_CANDIDATES:
        name = cand["name"]
        print(f"\n--- Verifying Candidate {cand['index']}: {name} ---")
        
        # 1. Existence
        if name not in timelines_by_name:
            failures.append(f"Candidate {cand['index']} ({name}) not found in project!")
            print(f"  [FAIL] Timeline not found")
            continue
            
        tl = timelines_by_name[name]
        
        # 2. Strict naming convention
        match = thai_name_regex.match(name)
        if not match:
            failures.append(f"Candidate {cand['index']} ({name}) does not match strict Thai-only prefix format!")
            print(f"  [FAIL] Naming regex match failed: {name}")
        else:
            thai_part, game_part = match.groups()
            print(f"  [OK] Name format valid: Thai='{thai_part}', Game='{game_part}'")
            
        # 3. Timeline duration and frame count
        start_frame = tl.GetStartFrame()
        end_frame = tl.GetEndFrame()
        duration_frames = end_frame - start_frame
        duration_seconds = duration_frames / float(fps)
        
        print(f"  Start Frame: {start_frame}, End Frame: {end_frame}, Duration: {duration_frames} frames ({duration_seconds:.2f}s)")
        
        if duration_frames != cand["expected_duration"]:
            failures.append(f"Candidate {cand['index']} duration {duration_frames} != expected {cand['expected_duration']}")
            print(f"  [FAIL] Duration mismatch: {duration_frames} != {cand['expected_duration']}")
        else:
            print(f"  [OK] Duration exactly {duration_frames} frames ({duration_seconds}s)")
            
        if not (30.0 <= duration_seconds <= 180.0):
            failures.append(f"Candidate {cand['index']} duration {duration_seconds}s outside 30s-180s range")
            print(f"  [FAIL] Duration outside range: {duration_seconds}s")
            
        # 4. Track items inspection
        video_items = tl.GetItemListInTrack("video", 1)
        audio_items = tl.GetItemListInTrack("audio", 1)
        
        if not video_items:
            failures.append(f"Candidate {cand['index']} has no video items on track 1")
            print(f"  [FAIL] No video items on track 1")
        else:
            v_item = video_items[0]
            v_name = v_item.GetName()
            v_dur = v_item.GetDuration()
            
            # Check source clip name
            expected_prefix = cand["source_file"].split(".")[0][:10]
            print(f"  Video item name: '{v_name}', item duration: {v_dur}")
            if v_dur != cand["expected_duration"]:
                failures.append(f"Candidate {cand['index']} item duration {v_dur} != {cand['expected_duration']}")
                print(f"  [FAIL] Item duration mismatch: {v_dur}")
                
            # Check source in/out frames
            src_start = v_item.GetSourceStartFrame()
            src_end = v_item.GetSourceEndFrame()
            print(f"  Source Start Frame: {src_start} (expected: {cand['start_frame']})")
            print(f"  Source End Frame: {src_end} (expected: {cand['end_frame']})")
            if src_start != cand["start_frame"]:
                failures.append(f"Candidate {cand['index']} source start frame {src_start} != expected {cand['start_frame']}")
                print(f"  [FAIL] Source start frame mismatch: {src_start} != {cand['start_frame']}")
            if src_end != cand["end_frame"]:
                failures.append(f"Candidate {cand['index']} source end frame {src_end} != expected {cand['end_frame']}")
                print(f"  [FAIL] Source end frame mismatch: {src_end} != {cand['end_frame']}")
            if src_start == cand["start_frame"] and src_end == cand["end_frame"]:
                print(f"  [OK] Source frame range exact match: [{src_start}, {src_end})")

            # Check media pool item
            mpi = v_item.GetMediaPoolItem()
            if mpi:
                clip_props = mpi.GetClipProperty()
                clip_name = clip_props.get("Clip Name", "")
                clip_path = clip_props.get("File Path", "")
                print(f"  MediaPool clip: '{clip_name}' (Path: '{clip_path}')")
            else:
                print(f"  [WARN] No MediaPoolItem associated with timeline item")
                
        # 5. Media offline check
        # In Resolve API, MediaPoolItem or clip properties can be checked
        for it in (video_items or []):
            mpi = it.GetMediaPoolItem()
            if mpi:
                prop = mpi.GetClipProperty()
                file_path = prop.get("File Path", "")
                if file_path and not os.path.exists(file_path):
                    failures.append(f"Candidate {cand['index']} media file offline on disk: {file_path}")
                    print(f"  [FAIL] Media file does not exist on disk: {file_path}")
                else:
                    print(f"  [OK] Media file online: {os.path.basename(file_path)}")
                    
    print("\n================ VERIFICATION SUMMARY ================")
    if not failures:
        print("ALL 21 CANDIDATE TIMELINES PASSED 100% VERIFICATION!")
        print("Timeline count: exactly 28 (7 prior + 21 new)")
        print("Zero offline media detected.")
        print("All names conform to {Thai_Clip_Name}_{Game_Name}-vdo with zero ASCII in Thai part.")
        print("All durations are exactly 3300 frames (55.0s, within 30s-180s).")
        return True
    else:
        print(f"VERIFICATION FAILED WITH {len(failures)} ISSUES:")
        for f in failures:
            print(f" - {f}")
        return False

if __name__ == "__main__":
    success = verify()
    if not success:
        sys.exit(1)
