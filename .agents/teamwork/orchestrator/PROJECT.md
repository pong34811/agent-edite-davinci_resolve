# Project: DaVinci Resolve 30-Timeline 9:16 Conversion

## Architecture
- **Environment**: DaVinci Resolve Studio 21.1.0.17 (GUI mode, Windows 11).
- **Project**: `KT404_2026-09-29` (Project ID: `7c38045b-c9ae-426c-8b4c-2e2d726d88ff`).
- **Data Flow**:
  1. Save current project state -> Export verified `.drp` backup to `G:\My Drive\Projects\Katy404\2026-09-29`.
  2. Snapshot 30-timeline baseline (names, durations, FPS, audio tracks, subtitle cue counts and timecodes).
  3. Pilot implementation: Duplicate `หนีฝ่าความหนาว_Minecraft-vdo` -> `หนีฝ่าความหนาว_Minecraft-vdo_9x16`.
  4. Vertical reframing:
     - Timeline custom settings: 1080x1920, matching source FPS.
     - Dual video track split screen:
       - V1 (Gameplay upper): Zoom 1.60, Pan 0.0, Tilt +480.0, CropBottom 486.0.
       - V2 (VTuber lower): Zoom 2.60, Pan -936.0, Tilt -200.0, CropTop 480.0.
     - V3 (Adjustment Clips): Fusion Transform Center (0.50, 0.25), Size 2.0 (full-screen VTuber close-up).
     - V4 (Reaction GIFs): Zoom 0.42, Pan -300.0, Tilt +600.0 (safe upper-left quadrant).
     - Subtitle Track & Audio Tracks: Locked 1:1 from source duplicate.
  5. Gate verification on Pilot timeline (Build/Exec, Review, Challenge, Audit).
  6. Batch processing of remaining 29 timelines (28 @ 60.0 FPS, 1 @ 30.0 FPS).
  7. Final E2E verification of all 30 original and 30 new timelines, `ProjectManager.SaveProject()`, and UI state restore.

---

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Full Project Backup (.drp) | Export `.drp` to `G:\My Drive\Projects\Katy404\2026-09-29` before mutations | Milestone 1 | ORIGINAL_REQUEST §R1 |
| 2 | Backup Integrity Verification | Test `.drp` zip archive integrity, check size (>500KB) and verify Project ID in `project.xml` | Milestone 1 | Explorer 1 |
| 3 | Preflight Baseline Capture | Record baseline metadata for all 30 16:9 original timelines | Milestone 1 | Explorer 2 |
| 4 | Preservation of 30 Originals | Keep 30 original 16:9 timelines completely untouched | Milestone 1, 4 | ORIGINAL_REQUEST §R1 |
| 5 | Non-Destructive Duplication | Duplicate each timeline to `<OriginalName>_9x16` preserving frame rates (29@60fps, 1@30fps) | Milestone 2, 3 | ORIGINAL_REQUEST §R1 |
| 6 | 9:16 Resolution Configuration | Set timeline custom resolution to 1080x1920 with `useCustomSettings: "1"` | Milestone 2, 3 | Explorer 3 |
| 7 | Split Screen Reframing | Game top (V1: Zoom 1.60, Tilt +480, CropBottom 486), VTuber bottom (V2: Zoom 2.60, Pan -936, Tilt -200, CropTop 480) | Milestone 2, 3 | ORIGINAL_REQUEST §R2 |
| 8 | Full-Screen VTuber Focus | V3 Adjustment Clips updated in Fusion: Center (0.50, 0.25), Size 2.0 | Milestone 2, 3 | ORIGINAL_REQUEST §R2 |
| 9 | Reaction GIF Safe Repositioning | V4 GIFs positioned at Pan -300, Tilt +600, Zoom 0.42 (safe from face & subtitles) | Milestone 2, 3 | ORIGINAL_REQUEST §R2 |
| 10 | 1:1 Subtitle Track Locking | Native subtitle tracks preserved 1:1 (text, timecodes, cue count, styling) | Milestone 2, 3, 4 | ORIGINAL_REQUEST §R3 |
| 11 | Audio Track & Mix Locking | Audio tracks, levels, dialogue balance, BGM/SFX fades 100% preserved | Milestone 2, 3, 4 | ORIGINAL_REQUEST §R3 |
| 12 | Cut Durations & Pacing Locking | Cuts and clip durations 100% retained without retiming | Milestone 2, 3, 4 | ORIGINAL_REQUEST §R3 |
| 13 | Zero Media Offline Invariant | Zero offline media across all Media Pool items and timeline clips | Milestone 2, 3, 4 | ORIGINAL_REQUEST §Acceptance |
| 14 | Pilot Timeline Verification | Pilot execution on `หนีฝ่าความหนาว_Minecraft-vdo_9x16` before batch execution | Milestone 2 | ORIGINAL_REQUEST §R4 |
| 15 | Project Save | Explicit `ProjectManager.SaveProject()` execution | Milestone 1, 2, 3, 4 | ORIGINAL_REQUEST §R4 |
| 16 | UI State Restoration | Restore active timeline, playhead position, and page state cleanly | Milestone 4 | Explorer 1 |

---

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Project Backup & Baseline Validation | Save project, export `.drp` to G: drive, verify integrity, snapshot 30 baseline timelines | none | DONE |
| 2 | Pilot Timeline Implementation & Verification | Duplicate and convert pilot `หนีฝ่าความหนาว_Minecraft-vdo_9x16`, verify full 9:16 layout, focus zoom, subtitles, audio | Milestone 1 | BLOCKED: Visual framing defects (crops & focus center) |
| 3 | Batch Execution (Remaining 29 Timelines) | Automated conversion of remaining 29 timelines (28 @ 60 FPS, 1 @ 30 FPS), verify all invariants | Milestone 2 | PLANNED |
| 4 | Final E2E Verification & State Restore | Comprehensive verification of 30 originals (untouched) and 30 new (valid), project save, UI state restore | Milestone 3 | PLANNED |

---

## Interface Contracts
### DaVinci Resolve Scripting API Contract
- `pm = resolve.GetProjectManager()`
- `project = pm.GetCurrentProject()`
- Save: `pm.SaveProject()` -> returns `True`
- Export: `pm.ExportProject("KT404_2026-09-29", export_path)` -> returns `True`
- Duplicate: `timeline.DuplicateTimeline(new_name)` -> returns new `Timeline` object
- Set Custom Resolution:
  ```python
  timeline.SetSetting("useCustomSettings", "1")
  timeline.SetSetting("timelineResolutionWidth", "1080")
  timeline.SetSetting("timelineResolutionHeight", "1920")
  ```
- Clip Transforms on TimelineItem:
  `item.SetProperty("ZoomX", val)`, `item.SetProperty("ZoomY", val)`, `item.SetProperty("Pan", val)`, `item.SetProperty("Tilt", val)`, `item.SetProperty("CropBottom", val)`, `item.SetProperty("CropTop", val)`

---

## Code Layout
- Scripts directory: `C:\Users\warit\Desktop\agent-edite-davinci_resolve\scripts\`
  - `backup_and_baseline.py` (Milestone 1)
  - `convert_pilot.py` (Milestone 2)
  - `convert_batch.py` (Milestone 3)
  - `verify_e2e.py` (Milestone 4)
- Agent metadata: `C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\`
