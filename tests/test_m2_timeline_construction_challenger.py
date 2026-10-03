"""
Empirical Challenger Verification & Stress Test Suite for Milestone M2:
DaVinci Resolve Highlight Timeline Construction in Project 'tygarina_2026-09-30'.

Challenger 1 (challenger_m2_1)
Persona: EMPIRICAL CHALLENGER (critic, specialist)
"""
import os
import sys
import pytest

# Ensure DaVinciResolveScript is in path
RESOLVE_SCRIPT_API_DIR = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"
if RESOLVE_SCRIPT_API_DIR not in sys.path:
    sys.path.append(RESOLVE_SCRIPT_API_DIR)

import DaVinciResolveScript as dvr

MEDIA_STORAGE_DIR = r"C:\Users\warit\SynologyDrive\Tygarina\2026-09-30"
EXPECTED_PROJECT_NAME = "tygarina_2026-09-30"
EXPECTED_FPS = 60.0

CANDIDATES = [
    {
        "id": "H1",
        "category": "Gaming",
        "name": "Highlight_Gaming_REPO_Jumpscare",
        "source_file": "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4",
        "start_sec": 6720.0,
        "end_sec": 6785.0,
        "duration_sec": 65.0,
        "start_frame": 403200,
        "end_frame": 407100,
        "duration_frames": 3900,
    },
    {
        "id": "H2",
        "category": "Gaming",
        "name": "Highlight_Gaming_Climbing_Clutch",
        "source_file": "ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4",
        "start_sec": 5855.0,
        "end_sec": 5915.0,
        "duration_sec": 60.0,
        "start_frame": 351300,
        "end_frame": 354900,
        "duration_frames": 3600,
    },
    {
        "id": "H3",
        "category": "Gaming",
        "name": "Highlight_Gaming_Ib_Horror",
        "source_file": "IB - สำรวจโลกภาพวาด P1.mp4",
        "start_sec": 4475.0,
        "end_sec": 4530.0,
        "duration_sec": 55.0,
        "start_frame": 268500,
        "end_frame": 271800,
        "duration_frames": 3300,
    },
    {
        "id": "H4",
        "category": "Fun",
        "name": "Highlight_Fun_DnD_Bard",
        "source_file": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4",
        "start_sec": 980.0,
        "end_sec": 1035.0,
        "duration_sec": 55.0,
        "start_frame": 58800,
        "end_frame": 62100,
        "duration_frames": 3300,
    },
    {
        "id": "H5",
        "category": "Meme",
        "name": "Highlight_Meme_GarticPhone_Art",
        "source_file": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4",
        "start_sec": 2510.0,
        "end_sec": 2575.0,
        "duration_sec": 65.0,
        "start_frame": 150600,
        "end_frame": 154500,
        "duration_frames": 3900,
    },
    {
        "id": "H6",
        "category": "Meme",
        "name": "Highlight_Meme_FreeTalk_Tiger",
        "source_file": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4",
        "start_sec": 2235.0,
        "end_sec": 2295.0,
        "duration_sec": 60.0,
        "start_frame": 134100,
        "end_frame": 137700,
        "duration_frames": 3600,
    },
    {
        "id": "H7",
        "category": "Fun/Gaming",
        "name": "Highlight_Fun_Overcooked_KitchenFire",
        "source_file": "เมื่อไทกะคือความชิบหายในครัว!.mp4",
        "start_sec": 7640.0,
        "end_sec": 7705.0,
        "duration_sec": 65.0,
        "start_frame": 458400,
        "end_frame": 462300,
        "duration_frames": 3900,
    },
]


@pytest.fixture(scope="session")
def resolve_app():
    resolve = dvr.scriptapp("Resolve")
    assert resolve is not None, "Failed to connect to DaVinci Resolve scriptapp"
    return resolve


@pytest.fixture(scope="session")
def current_project(resolve_app):
    pm = resolve_app.GetProjectManager()
    assert pm is not None, "Failed to get ProjectManager"
    proj = pm.GetCurrentProject()
    assert proj is not None, "No active project currently open in Resolve"
    assert proj.GetName() == EXPECTED_PROJECT_NAME, (
        f"Active project mismatch: expected '{EXPECTED_PROJECT_NAME}', got '{proj.GetName()}'"
    )
    return proj


@pytest.fixture(scope="session")
def timelines_map(current_project):
    count = current_project.GetTimelineCount()
    mapping = {}
    for i in range(1, count + 1):
        tl = current_project.GetTimelineByIndex(i)
        assert tl is not None, f"Timeline at index {i} returned None"
        mapping[tl.GetName()] = tl
    return mapping


def test_project_configuration(current_project):
    """Verify project name, timeline count, and project frame rate."""
    assert current_project.GetName() == EXPECTED_PROJECT_NAME
    assert current_project.GetTimelineCount() == 7, (
        f"Expected exactly 7 timelines, found {current_project.GetTimelineCount()}"
    )
    fps_setting = current_project.GetSetting("timelineFrameRate")
    assert float(fps_setting) == EXPECTED_FPS, (
        f"Project timelineFrameRate must be {EXPECTED_FPS}, got {fps_setting}"
    )


def test_all_expected_timelines_exist(timelines_map):
    """Verify all 7 expected timeline names are present and no missing or ghost timelines."""
    expected_names = {c["name"] for c in CANDIDATES}
    actual_names = set(timelines_map.keys())
    assert actual_names == expected_names, (
        f"Timelines mismatch! Missing: {expected_names - actual_names}, Unexpected: {actual_names - expected_names}"
    )


@pytest.mark.parametrize("cand", CANDIDATES, ids=[c["id"] for c in CANDIDATES])
def test_timeline_duration_boundaries_strict(timelines_map, cand):
    """
    Assert strictly that 30.0s <= duration <= 180.0s for every single timeline,
    and verify exact frame duration against candidate specification.
    """
    tl = timelines_map[cand["name"]]
    start_frame = tl.GetStartFrame()
    end_frame = tl.GetEndFrame()
    duration_frames = end_frame - start_frame
    duration_sec = duration_frames / EXPECTED_FPS

    # Strict constraint from prompt
    assert 30.0 <= duration_sec <= 180.0, (
        f"[{cand['id']}] Timeline '{cand['name']}' duration {duration_sec:.2f}s violates [30.0s, 180.0s]"
    )
    assert 1800 <= duration_frames <= 10800, (
        f"[{cand['id']}] Timeline '{cand['name']}' frame duration {duration_frames} violates [1800, 10800]"
    )

    # Exact duration match with candidate spec
    assert duration_frames == cand["duration_frames"], (
        f"[{cand['id']}] Expected {cand['duration_frames']} frames, got {duration_frames}"
    )
    assert duration_sec == pytest.approx(cand["duration_sec"], abs=1e-4), (
        f"[{cand['id']}] Expected {cand['duration_sec']}s, got {duration_sec}s"
    )


@pytest.mark.parametrize("cand", CANDIDATES, ids=[c["id"] for c in CANDIDATES])
def test_track_structure_and_clip_count(timelines_map, cand):
    """
    Verify video and audio tracks, ensuring video track 1 has exactly 1 item
    and no orphaned or extra clips on subsequent tracks.
    """
    tl = timelines_map[cand["name"]]
    v_track_count = tl.GetTrackCount("video")
    a_track_count = tl.GetTrackCount("audio")

    assert v_track_count >= 1, f"[{cand['id']}] Missing video tracks: {v_track_count}"
    assert a_track_count >= 1, f"[{cand['id']}] Missing audio tracks: {a_track_count}"

    v_items = tl.GetItemListInTrack("video", 1)
    assert v_items is not None and len(v_items) == 1, (
        f"[{cand['id']}] Video Track 1 must contain exactly 1 item, got {len(v_items) if v_items else 0}"
    )

    a_items = tl.GetItemListInTrack("audio", 1)
    assert a_items is not None and len(a_items) == 1, (
        f"[{cand['id']}] Audio Track 1 must contain exactly 1 item, got {len(a_items) if a_items else 0}"
    )

    # Check that video tracks > 1 are empty
    for vt in range(2, v_track_count + 1):
        extra_items = tl.GetItemListInTrack("video", vt)
        assert not extra_items, f"[{cand['id']}] Unexpected items on Video Track {vt}: {extra_items}"


@pytest.mark.parametrize("cand", CANDIDATES, ids=[c["id"] for c in CANDIDATES])
def test_timeline_item_boundaries_and_offsets(timelines_map, cand):
    """
    Stress-test timeline item start, end, duration, left offset, right offset,
    and verify zero dropped frames and absence of off-by-one errors.
    """
    tl = timelines_map[cand["name"]]
    v_item = tl.GetItemListInTrack("video", 1)[0]
    a_item = tl.GetItemListInTrack("audio", 1)[0]

    # Timeline record coordinates
    tl_start = tl.GetStartFrame()
    tl_end = tl.GetEndFrame()
    tl_duration = tl_end - tl_start

    # Item record coordinates
    item_start = v_item.GetStart()
    item_end = v_item.GetEnd()
    item_duration = v_item.GetDuration()

    assert item_start == tl_start, (
        f"[{cand['id']}] Video item start ({item_start}) does not align with timeline start ({tl_start})"
    )
    assert item_end == tl_end, (
        f"[{cand['id']}] Video item end ({item_end}) does not align with timeline end ({tl_end})"
    )
    assert item_duration == tl_duration, (
        f"[{cand['id']}] Video item duration ({item_duration}) != timeline duration ({tl_duration})"
    )
    assert item_duration == cand["duration_frames"], (
        f"[{cand['id']}] Video item duration ({item_duration}) != candidate duration ({cand['duration_frames']})"
    )

    # Source frame offsets
    source_start = v_item.GetSourceStartFrame()
    source_end = v_item.GetSourceEndFrame()
    left_offset = v_item.GetLeftOffset()
    right_offset = v_item.GetRightOffset()

    assert source_start == cand["start_frame"], (
        f"[{cand['id']}] Source start frame mismatch: expected {cand['start_frame']}, got {source_start}"
    )
    assert source_end == cand["end_frame"], (
        f"[{cand['id']}] Source end frame mismatch: expected {cand['end_frame']}, got {source_end}"
    )
    assert (source_end - source_start) == cand["duration_frames"], (
        f"[{cand['id']}] Source interval ({source_end} - {source_start} = {source_end - source_start}) != {cand['duration_frames']}"
    )

    # Offset validity
    assert left_offset == cand["start_frame"], (
        f"[{cand['id']}] LeftOffset ({left_offset}) != start_frame ({cand['start_frame']})"
    )
    assert left_offset >= 0, f"[{cand['id']}] Negative LeftOffset detected: {left_offset}"
    assert right_offset >= 0, f"[{cand['id']}] Negative RightOffset detected: {right_offset}"

    # Audio/Video perfect alignment
    assert a_item.GetStart() == item_start, f"[{cand['id']}] Audio/Video start mismatch"
    assert a_item.GetEnd() == item_end, f"[{cand['id']}] Audio/Video end mismatch"
    assert a_item.GetDuration() == item_duration, f"[{cand['id']}] Audio/Video duration mismatch"
    assert a_item.GetSourceStartFrame() == source_start, f"[{cand['id']}] Audio/Video source start mismatch"
    assert a_item.GetSourceEndFrame() == source_end, f"[{cand['id']}] Audio/Video source end mismatch"


@pytest.mark.parametrize("cand", CANDIDATES, ids=[c["id"] for c in CANDIDATES])
def test_underlying_media_pool_item(timelines_map, cand):
    """
    Verify underlying MediaPoolItem resolution, source file path, and format properties.
    """
    tl = timelines_map[cand["name"]]
    v_item = tl.GetItemListInTrack("video", 1)[0]
    mpi = v_item.GetMediaPoolItem()

    assert mpi is not None, f"[{cand['id']}] Video item GetMediaPoolItem() returned None!"
    assert mpi.GetName() == cand["source_file"], (
        f"[{cand['id']}] MediaPoolItem name '{mpi.GetName()}' != expected '{cand['source_file']}'"
    )

    clip_props = mpi.GetClipProperty()
    file_path = clip_props.get("File Path")
    assert file_path is not None, f"[{cand['id']}] ClipProperty 'File Path' is missing"

    expected_file_path = os.path.join(MEDIA_STORAGE_DIR, cand["source_file"])
    assert os.path.normpath(file_path).lower() == os.path.normpath(expected_file_path).lower(), (
        f"[{cand['id']}] File path mismatch: expected '{expected_file_path}', got '{file_path}'"
    )

    # Check physical existence of source file
    assert os.path.isfile(file_path), f"[{cand['id']}] Source file on disk does not exist: {file_path}"
    assert os.path.getsize(file_path) > 0, f"[{cand['id']}] Source file is empty: {file_path}"

    # FPS property
    clip_fps = float(clip_props.get("FPS", 0))
    assert clip_fps == EXPECTED_FPS, f"[{cand['id']}] Clip FPS {clip_fps} != {EXPECTED_FPS}"


def test_non_destructive_media_invariants():
    """Verify that source media directory remains strictly intact and unmodified."""
    assert os.path.isdir(MEDIA_STORAGE_DIR), f"Media dir not found: {MEDIA_STORAGE_DIR}"
    files = [f for f in os.listdir(MEDIA_STORAGE_DIR) if f.endswith(".mp4")]
    assert len(files) == 32, f"Expected 32 .mp4 source files, found {len(files)}"

    total_size = sum(os.path.getsize(os.path.join(MEDIA_STORAGE_DIR, f)) for f in files)
    assert total_size == 74624842819, f"Total byte size mismatch: {total_size}"


def test_no_spurious_markers_or_fusion_comps(timelines_map):
    """Verify timelines and items are clean of unexpected markers, fusion comps, or effects."""
    for cand in CANDIDATES:
        tl = timelines_map[cand["name"]]
        assert tl.GetMarkers() == {}, f"[{cand['id']}] Unexpected timeline markers: {tl.GetMarkers()}"
        v_item = tl.GetItemListInTrack("video", 1)[0]
        assert v_item.GetMarkers() == {}, f"[{cand['id']}] Unexpected video item markers: {v_item.GetMarkers()}"
        assert v_item.GetFusionCompCount() == 0, (
            f"[{cand['id']}] Unexpected fusion comps: {v_item.GetFusionCompCount()}"
        )
