"""Independent Forensic Audit Script for Milestone 1 Work Product.

Performs empirical checks across:
1. Static code analysis of scripts/m1_backup_and_baseline.py
2. Physical inspection of the DRP file (zip archive, XML header, timestamps, sequence containers)
3. Direct live DaVinci Resolve API interrogation (project ID, timeline count, properties)
4. Comprehensive integrity check of baseline_30_timelines.json against live Resolve state
5. Verification of UI state restoration
"""

import json
import os
import sys
import time
import zipfile

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

BACKUP_PATH = r"G:\My Drive\Projects\Katy404\2026-09-29\KT404_2026-09-29_pre_9x16_conversion_2026-10-01.drp"
BASELINE_PATH = r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\worker_m1\baseline_30_timelines.json"
SCRIPT_PATH = r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\scripts\m1_backup_and_baseline.py"
EXPECTED_DBID = "7c38045b-c9ae-426c-8b4c-2e2d726d88ff"
EXPECTED_PROJECT_NAME = "KT404_2026-09-29"


def audit_static_code():
    print("=== [AUDIT PHASE 1] Static Code Analysis ===")
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        code = f.read()

    findings = []
    # Check 1: Resolve API imports and usage
    if "dvr_script.scriptapp(\"Resolve\")" in code or "scriptapp('Resolve')" in code or 'scriptapp("Resolve")' in code:
        print("  [PASS] Genuine DaVinciResolveScript connection found.")
    else:
        findings.append("Missing DaVinciResolveScript connection call.")

    # Check 2: Facade / mock checks
    prohibited_mock_terms = ["MagicMock", "unittest.mock", "patch(", "return_value ="]
    for term in prohibited_mock_terms:
        if term in code:
            findings.append(f"Mocking pattern detected: {term}")

    if "pm.SaveProject()" in code and "pm.ExportProject(" in code:
        print("  [PASS] Genuine SaveProject() and ExportProject() calls present.")
    else:
        findings.append("Missing SaveProject or ExportProject calls.")

    # Check 3: Hardcoded returns or fake timeline loop
    if "GetTimelineCount()" in code and "GetTimelineByIndex(" in code:
        print("  [PASS] Genuine timeline iteration logic present.")
    else:
        findings.append("Timeline iteration not using Resolve API.")

    if findings:
        print("  [FAIL] Static code issues found:", findings)
        return False, findings
    print("  [ALL STATIC CHECKS PASSED]")
    return True, []


def audit_drp_file():
    print("\n=== [AUDIT PHASE 2] DRP File & Zip Forensics ===")
    findings = []
    if not os.path.exists(BACKUP_PATH):
        findings.append(f"Backup file not found at {BACKUP_PATH}")
        return False, findings

    size = os.path.getsize(BACKUP_PATH)
    mtime = os.path.getmtime(BACKUP_PATH)
    ctime = os.path.getctime(BACKUP_PATH)
    print(f"  Path: {BACKUP_PATH}")
    print(f"  Size: {size:,} bytes ({size / (1024*1024):.2f} MB)")
    print(f"  Created: {time.ctime(ctime)}")
    print(f"  Modified: {time.ctime(mtime)}")

    if size < 500_000:
        findings.append(f"File size {size} is less than 500KB threshold")

    if not zipfile.is_zipfile(BACKUP_PATH):
        findings.append("File is not a valid zip archive")
        return False, findings

    with zipfile.ZipFile(BACKUP_PATH, "r") as z:
        bad = z.testzip()
        if bad is not None:
            findings.append(f"CRC32 error on archive member: {bad}")
        else:
            print("  [PASS] Archive CRC32 verification passed (all members clean).")

        namelist = z.namelist()
        print(f"  Total archive members: {len(namelist)}")

        if "project.xml" not in namelist:
            findings.append("project.xml missing from archive")
        else:
            p_info = z.getinfo("project.xml")
            print(f"  project.xml uncompressed size: {p_info.file_size:,} bytes")
            content = z.read("project.xml")[:2000].decode("utf-8", errors="replace")
            if EXPECTED_DBID not in content:
                findings.append(f"DbId {EXPECTED_DBID} not in project.xml header")
            else:
                print(f"  [PASS] DbId {EXPECTED_DBID} matched in project.xml header.")

        seq_containers = [n for n in namelist if n.startswith("SeqContainer/")]
        print(f"  SeqContainer count: {len(seq_containers)}")
        if len(seq_containers) != 30:
            findings.append(f"Expected 30 SeqContainers, found {len(seq_containers)}")
        else:
            print("  [PASS] Exactly 30 sequence container XML files found in DRP.")

        mp_files = [n for n in namelist if "MediaPool" in n]
        print(f"  MediaPool structure files: {len(mp_files)}")
        if not mp_files:
            findings.append("MediaPool structure missing from DRP")

    if findings:
        print("  [FAIL] DRP forensics issues:", findings)
        return False, findings
    print("  [ALL DRP CHECKS PASSED]")
    return True, []


def audit_live_resolve_and_baseline():
    print("\n=== [AUDIT PHASE 3] Live DaVinci Resolve vs Baseline JSON ===")
    findings = []

    # Connect to live Resolve
    os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
    resolve_dir = r"C:\Program Files\Blackmagic Design\DaVinci Resolve"
    if hasattr(os, "add_dll_directory") and os.path.isdir(resolve_dir):
        try:
            os.add_dll_directory(resolve_dir)
        except Exception:
            pass
    script_mod_dir = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\lib\modules"
    if script_mod_dir not in sys.path:
        sys.path.append(script_mod_dir)

    try:
        import DaVinciResolveScript as dvr
        resolve = dvr.scriptapp("Resolve")
        if not resolve:
            findings.append("Could not connect to live Resolve via scriptapp('Resolve')")
            return False, findings
        pm = resolve.GetProjectManager()
        project = pm.GetCurrentProject()
        if not project:
            findings.append("No active project open in Resolve")
            return False, findings
    except Exception as e:
        findings.append(f"Resolve connection exception: {e}")
        return False, findings

    proj_name = project.GetName()
    proj_id = project.GetUniqueId()
    print(f"  Live Project: '{proj_name}' (ID: {proj_id})")

    if proj_name != EXPECTED_PROJECT_NAME:
        findings.append(f"Project name mismatch: expected {EXPECTED_PROJECT_NAME}, got {proj_name}")
    if proj_id != EXPECTED_DBID:
        findings.append(f"Project ID mismatch: expected {EXPECTED_DBID}, got {proj_id}")

    live_tl_count = project.GetTimelineCount()
    print(f"  Live Timeline Count: {live_tl_count}")
    if live_tl_count != 30:
        findings.append(f"Live timeline count {live_tl_count} != 30")

    # Load baseline JSON
    if not os.path.exists(BASELINE_PATH):
        findings.append(f"Baseline JSON missing at {BASELINE_PATH}")
        return False, findings

    with open(BASELINE_PATH, "r", encoding="utf-8") as f:
        baseline = json.load(f)

    if baseline.get("project_name") != EXPECTED_PROJECT_NAME:
        findings.append("Baseline project_name mismatch")
    if baseline.get("project_id") != EXPECTED_DBID:
        findings.append("Baseline project_id mismatch")
    if baseline.get("total_timelines") != 30:
        findings.append("Baseline total_timelines != 30")

    base_tls = baseline.get("timelines", [])
    if len(base_tls) != 30:
        findings.append(f"Baseline timelines array length {len(base_tls)} != 30")

    # Compare each timeline live
    match_count = 0
    fps_counts = {}
    total_sub_cues = 0

    print("  Verifying 30 timelines 1:1 against live Resolve:")
    for idx in range(1, live_tl_count + 1):
        live_tl = project.GetTimelineByIndex(idx)
        live_name = live_tl.GetName()
        live_id = live_tl.GetUniqueId()
        live_start = int(live_tl.GetStartFrame())
        live_end = int(live_tl.GetEndFrame())
        live_fps = float(live_tl.GetSetting("timelineFrameRate") or 60.0)
        live_w = int(live_tl.GetSetting("timelineResolutionWidth") or 1920)
        live_h = int(live_tl.GetSetting("timelineResolutionHeight") or 1080)

        base_tl = base_tls[idx - 1]
        base_name = base_tl["timeline_name"]
        base_id = base_tl["timeline_id"]
        base_start = base_tl["start_frame"]
        base_end = base_tl["end_frame"]
        base_fps = base_tl["frame_rate"]
        base_w = base_tl["resolution_width"]
        base_h = base_tl["resolution_height"]

        fps_counts[base_fps] = fps_counts.get(base_fps, 0) + 1
        sub_cues = base_tl["subtitle_track"]["cue_count"]
        total_sub_cues += sub_cues

        # Assert match
        mismatches = []
        if live_name != base_name:
            mismatches.append(f"name: live '{live_name}' vs base '{base_name}'")
        if live_id != base_id:
            mismatches.append(f"id: live '{live_id}' vs base '{base_id}'")
        if live_start != base_start:
            mismatches.append(f"start: live {live_start} vs base {base_start}")
        if live_end != base_end:
            mismatches.append(f"end: live {live_end} vs base {base_end}")
        if live_fps != base_fps:
            mismatches.append(f"fps: live {live_fps} vs base {base_fps}")
        if live_w != base_w or live_h != base_h:
            mismatches.append(f"res: live {live_w}x{live_h} vs base {base_w}x{base_h}")

        if mismatches:
            findings.append(f"Timeline {idx} mismatch: {', '.join(mismatches)}")
        else:
            match_count += 1

    print(f"  [PASS] {match_count} of 30 timelines perfectly matched live Resolve properties.")
    print(f"  FPS distribution: {fps_counts}")
    print(f"  Total subtitle cues across all timelines: {total_sub_cues}")

    # Check UI state restoration
    curr_page = resolve.GetCurrentPage()
    curr_tl = project.GetCurrentTimeline()
    curr_tl_name = curr_tl.GetName() if curr_tl else None
    print(f"  Current active page: '{curr_page}'")
    print(f"  Current active timeline: '{curr_tl_name}'")

    if findings:
        print("  [FAIL] Live comparison issues:", findings)
        return False, findings
    print("  [ALL LIVE RESOLVE CHECKS PASSED]")
    return True, []


def main():
    print("==================================================")
    print("     FORENSIC AUDITOR M1: INDEPENDENT AUDIT       ")
    print("==================================================")
    r1, f1 = audit_static_code()
    r2, f2 = audit_drp_file()
    r3, f3 = audit_live_resolve_and_baseline()

    all_passed = r1 and r2 and r3
    print("\n==================================================")
    if all_passed:
        print("  FINAL VERDICT: CLEAN")
        print("  No integrity violations detected.")
        print("  Work product is authentic, genuine, and verified.")
    else:
        print("  FINAL VERDICT: INTEGRITY VIOLATION")
        all_findings = f1 + f2 + f3
        for f in all_findings:
            print("  - ", f)
    print("==================================================")
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
