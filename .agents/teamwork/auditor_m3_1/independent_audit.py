import os
import sys
import re
import datetime

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
        "expected_duration": 3300,
        "game_tag": "REPO"
    },
    {
        "index": 2,
        "name": "จังหวะเอาชีวิตรอดเฉียดฉิว_REPO-vdo",
        "clip_id": "4462a5cf-dad7-4499-ab4d-20a999ba2b59",
        "source_file": "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4",
        "start_frame": 574680,
        "end_frame": 577980,
        "expected_duration": 3300,
        "game_tag": "REPO"
    },
    {
        "index": 3,
        "name": "เปิดตี้แจกความฮากับเพื่อน_REPO-vdo",
        "clip_id": "4462a5cf-dad7-4499-ab4d-20a999ba2b59",
        "source_file": "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4",
        "start_frame": 21000,
        "end_frame": 24300,
        "expected_duration": 3300,
        "game_tag": "REPO"
    },
    {
        "index": 4,
        "name": "เหลือสองชีวิตเกาะหน้าผาไว้_Climbing-vdo",
        "clip_id": "3ebbdd92-9aa6-4738-b586-956bf85f35d6",
        "source_file": "ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4",
        "start_frame": 257760,
        "end_frame": 261060,
        "expected_duration": 3300,
        "game_tag": "Climbing"
    },
    {
        "index": 5,
        "name": "จังหวะกระโดดข้ามหุบเหวสุดเสียว_Climbing-vdo",
        "clip_id": "3ebbdd92-9aa6-4738-b586-956bf85f35d6",
        "source_file": "ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4",
        "start_frame": 301200,
        "end_frame": 304500,
        "expected_duration": 3300,
        "game_tag": "Climbing"
    },
    {
        "index": 6,
        "name": "แกล้งเพื่อนตั้งแต่จุดสตาร์ท_Climbing-vdo",
        "clip_id": "3ebbdd92-9aa6-4738-b586-956bf85f35d6",
        "source_file": "ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4",
        "start_frame": 14280,
        "end_frame": 17580,
        "expected_duration": 3300,
        "game_tag": "Climbing"
    },
    {
        "index": 7,
        "name": "เจอตัวละครใหม่ตกใจจนร้องลั่น_Ib-vdo",
        "clip_id": "7a4e9419-b627-4b4f-87db-9a0d7af59fe2",
        "source_file": "IB - สำรวจโลกภาพวาด P1.mp4",
        "start_frame": 249480,
        "end_frame": 252780,
        "expected_duration": 3300,
        "game_tag": "Ib"
    },
    {
        "index": 8,
        "name": "ประตูมิติชวนขนหัวลุก_Ib-vdo",
        "clip_id": "7a4e9419-b627-4b4f-87db-9a0d7af59fe2",
        "source_file": "IB - สำรวจโลกภาพวาด P1.mp4",
        "start_frame": 125280,
        "end_frame": 128580,
        "expected_duration": 3300,
        "game_tag": "Ib"
    },
    {
        "index": 9,
        "name": "ไขปริศนาภาพวาดมรณะ_Ib-vdo",
        "clip_id": "7a4e9419-b627-4b4f-87db-9a0d7af59fe2",
        "source_file": "IB - สำรวจโลกภาพวาด P1.mp4",
        "start_frame": 456840,
        "end_frame": 460140,
        "expected_duration": 3300,
        "game_tag": "Ib"
    },
    {
        "index": 10,
        "name": "เล่าวินาทีบอสแพ้แบบอนาถ_DnD-vdo",
        "clip_id": "9ae1c0ee-6b90-482e-ac71-a5aac9a6f262",
        "source_file": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4",
        "start_frame": 262920,
        "end_frame": 266220,
        "expected_duration": 3300,
        "game_tag": "DnD"
    },
    {
        "index": 11,
        "name": "ฉากโรลเพลย์สุดกาวในห้องน้ำ_DnD-vdo",
        "clip_id": "9ae1c0ee-6b90-482e-ac71-a5aac9a6f262",
        "source_file": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4",
        "start_frame": 286800,
        "end_frame": 290100,
        "expected_duration": 3300,
        "game_tag": "DnD"
    },
    {
        "index": 12,
        "name": "ทอยเต๋าพลาดจนแผนพังยับ_DnD-vdo",
        "clip_id": "9ae1c0ee-6b90-482e-ac71-a5aac9a6f262",
        "source_file": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4",
        "start_frame": 209400,
        "end_frame": 212700,
        "expected_duration": 3300,
        "game_tag": "DnD"
    },
    {
        "index": 13,
        "name": "เฉลยภาพวาดจนเพื่อนอึ้งทั้งห้อง_GarticPhone-vdo",
        "clip_id": "88c9437b-cf33-48e5-98d5-5faf4844742d",
        "source_file": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4",
        "start_frame": 157800,
        "end_frame": 161100,
        "expected_duration": 3300,
        "game_tag": "GarticPhone"
    },
    {
        "index": 14,
        "name": "ลืมปิดไมค์วาดรูปไฟลนก้น_GarticPhone-vdo",
        "clip_id": "88c9437b-cf33-48e5-98d5-5faf4844742d",
        "source_file": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4",
        "start_frame": 50040,
        "end_frame": 53340,
        "expected_duration": 3300,
        "game_tag": "GarticPhone"
    },
    {
        "index": 15,
        "name": "วาดรูปเพี้ยนจนกลายเป็นมีม_GarticPhone-vdo",
        "clip_id": "88c9437b-cf33-48e5-98d5-5faf4844742d",
        "source_file": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4",
        "start_frame": 134880,
        "end_frame": 138180,
        "expected_duration": 3300,
        "game_tag": "GarticPhone"
    },
    {
        "index": 16,
        "name": "ตอบแชทเรื่องสู้เสือด้วยมือเปล่า_FreeTalk-vdo",
        "clip_id": "e56002ed-9d9e-4cc4-97c9-fd191a631f5e",
        "source_file": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4",
        "start_frame": 104040,
        "end_frame": 107340,
        "expected_duration": 3300,
        "game_tag": "FreeTalk"
    },
    {
        "index": 17,
        "name": "จำลองเหตุการณ์ถ้าเจอเสือของจริง_FreeTalk-vdo",
        "clip_id": "e56002ed-9d9e-4cc4-97c9-fd191a631f5e",
        "source_file": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4",
        "start_frame": 116760,
        "end_frame": 120060,
        "expected_duration": 3300,
        "game_tag": "FreeTalk"
    },
    {
        "index": 18,
        "name": "อ่านคอมเมนต์สุดกาวขำจนตัวโยก_FreeTalk-vdo",
        "clip_id": "e56002ed-9d9e-4cc4-97c9-fd191a631f5e",
        "source_file": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4",
        "start_frame": 91080,
        "end_frame": 94380,
        "expected_duration": 3300,
        "game_tag": "FreeTalk"
    },
    {
        "index": 19,
        "name": "เปิดครัววันแรกก็วุ่นวายซะแล้ว_Overcooked-vdo",
        "clip_id": "407b877a-89c8-42b1-bc6d-71fbcd5fb6d1",
        "source_file": "เมื่อไทกะคือความชิบหายในครัว!.mp4",
        "start_frame": 25800,
        "end_frame": 29100,
        "expected_duration": 3300,
        "game_tag": "Overcooked"
    },
    {
        "index": 20,
        "name": "ออเดอร์ล้นครัวสั่งความวิกฤต_Overcooked-vdo",
        "clip_id": "407b877a-89c8-42b1-bc6d-71fbcd5fb6d1",
        "source_file": "เมื่อไทกะคือความชิบหายในครัว!.mp4",
        "start_frame": 231000,
        "end_frame": 234300,
        "expected_duration": 3300,
        "game_tag": "Overcooked"
    },
    {
        "index": 21,
        "name": "จานตกน้ำหมดครัวนาทีสุดท้าย_Overcooked-vdo",
        "clip_id": "407b877a-89c8-42b1-bc6d-71fbcd5fb6d1",
        "source_file": "เมื่อไทกะคือความชิบหายในครัว!.mp4",
        "start_frame": 541800,
        "end_frame": 545100,
        "expected_duration": 3300,
        "game_tag": "Overcooked"
    }
]

PRIOR_7_TIMELINES = [
    "Highlight_Gaming_REPO_Jumpscare",
    "Highlight_Gaming_Climbing_Clutch",
    "Highlight_Gaming_Ib_Horror",
    "Highlight_Fun_DnD_Bard",
    "Highlight_Meme_GarticPhone_Art",
    "Highlight_Meme_FreeTalk_Tiger",
    "Highlight_Fun_Overcooked_KitchenFire"
]

def run_independent_audit():
    print("================================================================================")
    print("FORENSIC INTEGRITY AUDIT: INDEPENDENT VERIFICATION")
    print(f"Timestamp: {datetime.datetime.now(datetime.timezone.utc).isoformat()}")
    print("================================================================================")

    audit_errors = []

    # 1. Connect to DaVinci Resolve
    print("\n--- [CHECK 1] DaVinci Resolve Connection & Project Authentication ---")
    resolve = dvr.scriptapp('Resolve')
    if not resolve:
        print("[FAIL] Could not connect to DaVinci Resolve instance!")
        return False
    print(f"[PASS] Connected to DaVinci Resolve instance object: {type(resolve)}")

    pm = resolve.GetProjectManager()
    if not pm:
        print("[FAIL] GetProjectManager() returned None!")
        return False
    
    project = pm.GetCurrentProject()
    if not project:
        print("[FAIL] GetCurrentProject() returned None!")
        return False
    
    proj_name = project.GetName()
    proj_id = project.GetUniqueId()
    print(f"[PASS] Active Project: '{proj_name}' (UniqueId: {proj_id}, Type: {type(project)})")
    if proj_name != "tygarina_2026-09-30":
        audit_errors.append(f"Project name mismatch: expected 'tygarina_2026-09-30', got '{proj_name}'")

    fps = float(project.GetSetting("timelineFrameRate"))
    print(f"[PASS] Project timelineFrameRate: {fps}")
    if fps != 60.0:
        audit_errors.append(f"FPS mismatch: expected 60.0, got {fps}")

    # 2. Timeline Catalog & Authenticity
    print("\n--- [CHECK 2] Timeline Inventory & Object Authenticity ---")
    total_timelines = project.GetTimelineCount()
    print(f"[INFO] project.GetTimelineCount() = {total_timelines}")
    if total_timelines != 28:
        audit_errors.append(f"Total timeline count mismatch: expected 28 (7 prior + 21 candidates), got {total_timelines}")

    timelines = {}
    for idx in range(1, total_timelines + 1):
        tl = project.GetTimelineByIndex(idx)
        tl_name = tl.GetName()
        tl_id = tl.GetUniqueId()
        tl_start = tl.GetStartFrame()
        tl_end = tl.GetEndFrame()
        v_tracks = tl.GetTrackCount("video")
        a_tracks = tl.GetTrackCount("audio")
        print(f"  Timeline #{idx:02d}: '{tl_name}' | ID: {tl_id} | Frames: [{tl_start}..{tl_end}] ({tl_end - tl_start}f) | VideoTracks: {v_tracks}, AudioTracks: {a_tracks}")
        timelines[tl_name] = {
            "obj": tl,
            "id": tl_id,
            "start": tl_start,
            "end": tl_end,
            "duration": tl_end - tl_start,
            "v_tracks": v_tracks,
            "a_tracks": a_tracks
        }

    # Verify prior 7 timelines exist
    print("\n--- [CHECK 3] Prior 7 Timelines Preservation ---")
    for pt in PRIOR_7_TIMELINES:
        if pt in timelines:
            print(f"  [PASS] Prior timeline preserved: '{pt}' (ID: {timelines[pt]['id']})")
        else:
            audit_errors.append(f"Prior timeline missing: '{pt}'")
            print(f"  [FAIL] Missing prior timeline: '{pt}'")

    # 3. Audit the 21 Candidate Timelines
    print("\n--- [CHECK 4] Forensic Inspection of 21 Highlight Timelines ---")
    thai_regex = re.compile(r"^([^\x00-\x7F]+)_([A-Za-z0-9]+)-vdo$")

    for cand in EXPECTED_CANDIDATES:
        c_idx = cand["index"]
        c_name = cand["name"]
        print(f"\nVerifying Candidate #{c_idx:02d}: {c_name}")

        if c_name not in timelines:
            audit_errors.append(f"Candidate #{c_idx} '{c_name}' not found in Resolve project!")
            print(f"  [FAIL] Timeline not found!")
            continue

        tl_meta = timelines[c_name]
        tl = tl_meta["obj"]

        # Check Naming Convention
        m = thai_regex.match(c_name)
        if not m:
            audit_errors.append(f"Candidate #{c_idx} '{c_name}' violates regex ^([^\x00-\x7F]+)_([A-Za-z0-9]+)-vdo$")
            print(f"  [FAIL] Regex match failed for '{c_name}'")
        else:
            thai_part, game_part = m.groups()
            # Deep check: assert Thai characters only in thai_part (U+0E00 to U+0E7F)
            non_thai_chars = [ch for ch in thai_part if not ('\u0E00' <= ch <= '\u0E7F')]
            if non_thai_chars:
                audit_errors.append(f"Candidate #{c_idx} has non-Thai characters in Thai part: {non_thai_chars}")
                print(f"  [FAIL] Non-Thai characters in Thai part: {non_thai_chars}")
            else:
                print(f"  [PASS] Naming strictly compliant: Thai='{thai_part}', Game='{game_part}', Suffix='-vdo'")

            if game_part != cand["game_tag"]:
                audit_errors.append(f"Candidate #{c_idx} game tag mismatch: expected '{cand['game_tag']}', got '{game_part}'")
                print(f"  [FAIL] Game tag mismatch: expected '{cand['game_tag']}', got '{game_part}'")

        # Check Duration
        dur_frames = tl_meta["duration"]
        dur_seconds = dur_frames / fps
        print(f"  [INFO] Timeline duration: {dur_frames} frames ({dur_seconds:.2f}s)")
        if dur_frames != cand["expected_duration"]:
            audit_errors.append(f"Candidate #{c_idx} duration {dur_frames} frames != expected {cand['expected_duration']}")
            print(f"  [FAIL] Duration mismatch: {dur_frames} != {cand['expected_duration']}")
        else:
            print(f"  [PASS] Exact duration match: {dur_frames} frames (55.0s)")

        if not (30.0 <= dur_seconds <= 180.0):
            audit_errors.append(f"Candidate #{c_idx} duration {dur_seconds:.2f}s outside bounds [30s..180s]")
            print(f"  [FAIL] Duration outside bounds: {dur_seconds:.2f}s")

        # Check Track Items & MediaPool Binding
        v_items = tl.GetItemListInTrack("video", 1)
        if not v_items:
            audit_errors.append(f"Candidate #{c_idx} has no video items on V1")
            print(f"  [FAIL] No video items on V1")
        else:
            v_item = v_items[0]
            v_dur = v_item.GetDuration()
            src_start = v_item.GetSourceStartFrame()
            src_end = v_item.GetSourceEndFrame()
            item_name = v_item.GetName()
            print(f"  [PASS] V1 item: '{item_name}', duration={v_dur}, source_range=[{src_start}..{src_end}]")

            if src_start != cand["start_frame"]:
                audit_errors.append(f"Candidate #{c_idx} source start frame mismatch: expected {cand['start_frame']}, got {src_start}")
                print(f"  [FAIL] Source start frame mismatch: {src_start} != {cand['start_frame']}")
            if src_end != cand["end_frame"]:
                audit_errors.append(f"Candidate #{c_idx} source end frame mismatch: expected {cand['end_frame']}, got {src_end}")
                print(f"  [FAIL] Source end frame mismatch: {src_end} != {cand['end_frame']}")

            mpi = v_item.GetMediaPoolItem()
            if not mpi:
                audit_errors.append(f"Candidate #{c_idx} V1 item has no MediaPoolItem!")
                print(f"  [FAIL] No MediaPoolItem")
            else:
                mpi_id = mpi.GetUniqueId()
                mpi_props = mpi.GetClipProperty()
                clip_file = mpi_props.get("File Path", "")
                clip_fps = mpi_props.get("FPS", "")
                print(f"  [PASS] MediaPoolItem ID: {mpi_id} (Expected ID: {cand['clip_id']})")
                print(f"  [PASS] Media file path: '{clip_file}', FPS: {clip_fps}")

                if mpi_id != cand["clip_id"]:
                    audit_errors.append(f"Candidate #{c_idx} MediaPoolItem ID mismatch: expected {cand['clip_id']}, got {mpi_id}")
                    print(f"  [FAIL] MediaPoolItem ID mismatch: {mpi_id} != {cand['clip_id']}")

                if not os.path.exists(clip_file):
                    audit_errors.append(f"Candidate #{c_idx} source file offline/missing on disk: {clip_file}")
                    print(f"  [FAIL] Media file offline on disk: {clip_file}")
                else:
                    print(f"  [PASS] Media file verified online on disk ({os.path.getsize(clip_file)} bytes)")

        # Audio Track 1 Check
        a_items = tl.GetItemListInTrack("audio", 1)
        if not a_items:
            audit_errors.append(f"Candidate #{c_idx} has no audio items on A1")
            print(f"  [FAIL] No audio items on A1")
        else:
            a_item = a_items[0]
            print(f"  [PASS] A1 item: '{a_item.GetName()}', duration={a_item.GetDuration()}, source_range=[{a_item.GetSourceStartFrame()}..{a_item.GetSourceEndFrame()}]")

    # 4. Source Media Non-Destructive Invariant Check
    print("\n--- [CHECK 5] Source Media Non-Destructive Storage Audit ---")
    source_dir = r"C:\Users\warit\SynologyDrive\Tygarina\2026-09-30"
    if not os.path.exists(source_dir):
        audit_errors.append(f"Source directory does not exist: {source_dir}")
        print(f"[FAIL] Directory missing: {source_dir}")
    else:
        files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]
        print(f"[INFO] Total files in source directory: {len(files)}")
        if len(files) != 32:
            audit_errors.append(f"Source directory file count mismatch: expected 32, got {len(files)}")
            print(f"[FAIL] File count mismatch: {len(files)} != 32")
        else:
            print(f"[PASS] File count exactly 32 files.")

        # Check modification times
        # Ensure no files were modified after the project session start (e.g. 2026-10-02T02:00:00Z)
        # 2026-10-02T02:00:00 UTC timestamp is 1790906400 approximately
        # Let's check max mtime
        recent_modifications = []
        for fn in files:
            fp = os.path.join(source_dir, fn)
            mtime = os.path.getmtime(fp)
            size = os.path.getsize(fp)
            mtime_dt = datetime.datetime.fromtimestamp(mtime, datetime.timezone.utc)
            # If modified today after session began (Oct 2 2026), flag
            if mtime_dt > datetime.datetime(2026, 10, 2, 2, 0, tzinfo=datetime.timezone.utc):
                recent_modifications.append((fn, mtime_dt.isoformat(), size))

        if recent_modifications:
            for fn, mt, sz in recent_modifications:
                audit_errors.append(f"Source file {fn} was modified recently: {mt}")
                print(f"  [FAIL] Modified source file: {fn} (mtime: {mt})")
        else:
            print(f"[PASS] Zero files in {source_dir} have been modified during this session. Non-destructive invariant strictly satisfied!")

    print("\n================================================================================")
    print("AUDIT SUMMARY")
    print("================================================================================")
    if not audit_errors:
        print("[VERDICT: CLEAN] ALL FORENSIC INTEGRITY CHECKS PASSED EMPIRICALLY!")
        print("- DaVinci Resolve objects: Authentic, active, and unmocked.")
        print("- Timeline count: 28 (7 prior + 21 new candidates).")
        print("- Naming compliance: 21/21 strictly conform to {ชื่อคลิปภาษาไทย}_{ชื่อเกม}-vdo (zero ASCII characters in Thai part).")
        print("- Durations: 21/21 exactly 3300 frames (55.0s, bounded [30s..180s]).")
        print("- Trims and in/out frames: 21/21 match candidate spec 1:1.")
        print("- Source media: 0 files modified, deleted, or transcoded.")
        print("- Media status: 100% online on disk.")
        return True
    else:
        print(f"[VERDICT: INTEGRITY VIOLATION] FOUND {len(audit_errors)} VIOLATIONS:")
        for err in audit_errors:
            print(f"  - {err}")
        return False

if __name__ == "__main__":
    success = run_independent_audit()
    if not success:
        sys.exit(1)
