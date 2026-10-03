"""
Independent Victory Audit Script
Written and executed independently by Victory Auditor 2.
Directly probes DaVinci Resolve Studio and filesystem.
"""
import sys
import os
import json
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')


# Resolve API path
RESOLVE_SCRIPT_API_DIR = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"
if RESOLVE_SCRIPT_API_DIR not in sys.path:
    sys.path.append(RESOLVE_SCRIPT_API_DIR)

import DaVinciResolveScript as dvr

EXPECTED_PROJECT = "tygarina_2026-09-30"
EXPECTED_FPS = 60.0
STORAGE_DIR = r"C:\Users\warit\SynologyDrive\Tygarina\2026-09-30"
WORKFLOW_START_TIME = datetime.fromisoformat("2026-10-02T02:21:27+00:00")

EXPECTED_CANDIDATES = {
    "Highlight_Gaming_REPO_Jumpscare": {
        "category": "Gaming",
        "source_file": "Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4",
        "start_sec": 6720.0,
        "end_sec": 6785.0,
        "duration_sec": 65.0,
        "start_frame": 403200,
        "end_frame": 407100,
        "duration_frames": 3900
    },
    "Highlight_Gaming_Climbing_Clutch": {
        "category": "Gaming",
        "source_file": "ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4",
        "start_sec": 5855.0,
        "end_sec": 5915.0,
        "duration_sec": 60.0,
        "start_frame": 351300,
        "end_frame": 354900,
        "duration_frames": 3600
    },
    "Highlight_Gaming_Ib_Horror": {
        "category": "Gaming",
        "source_file": "IB - สำรวจโลกภาพวาด P1.mp4",
        "start_sec": 4475.0,
        "end_sec": 4530.0,
        "duration_sec": 55.0,
        "start_frame": 268500,
        "end_frame": 271800,
        "duration_frames": 3300
    },
    "Highlight_Fun_DnD_Bard": {
        "category": "Fun",
        "source_file": "After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4",
        "start_sec": 980.0,
        "end_sec": 1035.0,
        "duration_sec": 55.0,
        "start_frame": 58800,
        "end_frame": 62100,
        "duration_frames": 3300
    },
    "Highlight_Meme_GarticPhone_Art": {
        "category": "Meme",
        "source_file": "Gartic phone - ไทกะสกิลวาดรูป 999999.mp4",
        "start_sec": 2510.0,
        "end_sec": 2575.0,
        "duration_sec": 65.0,
        "start_frame": 150600,
        "end_frame": 154500,
        "duration_frames": 3900
    },
    "Highlight_Meme_FreeTalk_Tiger": {
        "category": "Meme",
        "source_file": "Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4",
        "start_sec": 2235.0,
        "end_sec": 2295.0,
        "duration_sec": 60.0,
        "start_frame": 134100,
        "end_frame": 137700,
        "duration_frames": 3600
    },
    "Highlight_Fun_Overcooked_KitchenFire": {
        "category": "Fun/Gaming",
        "source_file": "เมื่อไทกะคือความชิบหายในครัว!.mp4",
        "start_sec": 7640.0,
        "end_sec": 7705.0,
        "duration_sec": 65.0,
        "start_frame": 458400,
        "end_frame": 462300,
        "duration_frames": 3900
    }
}

def run_independent_audit():
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "resolve_connected": False,
        "project_verified": False,
        "timelines_verified": False,
        "storage_verified": False,
        "verdict": "REJECT",
        "details": {}
    }
    
    # 1. Connect to Resolve
    resolve = dvr.scriptapp("Resolve")
    if not resolve:
        results["details"]["error"] = "Could not connect to DaVinciResolveScript"
        return results
    results["resolve_connected"] = True
    
    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    if not proj or proj.GetName() != EXPECTED_PROJECT:
        results["details"]["error"] = f"Expected project {EXPECTED_PROJECT}, got {proj.GetName() if proj else None}"
        return results
        
    fps = float(proj.GetSetting("timelineFrameRate"))
    if fps != EXPECTED_FPS:
        results["details"]["error"] = f"Expected fps {EXPECTED_FPS}, got {fps}"
        return results
    results["project_verified"] = True
    
    # 2. Inspect Timelines
    tl_count = proj.GetTimelineCount()
    if tl_count != len(EXPECTED_CANDIDATES):
        results["details"]["error"] = f"Expected {len(EXPECTED_CANDIDATES)} timelines, got {tl_count}"
        return results
        
    tl_map = {}
    for i in range(1, tl_count + 1):
        tl = proj.GetTimelineByIndex(i)
        tl_map[tl.GetName()] = tl
        
    timelines_detail = {}
    all_tl_ok = True
    for name, spec in EXPECTED_CANDIDATES.items():
        if name not in tl_map:
            all_tl_ok = False
            timelines_detail[name] = {"error": "Missing timeline"}
            continue
            
        tl = tl_map[name]
        start_frame = tl.GetStartFrame()
        end_frame = tl.GetEndFrame()
        duration_frames = end_frame - start_frame
        duration_sec = duration_frames / EXPECTED_FPS
        
        # Check strict duration bounds 30s to 180s
        duration_valid = (30.0 <= duration_sec <= 180.0) and (duration_frames == spec["duration_frames"])
        
        # Check video and audio tracks
        v_items = tl.GetItemListInTrack("video", 1) or []
        a_items = tl.GetItemListInTrack("audio", 1) or []
        track_ok = (len(v_items) == 1) and (len(a_items) == 1)
        
        v_item = v_items[0] if v_items else None
        v_mpi = v_item.GetMediaPoolItem() if v_item else None
        v_file = v_mpi.GetClipProperty("File Path") if v_mpi else ""
        
        # Check source boundaries
        s_start = v_item.GetSourceStartFrame() if v_item else -1
        s_end = v_item.GetSourceEndFrame() if v_item else -1
        l_offset = v_item.GetLeftOffset() if v_item else -1
        r_offset = v_item.GetRightOffset() if v_item else -1
        
        boundaries_ok = (s_start == spec["start_frame"]) and (s_end == spec["end_frame"])
        source_file_ok = os.path.basename(v_file) == spec["source_file"]
        
        tl_status = duration_valid and track_ok and boundaries_ok and source_file_ok
        if not tl_status:
            all_tl_ok = False
            
        timelines_detail[name] = {
            "status": "PASS" if tl_status else "FAIL",
            "category": spec["category"],
            "duration_sec": duration_sec,
            "duration_frames": duration_frames,
            "source_start": s_start,
            "source_end": s_end,
            "left_offset": l_offset,
            "right_offset": r_offset,
            "source_file": os.path.basename(v_file),
            "file_exists": os.path.exists(v_file),
            "duration_valid_30s_to_180s": duration_valid,
            "track_ok": track_ok,
            "boundaries_ok": boundaries_ok,
            "source_file_ok": source_file_ok
        }
        
    results["details"]["timelines"] = timelines_detail
    results["timelines_verified"] = all_tl_ok
    
    # 3. Check Storage Invariants
    files = [f for f in os.listdir(STORAGE_DIR) if f.lower().endswith(".mp4")]
    storage_ok = True
    storage_details = {
        "file_count": len(files),
        "total_bytes": sum(os.path.getsize(os.path.join(STORAGE_DIR, f)) for f in files),
        "modified_after_start": []
    }
    
    for f in files:
        fpath = os.path.join(STORAGE_DIR, f)
        mtime = datetime.fromtimestamp(os.path.getmtime(fpath), tz=datetime.now().astimezone().tzinfo)
        # Check if modified after workflow started
        if mtime > WORKFLOW_START_TIME:
            storage_ok = False
            storage_details["modified_after_start"].append({"file": f, "mtime": mtime.isoformat()})
            
    if len(files) != 32 or storage_details["total_bytes"] != 74624842819:
        storage_ok = False
        
    storage_details["storage_ok"] = storage_ok
    results["details"]["storage"] = storage_details
    results["storage_verified"] = storage_ok
    
    if results["project_verified"] and results["timelines_verified"] and results["storage_verified"]:
        results["verdict"] = "CONFIRMED"
        
    return results

if __name__ == "__main__":
    res = run_independent_audit()
    out_path = r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\victory_auditor_2\independent_audit_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    print(f"Independent Audit Completed. Verdict: {res['verdict']}")
    print(json.dumps(res, indent=2, ensure_ascii=False))
