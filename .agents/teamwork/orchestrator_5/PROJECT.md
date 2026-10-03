# Project: Tygarina 60 New Highlight Moments & Resolve Timeline Construction (Round 4)

## Architecture
- **Source Footage**: 32 video files in `C:\Users\warit\SynologyDrive\Tygarina\2026-09-30` (69.50 GiB, 78.85 hrs, constant 60.0 fps, stereo Opus 48kHz). 100% read-only and unmutated.
- **DaVinci Resolve Environment**: DaVinci Resolve Studio 21.1.0.17 running in GUI mode, active project `tygarina_2026-09-30`. All 32 source clips pre-imported in Media Pool `Master` bin.
- **Pre-existing State**: Exactly 28 existing timelines (7 from R1/R2, 21 from R3).
- **Target State**: Exactly 60 new highlight timelines added, bringing total to 88 timelines (28 existing + 60 new).
- **Candidate Specification Input**: `C:\Users\warit\Desktop\agent-edite-davinci_resolve\scratch\round4_60_candidates_complete.json`
- **Highlight Properties**:
  - Each highlight is exactly 55.0s (3300 frames at 60.0 fps).
  - 100% pure Thai Unicode naming: `{ชื่อคลิปภาษาไทย}_{ชื่อเกม}-vdo` (0 Latin letters in Thai prefix).
  - 100% coverage of all 25 untouched files (2 clips per file = 50 clips) + 10 peak clips across high-action footage.
  - 0.00s overlap with any of the 28 existing timelines or between candidate clips.
  - Zero offline media across all created timelines.
  - Project cleanly saved via `ProjectManager.SaveProject()`.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Full Library Survey & Media Pool Audit | Catalog 32 files (78.85 hrs) & 28 existing timelines; map MediaPoolItem IDs | M0 (Done) | Survey |
| 2 | Audio Peak & Whisper Rationale Extraction | Scan 25 untouched files via FFmpeg audio energy & faster-whisper transcripts | M1 (Done) | Survey |
| 3 | Pure Thai Naming & Game Mapping | Map 32 files to game tags, validate 60 pure Thai titles with 0 Latin characters | M1 (Done) | Survey |
| 4 | Non-Overlap & Duration Alignment | Ensure 60 intervals are strictly 55s (3300f) with 0.00s collision | M1 (Done) | Survey |
| 5 | DaVinci Resolve Timeline Construction | Construct 60 new highlight timelines in `tygarina_2026-09-30` reaching 88 timelines | M2 | Request R4 |
| 6 | Project Persistence & Non-Destructive Invariant | Save project cleanly via API, preserve 100% read-only source files | M2 | Request R4 |
| 7 | Specification & Resolve State Review | Independent verification of 88 timelines, pure Thai naming, exact durations | M3 | Gate Review |
| 8 | Adversarial Empirical Stress Testing | Pytest suite & mathematical boundary verification for 0.00s overlap | M3 | Gate Challenger |
| 9 | Forensic Integrity Audit | Static analysis and live unmocked Resolve query confirming authentic implementation | M3 | Gate Auditor |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M0 | Survey & Footage Profiling | Technical inventory of 32 files, 28 timelines, MediaPool IDs | None | DONE |
| M1 | Candidate Specification & Timing | 60 highlight candidates (55s, 0.00s overlap, pure Thai naming) | M0 | DONE |
| M2 | DaVinci Resolve Timeline Construction | Build 60 timelines in active Resolve project via MCP/scripting API | M1 | IN_PROGRESS |
| M3 | Multi-Layer Independent Verification Gate | 2 Reviewers, 2 Challengers, 1 Forensic Auditor | M2 | PENDING |

## Interface Contracts
### Candidate Specification ↔ DaVinci Resolve Construction Worker
- Source Data: `C:\Users\warit\Desktop\agent-edite-davinci_resolve\scratch\round4_60_candidates_complete.json`
- Target Project: `tygarina_2026-09-30`
- Folder: `Master` bin
- API:
  - Connect to DaVinci Resolve via Python scripting API (`fusionscript` / `DaVinciResolveScript`) or Resolve MCP.
  - For each of the 60 candidates:
    - Target Timeline Name: `candidate["target_timeline_name"]`
    - MediaPoolItem Unique ID: `candidate["mediapool_item_id"]`
    - Source File: `candidate["source_file"]`
    - Start Frame: `candidate["start_frame"]`
    - End Frame: `candidate["end_frame"]`
    - Duration: `3300` frames (55.0s at 60fps)
    - Timeline configuration: 1 Video Track (V1), 1 Audio Track (A1)
  - After creating all 60 timelines:
    - Verify timeline count in project is exactly 88 (28 existing + 60 new).
    - Verify 0 offline media items.
    - Save project via `project_manager.SaveProject()`.

## Code Layout
- Agent Workspaces: `C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\`
- Candidate Specification: `C:\Users\warit\Desktop\agent-edite-davinci_resolve\scratch\round4_60_candidates_complete.json`
- Verification Script: `C:\Users\warit\Desktop\agent-edite-davinci_resolve\scratch\verify_60_specs.py`
- Worker Workspace: `C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\worker_timeline_construction_r4\`
