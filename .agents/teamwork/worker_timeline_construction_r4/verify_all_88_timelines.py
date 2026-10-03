import os
import sys
import json
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

os.environ['RESOLVE_SCRIPT_LIB'] = r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
sys.path.append(r'C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\lib\modules')

import DaVinciResolveScript as dvr

SPEC_FILE = r'C:\Users\warit\Desktop\agent-edite-davinci_resolve\scratch\round4_60_candidates_complete.json'
EXPECTED_PREEXISTING_COUNT = 28
EXPECTED_NEW_COUNT = 60
EXPECTED_TOTAL_COUNT = 88
EXPECTED_DURATION = 3300

NAMING_REGEX = re.compile(r"^([\u0E00-\u0E7F]+)_([A-Za-z0-9]+)-vdo$")

def main():
    print("=" * 80)
    print("INDEPENDENT POST-CONSTRUCTION COMPREHENSIVE VERIFICATION AUDIT")
    print("=" * 80)

    # 1. Load candidate spec
    with open(SPEC_FILE, 'r', encoding='utf-8') as f:
        candidates = json.load(f)
    assert len(candidates) == EXPECTED_NEW_COUNT, f"Candidates spec count is {len(candidates)}"

    # 2. Connect to DaVinci Resolve
    resolve = dvr.scriptapp('Resolve')
    assert resolve is not None, "Could not connect to DaVinci Resolve"
    
    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    assert proj is not None, "No current project open"
    
    proj_name = proj.GetName()
    print(f"[OK] Project: '{proj_name}' (ID: {proj.GetUniqueId()})")
    assert proj_name == "tygarina_2026-09-30", f"Unexpected project: {proj_name}"

    fps = proj.GetSetting('timelineFrameRate')
    print(f"[OK] Project timelineFrameRate: {fps}")
    assert float(fps) == 60.0, f"Unexpected fps: {fps}"

    total_timelines = proj.GetTimelineCount()
    print(f"[OK] Total Timelines in Project: {total_timelines}")
    assert total_timelines == EXPECTED_TOTAL_COUNT, f"Expected {EXPECTED_TOTAL_COUNT}, got {total_timelines}"

    all_tls = {}
    for i in range(1, total_timelines + 1):
        tl = proj.GetTimelineByIndex(i)
        all_tls[tl.GetName()] = tl

    # 3. Verify Pre-existing 28 Timelines Preserved
    print("\n--- Auditing 28 Pre-existing Timelines ---")
    preexisting_names = [
        "Highlight_Gaming_REPO_Jumpscare",
        "Highlight_Gaming_Climbing_Clutch",
        "Highlight_Gaming_Ib_Horror",
        "Highlight_Fun_DnD_Bard",
        "Highlight_Meme_GarticPhone_Art",
        "Highlight_Meme_FreeTalk_Tiger",
        "Highlight_Fun_Overcooked_KitchenFire",
        "วิ่งหนีปีศาจแทบไม่ทัน_REPO-vdo",
        "จังหวะเอาชีวิตรอดเฉียดฉิว_REPO-vdo",
        "เปิดตี้แจกความฮากับเพื่อน_REPO-vdo",
        "เหลือสองชีวิตเกาะหน้าผาไว้_Climbing-vdo",
        "จังหวะกระโดดข้ามหุบเหวสุดเสียว_Climbing-vdo",
        "แกล้งเพื่อนตั้งแต่จุดสตาร์ท_Climbing-vdo",
        "เจอตัวละครใหม่ตกใจจนร้องลั่น_Ib-vdo",
        "ประตูมิติชวนขนหัวลุก_Ib-vdo",
        "ไขปริศนาภาพวาดมรณะ_Ib-vdo",
        "เล่าวินาทีบอสแพ้แบบอนาถ_DnD-vdo",
        "ฉากโรลเพลย์สุดกาวในห้องน้ำ_DnD-vdo",
        "ทอยเต๋าพลาดจนแผนพังยับ_DnD-vdo",
        "เฉลยภาพวาดจนเพื่อนอึ้งทั้งห้อง_GarticPhone-vdo",
        "ลืมปิดไมค์วาดรูปไฟลนก้น_GarticPhone-vdo",
        "วาดรูปเพี้ยนจนกลายเป็นมีม_GarticPhone-vdo",
        "ตอบแชทเรื่องสู้เสือด้วยมือเปล่า_FreeTalk-vdo",
        "จำลองเหตุการณ์ถ้าเจอเสือของจริง_FreeTalk-vdo",
        "อ่านคอมเมนต์สุดกาวขำจนตัวโยก_FreeTalk-vdo",
        "เปิดครัววันแรกก็วุ่นวายซะแล้ว_Overcooked-vdo",
        "ออเดอร์ล้นครัวสั่งความวิกฤต_Overcooked-vdo",
        "จานตกน้ำหมดครัวนาทีสุดท้าย_Overcooked-vdo",
    ]

    for pre_idx, pre_name in enumerate(preexisting_names, 1):
        assert pre_name in all_tls, f"Pre-existing timeline '{pre_name}' is MISSING!"
        t = all_tls[pre_name]
        v_items = t.GetItemListInTrack("video", 1) or []
        assert len(v_items) > 0, f"Pre-existing timeline '{pre_name}' has 0 video items!"
    print(f"[PASS] All {len(preexisting_names)} pre-existing timelines verified intact and undamaged.")

    # 4. Verify 60 New Candidate Timelines
    print("\n--- Auditing 60 New Candidate Timelines ---")
    failures = []
    audited_count = 0

    for cand in candidates:
        cid = cand["id"]
        title = cand["title"]
        s_f = cand["start_frame"]
        e_f = cand["end_frame"]
        src_file = cand["source_file"]

        if title not in all_tls:
            failures.append(f"Candidate #{cid} '{title}' is MISSING from project!")
            continue

        tl = all_tls[title]
        audited_count += 1

        # Check pure Thai naming regex
        m = NAMING_REGEX.match(title)
        if not m:
            failures.append(f"Candidate #{cid} '{title}' failed naming regex!")
        else:
            thai_part, game_part = m.groups()
            if re.search(r"[a-zA-Z]", thai_part):
                failures.append(f"Candidate #{cid} '{title}' contains Latin letters in Thai prefix!")

        # Check duration
        tl_start = tl.GetStartFrame()
        tl_end = tl.GetEndFrame()
        dur = tl_end - tl_start
        if dur != EXPECTED_DURATION:
            failures.append(f"Candidate #{cid} '{title}' duration is {dur}, expected {EXPECTED_DURATION}!")

        # Check tracks
        v_items = tl.GetItemListInTrack("video", 1) or []
        a_items = tl.GetItemListInTrack("audio", 1) or []

        if len(v_items) != 1:
            failures.append(f"Candidate #{cid} '{title}' video track 1 item count {len(v_items)} != 1")
        else:
            v = v_items[0]
            if v.GetDuration() != EXPECTED_DURATION:
                failures.append(f"Candidate #{cid} '{title}' video item duration {v.GetDuration()} != {EXPECTED_DURATION}")
            if v.GetSourceStartFrame() != s_f:
                failures.append(f"Candidate #{cid} '{title}' video srcStart {v.GetSourceStartFrame()} != {s_f}")
            if v.GetSourceEndFrame() != e_f:
                failures.append(f"Candidate #{cid} '{title}' video srcEnd {v.GetSourceEndFrame()} != {e_f}")

            # Check media online
            mpi = v.GetMediaPoolItem()
            if not mpi:
                failures.append(f"Candidate #{cid} '{title}' video item has no MediaPoolItem")
            else:
                fpath = mpi.GetClipProperty().get("File Path", "")
                if not fpath or not os.path.exists(fpath):
                    failures.append(f"Candidate #{cid} '{title}' media file offline: {fpath}")

        if len(a_items) != 1:
            failures.append(f"Candidate #{cid} '{title}' audio track 1 item count {len(a_items)} != 1")
        else:
            a = a_items[0]
            if a.GetDuration() != EXPECTED_DURATION:
                failures.append(f"Candidate #{cid} '{title}' audio item duration {a.GetDuration()} != {EXPECTED_DURATION}")
            if a.GetSourceStartFrame() != s_f:
                failures.append(f"Candidate #{cid} '{title}' audio srcStart {a.GetSourceStartFrame()} != {s_f}")
            if a.GetSourceEndFrame() != e_f:
                failures.append(f"Candidate #{cid} '{title}' audio srcEnd {a.GetSourceEndFrame()} != {e_f}")

            # Check media online
            mpi = a.GetMediaPoolItem()
            if not mpi:
                failures.append(f"Candidate #{cid} '{title}' audio item has no MediaPoolItem")
            else:
                fpath = mpi.GetClipProperty().get("File Path", "")
                if not fpath or not os.path.exists(fpath):
                    failures.append(f"Candidate #{cid} '{title}' media file offline: {fpath}")

    # 5. Offline Media Check across all 88 Timelines
    print("\n--- Auditing Offline Media Across All 88 Timelines ---")
    offline_items = []
    for tname, tl in all_tls.items():
        for track_type in ["video", "audio"]:
            track_count = tl.GetTrackCount(track_type)
            for tidx in range(1, track_count + 1):
                items = tl.GetItemListInTrack(track_type, tidx) or []
                for it in items:
                    mpi = it.GetMediaPoolItem()
                    if mpi:
                        props = mpi.GetClipProperty()
                        fpath = props.get("File Path", "")
                        if fpath and not os.path.exists(fpath):
                            offline_items.append((tname, track_type, tidx, it.GetName(), fpath))
    
    print(f"[OK] Total offline media items detected: {len(offline_items)}")
    assert len(offline_items) == 0, f"Offline media detected: {offline_items}"

    # 6. Save Project Confirmation
    print("\n--- Clean Project Save ---")
    saved = pm.SaveProject()
    print(f"[OK] ProjectManager.SaveProject() returned: {saved}")
    assert saved is True, "ProjectManager.SaveProject() failed!"

    # 7. Final Report
    print("\n" + "=" * 80)
    print("FINAL VERIFICATION SUMMARY")
    print("=" * 80)
    if failures:
        print(f"[FAIL] {len(failures)} failures encountered:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("[PASS] 100% VERIFICATION PASSED WITH ZERO ERRORS!")
        print(f"  1. Pre-existing timelines: exactly 28 preserved.")
        print(f"  2. New highlight timelines: exactly 60 created.")
        print(f"  3. Total project timelines: exactly 88.")
        print(f"  4. Every one of the 60 new timelines duration: exactly 3300 frames (55.0s at 60 fps).")
        print(f"  5. Every one of the 60 new timelines naming: 100% pure Thai prefix (0 Latin letters).")
        print(f"  6. Every one of the 60 new timelines tracks: V1 and A1 populated with exact source frames.")
        print(f"  7. Total offline media across all 88 timelines: exactly 0.")
        print(f"  8. Project persistence: cleanly saved via ProjectManager.SaveProject().")
        print("=" * 80)

if __name__ == "__main__":
    main()
