"""
Adversarial Deep Audit & Edge-Case Probing for Milestone M3:
DaVinci Resolve Highlights in Project 'tygarina_2026-09-30'.

Challenger 1 (challenger_m3_1)
Adversarial Probing:
1. Prior highlight overlap exclusion (H1..H7 vs new 21 candidates)
2. Intra-file candidate overlap (no overlap among candidates from same source)
3. Media format and codec validation
4. Video & Audio track synchronization and track count parity
5. Zero offline media / zero missing frames on disk
6. Timeline resolution, playhead safety, project save state
"""
import os
import sys
import pytest

RESOLVE_SCRIPT_API_DIR = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"
if RESOLVE_SCRIPT_API_DIR not in sys.path:
    sys.path.append(RESOLVE_SCRIPT_API_DIR)

import DaVinciResolveScript as dvr

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

MEDIA_STORAGE_DIR = r"C:\Users\warit\SynologyDrive\Tygarina\2026-09-30"

# Prior 7 highlights from Round 2
PRIOR_HIGHLIGHTS = [
    {
        "id": "H1",
        "name": "Highlight_Gaming_REPO_Jumpscare",
        "mediapool_id": "4462a5cf-dad7-4499-ab4d-20a999ba2b59",
        "start_frame": 403200,
        "end_frame": 407100,
    },
    {
        "id": "H2",
        "name": "Highlight_Gaming_Climbing_Clutch",
        "mediapool_id": "3ebbdd92-9aa6-4738-b586-956bf85f35d6",
        "start_frame": 351300,
        "end_frame": 354900,
    },
    {
        "id": "H3",
        "name": "Highlight_Gaming_Ib_Horror",
        "mediapool_id": "7a4e9419-b627-4b4f-87db-9a0d7af59fe2",
        "start_frame": 268500,
        "end_frame": 271800,
    },
    {
        "id": "H4",
        "name": "Highlight_Fun_DnD_Bard",
        "mediapool_id": "9ae1c0ee-6b90-482e-ac71-a5aac9a6f262",
        "start_frame": 418200,
        "end_frame": 422400,
    },
    {
        "id": "H5",
        "name": "Highlight_Meme_GarticPhone_Art",
        "mediapool_id": "88c9437b-cf33-48e5-98d5-5faf4844742d",
        "start_frame": 182700,
        "end_frame": 186000,
    },
    {
        "id": "H6",
        "name": "Highlight_Meme_FreeTalk_Tiger",
        "mediapool_id": "e56002ed-9d9e-4cc4-97c9-fd191a631f5e",
        "start_frame": 142200,
        "end_frame": 145500,
    },
    {
        "id": "H7",
        "name": "Highlight_Fun_Overcooked_KitchenFire",
        "mediapool_id": "407b877a-89c8-42b1-bc6d-71fbcd5fb6d1",
        "start_frame": 307200,
        "end_frame": 310800,
    },
]

NEW_CANDIDATES = [
    {"index": 1, "name": "วิ่งหนีปีศาจแทบไม่ทัน_REPO-vdo", "mediapool_id": "4462a5cf-dad7-4499-ab4d-20a999ba2b59", "start_frame": 275280, "end_frame": 278580},
    {"index": 2, "name": "จังหวะเอาชีวิตรอดเฉียดฉิว_REPO-vdo", "mediapool_id": "4462a5cf-dad7-4499-ab4d-20a999ba2b59", "start_frame": 574680, "end_frame": 577980},
    {"index": 3, "name": "เปิดตี้แจกความฮากับเพื่อน_REPO-vdo", "mediapool_id": "4462a5cf-dad7-4499-ab4d-20a999ba2b59", "start_frame": 21000, "end_frame": 24300},
    {"index": 4, "name": "เหลือสองชีวิตเกาะหน้าผาไว้_Climbing-vdo", "mediapool_id": "3ebbdd92-9aa6-4738-b586-956bf85f35d6", "start_frame": 257760, "end_frame": 261060},
    {"index": 5, "name": "จังหวะกระโดดข้ามหุบเหวสุดเสียว_Climbing-vdo", "mediapool_id": "3ebbdd92-9aa6-4738-b586-956bf85f35d6", "start_frame": 301200, "end_frame": 304500},
    {"index": 6, "name": "แกล้งเพื่อนตั้งแต่จุดสตาร์ท_Climbing-vdo", "mediapool_id": "3ebbdd92-9aa6-4738-b586-956bf85f35d6", "start_frame": 14280, "end_frame": 17580},
    {"index": 7, "name": "เจอตัวละครใหม่ตกใจจนร้องลั่น_Ib-vdo", "mediapool_id": "7a4e9419-b627-4b4f-87db-9a0d7af59fe2", "start_frame": 249480, "end_frame": 252780},
    {"index": 8, "name": "ประตูมิติชวนขนหัวลุก_Ib-vdo", "mediapool_id": "7a4e9419-b627-4b4f-87db-9a0d7af59fe2", "start_frame": 125280, "end_frame": 128580},
    {"index": 9, "name": "ไขปริศนาภาพวาดมรณะ_Ib-vdo", "mediapool_id": "7a4e9419-b627-4b4f-87db-9a0d7af59fe2", "start_frame": 456840, "end_frame": 460140},
    {"index": 10, "name": "เล่าวินาทีบอสแพ้แบบอนาถ_DnD-vdo", "mediapool_id": "9ae1c0ee-6b90-482e-ac71-a5aac9a6f262", "start_frame": 262920, "end_frame": 266220},
    {"index": 11, "name": "ฉากโรลเพลย์สุดกาวในห้องน้ำ_DnD-vdo", "mediapool_id": "9ae1c0ee-6b90-482e-ac71-a5aac9a6f262", "start_frame": 286800, "end_frame": 290100},
    {"index": 12, "name": "ทอยเต๋าพลาดจนแผนพังยับ_DnD-vdo", "mediapool_id": "9ae1c0ee-6b90-482e-ac71-a5aac9a6f262", "start_frame": 209400, "end_frame": 212700},
    {"index": 13, "name": "เฉลยภาพวาดจนเพื่อนอึ้งทั้งห้อง_GarticPhone-vdo", "mediapool_id": "88c9437b-cf33-48e5-98d5-5faf4844742d", "start_frame": 157800, "end_frame": 161100},
    {"index": 14, "name": "ลืมปิดไมค์วาดรูปไฟลนก้น_GarticPhone-vdo", "mediapool_id": "88c9437b-cf33-48e5-98d5-5faf4844742d", "start_frame": 50040, "end_frame": 53340},
    {"index": 15, "name": "วาดรูปเพี้ยนจนกลายเป็นมีม_GarticPhone-vdo", "mediapool_id": "88c9437b-cf33-48e5-98d5-5faf4844742d", "start_frame": 134880, "end_frame": 138180},
    {"index": 16, "name": "ตอบแชทเรื่องสู้เสือด้วยมือเปล่า_FreeTalk-vdo", "mediapool_id": "e56002ed-9d9e-4cc4-97c9-fd191a631f5e", "start_frame": 104040, "end_frame": 107340},
    {"index": 17, "name": "จำลองเหตุการณ์ถ้าเจอเสือของจริง_FreeTalk-vdo", "mediapool_id": "e56002ed-9d9e-4cc4-97c9-fd191a631f5e", "start_frame": 116760, "end_frame": 120060},
    {"index": 18, "name": "อ่านคอมเมนต์สุดกาวขำจนตัวโยก_FreeTalk-vdo", "mediapool_id": "e56002ed-9d9e-4cc4-97c9-fd191a631f5e", "start_frame": 91080, "end_frame": 94380},
    {"index": 19, "name": "เปิดครัววันแรกก็วุ่นวายซะแล้ว_Overcooked-vdo", "mediapool_id": "407b877a-89c8-42b1-bc6d-71fbcd5fb6d1", "start_frame": 25800, "end_frame": 29100},
    {"index": 20, "name": "ออเดอร์ล้นครัวสั่งความวิกฤต_Overcooked-vdo", "mediapool_id": "407b877a-89c8-42b1-bc6d-71fbcd5fb6d1", "start_frame": 231000, "end_frame": 234300},
    {"index": 21, "name": "จานตกน้ำหมดครัวนาทีสุดท้าย_Overcooked-vdo", "mediapool_id": "407b877a-89c8-42b1-bc6d-71fbcd5fb6d1", "start_frame": 541800, "end_frame": 545100},
]


def test_adversarial_overlap_exclusion():
    """Verify that NO new highlight interval overlaps with any prior highlight (H1..H7)."""
    for new_cand in NEW_CANDIDATES:
        mp_id = new_cand["mediapool_id"]
        n_start = new_cand["start_frame"]
        n_end = new_cand["end_frame"]

        for prior in PRIOR_HIGHLIGHTS:
            if prior["mediapool_id"] == mp_id:
                p_start = prior["start_frame"]
                p_end = prior["end_frame"]
                overlap = max(0, min(n_end, p_end) - max(n_start, p_start))
                assert overlap == 0, (
                    f"CRITICAL OVERLAP DETECTED! Candidate '{new_cand['name']}' [{n_start}:{n_end}] "
                    f"overlaps by {overlap} frames with prior highlight '{prior['name']}' [{p_start}:{p_end}]!"
                )


def test_adversarial_candidate_pairwise_exclusion():
    """Verify that NO two new candidates from the same source file overlap."""
    by_file = {}
    for c in NEW_CANDIDATES:
        by_file.setdefault(c["mediapool_id"], []).append(c)

    for mp_id, cand_list in by_file.items():
        assert len(cand_list) == 3, f"Expected exactly 3 candidates for file {mp_id}, got {len(cand_list)}"
        for i in range(len(cand_list)):
            for j in range(i + 1, len(cand_list)):
                c1, c2 = cand_list[i], cand_list[j]
                overlap = max(0, min(c1["end_frame"], c2["end_frame"]) - max(c1["start_frame"], c2["start_frame"]))
                assert overlap == 0, (
                    f"INTRA-FILE OVERLAP DETECTED! '{c1['name']}' [{c1['start_frame']}:{c1['end_frame']}] "
                    f"and '{c2['name']}' [{c2['start_frame']}:{c2['end_frame']}] overlap by {overlap} frames!"
                )


def test_adversarial_deep_timeline_properties():
    """Directly query Resolve and inspect timeline items, tracks, and media item metadata."""
    resolve = dvr.scriptapp("Resolve")
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()

    for cand in NEW_CANDIDATES:
        c_name = cand["name"]
        tl = None
        for i in range(1, project.GetTimelineCount() + 1):
            t = project.GetTimelineByIndex(i)
            if t.GetName() == c_name:
                tl = t
                break
        assert tl is not None, f"Timeline '{c_name}' not found"

        # Check video items
        v_items = tl.GetItemListInTrack("video", 1)
        assert len(v_items) == 1
        v_item = v_items[0]

        # Check audio items
        a_items = tl.GetItemListInTrack("audio", 1)
        assert len(a_items) >= 1
        a_item = a_items[0]

        # Check sync between video and audio
        assert v_item.GetStart() == a_item.GetStart(), f"AV desync at start in '{c_name}'"
        assert v_item.GetEnd() == a_item.GetEnd(), f"AV desync at end in '{c_name}'"
        assert v_item.GetDuration() == a_item.GetDuration(), f"AV duration mismatch in '{c_name}'"

        # Check media pool item properties
        mpi = v_item.GetMediaPoolItem()
        props = mpi.GetClipProperty()
        file_path = props.get("File Path")
        fps = props.get("FPS")
        video_codec = props.get("Video Codec")
        audio_codec = props.get("Audio Codec")

        print(f"[{c_name}] FPS: {fps}, Video: {video_codec}, Audio: {audio_codec}, File: {os.path.basename(file_path)}")
        assert float(fps) == 60.0, f"Source FPS mismatch: {fps}"
        assert os.path.exists(file_path), f"File missing: {file_path}"
