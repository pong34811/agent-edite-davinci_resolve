# Execution Plan: DaVinci Resolve 30-Timeline 9:16 Conversion

## Objective
Convert all 30 existing 16:9 horizontal edited timelines in DaVinci Resolve project `KT404_2026-09-29` into vertical 9:16 (1080x1920) short-form timelines (`<OriginalName>_9x16`) with Split Screen layout (Game top + VTuber bottom), full-screen VTuber focus moments, repositioned reaction GIFs, and strictly locked subtitles/audio/timing.

---

## Phase 0: Survey & Environment Assessment
- **Action**: Dispatch 3 parallel Explorers:
  1. `explorer_1`: Resolve environment, project connection (`KT404_2026-09-29`), backup destination (`G:\My Drive\Projects\Katy404\2026-09-29`), project export/save APIs.
  2. `explorer_2`: Inventory of all 30 source timelines, track layouts (V1/V2/V3, Subtitles, Audio), pilot timeline analysis (`หนีฝ่าความหนาว_Minecraft-vdo`), media pool status.
  3. `explorer_3`: Reframing mechanics, timeline duplication, 1080x1920 timeline settings, clip transform properties, V3 adjustment clip behavior, V2 reaction GIF safe zones.
- **Output**: Merged survey report into `PROJECT.md` (§ Feature Inventory & Architecture).

---

## Milestone 1: Project Backup & Baseline Capture
- **Objective**: Non-destructive safety check before any mutations.
- **Tasks**:
  1. Export full `.drp` project backup to `G:\My Drive\Projects\Katy404\2026-09-29`.
  2. Verify backup file exists, is non-empty, and valid.
  3. Snapshot metadata baseline of all 30 original 16:9 timelines (name, duration, frame rate, track count, subtitle cue count).
- **Verification Gate**: Worker executes backup -> Reviewer verifies -> Challenger validates -> Auditor confirms integrity -> Gate Pass.

---

## Milestone 2: Pilot Timeline Implementation & Verification
- **Objective**: Implement 9:16 conversion on 1 sample timeline (`หนีฝ่าความหนาว_Minecraft-vdo_9x16`).
- **Tasks**:
  1. Duplicate `หนีฝ่าความหนาว_Minecraft-vdo` to `หนีฝ่าความหนาว_Minecraft-vdo_9x16`.
  2. Configure timeline resolution to 1080x1920 (9:16), matching source frame rate.
  3. Apply Split Screen layout (Game upper portion, VTuber lower portion safely framed).
  4. Transform V3 Adjustment Clip intervals into full-screen 9:16 VTuber close-ups.
  5. Reposition V2 reaction GIFs to safe vertical positions (no overlap on face/subtitles).
  6. Verify native subtitle track is untouched (1:1 cues, text, timecodes).
  7. Verify audio tracks and cuts/durations are 100% preserved.
  8. Save project via `ProjectManager.SaveProject()` and verify stability.
- **Verification Gate**: Worker executes -> Reviewers review -> Challengers test -> Auditor audits -> Gate Pass.

---

## Milestone 3: Batch Conversion (Remaining 29 Timelines)
- **Objective**: Automate conversion across remaining 29 timelines using the verified pilot formula.
- **Tasks**:
  1. Duplicate each remaining timeline to `<OriginalName>_9x16`.
  2. Set 1080x1920 resolution matching each source frame rate.
  3. Apply verified Split Screen reframing, V3 VTuber close-up logic, and V2 GIF repositioning.
  4. Preserve subtitles, audio, and cuts 1:1.
  5. Batch save and check for any media offline.
- **Verification Gate**: Worker executes batch -> Reviewers review sample + aggregate -> Challengers test invariant preservation -> Auditor checks integrity -> Gate Pass.

---

## Milestone 4: Comprehensive E2E Verification & Project State Restore
- **Objective**: Final project-wide quality assurance and clean restoration.
- **Tasks**:
  1. Audit all 30 original 16:9 timelines to ensure 100% untouched.
  2. Audit all 30 new `_9x16` timelines: 1080x1920, matching FPS, zero media offline, subtitle & audio parity, duration equality.
  3. Save project via `ProjectManager.SaveProject()`.
  4. Restore active project, playhead, and page states cleanly.
- **Verification Gate**: Full E2E audit -> Gate Pass -> Final Sentinel handoff.
