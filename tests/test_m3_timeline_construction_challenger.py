"""
Empirical Challenger Verification & Stress Test Suite for Milestone M3:
DaVinci Resolve Highlight Timeline Construction in Project 'tygarina_2026-09-30'.

Challenger 1 (challenger_m3_1)
Persona: EMPIRICAL CHALLENGER (critic, specialist)
Verification Standard: Evidence before claims; unmocked Resolve API testing; adversarial stress testing.
"""
import os
import re
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
EXPECTED_PROJECT_NAME = "tygarina_2026-09-30"
EXPECTED_PROJECT_ID = "c0d08784-1fd9-4675-921b-d77a6b5cccdf"
EXPECTED_FPS = 60.0
EXPECTED_DURATION_FRAMES = 3300
EXPECTED_DURATION_SEC = 55.0
MIN_DURATION_SEC = 30.0
MAX_DURATION_SEC = 180.0

TIMELINE_NAME_REGEX = re.compile(r"^([^\x00-\x7F]+)_([A-Za-z0-9]+)-vdo$")

EXPECTED_PRIOR_TIMELINE_NAMES = [
    "Highlight_Gaming_REPO_Jumpscare",
    "Highlight_Gaming_Climbing_Clutch",
    "Highlight_Gaming_Ib_Horror",
    "Highlight_Fun_DnD_Bard",
    "Highlight_Meme_GarticPhone_Art",
    "Highlight_Meme_FreeTalk_Tiger",
    "Highlight_Fun_Overcooked_KitchenFire",
]

CANDIDATES = [
    {
        "index": 1,
        "name": "วิ่งหนีปีศาจแทบไม่ทัน_REPO-vdo",
        "mediapool_id": "4462a5cf-dad7-4499-ab4d-20a999ba2b59",
        "worker_timeline_id": "d89052c9-a83b-4c47-a826-1fbb008751fb",
        "game": "REPO",
        "source_file": "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4",
        "start_sec": 4588.0,
        "end_sec": 4643.0,
        "start_frame": 275280,
        "end_frame": 278580,
        "duration_frames": 3300,
    },
    {
        "index": 2,
        "name": "จังหวะเอาชีวิตรอดเฉียดฉิว_REPO-vdo",
        "mediapool_id": "4462a5cf-dad7-4499-ab4d-20a999ba2b59",
        "worker_timeline_id": "d5a7e5dc-f5fe-4378-90f6-d5904576e0d5",
        "game": "REPO",
        "source_file": "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4",
        "start_sec": 9578.0,
        "end_sec": 9633.0,
        "start_frame": 574680,
        "end_frame": 577980,
        "duration_frames": 3300,
    },
    {
        "index": 3,
        "name": "เปิดตี้แจกความฮากับเพื่อน_REPO-vdo",
        "mediapool_id": "4462a5cf-dad7-4499-ab4d-20a999ba2b59",
        "worker_timeline_id": "47107ecd-2608-4931-8ecc-d286a2a11014",
        "game": "REPO",
        "source_file": "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4",
        "start_sec": 350.0,
        "end_sec": 405.0,
        "start_frame": 21000,
        "end_frame": 24300,
        "duration_frames": 3300,
    },
    {
        "index": 4,
        "name": "เหลือสองชีวิตเกาะหน้าผาไว้_Climbing-vdo",
        "mediapool_id": "3ebbdd92-9aa6-4738-b586-956bf85f35d6",
        "worker_timeline_id": "8ee0e8d9-fc6f-43f1-8c44-3dacfb778e8a",
        "game": "Climbing",
        "source_file_prefix": "ปืนเขาที่เราหมดแรง @KRATOI_26",
        "start_sec": 4296.0,
        "end_sec": 4351.0,
        "start_frame": 257760,
        "end_frame": 261060,
        "duration_frames": 3300,
    },
    {
        "index": 5,
        "name": "จังหวะกระโดดข้ามหุบเหวสุดเสียว_Climbing-vdo",
        "mediapool_id": "3ebbdd92-9aa6-4738-b586-956bf85f35d6",
        "worker_timeline_id": "ad7c1cce-c612-43c3-aa7a-9f476ee88ed9",
        "game": "Climbing",
        "source_file_prefix": "ปืนเขาที่เราหมดแรง @KRATOI_26",
        "start_sec": 5020.0,
        "end_sec": 5075.0,
        "start_frame": 301200,
        "end_frame": 304500,
        "duration_frames": 3300,
    },
    {
        "index": 6,
        "name": "แกล้งเพื่อนตั้งแต่จุดสตาร์ท_Climbing-vdo",
        "mediapool_id": "3ebbdd92-9aa6-4738-b586-956bf85f35d6",
        "worker_timeline_id": "dfcba33d-4abd-458f-b1f6-ae1572b129e6",
        "game": "Climbing",
        "source_file_prefix": "ปืนเขาที่เราหมดแรง @KRATOI_26",
        "start_sec": 238.0,
        "end_sec": 293.0,
        "start_frame": 14280,
        "end_frame": 17580,
        "duration_frames": 3300,
    },
    {
        "index": 7,
        "name": "เจอตัวละครใหม่ตกใจจนร้องลั่น_Ib-vdo",
        "mediapool_id": "7a4e9419-b627-4b4f-87db-9a0d7af59fe2",
        "worker_timeline_id": "dedc4c20-3768-404a-b5a8-a31c79ec0931",
        "game": "Ib",
        "source_file": "IB - สำรวจโลกภาพวาด P1.mp4",
        "start_sec": 4158.0,
        "end_sec": 4213.0,
        "start_frame": 249480,
        "end_frame": 252780,
        "duration_frames": 3300,
    },
    {
        "index": 8,
        "name": "ประตูมิติชวนขนหัวลุก_Ib-vdo",
        "mediapool_id": "7a4e9419-b627-4b4f-87db-9a0d7af59fe2",
        "worker_timeline_id": "67288d5f-5695-4094-83f3-e962701bc9c6",
        "game": "Ib",
        "source_file": "IB - สำรวจโลกภาพวาด P1.mp4",
        "start_sec": 2088.0,
        "end_sec": 2143.0,
        "start_frame": 125280,
        "end_frame": 128580,
        "duration_frames": 3300,
    },
    {
        "index": 9,
        "name": "ไขปริศนาภาพวาดมรณะ_Ib-vdo",
        "mediapool_id": "7a4e9419-b627-4b4f-87db-9a0d7af59fe2",
        "worker_timeline_id": "c2fdeaf9-9886-4cd6-9ec3-3c24190f0fef",
        "game": "Ib",
        "source_file": "IB - สำรวจโลกภาพวาด P1.mp4",
        "start_sec": 7614.0,
        "end_sec": 7669.0,
        "start_frame": 456840,
        "end_frame": 460140,
        "duration_frames": 3300,
    },
    {
        "index": 10,
        "name": "เล่าวินาทีบอสแพ้แบบอนาถ_DnD-vdo",
        "mediapool_id": "9ae1c0ee-6b90-482e-ac71-a5aac9a6f262",
        "worker_timeline_id": "cd3efb75-4cee-4b5f-808c-eb3be4ac6c0a",
        "game": "DnD",
        "source_file": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4",
        "start_sec": 4382.0,
        "end_sec": 4437.0,
        "start_frame": 262920,
        "end_frame": 266220,
        "duration_frames": 3300,
    },
    {
        "index": 11,
        "name": "ฉากโรลเพลย์สุดกาวในห้องน้ำ_DnD-vdo",
        "mediapool_id": "9ae1c0ee-6b90-482e-ac71-a5aac9a6f262",
        "worker_timeline_id": "9921f006-bb9c-44f2-8f1b-43cf0874d174",
        "game": "DnD",
        "source_file": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4",
        "start_sec": 4780.0,
        "end_sec": 4835.0,
        "start_frame": 286800,
        "end_frame": 290100,
        "duration_frames": 3300,
    },
    {
        "index": 12,
        "name": "ทอยเต๋าพลาดจนแผนพังยับ_DnD-vdo",
        "mediapool_id": "9ae1c0ee-6b90-482e-ac71-a5aac9a6f262",
        "worker_timeline_id": "7f5e9103-b889-418b-b1e8-2516bb35871a",
        "game": "DnD",
        "source_file": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4",
        "start_sec": 3490.0,
        "end_sec": 3545.0,
        "start_frame": 209400,
        "end_frame": 212700,
        "duration_frames": 3300,
    },
    {
        "index": 13,
        "name": "เฉลยภาพวาดจนเพื่อนอึ้งทั้งห้อง_GarticPhone-vdo",
        "mediapool_id": "88c9437b-cf33-48e5-98d5-5faf4844742d",
        "worker_timeline_id": "b65b8fba-f1af-4e7f-b293-047e6bd2d9ea",
        "game": "GarticPhone",
        "source_file": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4",
        "start_sec": 2630.0,
        "end_sec": 2685.0,
        "start_frame": 157800,
        "end_frame": 161100,
        "duration_frames": 3300,
    },
    {
        "index": 14,
        "name": "ลืมปิดไมค์วาดรูปไฟลนก้น_GarticPhone-vdo",
        "mediapool_id": "88c9437b-cf33-48e5-98d5-5faf4844742d",
        "worker_timeline_id": "d717627c-10d4-47ce-9ec7-676272a21fa2",
        "game": "GarticPhone",
        "source_file": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4",
        "start_sec": 834.0,
        "end_sec": 889.0,
        "start_frame": 50040,
        "end_frame": 53340,
        "duration_frames": 3300,
    },
    {
        "index": 15,
        "name": "วาดรูปเพี้ยนจนกลายเป็นมีม_GarticPhone-vdo",
        "mediapool_id": "88c9437b-cf33-48e5-98d5-5faf4844742d",
        "worker_timeline_id": "bfea8d6b-57e8-43fb-ac00-3dba97368b2c",
        "game": "GarticPhone",
        "source_file": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4",
        "start_sec": 2248.0,
        "end_sec": 2303.0,
        "start_frame": 134880,
        "end_frame": 138180,
        "duration_frames": 3300,
    },
    {
        "index": 16,
        "name": "ตอบแชทเรื่องสู้เสือด้วยมือเปล่า_FreeTalk-vdo",
        "mediapool_id": "e56002ed-9d9e-4cc4-97c9-fd191a631f5e",
        "worker_timeline_id": "0dbc2a8c-f90c-4957-a484-bf419ba5100c",
        "game": "FreeTalk",
        "source_file": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4",
        "start_sec": 1734.0,
        "end_sec": 1789.0,
        "start_frame": 104040,
        "end_frame": 107340,
        "duration_frames": 3300,
    },
    {
        "index": 17,
        "name": "จำลองเหตุการณ์ถ้าเจอเสือของจริง_FreeTalk-vdo",
        "mediapool_id": "e56002ed-9d9e-4cc4-97c9-fd191a631f5e",
        "worker_timeline_id": "5d5ad297-a592-4102-b27a-d8a82178ad9e",
        "game": "FreeTalk",
        "source_file": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4",
        "start_sec": 1946.0,
        "end_sec": 2001.0,
        "start_frame": 116760,
        "end_frame": 120060,
        "duration_frames": 3300,
    },
    {
        "index": 18,
        "name": "อ่านคอมเมนต์สุดกาวขำจนตัวโยก_FreeTalk-vdo",
        "mediapool_id": "e56002ed-9d9e-4cc4-97c9-fd191a631f5e",
        "worker_timeline_id": "594d2d8e-8860-4565-a184-9dee7518e61a",
        "game": "FreeTalk",
        "source_file": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4",
        "start_sec": 1518.0,
        "end_sec": 1573.0,
        "start_frame": 91080,
        "end_frame": 94380,
        "duration_frames": 3300,
    },
    {
        "index": 19,
        "name": "เปิดครัววันแรกก็วุ่นวายซะแล้ว_Overcooked-vdo",
        "mediapool_id": "407b877a-89c8-42b1-bc6d-71fbcd5fb6d1",
        "worker_timeline_id": "0e5d2572-ffd3-4d12-b32e-82ae265395c0",
        "game": "Overcooked",
        "source_file": "เมื่อไทกะคือความชิบหายในครัว!.mp4",
        "start_sec": 430.0,
        "end_sec": 485.0,
        "start_frame": 25800,
        "end_frame": 29100,
        "duration_frames": 3300,
    },
    {
        "index": 20,
        "name": "ออเดอร์ล้นครัวสั่งความวิกฤต_Overcooked-vdo",
        "mediapool_id": "407b877a-89c8-42b1-bc6d-71fbcd5fb6d1",
        "worker_timeline_id": "e11e0cfd-857d-41ba-9df0-3628f3dde5fe",
        "game": "Overcooked",
        "source_file": "เมื่อไทกะคือความชิบหายในครัว!.mp4",
        "start_sec": 3850.0,
        "end_sec": 3905.0,
        "start_frame": 231000,
        "end_frame": 234300,
        "duration_frames": 3300,
    },
    {
        "index": 21,
        "name": "จานตกน้ำหมดครัวนาทีสุดท้าย_Overcooked-vdo",
        "mediapool_id": "407b877a-89c8-42b1-bc6d-71fbcd5fb6d1",
        "worker_timeline_id": "d46db32c-6d6f-4b22-bdaf-dfc71fba0c58",
        "game": "Overcooked",
        "source_file": "เมื่อไทกะคือความชิบหายในครัว!.mp4",
        "start_sec": 9030.0,
        "end_sec": 9085.0,
        "start_frame": 541800,
        "end_frame": 545100,
        "duration_frames": 3300,
    },
]


@pytest.fixture(scope="session")
def resolve_context():
    """Connect to live DaVinci Resolve Studio and return active project."""
    resolve = dvr.scriptapp("Resolve")
    assert resolve is not None, "FATAL: Could not connect to live DaVinci Resolve process!"
    pm = resolve.GetProjectManager()
    assert pm is not None, "FATAL: GetProjectManager() returned None!"
    project = pm.GetCurrentProject()
    assert project is not None, "FATAL: GetCurrentProject() returned None! No project open."
    return {"resolve": resolve, "pm": pm, "project": project}


def test_1_resolve_connection_and_project_state(resolve_context):
    """Stress-test project identity, frame rate, and unmocked environment."""
    project = resolve_context["project"]
    project_name = project.GetName()
    project_id = project.GetUniqueId()
    fps_val = project.GetSetting("timelineFrameRate")

    print(f"\n[Resolve Connection] Project Name: {project_name}, ID: {project_id}, FPS: {fps_val}")
    assert project_name == EXPECTED_PROJECT_NAME, f"Project name mismatch: {project_name} != {EXPECTED_PROJECT_NAME}"
    assert project_id == EXPECTED_PROJECT_ID, f"Project ID mismatch: {project_id} != {EXPECTED_PROJECT_ID}"
    assert float(fps_val) == EXPECTED_FPS, f"Project timelineFrameRate mismatch: {fps_val} != {EXPECTED_FPS}"


def test_2_timeline_inventory_counts_and_uniqueness(resolve_context):
    """Stress-test timeline count (28 total), unique IDs, and zero collision."""
    project = resolve_context["project"]
    total_timelines = project.GetTimelineCount()
    print(f"\n[Timeline Inventory] Total timeline count: {total_timelines}")
    assert total_timelines == 28, f"Expected exactly 28 timelines (7 prior + 21 new), got {total_timelines}"

    timeline_map = {}
    timeline_ids = set()
    all_names = set()

    for idx in range(1, total_timelines + 1):
        tl = project.GetTimelineByIndex(idx)
        assert tl is not None, f"GetTimelineByIndex({idx}) returned None!"
        name = tl.GetName()
        tl_id = tl.GetUniqueId()

        assert tl_id not in timeline_ids, f"DUPLICATE TIMELINE ID DETECTED: {tl_id} for timeline '{name}'!"
        assert name not in all_names, f"DUPLICATE TIMELINE NAME DETECTED: '{name}'!"
        timeline_ids.add(tl_id)
        all_names.add(name)
        timeline_map[name] = tl

    assert len(timeline_ids) == 28, f"Timeline IDs count {len(timeline_ids)} != 28"
    assert len(all_names) == 28, f"Timeline names count {len(all_names)} != 28"

    # Verify all 7 prior timelines exist and were not overwritten
    for prior_name in EXPECTED_PRIOR_TIMELINE_NAMES:
        assert prior_name in timeline_map, f"Prior timeline '{prior_name}' missing from project!"

    # Verify all 21 new candidate timelines exist
    for cand in CANDIDATES:
        c_name = cand["name"]
        assert c_name in timeline_map, f"Candidate timeline '{c_name}' missing from project!"


def test_3_naming_convention_adversarial_regex(resolve_context):
    """Stress-test 21 new timeline names against regex and 0 ASCII in Thai prefix."""
    project = resolve_context["project"]

    for cand in CANDIDATES:
        c_name = cand["name"]
        match = TIMELINE_NAME_REGEX.match(c_name)
        assert match is not None, f"Timeline name '{c_name}' failed regex ^([^\\x00-\\x7F]+)_([A-Za-z0-9]+)-vdo$"

        thai_prefix, game_part = match.groups()

        # Adversarial check 1: ZERO ASCII letters or symbols in Thai prefix
        ascii_in_thai = [c for c in thai_prefix if ord(c) <= 127]
        assert len(ascii_in_thai) == 0, f"Found ASCII characters {ascii_in_thai} in Thai prefix of '{c_name}'!"

        # Adversarial check 2: Every character in Thai prefix must be in Thai Unicode range (\u0E00-\u0E7F)
        non_thai = [c for c in thai_prefix if not ('\u0E00' <= c <= '\u0E7F')]
        assert len(non_thai) == 0, f"Found non-Thai Unicode characters {non_thai} in Thai prefix of '{c_name}'!"

        # Adversarial check 3: No spaces or control characters
        assert " " not in thai_prefix, f"Whitespace found in Thai prefix of '{c_name}'"
        assert "\t" not in thai_prefix and "\n" not in thai_prefix

        # Adversarial check 4: Game part matches expected
        assert game_part == cand["game"], f"Game tag mismatch in '{c_name}': expected {cand['game']}, got {game_part}"

        # Adversarial check 5: Suffix ends with '-vdo'
        assert c_name.endswith("-vdo"), f"Suffix mismatch in '{c_name}'"


def test_4_durations_and_frame_bounds(resolve_context):
    """Stress-test duration: exactly 3300 frames, 55.0s, strictly within 30s-180s."""
    project = resolve_context["project"]

    for cand in CANDIDATES:
        c_name = cand["name"]
        tl = None
        for i in range(1, project.GetTimelineCount() + 1):
            t = project.GetTimelineByIndex(i)
            if t.GetName() == c_name:
                tl = t
                break
        assert tl is not None, f"Could not find timeline '{c_name}'"

        start_frame = tl.GetStartFrame()
        end_frame = tl.GetEndFrame()
        duration_frames = end_frame - start_frame
        duration_sec = duration_frames / EXPECTED_FPS

        assert duration_frames == EXPECTED_DURATION_FRAMES, (
            f"Timeline '{c_name}' duration mismatch: {duration_frames} != {EXPECTED_DURATION_FRAMES} frames "
            f"(start: {start_frame}, end: {end_frame})"
        )
        assert abs(duration_sec - EXPECTED_DURATION_SEC) < 1e-4, (
            f"Timeline '{c_name}' duration in sec mismatch: {duration_sec} != {EXPECTED_DURATION_SEC}s"
        )
        assert MIN_DURATION_SEC <= duration_sec <= MAX_DURATION_SEC, (
            f"Timeline '{c_name}' duration {duration_sec}s outside allowed bounds [30s, 180s]"
        )


def test_5_tracks_and_clip_boundaries(resolve_context):
    """Stress-test track layout: V1 has exactly 1 clip, no gaps, exact source trim frames."""
    project = resolve_context["project"]

    for cand in CANDIDATES:
        c_name = cand["name"]
        tl = None
        for i in range(1, project.GetTimelineCount() + 1):
            t = project.GetTimelineByIndex(i)
            if t.GetName() == c_name:
                tl = t
                break
        assert tl is not None

        video_track_count = tl.GetTrackCount("video")
        assert video_track_count >= 1, f"Timeline '{c_name}' has 0 video tracks!"

        items = tl.GetItemListInTrack("video", 1)
        assert items is not None, f"GetItemListInTrack('video', 1) returned None for '{c_name}'"
        assert len(items) == 1, (
            f"Timeline '{c_name}' V1 expected exactly 1 item, found {len(items)} items! "
            f"(Gap fragmentation or empty track)"
        )

        item = items[0]
        item_start = item.GetStart()
        item_end = item.GetEnd()
        item_duration = item.GetDuration()

        tl_start = tl.GetStartFrame()
        tl_end = tl.GetEndFrame()

        assert item_start == tl_start, (
            f"Clip start {item_start} does not align with timeline start {tl_start} in '{c_name}'"
        )
        assert item_end == tl_end, (
            f"Clip end {item_end} does not align with timeline end {tl_end} in '{c_name}'"
        )
        assert item_duration == EXPECTED_DURATION_FRAMES, (
            f"Clip duration {item_duration} != {EXPECTED_DURATION_FRAMES} in '{c_name}'"
        )

        # Source trim bounds verification
        src_start = item.GetSourceStartFrame()
        src_end = item.GetSourceEndFrame()
        assert src_start == cand["start_frame"], (
            f"SourceStartFrame mismatch in '{c_name}': expected {cand['start_frame']}, got {src_start}"
        )
        assert src_end == cand["end_frame"], (
            f"SourceEndFrame mismatch in '{c_name}': expected {cand['end_frame']}, got {src_end}"
        )
        assert (src_end - src_start) == EXPECTED_DURATION_FRAMES, (
            f"Source frame range {src_end - src_start} != {EXPECTED_DURATION_FRAMES} in '{c_name}'"
        )


def test_6_media_pool_items_and_file_existence(resolve_context):
    """Stress-test underlying MediaPoolItem reference, file existence, and zero offline media."""
    project = resolve_context["project"]

    for cand in CANDIDATES:
        c_name = cand["name"]
        tl = None
        for i in range(1, project.GetTimelineCount() + 1):
            t = project.GetTimelineByIndex(i)
            if t.GetName() == c_name:
                tl = t
                break
        assert tl is not None

        items = tl.GetItemListInTrack("video", 1)
        item = items[0]
        mpi = item.GetMediaPoolItem()
        assert mpi is not None, f"Item in '{c_name}' has NULL MediaPoolItem! (Disconnected clip)"

        mpi_id = mpi.GetUniqueId()
        assert mpi_id == cand["mediapool_id"], (
            f"MediaPoolItem ID mismatch in '{c_name}': expected {cand['mediapool_id']}, got {mpi_id}"
        )

        props = mpi.GetClipProperty()
        file_path = props.get("File Path")
        assert file_path, f"MediaPoolItem for '{c_name}' has empty 'File Path' property!"
        assert os.path.exists(file_path), f"Underlying media file DOES NOT EXIST ON DISK: {file_path}"
        assert os.path.getsize(file_path) > 0, f"Underlying media file is empty (0 bytes): {file_path}"

        # Zero offline media check
        clip_name = props.get("Clip Name", "")
        assert "offline" not in clip_name.lower(), f"Clip indicates offline media: {clip_name}"


def test_7_audio_tracks_and_sync(resolve_context):
    """Stress-test audio track presence and timeline alignment."""
    project = resolve_context["project"]

    for cand in CANDIDATES:
        c_name = cand["name"]
        tl = None
        for i in range(1, project.GetTimelineCount() + 1):
            t = project.GetTimelineByIndex(i)
            if t.GetName() == c_name:
                tl = t
                break
        assert tl is not None

        audio_track_count = tl.GetTrackCount("audio")
        assert audio_track_count >= 1, f"Timeline '{c_name}' has 0 audio tracks!"

        a_items = tl.GetItemListInTrack("audio", 1)
        assert a_items is not None and len(a_items) >= 1, f"Audio track 1 has 0 clips in '{c_name}'"
        a_item = a_items[0]

        assert a_item.GetStart() == tl.GetStartFrame(), (
            f"Audio clip start {a_item.GetStart()} does not match timeline start {tl.GetStartFrame()} in '{c_name}'"
        )
        assert a_item.GetDuration() == EXPECTED_DURATION_FRAMES, (
            f"Audio clip duration {a_item.GetDuration()} != {EXPECTED_DURATION_FRAMES} in '{c_name}'"
        )


def test_8_worker_report_honesty_audit(resolve_context):
    """Audit worker's handoff report claims against live Resolve object model."""
    project = resolve_context["project"]

    for cand in CANDIDATES:
        c_name = cand["name"]
        tl = None
        for i in range(1, project.GetTimelineCount() + 1):
            t = project.GetTimelineByIndex(i)
            if t.GetName() == c_name:
                tl = t
                break
        assert tl is not None

        actual_tl_id = tl.GetUniqueId()
        expected_tl_id = cand["worker_timeline_id"]
        assert actual_tl_id == expected_tl_id, (
            f"Worker report ID discrepancy for '{c_name}': reported '{expected_tl_id}', actual is '{actual_tl_id}'"
        )


def test_9_non_destructive_storage_invariant():
    """Verify that source footage directory was untouched (32 .mp4 files, no mutations)."""
    assert os.path.exists(MEDIA_STORAGE_DIR), f"Storage directory {MEDIA_STORAGE_DIR} does not exist!"
    files = [f for f in os.listdir(MEDIA_STORAGE_DIR) if f.lower().endswith(".mp4")]
    assert len(files) == 32, f"Expected 32 source mp4 files in {MEDIA_STORAGE_DIR}, found {len(files)}"

    for f in files:
        full_path = os.path.join(MEDIA_STORAGE_DIR, f)
        assert os.path.getsize(full_path) > 1_000_000, f"Source file {f} appears truncated or corrupt!"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
