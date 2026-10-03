"""
Challenger 2: Empirical Stress Test Suite for DaVinci Resolve Highlight Timelines.
Objective:
1. Verify all 32 source video files remain 100% untouched.
2. Test timeline switching and current timeline retrieval across all 7 highlight timelines.
3. Verify video and audio track structure, precise frame boundaries, and audio/video alignment.
4. Confirm zero media offline items.
"""
import sys
import os
import json
from datetime import datetime
import pytest

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules')
import DaVinciResolveScript as dvr

EXPECTED_HIGHLIGHTS = [
    {
        "id": "H1",
        "category": "Gaming",
        "timeline_name": "Highlight_Gaming_REPO_Jumpscare",
        "source_file": "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4",
        "start_sec": 6720.0,
        "end_sec": 6785.0,
        "duration_sec": 65.0,
        "start_frame": 403200,
        "end_frame": 407100,
        "duration_frames": 3900
    },
    {
        "id": "H2",
        "category": "Gaming",
        "timeline_name": "Highlight_Gaming_Climbing_Clutch",
        "source_file": "ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4",
        "start_sec": 5855.0,
        "end_sec": 5915.0,
        "duration_sec": 60.0,
        "start_frame": 351300,
        "end_frame": 354900,
        "duration_frames": 3600
    },
    {
        "id": "H3",
        "category": "Gaming",
        "timeline_name": "Highlight_Gaming_Ib_Horror",
        "source_file": "IB - สำรวจโลกภาพวาด P1.mp4",
        "start_sec": 4475.0,
        "end_sec": 4530.0,
        "duration_sec": 55.0,
        "start_frame": 268500,
        "end_frame": 271800,
        "duration_frames": 3300
    },
    {
        "id": "H4",
        "category": "Fun",
        "timeline_name": "Highlight_Fun_DnD_Bard",
        "source_file": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4",
        "start_sec": 980.0,
        "end_sec": 1035.0,
        "duration_sec": 55.0,
        "start_frame": 58800,
        "end_frame": 62100,
        "duration_frames": 3300
    },
    {
        "id": "H5",
        "category": "Meme",
        "timeline_name": "Highlight_Meme_GarticPhone_Art",
        "source_file": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4",
        "start_sec": 2510.0,
        "end_sec": 2575.0,
        "duration_sec": 65.0,
        "start_frame": 150600,
        "end_frame": 154500,
        "duration_frames": 3900
    },
    {
        "id": "H6",
        "category": "Meme",
        "timeline_name": "Highlight_Meme_FreeTalk_Tiger",
        "source_file": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4",
        "start_sec": 2235.0,
        "end_sec": 2295.0,
        "duration_sec": 60.0,
        "start_frame": 134100,
        "end_frame": 137700,
        "duration_frames": 3600
    },
    {
        "id": "H7",
        "category": "Fun/Gaming",
        "timeline_name": "Highlight_Fun_Overcooked_KitchenFire",
        "source_file": "เมื่อไทกะคือความชิบหายในครัว!.mp4",
        "start_sec": 7640.0,
        "end_sec": 7705.0,
        "duration_sec": 65.0,
        "start_frame": 458400,
        "end_frame": 462300,
        "duration_frames": 3900
    }
]

SOURCE_DIR = r"C:\Users\warit\SynologyDrive\Tygarina\2026-09-30"

@pytest.fixture(scope="module")
def resolve_context():
    """Connect to DaVinci Resolve and yield project context, restoring original timeline on exit."""
    resolve = dvr.scriptapp('Resolve')
    assert resolve is not None, "Failed to connect to DaVinci Resolve"
    pm = resolve.GetProjectManager()
    assert pm is not None, "Failed to get ProjectManager"
    proj = pm.GetCurrentProject()
    assert proj is not None, "No active project in DaVinci Resolve"
    
    initial_timeline = proj.GetCurrentTimeline()
    initial_name = initial_timeline.GetName() if initial_timeline else None
    
    yield {
        "resolve": resolve,
        "pm": pm,
        "proj": proj,
        "initial_timeline_name": initial_name
    }
    
    # Restore initial timeline if available
    if initial_name:
        for i in range(1, proj.GetTimelineCount() + 1):
            tl = proj.GetTimelineByIndex(i)
            if tl.GetName() == initial_name:
                proj.SetCurrentTimeline(tl)
                break
        pm.SaveProject()


def test_source_media_directory_integrity():
    """Test 1: Verify all 32 source video files remain 100% untouched."""
    assert os.path.exists(SOURCE_DIR), f"Source directory {SOURCE_DIR} does not exist"
    
    entries = os.listdir(SOURCE_DIR)
    assert len(entries) == 32, f"Expected exactly 32 entries in source directory, found {len(entries)}"
    
    # Verify no subdirectories exist
    for e in entries:
        full_path = os.path.join(SOURCE_DIR, e)
        assert os.path.isfile(full_path), f"Found subdirectory or non-file: {e}"
        assert e.endswith(".mp4"), f"Found non-mp4 file in source directory: {e}"
        
        # Verify file size > 0
        size = os.path.getsize(full_path)
        assert size > 0, f"Source file {e} has 0 bytes"
        
        # Verify file modification time is not recent (before 2026-10-02 07:00:00 UTC/local)
        mtime = datetime.fromtimestamp(os.path.getmtime(full_path))
        # Ensure mtime is before October 2, 2026 07:00:00 (task start was ~09:21 local time)
        cutoff = datetime(2026, 10, 2, 7, 0, 0)
        assert mtime < cutoff, f"Source file {e} was modified at {mtime}, which violates the non-destructive invariant!"


def test_resolve_project_invariants(resolve_context):
    """Test 2: Verify active project name, timeline count, and project frame rate."""
    proj = resolve_context["proj"]
    assert proj.GetName() == "tygarina_2026-09-30", f"Unexpected project name: {proj.GetName()}"
    assert proj.GetTimelineCount() == 7, f"Expected 7 timelines, got {proj.GetTimelineCount()}"
    
    fps = proj.GetSetting('timelineFrameRate')
    assert float(fps) == 60.0, f"Expected timelineFrameRate 60.0, got {fps}"


def test_timeline_switching_and_retrieval(resolve_context):
    """Test 3: Stress-test timeline switching and current timeline retrieval."""
    proj = resolve_context["proj"]
    timeline_count = proj.GetTimelineCount()
    timelines = [proj.GetTimelineByIndex(i) for i in range(1, timeline_count + 1)]
    
    # 1. Forward switching
    for tl in timelines:
        name = tl.GetName()
        unique_id = tl.GetUniqueId()
        success = proj.SetCurrentTimeline(tl)
        assert success is True, f"Failed to switch to timeline {name}"
        
        cur = proj.GetCurrentTimeline()
        assert cur is not None, f"GetCurrentTimeline() returned None after switching to {name}"
        assert cur.GetName() == name, f"Current timeline name mismatch: expected {name}, got {cur.GetName()}"
        assert cur.GetUniqueId() == unique_id, f"Current timeline ID mismatch for {name}"

    # 2. Reverse switching stress test
    for tl in reversed(timelines):
        name = tl.GetName()
        success = proj.SetCurrentTimeline(tl)
        assert success is True, f"Failed reverse switch to timeline {name}"
        cur = proj.GetCurrentTimeline()
        assert cur.GetName() == name, f"Reverse switch name mismatch: {name} vs {cur.GetName()}"


def test_timeline_items_and_audio_video_alignment(resolve_context):
    """Test 4: Verify track structure, duration, source frames, and video/audio alignment."""
    proj = resolve_context["proj"]
    
    # Map timelines by name
    timeline_map = {proj.GetTimelineByIndex(i).GetName(): proj.GetTimelineByIndex(i) 
                    for i in range(1, proj.GetTimelineCount() + 1)}
    
    for exp in EXPECTED_HIGHLIGHTS:
        tname = exp["timeline_name"]
        assert tname in timeline_map, f"Timeline {tname} not found"
        tl = timeline_map[tname]
        
        # Switch to timeline
        proj.SetCurrentTimeline(tl)
        cur = proj.GetCurrentTimeline()
        assert cur.GetName() == tname
        
        # Check timeline frame bounds
        start_f = tl.GetStartFrame()
        end_f = tl.GetEndFrame()
        duration_f = end_f - start_f
        duration_s = duration_f / 60.0
        
        assert duration_f == exp["duration_frames"], (
            f"Timeline {tname} duration {duration_f} frames does not match expected {exp['duration_frames']}"
        )
        assert 30.0 <= duration_s <= 180.0, (
            f"Timeline {tname} duration {duration_s}s outside [30s, 180s]"
        )
        
        # Check tracks
        v_track_count = tl.GetTrackCount("video")
        a_track_count = tl.GetTrackCount("audio")
        assert v_track_count >= 1, f"Timeline {tname} has {v_track_count} video tracks (expected >= 1)"
        assert a_track_count >= 1, f"Timeline {tname} has {a_track_count} audio tracks (expected >= 1)"
        
        # Check Video Track 1 Item
        v_items = tl.GetItemListInTrack("video", 1)
        assert len(v_items) == 1, f"Timeline {tname} video track 1 has {len(v_items)} items (expected 1)"
        v_item = v_items[0]
        assert v_item.GetName() == exp["source_file"], (
            f"Timeline {tname} video clip name mismatch: {v_item.GetName()} vs {exp['source_file']}"
        )
        assert v_item.GetStart() == 0, f"Timeline {tname} video item does not start at 0"
        assert v_item.GetDuration() == exp["duration_frames"], f"Timeline {tname} video item duration mismatch"
        assert v_item.GetSourceStartFrame() == exp["start_frame"], (
            f"Timeline {tname} video source start mismatch: {v_item.GetSourceStartFrame()} vs {exp['start_frame']}"
        )
        assert v_item.GetSourceEndFrame() == exp["end_frame"], (
            f"Timeline {tname} video source end mismatch: {v_item.GetSourceEndFrame()} vs {exp['end_frame']}"
        )
        
        # Check Audio Track 1 Item
        a_items = tl.GetItemListInTrack("audio", 1)
        assert len(a_items) == 1, f"Timeline {tname} audio track 1 has {len(a_items)} items (expected 1)"
        a_item = a_items[0]
        assert a_item.GetName() == exp["source_file"], (
            f"Timeline {tname} audio clip name mismatch: {a_item.GetName()} vs {exp['source_file']}"
        )
        assert a_item.GetStart() == 0, f"Timeline {tname} audio item does not start at 0"
        assert a_item.GetDuration() == exp["duration_frames"], f"Timeline {tname} audio item duration mismatch"
        assert a_item.GetSourceStartFrame() == exp["start_frame"], (
            f"Timeline {tname} audio source start mismatch: {a_item.GetSourceStartFrame()} vs {exp['start_frame']}"
        )
        assert a_item.GetSourceEndFrame() == exp["end_frame"], (
            f"Timeline {tname} audio source end mismatch: {a_item.GetSourceEndFrame()} vs {exp['end_frame']}"
        )
        
        # Audio / Video Alignment Check
        assert v_item.GetStart() == a_item.GetStart(), f"Timeline {tname} A/V start misaligned"
        assert v_item.GetEnd() == a_item.GetEnd(), f"Timeline {tname} A/V end misaligned"
        assert v_item.GetDuration() == a_item.GetDuration(), f"Timeline {tname} A/V duration misaligned"
        assert v_item.GetSourceStartFrame() == a_item.GetSourceStartFrame(), f"Timeline {tname} A/V source start misaligned"
        assert v_item.GetSourceEndFrame() == a_item.GetSourceEndFrame(), f"Timeline {tname} A/V source end misaligned"


def test_zero_media_offline(resolve_context):
    """Test 5: Verify zero media offline across all clips in all 7 timelines."""
    proj = resolve_context["proj"]
    timeline_count = proj.GetTimelineCount()
    
    for i in range(1, timeline_count + 1):
        tl = proj.GetTimelineByIndex(i)
        tname = tl.GetName()
        proj.SetCurrentTimeline(tl)
        
        # Check video items
        v_items = tl.GetItemListInTrack("video", 1) or []
        for v in v_items:
            mpi = v.GetMediaPoolItem()
            assert mpi is not None, f"Video item {v.GetName()} in {tname} has null MediaPoolItem"
            props = mpi.GetClipProperty()
            file_path = props.get("File Path", "")
            assert file_path != "", f"Video item {v.GetName()} in {tname} has empty File Path"
            assert os.path.exists(file_path), f"Video file {file_path} for {tname} does not exist on disk"
            
        # Check audio items
        a_items = tl.GetItemListInTrack("audio", 1) or []
        for a in a_items:
            mpi = a.GetMediaPoolItem()
            assert mpi is not None, f"Audio item {a.GetName()} in {tname} has null MediaPoolItem"
            props = mpi.GetClipProperty()
            file_path = props.get("File Path", "")
            assert file_path != "", f"Audio item {a.GetName()} in {tname} has empty File Path"
            assert os.path.exists(file_path), f"Audio file {file_path} for {tname} does not exist on disk"


def run_standalone():
    """Run verification standalone and generate json report."""
    resolve = dvr.scriptapp('Resolve')
    if not resolve:
        print("ERROR: Cannot connect to Resolve")
        return False
    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    if not proj:
        print("ERROR: No current project")
        return False
        
    initial_tl = proj.GetCurrentTimeline()
    initial_name = initial_tl.GetName() if initial_tl else None
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "source_dir": SOURCE_DIR,
        "project_name": proj.GetName(),
        "timeline_count": proj.GetTimelineCount(),
        "timeline_frame_rate": proj.GetSetting('timelineFrameRate'),
        "source_files_check": {},
        "switching_stress_test": {},
        "timelines_detail": [],
        "overall_verdict": "UNKNOWN"
    }
    
    # 1. Source Files Check
    entries = os.listdir(SOURCE_DIR)
    mp4_files = [f for f in entries if f.endswith(".mp4")]
    non_mp4 = [f for f in entries if not f.endswith(".mp4")]
    total_bytes = sum(os.path.getsize(os.path.join(SOURCE_DIR, f)) for f in mp4_files)
    
    mtimes = [datetime.fromtimestamp(os.path.getmtime(os.path.join(SOURCE_DIR, f))) for f in mp4_files]
    newest_mtime = max(mtimes) if mtimes else None
    
    cutoff = datetime(2026, 10, 2, 7, 0, 0)
    source_untouched = (len(entries) == 32 and len(non_mp4) == 0 and newest_mtime < cutoff)
    
    report["source_files_check"] = {
        "total_entries": len(entries),
        "mp4_count": len(mp4_files),
        "non_mp4_count": len(non_mp4),
        "total_bytes": total_bytes,
        "total_gib": round(total_bytes / (1024**3), 2),
        "newest_mtime": newest_mtime.isoformat() if newest_mtime else None,
        "cutoff_threshold": cutoff.isoformat(),
        "untouched_and_pristine": source_untouched
    }
    
    # 2. Timeline Switching Test
    timelines = [proj.GetTimelineByIndex(i) for i in range(1, proj.GetTimelineCount() + 1)]
    switching_passes = 0
    total_switches = len(timelines) * 2
    
    for tl in timelines:
        proj.SetCurrentTimeline(tl)
        cur = proj.GetCurrentTimeline()
        if cur and cur.GetName() == tl.GetName() and cur.GetUniqueId() == tl.GetUniqueId():
            switching_passes += 1
            
    for tl in reversed(timelines):
        proj.SetCurrentTimeline(tl)
        cur = proj.GetCurrentTimeline()
        if cur and cur.GetName() == tl.GetName() and cur.GetUniqueId() == tl.GetUniqueId():
            switching_passes += 1
            
    report["switching_stress_test"] = {
        "total_switches_tested": total_switches,
        "successful_switches": switching_passes,
        "passed": (switching_passes == total_switches)
    }
    
    # 3. Timelines Detail & Alignment Probe
    timeline_map = {tl.GetName(): tl for tl in timelines}
    all_tl_passed = True
    
    for exp in EXPECTED_HIGHLIGHTS:
        tname = exp["timeline_name"]
        tl = timeline_map.get(tname)
        if not tl:
            all_tl_passed = False
            continue
            
        proj.SetCurrentTimeline(tl)
        cur = proj.GetCurrentTimeline()
        
        start_f = tl.GetStartFrame()
        end_f = tl.GetEndFrame()
        dur_f = end_f - start_f
        dur_s = dur_f / 60.0
        
        v_items = tl.GetItemListInTrack("video", 1) or []
        a_items = tl.GetItemListInTrack("audio", 1) or []
        
        v_ok = len(v_items) == 1
        a_ok = len(a_items) == 1
        
        v_item = v_items[0] if v_ok else None
        a_item = a_items[0] if a_ok else None
        
        v_src_start = v_item.GetSourceStartFrame() if v_item else None
        v_src_end = v_item.GetSourceEndFrame() if v_item else None
        a_src_start = a_item.GetSourceStartFrame() if a_item else None
        a_src_end = a_item.GetSourceEndFrame() if a_item else None
        
        v_mpi = v_item.GetMediaPoolItem() if v_item else None
        a_mpi = a_item.GetMediaPoolItem() if a_item else None
        
        v_path = v_mpi.GetClipProperty().get("File Path") if v_mpi else None
        a_path = a_mpi.GetClipProperty().get("File Path") if a_mpi else None
        
        v_online = os.path.exists(v_path) if v_path else False
        a_online = os.path.exists(a_path) if a_path else False
        
        av_aligned = (
            v_ok and a_ok and
            v_item.GetStart() == a_item.GetStart() == 0 and
            v_item.GetEnd() == a_item.GetEnd() == dur_f and
            v_item.GetDuration() == a_item.GetDuration() == dur_f and
            v_src_start == a_src_start == exp["start_frame"] and
            v_src_end == a_src_end == exp["end_frame"]
        )
        
        dur_match = (dur_f == exp["duration_frames"] and 30.0 <= dur_s <= 180.0)
        
        tl_detail = {
            "id": exp["id"],
            "name": tname,
            "source_file": exp["source_file"],
            "duration_frames": dur_f,
            "duration_seconds": dur_s,
            "expected_frames": exp["duration_frames"],
            "video_clip": v_item.GetName() if v_item else None,
            "audio_clip": a_item.GetName() if a_item else None,
            "source_start_frame": v_src_start,
            "source_end_frame": v_src_end,
            "audio_video_aligned": av_aligned,
            "video_media_online": v_online,
            "audio_media_online": a_online,
            "passed": (dur_match and av_aligned and v_online and a_online)
        }
        
        if not tl_detail["passed"]:
            all_tl_passed = False
            
        report["timelines_detail"].append(tl_detail)
        
    # Restore initial timeline
    if initial_name and initial_name in timeline_map:
        proj.SetCurrentTimeline(timeline_map[initial_name])
    pm.SaveProject()
    
    overall = (source_untouched and report["switching_stress_test"]["passed"] and all_tl_passed)
    report["overall_verdict"] = "APPROVE" if overall else "REQUEST_CHANGES"
    
    out_path = r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\challenger_m2_2\empirical_test_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Standalone execution completed. Saved report to {out_path}")
    print(f"Overall Verdict: {report['overall_verdict']}")
    return overall

if __name__ == "__main__":
    success = run_standalone()
    sys.exit(0 if success else 1)
