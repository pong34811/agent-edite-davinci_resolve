# Project: Tygarina Highlight Moments & DaVinci Resolve Timeline Construction

## Architecture
- **Source Footage**: 32 video files in `C:\Users\warit\SynologyDrive\Tygarina\2026-09-30` (69.50 GiB, constant 60.0 fps, stereo Opus 48kHz audio). Read-only and non-destructive.
- **DaVinci Resolve Environment**: Resolve Studio 21.1.0.17 running in GUI mode, active project `tygarina_2026-09-30`. All 32 source clips are pre-imported in Media Pool `Master` bin.
- **MCP Server**: `davinci-resolve` MCP server (Python scripting API bridge).
- **Highlight Pipeline**:
  1. Audio peak & energy scanning (FFmpeg RMS/Peak) + Speech transcription (faster-whisper GPU).
  2. Candidate selection (Gaming, Fun, Meme categories with duration 30s-180s).
  3. Timeline assembly via `media_pool.create_timeline_from_clips` with precise frame offsets ($t \times 60$ frames).
  4. Programmatic verification via `timeline.list`, `timeline.get_current_timeline`, and forensic auditing.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Footage Profiling & Technical Audit | 32 files cataloged, 60fps verified, read-only preserved | M0 (Done) | Survey |
| 2 | Highlight Moment Extraction | 7 verified candidates (Gaming, Fun, Meme; 55s-65s) with objective audio/transcript rationale | M1 (Done) | Survey |
| 3 | Project Safety & Preflight Check | Verify project state, active project name, media pool items | M2 | Survey/R3 |
| 4 | Resolve Timeline Construction | Construct 7 individual highlight timelines in DaVinci Resolve via MCP | M2 | Request R2 |
| 5 | Frame Accuracy & Duration Check | Ensure timeline start/end frames strictly match selected candidate duration (30s-180s) | M3 | Request R1/R2 |
| 6 | Non-Destructive Integrity Verification | Confirm zero source footage modifications, zero deletions, and clean Resolve project save | M3 | Request R3 |
| 7 | Forensic Integrity Audit | Independent verification of authenticity and absence of shortcuts/cheating | M3 | Integrity Mode |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M0 | Survey & Footage Profiling | Technical inventory, audio/video specs, Resolve environment check | None | DONE |
| M1 | Highlight Analysis & Rationale | Candidate selection, category classification, transcript/audio verification | M0 | DONE |
| M2 | DaVinci Resolve Timeline Construction | Creation of 21 new highlight timelines (28 total) in active Resolve project via MCP | M1 | DONE |
| M3 | Verification, QC & Forensic Audit | Verification of timeline existence, durations, clips, and forensic audit | M2 | DONE |

## Highlight Candidates Specification (Input to M2)
| ID | Category | Source File | Start Time | End Time | Duration | Start Frame (60fps) | End Frame (60fps) | Target Timeline Name |
|---|---|---|---|---|---|---|---|---|
| H1 | Gaming | `Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4` | 6720.0s | 6785.0s | 65.0s | 403200 | 407100 | `Highlight_Gaming_REPO_Jumpscare` |
| H2 | Gaming | `ปืนเขาที่เราหมดแรง @KRATOI_26...mp4` | 5855.0s | 5915.0s | 60.0s | 351300 | 354900 | `Highlight_Gaming_Climbing_Clutch` |
| H3 | Gaming | `IB - สำรวจโลกภาพวาด P1.mp4` | 4475.0s | 4530.0s | 55.0s | 268500 | 271800 | `Highlight_Gaming_Ib_Horror` |
| H4 | Fun | `After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4` | 980.0s | 1035.0s | 55.0s | 58800 | 62100 | `Highlight_Fun_DnD_Bard` |
| H5 | Meme | `Gartic phone - ไทกะสกิลวาดรูป 999999.mp4` | 2510.0s | 2575.0s | 65.0s | 150600 | 154500 | `Highlight_Meme_GarticPhone_Art` |
| H6 | Meme | `Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4` | 2235.0s | 2295.0s | 60.0s | 134100 | 137700 | `Highlight_Meme_FreeTalk_Tiger` |
| H7 | Fun/Gaming | `เมื่อไทกะคือความชิบหายในครัว!.mp4` | 7640.0s | 7705.0s | 65.0s | 458400 | 462300 | `Highlight_Fun_Overcooked_KitchenFire` |

## Round 3 Highlight Candidates Specification (21 New Timelines - M2 COMPLETED)
| # | Category / Game | Source File | MediaPool ID | Start Frame | End Frame | Duration (Frames / Sec) | Target Timeline Name | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | REPO | `Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4` | `4462a5cf-dad7-4499-ab4d-20a999ba2b59` | 275280 | 278580 | 3300 f (55.0s) | `วิ่งหนีปีศาจแทบไม่ทัน_REPO-vdo` | VERIFIED |
| 2 | REPO | `Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4` | `4462a5cf-dad7-4499-ab4d-20a999ba2b59` | 574680 | 577980 | 3300 f (55.0s) | `จังหวะเอาชีวิตรอดเฉียดฉิว_REPO-vdo` | VERIFIED |
| 3 | REPO | `Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4` | `4462a5cf-dad7-4499-ab4d-20a999ba2b59` | 21000 | 24300 | 3300 f (55.0s) | `เปิดตี้แจกความฮากับเพื่อน_REPO-vdo` | VERIFIED |
| 4 | Climbing | `ปืนเขาที่เราหมดแรง @KRATOI_26...mp4` | `3ebbdd92-9aa6-4738-b586-956bf85f35d6` | 257760 | 261060 | 3300 f (55.0s) | `เหลือสองชีวิตเกาะหน้าผาไว้_Climbing-vdo` | VERIFIED |
| 5 | Climbing | `ปืนเขาที่เราหมดแรง @KRATOI_26...mp4` | `3ebbdd92-9aa6-4738-b586-956bf85f35d6` | 301200 | 304500 | 3300 f (55.0s) | `จังหวะกระโดดข้ามหุบเหวสุดเสียว_Climbing-vdo` | VERIFIED |
| 6 | Climbing | `ปืนเขาที่เราหมดแรง @KRATOI_26...mp4` | `3ebbdd92-9aa6-4738-b586-956bf85f35d6` | 14280 | 17580 | 3300 f (55.0s) | `แกล้งเพื่อนตั้งแต่จุดสตาร์ท_Climbing-vdo` | VERIFIED |
| 7 | Ib | `IB - สำรวจโลกภาพวาด P1.mp4` | `7a4e9419-b627-4b4f-87db-9a0d7af59fe2` | 249480 | 252780 | 3300 f (55.0s) | `เจอตัวละครใหม่ตกใจจนร้องลั่น_Ib-vdo` | VERIFIED |
| 8 | Ib | `IB - สำรวจโลกภาพวาด P1.mp4` | `7a4e9419-b627-4b4f-87db-9a0d7af59fe2` | 125280 | 128580 | 3300 f (55.0s) | `ประตูมิติชวนขนหัวลุก_Ib-vdo` | VERIFIED |
| 9 | Ib | `IB - สำรวจโลกภาพวาด P1.mp4` | `7a4e9419-b627-4b4f-87db-9a0d7af59fe2` | 456840 | 460140 | 3300 f (55.0s) | `ไขปริศนาภาพวาดมรณะ_Ib-vdo` | VERIFIED |
| 10 | DnD | `After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4` | `9ae1c0ee-6b90-482e-ac71-a5aac9a6f262` | 262920 | 266220 | 3300 f (55.0s) | `เล่าวินาทีบอสแพ้แบบอนาถ_DnD-vdo` | VERIFIED |
| 11 | DnD | `After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4` | `9ae1c0ee-6b90-482e-ac71-a5aac9a6f262` | 286800 | 290100 | 3300 f (55.0s) | `ฉากโรลเพลย์สุดกาวในห้องน้ำ_DnD-vdo` | VERIFIED |
| 12 | DnD | `After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4` | `9ae1c0ee-6b90-482e-ac71-a5aac9a6f262` | 209400 | 212700 | 3300 f (55.0s) | `ทอยเต๋าพลาดจนแผนพังยับ_DnD-vdo` | VERIFIED |
| 13 | GarticPhone | `Gartic phone - ไทกะสกิลวาดรูป 999999.mp4` | `88c9437b-cf33-48e5-98d5-5faf4844742d` | 157800 | 161100 | 3300 f (55.0s) | `เฉลยภาพวาดจนเพื่อนอึ้งทั้งห้อง_GarticPhone-vdo` | VERIFIED |
| 14 | GarticPhone | `Gartic phone - ไทกะสกิลวาดรูป 999999.mp4` | `88c9437b-cf33-48e5-98d5-5faf4844742d` | 50040 | 53340 | 3300 f (55.0s) | `ลืมปิดไมค์วาดรูปไฟลนก้น_GarticPhone-vdo` | VERIFIED |
| 15 | GarticPhone | `Gartic phone - ไทกะสกิลวาดรูป 999999.mp4` | `88c9437b-cf33-48e5-98d5-5faf4844742d` | 134880 | 138180 | 3300 f (55.0s) | `วาดรูปเพี้ยนจนกลายเป็นมีม_GarticPhone-vdo` | VERIFIED |
| 16 | FreeTalk | `Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4` | `e56002ed-9d9e-4cc4-97c9-fd191a631f5e` | 104040 | 107340 | 3300 f (55.0s) | `ตอบแชทเรื่องสู้เสือด้วยมือเปล่า_FreeTalk-vdo` | VERIFIED |
| 17 | FreeTalk | `Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4` | `e56002ed-9d9e-4cc4-97c9-fd191a631f5e` | 116760 | 120060 | 3300 f (55.0s) | `จำลองเหตุการณ์ถ้าเจอเสือของจริง_FreeTalk-vdo` | VERIFIED |
| 18 | FreeTalk | `Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4` | `e56002ed-9d9e-4cc4-97c9-fd191a631f5e` | 91080 | 94380 | 3300 f (55.0s) | `อ่านคอมเมนต์สุดกาวขำจนตัวโยก_FreeTalk-vdo` | VERIFIED |
| 19 | Overcooked | `เมื่อไทกะคือความชิบหายในครัว!.mp4` | `407b877a-89c8-42b1-bc6d-71fbcd5fb6d1` | 25800 | 29100 | 3300 f (55.0s) | `เปิดครัววันแรกก็วุ่นวายซะแล้ว_Overcooked-vdo` | VERIFIED |
| 20 | Overcooked | `เมื่อไทกะคือความชิบหายในครัว!.mp4` | `407b877a-89c8-42b1-bc6d-71fbcd5fb6d1` | 231000 | 234300 | 3300 f (55.0s) | `ออเดอร์ล้นครัวสั่งความวิกฤต_Overcooked-vdo` | VERIFIED |
| 21 | Overcooked | `เมื่อไทกะคือความชิบหายในครัว!.mp4` | `407b877a-89c8-42b1-bc6d-71fbcd5fb6d1` | 541800 | 545100 | 3300 f (55.0s) | `จานตกน้ำหมดครัวนาทีสุดท้าย_Overcooked-vdo` | VERIFIED |

## Interface Contracts
### Candidate Specification ↔ DaVinci Resolve MCP
- Each highlight is created as an independent timeline.
- API Route:
  1. `media_pool.set_current_folder("Master")`
  2. Resolve clip ID retrieved from Media Pool Master bin matching `Source File`.
  3. `media_pool.create_timeline_from_clips` with `name=Target Timeline Name`, `clip_infos=[{clip_id, start_frame, end_frame, record_frame: 0}]`.
  4. Project saved via `project_manager.save_project`.
  5. Total project timelines verified: exactly 28 (7 prior + 21 new).

## Code Layout
- Agent Workspaces: `.agents/teamwork/`
- Documentation & Reports:
  - Round 3 Candidate Specification: `.agents/teamwork/orchestrator_3/PROJECT.md`
  - Explorer Survey & Analysis: `.agents/teamwork/explorer_survey_r3_3/analysis.md`
  - Timeline Construction Worker: `.agents/teamwork/worker_timeline_construction_r3/`
  - Verification & Handoff: `.agents/teamwork/worker_timeline_construction_r3/handoff.md`

