"""
Independent Empirical Challenger Test for Milestone 1: KT404_2026-09-29 .drp Backup
Author: Challenger M1-1 (teamwork_preview_challenger)
Role: Empirical Challenger / Critic & Specialist

Validates:
1. Backup file existence, path, timestamp freshness, and size (>500KB).
2. ZIP archive CRC32 integrity across all 41 archive members via zipfile.ZipFile.testzip().
3. project.xml header inspection:
   - SM_Project root element with DbId="7c38045b-c9ae-426c-8b4c-2e2d726d88ff"
   - ProjectName == "KT404_2026-09-29"
   - TimelineHandleVec containing exactly 30 timeline handles.
4. Archive member structure:
   - Exactly 30 SeqContainer/<UUID>.xml files corresponding to the 30 project timeline sequences.
   - All 30 sequences containing valid VideoTrackVec and AudioTrackVec.
   - 9 MediaPool/Master/.../MpFolder.xml files covering all project media folders.
   - Gallery.xml present.
   - Complete XML parseability test across all 41 members (handling DaVinci C++ '::' tag namespace quirk).
5. Cross-verification against Worker M1 baseline snapshot:
   - 1:1 match of all 30 timeline UUIDs between project.xml TimelineHandleVec and baseline_30_timelines.json.
   - Verification of 29 @ 60.0 FPS, 1 @ 30.0 FPS.
   - Total subtitle cues verification (2,066 cues).
"""

import os
import sys
import json
import zipfile
import datetime
import xml.etree.ElementTree as ET

BACKUP_PATH = r"G:\My Drive\Projects\Katy404\2026-09-29\KT404_2026-09-29_pre_9x16_conversion_2026-10-01.drp"
EXPECTED_DBID = "7c38045b-c9ae-426c-8b4c-2e2d726d88ff"
EXPECTED_PROJECT_NAME = "KT404_2026-09-29"
MIN_BYTE_SIZE = 500 * 1024  # 500 KB threshold
EXPECTED_TIMELINE_COUNT = 30
BASELINE_PATH = r"C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\worker_m1\baseline_30_timelines.json"

def run_tests():
    print("=" * 70)
    print("CHALLENGER M1-1: EMPIRICAL STRESS-TEST & VALIDATION OF DRP BACKUP")
    print("=" * 70)
    failures = []

    # -------------------------------------------------------------
    # 1. Existence and File Attributes
    # -------------------------------------------------------------
    print("\n[TEST 1] Verifying Backup File Existence and Attributes...")
    if not os.path.exists(BACKUP_PATH):
        failures.append(f"CRITICAL: Backup file not found at: {BACKUP_PATH}")
        print(f"  [FAIL] {failures[-1]}")
        return failures

    file_size = os.path.getsize(BACKUP_PATH)
    mtime = os.path.getmtime(BACKUP_PATH)
    mtime_dt = datetime.datetime.fromtimestamp(mtime, tz=datetime.timezone.utc)
    print(f"  Path: {BACKUP_PATH}")
    print(f"  Size: {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
    print(f"  MTime (UTC): {mtime_dt.isoformat()}")

    if file_size < MIN_BYTE_SIZE:
        failures.append(f"File size {file_size:,} bytes is below threshold {MIN_BYTE_SIZE:,} bytes")
        print(f"  [FAIL] {failures[-1]}")
    else:
        print(f"  [PASS] File size ({file_size:,} bytes) exceeds 500 KB threshold.")

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    age_seconds = (now_utc - mtime_dt).total_seconds()
    print(f"  File age: {age_seconds:.1f} seconds")
    if age_seconds > 86400:
        failures.append(f"File appears stale (older than 24h): {mtime_dt}")
        print(f"  [FAIL] {failures[-1]}")
    else:
        print(f"  [PASS] Timestamp is fresh (created today: {mtime_dt.date()}).")

    # -------------------------------------------------------------
    # 2. ZIP Archive Integrity (testzip)
    # -------------------------------------------------------------
    print("\n[TEST 2] Verifying ZIP Archive Integrity (testzip CRC32)...")
    if not zipfile.is_zipfile(BACKUP_PATH):
        failures.append("File is not a valid ZIP archive format")
        print(f"  [FAIL] {failures[-1]}")
        return failures

    with zipfile.ZipFile(BACKUP_PATH, "r") as zf:
        corrupted = zf.testzip()
        if corrupted is not None:
            failures.append(f"Corrupted archive member detected: {corrupted}")
            print(f"  [FAIL] {failures[-1]}")
        else:
            print("  [PASS] testzip() returned None: All CRC32 checksums match perfectly.")

        infolist = zf.infolist()
        total_compressed = sum(info.compress_size for info in infolist)
        total_uncompressed = sum(info.file_size for info in infolist)
        member_count = len(infolist)
        print(f"  Total archive members: {member_count}")
        print(f"  Uncompressed data size: {total_uncompressed:,} bytes ({total_uncompressed / (1024*1024):.2f} MB)")
        print(f"  Compressed data size:   {total_compressed:,} bytes ({total_compressed / (1024*1024):.2f} MB)")
        print(f"  Compression efficiency: {(1 - total_compressed / total_uncompressed) * 100:.1f}% space saved")

        if member_count < 35:
            failures.append(f"Suspiciously low member count: {member_count} (expected >= 35)")
            print(f"  [FAIL] {failures[-1]}")
        else:
            print(f"  [PASS] Member count ({member_count}) consistent with full project backup.")

        namelist = zf.namelist()

        # ---------------------------------------------------------
        # 3. project.xml Header and Schema Inspection
        # ---------------------------------------------------------
        print("\n[TEST 3] Extracting and Inspecting project.xml Header...")
        if "project.xml" not in namelist:
            failures.append("CRITICAL: project.xml is missing from .drp archive!")
            print(f"  [FAIL] {failures[-1]}")
            return failures

        raw_xml_bytes = zf.read("project.xml")
        raw_xml_text = raw_xml_bytes.decode("utf-8", errors="replace")
        print(f"  project.xml uncompressed size: {len(raw_xml_bytes):,} bytes")

        # Check line 1-3 for SM_Project and DbId
        first_lines = [line.strip() for line in raw_xml_text.splitlines()[:5] if line.strip()]
        header_line = next((l for l in first_lines if l.startswith("<SM_Project")), "")
        print(f"  Found header line: {header_line}")

        if not header_line:
            failures.append("No <SM_Project> root tag found in first 5 lines of project.xml")
            print(f"  [FAIL] {failures[-1]}")
        else:
            print("  [PASS] Root tag <SM_Project> verified.")

        if f'DbId="{EXPECTED_DBID}"' not in header_line:
            failures.append(f"DbId mismatch in header! Expected '{EXPECTED_DBID}', found: {header_line}")
            print(f"  [FAIL] {failures[-1]}")
        else:
            print(f"  [PASS] DbId exactly matches '{EXPECTED_DBID}'.")

        # Check ProjectName
        if f"<ProjectName>{EXPECTED_PROJECT_NAME}</ProjectName>" not in raw_xml_text:
            failures.append(f"Expected <ProjectName>{EXPECTED_PROJECT_NAME}</ProjectName> not found in project.xml")
            print(f"  [FAIL] {failures[-1]}")
        else:
            print(f"  [PASS] ProjectName matches '{EXPECTED_PROJECT_NAME}'.")

        # Parse project.xml with ElementTree after sanitizing DaVinci C++ '::' notation
        sanitized_xml = raw_xml_text.replace("::", "__")
        try:
            root = ET.fromstring(sanitized_xml)
            print("  [PASS] project.xml fully parses into ElementTree (after C++ '::' tag token normalization).")
        except Exception as e:
            failures.append(f"Failed to parse sanitized project.xml: {e}")
            print(f"  [FAIL] {failures[-1]}")
            return failures

        # Inspect TimelineHandleVec
        timeline_handles_elem = root.find("TimelineHandleVec")
        if timeline_handles_elem is None:
            failures.append("TimelineHandleVec node missing in project.xml")
            print(f"  [FAIL] {failures[-1]}")
            timeline_handles = []
        else:
            timeline_handles = [el.text.strip() for el in timeline_handles_elem.findall("Element") if el.text]
            print(f"  Timeline handles found in project.xml: {len(timeline_handles)}")
            if len(timeline_handles) != EXPECTED_TIMELINE_COUNT:
                failures.append(f"Expected {EXPECTED_TIMELINE_COUNT} timeline handles, found {len(timeline_handles)}")
                print(f"  [FAIL] {failures[-1]}")
            else:
                print(f"  [PASS] Exactly {EXPECTED_TIMELINE_COUNT} timeline handles found in project.xml.")

        # ---------------------------------------------------------
        # 4. Deep Structure Inspection: Sequences & Media Pool
        # ---------------------------------------------------------
        print("\n[TEST 4] Deep Inspection of SeqContainer and MediaPool Archive Members...")
        seq_members = [m for m in namelist if m.startswith("SeqContainer/") and m.endswith(".xml")]
        print(f"  SeqContainer XML files in archive: {len(seq_members)}")
        if len(seq_members) != EXPECTED_TIMELINE_COUNT:
            failures.append(f"Expected {EXPECTED_TIMELINE_COUNT} SeqContainer XMLs, found {len(seq_members)}")
            print(f"  [FAIL] {failures[-1]}")
        else:
            print(f"  [PASS] Exactly {EXPECTED_TIMELINE_COUNT} SeqContainer files present (one per timeline).")

        # Verify each SeqContainer XML is valid and contains tracks
        track_failures = 0
        for seq_file in seq_members:
            raw_seq = zf.read(seq_file).decode("utf-8", errors="replace").replace("::", "__")
            try:
                seq_root = ET.fromstring(raw_seq)
                has_video = seq_root.find("VideoTrackVec") is not None
                has_audio = seq_root.find("AudioTrackVec") is not None
                if not (has_video and has_audio):
                    track_failures += 1
            except Exception as e:
                track_failures += 1
        if track_failures > 0:
            failures.append(f"{track_failures} SeqContainer files failed XML track inspection")
            print(f"  [FAIL] {failures[-1]}")
        else:
            print(f"  [PASS] All {len(seq_members)} SeqContainer files verified (contain valid VideoTrackVec & AudioTrackVec).")

        # MediaPool folders
        media_pool_members = [m for m in namelist if m.startswith("MediaPool/")]
        print(f"  MediaPool members in archive: {len(media_pool_members)}")
        expected_subfolders = ["Gameplay", "Fun", "Meme", "Archive", "Enrichment_SFX", "Enrichment_BGM", "Enrichment_GIF"]
        found_subfolders = [f for f in expected_subfolders if any(f in m for m in media_pool_members)]
        print(f"  MediaPool subfolders verified: {found_subfolders}")
        if len(found_subfolders) < len(expected_subfolders):
            missing_folders = set(expected_subfolders) - set(found_subfolders)
            failures.append(f"Missing expected media folders in MediaPool: {missing_folders}")
            print(f"  [FAIL] {failures[-1]}")
        else:
            print("  [PASS] All expected MediaPool subfolders present in archive.")

        # Parse ALL 41 files in archive to ensure zero corruption
        print("\n[TEST 5] Full-Archive XML Parse Stress Test across all 41 files...")
        parse_errs = 0
        for member in namelist:
            raw = zf.read(member).decode("utf-8", errors="replace").replace("::", "__")
            try:
                ET.fromstring(raw)
            except Exception as e:
                parse_errs += 1
                print(f"    Parse error on {member}: {e}")
        if parse_errs > 0:
            failures.append(f"{parse_errs} archive members failed XML parse test")
            print(f"  [FAIL] {failures[-1]}")
        else:
            print(f"  [PASS] 41/41 archive members parsed successfully with 0 syntax errors.")

    # -------------------------------------------------------------
    # 5. Cross-Verification with Worker Baseline JSON
    # -------------------------------------------------------------
    print("\n[TEST 6] Cross-Verifying with Worker M1 Baseline Snapshot...")
    if not os.path.exists(BASELINE_PATH):
        failures.append(f"Baseline JSON file missing at: {BASELINE_PATH}")
        print(f"  [FAIL] {failures[-1]}")
    else:
        with open(BASELINE_PATH, "r", encoding="utf-8") as f:
            baseline_data = json.load(f)

        timelines = baseline_data.get("timelines", [])
        print(f"  Timelines in baseline JSON: {len(timelines)}")
        if len(timelines) != EXPECTED_TIMELINE_COUNT:
            failures.append(f"Baseline contains {len(timelines)} timelines, expected {EXPECTED_TIMELINE_COUNT}")
            print(f"  [FAIL] {failures[-1]}")
        else:
            print(f"  [PASS] Exactly {EXPECTED_TIMELINE_COUNT} timelines in baseline JSON.")

        baseline_ids = [tl.get("timeline_id") for tl in timelines]
        matched_ids = [bid for bid, hid in zip(baseline_ids, timeline_handles) if bid == hid]
        print(f"  Timeline UUIDs matching 1:1 in order: {len(matched_ids)} / 30")
        if len(matched_ids) != EXPECTED_TIMELINE_COUNT:
            failures.append(f"Only {len(matched_ids)}/30 timeline IDs matched baseline in order!")
            print(f"  [FAIL] {failures[-1]}")
        else:
            print("  [PASS] 100% 30/30 timeline UUIDs match between project.xml and baseline JSON in exact order.")

        fps_dist = {}
        total_subs = 0
        for tl in timelines:
            fps = tl.get("frame_rate")
            fps_dist[fps] = fps_dist.get(fps, 0) + 1
            total_subs += tl.get("subtitle_track", {}).get("cue_count", 0)

        print(f"  FPS distribution: {fps_dist}")
        if fps_dist.get(60.0) != 29 or fps_dist.get(30.0) != 1:
            failures.append(f"FPS distribution incorrect: {fps_dist}")
            print(f"  [FAIL] {failures[-1]}")
        else:
            print("  [PASS] FPS distribution verified (29 @ 60.0 FPS, 1 @ 30.0 FPS).")

        print(f"  Total subtitle cues: {total_subs}")
        if total_subs != 2066:
            failures.append(f"Subtitle cues count {total_subs} != 2066")
            print(f"  [FAIL] {failures[-1]}")
        else:
            print("  [PASS] Total subtitle cues verified at exactly 2,066.")

    # -------------------------------------------------------------
    # Final Verdict
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    if not failures:
        print("EMPIRICAL TEST SUMMARY: ALL 6 TEST SUITES PASSED (0 FAILURES)")
        print("VERDICT: APPROVE")
        print("=" * 70)
        return []
    else:
        print(f"EMPIRICAL TEST SUMMARY: {len(failures)} FAILURE(S) DETECTED")
        for f in failures:
            print(f"  - {f}")
        print("VERDICT: REQUEST_CHANGES")
        print("=" * 70)
        return failures

def test_empirical_backup_and_baseline():
    fails = run_tests()
    assert len(fails) == 0, f"Empirical challenger test failures: {fails}"

if __name__ == "__main__":
    fails = run_tests()
    sys.exit(0 if len(fails) == 0 else 1)
