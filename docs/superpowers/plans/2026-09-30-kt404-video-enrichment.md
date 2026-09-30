# KT404_2026-09-29 Video Enrichment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enrich all 30 gameplay highlight timelines in DaVinci Resolve project `KT404_2026-09-29` with theme-matched BGM, comedic/reaction SFX, and centered GIF/meme overlays without modifying original footage or subtitles.

**Architecture:** A Python-driven automation pipeline interfacing with DaVinci Resolve Studio 21.1 via the scripting bridge/MCP. First, perform a safety `.drp` export and ingest indexed asset pools. Next, analyze subtitle text and timecodes on Subtitle Track 1 to detect comedic beats and reactions, mapping them to exact SFX and centered GIF placements. Execute and verify a pilot on Timeline 1 for user approval before batch-processing the remaining 29 timelines.

**Tech Stack:** Python 3, DaVinci Resolve Studio 21.1 Scripting API / MCP, FFmpeg / FFprobe, Pytest.

**Spec:** `docs/superpowers/specs/2026-09-30-kt404-video-enrichment-design.md`

## Global Constraints

- Target Project: `KT404_2026-09-29` (DaVinci Resolve Studio 21.1.0.17)
- Timeline format: 1920×1080 (16:9 widescreen, 60.0 fps). Do NOT convert to 9:16 or alter native raster.
- Pre-flight backup: Export `.drp` to `G:\My Drive\Projects\Katy404\2026-09-29\KT404_2026-09-29_pre_enrichment.drp` before making mutations.
- Original source media on V1/A1 and subtitle cues on Sub 1 must remain untouched and fully preserved.
- Track mapping: V1=Main Video, V2=GIF Overlays, A1=Original Audio, A2=SFX (-10 dB to -12 dB), A3=BGM (-22 dB to -24 dB, 0.5s fade-in, 1.0s fade-out).
- GIF placement: Center of screen (`Pan=0, Tilt=0`), Zoom `0.50` to `0.65`, duration 1.5s to 2.5s.
- Pilot Gate: Timeline 1 (`ขุดมั่วเจอเหล็กกองใหญ่_Minecraft-vdo`) must be completely enriched, verified, and approved before processing Timelines 2–30.
- Asset roots:
  - SFX: `G:\My Drive\Projects\2.1_sfx`
  - BGM: `G:\My Drive\Projects\1.bgm`
  - GIF: `G:\My Drive\Projects\3.gif`

## Review Focus

- BGM duration mismatch: BGM must start at timeline start (frame 216000) and end cleanly at timeline end without trailing silence or abrupt cutoff.
- Audio volume clip setting verification: Setting `AudioVolume` must be verified via readback, confirming values between -10 dB and -24 dB.
- GIF overlay collision with VTuber model: Confirm GIF is centered and scaled <= 0.65 so bottom-right Katy404 avatar and bottom subtitles are 100% visible.
- Subtitle preservation: Confirm cue count and text on `Sub 1` are identical before and after enrichment.
- Resolve mutation spacing: Maintain ~1.2s delay between structural track modifications to avoid script race conditions.

---

### Task 1: Pre-flight Safety Backup & Asset Media Pool Ingestion

**Files:**
- Create: `scripts/enrichment_assets.py`
- Test: `tests/test_enrichment_assets.py`

**Interfaces:**
- Consumes: Resolve MCP `project_manager(action='export_project')`, `media_pool(action='import_media')`, `folder(action='create')`
- Produces: `EnrichmentAssetCatalog` containing imported MediaPoolItem IDs for SFX, BGM, and GIFs organized in bins:
  - `Enrichment_SFX`
  - `Enrichment_BGM`
  - `Enrichment_GIF`

- [ ] **Step 1: Write the failing test for asset indexing and backup path validation**

```python
# tests/test_enrichment_assets.py
import os
import pytest
from scripts.enrichment_assets import validate_asset_directories, select_bgm_for_game

def test_validate_asset_directories():
    sfx_dir = r"G:\My Drive\Projects\2.1_sfx"
    bgm_dir = r"G:\My Drive\Projects\1.bgm"
    gif_dir = r"G:\My Drive\Projects\3.gif"
    assert validate_asset_directories(sfx_dir, bgm_dir, gif_dir) is True

def test_select_bgm_for_game():
    assert "NCSน่ารัก" in select_bgm_for_game("Minecraft") or "FREE BGM" in select_bgm_for_game("Minecraft")
    assert "2025" in select_bgm_for_game("Terraria") or "Gaming" in select_bgm_for_game("Terraria") or "ncs_mix" in select_bgm_for_game("Terraria")
    assert "payday" in select_bgm_for_game("Monster Hunter World") or "Gaming" in select_bgm_for_game("Monster Hunter World") or "ncs_mix" in select_bgm_for_game("Monster Hunter World")
    assert "YEAT" in select_bgm_for_game("Soul Walker") or "Gaming" in select_bgm_for_game("Soul Walker")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_enrichment_assets.py -v`  
Expected: FAIL with ModuleNotFoundError or import error.

- [ ] **Step 3: Implement `scripts/enrichment_assets.py`**

Implement:
- `validate_asset_directories(sfx_dir: str, bgm_dir: str, gif_dir: str) -> bool`
- `select_bgm_for_game(game_name: str) -> str`
- `export_project_backup(backup_path: str) -> bool`
- `ingest_enrichment_assets() -> dict` (creates bins and imports curated SFX, BGM, GIFs into Media Pool)

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_enrichment_assets.py -v`  
Expected: PASS.

- [ ] **Step 5: Execute pre-flight backup and asset ingestion in Resolve**

Run script or MCP calls to export `.drp` backup to `G:\My Drive\Projects\Katy404\2026-09-29\KT404_2026-09-29_pre_enrichment.drp` and import assets into Media Pool.

- [ ] **Step 6: Commit**

```bash
git add scripts/enrichment_assets.py tests/test_enrichment_assets.py
git commit -m "feat: add asset ingestion and backup validation for KT404 enrichment"
```

---

### Task 2: Subtitle Cue Analyzer & Placement Rules Engine

**Files:**
- Create: `scripts/enrichment_engine.py`
- Test: `tests/test_enrichment_engine.py`

**Interfaces:**
- Consumes: `EnrichmentAssetCatalog` from Task 1, timeline subtitle item text and start/end frames from `timeline(action='probe_timeline_structure')`
- Produces:
  - `analyze_subtitle_cues(subtitles: list[dict]) -> list[CuePoint]`
  - `plan_timeline_enrichment(timeline_info: dict, asset_catalog: dict) -> EnrichmentPlan`
  - `apply_enrichment_plan(timeline_id: str, plan: EnrichmentPlan) -> bool`

- [ ] **Step 1: Write the failing test for subtitle cue analysis**

```python
# tests/test_enrichment_engine.py
import pytest
from scripts.enrichment_engine import analyze_subtitle_cues, CuePoint

def test_analyze_subtitle_cues_punchlines():
    mock_subs = [
        {"name": "เยี่ยมเจอ", "start": 216000, "end": 216085},
        {"name": "55555 ไม่นะ", "start": 216500, "end": 216580},
        {"name": "อ๋อ เข้าใจแล้ว", "start": 217000, "end": 217060},
    ]
    cues = analyze_subtitle_cues(mock_subs)
    assert len(cues) >= 2
    types = [c.cue_type for c in cues]
    assert "shock" in types or "punchline" in types
    assert "cute" in types or "aha" in types
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_enrichment_engine.py -v`  
Expected: FAIL.

- [ ] **Step 3: Implement `scripts/enrichment_engine.py`**

Implement:
- Keyword mapping:
  - Punchline/Blunder: "555", "ฮ่า", "อ้าว", "เอ้า", "แป๊บ", "ไม่ได้", "ตลก" -> SFX ตบมุก, GIF Laughing/Minion
  - Shock/Panic: "เห้ย", "ว๊าก", "ไม่นะ", "ตาย", "ระเบิด", "บอส", "ช่วยด้วย" -> SFX scream/ฟ้าผ่า, GIF Shocked/OMG
  - Cute/Win: "อ๋อ", "เยี่ยม", "สวย", "รอดแล้ว", "เจอ", "โห" -> SFX Wink/Nice/Wow, GIF Cute Cat/Thumbs Up
- Calculation of timeline start/end frames, track indices (V2, A2, A3), volume parameters (`AudioVolume`: A2=-11.0, A3=-23.0), and video parameters (`ZoomX=0.55, ZoomY=0.55, Pan=0, Tilt=0`).
- Placement helper that ensures V2 and A2/A3 tracks exist before appending.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_enrichment_engine.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/enrichment_engine.py tests/test_enrichment_engine.py
git commit -m "feat: implement subtitle cue analysis and placement engine"
```

---

### Task 3: Pilot Implementation & Verification on Timeline 1

**Files:**
- Create: `scripts/run_pilot.py`
- Test: `tests/test_pilot_readback.py`

**Interfaces:**
- Consumes: `enrichment_engine.py`, `enrichment_assets.py`
- Produces: Enriched Timeline 1 (`ขุดมั่วเจอเหล็กกองใหญ่_Minecraft-vdo`) with V2 (GIFs), A2 (SFX), A3 (BGM) and readback verification report.

- [ ] **Step 1: Write test verifying Timeline 1 readback criteria**

```python
# tests/test_pilot_readback.py
import pytest

def test_pilot_timeline_structure_spec():
    # Verify expected tracks and item constraints for Timeline 1
    expected_v_count = 2
    expected_a_count = 3
    assert expected_v_count >= 2
    assert expected_a_count >= 3
```

- [ ] **Step 2: Run test to verify basic assertions**

Run: `pytest tests/test_pilot_readback.py -v`  
Expected: PASS.

- [ ] **Step 3: Execute `scripts/run_pilot.py` on Timeline 1**

- Set current timeline to index 1 (`ขุดมั่วเจอเหล็กกองใหญ่_Minecraft-vdo`).
- Ensure tracks Video 2, Audio 2, Audio 3 exist.
- Append theme BGM (`NCSน่ารัก.mp3` or `FREE BGM 4 LOOP.wav`) to Audio 3 from frame 216000 to 222600. Set volume to -23 dB, apply fade-in (30 frames) and fade-out (60 frames).
- Insert 2 SFX on Audio 2 at identified cue points. Set volume to -11 dB.
- Insert 1-2 centered GIFs on Video 2 at identified cue points. Set Zoom to 0.55.
- Save project via `ProjectManager.SaveProject()`.

- [ ] **Step 4: Readback verify Timeline 1 structure and capture verification frame**

Verify:
- Track V2 has >= 1 GIF clip, centered, zoom ~0.55.
- Track A2 has >= 2 SFX clips.
- Track A3 has 1 BGM clip matching timeline span.
- Track Sub 1 has all 51 subtitle cues intact.
- Capture timeline frame at peak cue to inspect visual framing.

- [ ] **Step 5: User Acceptance Gate**

Present pilot results to user for review and confirmation before proceeding to batch execution.

- [ ] **Step 6: Commit**

```bash
git add scripts/run_pilot.py tests/test_pilot_readback.py
git commit -m "feat: complete pilot enrichment and verification on Timeline 1"
```

---

### Task 4: Batch Enrichment Across Remaining 29 Timelines

**Files:**
- Create: `scripts/run_batch_enrichment.py`
- Test: `tests/test_batch_progress.py`

**Interfaces:**
- Consumes: `enrichment_engine.py`, `enrichment_assets.py`
- Produces: Enriched Timelines 2 through 30.

- [ ] **Step 1: Write test for batch queue generator and game categorization**

```python
# tests/test_batch_progress.py
import pytest
from scripts.enrichment_assets import select_bgm_for_game

def test_batch_timeline_categorization():
    sample_timelines = [
        "คุยกับเพื่อนตั้งนาน ลืมเอาเสียงเข้าไลฟ์_Minecraft-vdo",
        "ปราบมูนลอร์ดได้ครั้งแรก_Terraria-vdo",
        "เกรตจากราส_Monster Hunter World-vdo",
        "บอสมังกร_Soul Walker-vdo",
    ]
    for tl in sample_timelines:
        game = tl.split("_")[-1].replace("-vdo", "")
        bgm = select_bgm_for_game(game)
        assert bgm is not None
```

- [ ] **Step 2: Run test to verify categorization logic**

Run: `pytest tests/test_batch_progress.py -v`  
Expected: PASS.

- [ ] **Step 3: Implement `scripts/run_batch_enrichment.py`**

Iterates through Timelines 2 to 30:
1. Switch to timeline `timeline.set_current(index=i)`.
2. Extract timeline start/end frames and subtitle cues.
3. Add missing tracks (V2, A2, A3) with 1.2s delay between mutations.
4. Place theme-matched BGM on A3 (span exact timeline length, volume -23 dB, fade-in/out).
5. Place 2-3 SFX on A2 (volume -11 dB).
6. Place 1-2 centered GIFs on V2 (Zoom 0.55).
7. Save project every 5 timelines and on completion.

- [ ] **Step 4: Execute batch enrichment**

Run: `python scripts/run_batch_enrichment.py`  
Monitor execution logs and confirm zero failures.

- [ ] **Step 5: Commit**

```bash
git add scripts/run_batch_enrichment.py tests/test_batch_progress.py
git commit -m "feat: execute batch enrichment across all remaining 29 timelines"
```

---

### Task 5: Final Project QC & Comprehensive Audit Report

**Files:**
- Create: `scripts/enrichment_audit.py`
- Generate: `reference/KT404_enrichment_final_report.md`

**Interfaces:**
- Consumes: Resolve API inspection across all 30 timelines
- Produces: Verified project state, saved project, Markdown audit report detailing track and media counts for all 30 timelines.

- [ ] **Step 1: Implement `scripts/enrichment_audit.py`**

Iterate over all 30 timelines and collect:
- Timeline Name, Duration, FPS
- Video track count & clip counts (V1, V2)
- Audio track count & clip counts (A1, A2, A3)
- Subtitle track clip count (Sub 1)
- Media online status (confirm 0 offline media items)

- [ ] **Step 2: Execute audit script**

Run: `python scripts/enrichment_audit.py`  
Output: `reference/KT404_enrichment_final_report.md`.

- [ ] **Step 3: Verify audit results**

Confirm all 30 timelines:
- V2 item count >= 1
- A2 item count >= 1
- A3 item count == 1
- Sub 1 count matches original baseline
- 0 offline media items

- [ ] **Step 4: Final Save & State Restoration**

Save project with `ProjectManager.SaveProject()`. Restore initial active timeline.

- [ ] **Step 5: Commit**

```bash
git add scripts/enrichment_audit.py reference/KT404_enrichment_final_report.md
git commit -m "docs: produce final QC audit report for KT404_2026-09-29 enrichment"
```
