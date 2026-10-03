# Project: Tygarina Deep Highlight Moments & DaVinci Resolve Timeline Construction (Round 3)

## Architecture
- **Source Footage**: 32 video files in `C:\Users\warit\SynologyDrive\Tygarina\2026-09-30` (69.50 GiB, constant 60.0 fps, stereo Opus 48kHz audio). Read-only and non-destructive.
- **DaVinci Resolve Environment**: Resolve Studio 21.1.0.17 running in GUI mode, active project `tygarina_2026-09-30`. All 32 source clips pre-imported in Media Pool `Master` bin.
- **MCP Server**: `davinci-resolve` MCP server (Python scripting API bridge).
- **Highlight Pipeline**:
  1. Survey & Deep Footage Analysis: Audio RMS peak scanning + GPU faster-whisper transcription (completed by Explorers).
  2. Candidate selection: Exactly 3 new highlight moments per processed source video file (21 total), excluding the 7 prior clips (H1..H7) to ensure zero overlap.
  3. Timeline construction: Construct 21 individual highlight timelines in DaVinci Resolve strictly named `{ชื่อคลิปภาษาไทย}_{ชื่อเกม}-vdo` where `{ชื่อคลิปภาษาไทย}` has zero English letters.
  4. Programmatic verification: Dual-layer verification via Resolve MCP and Python scripting, Reviewers, Challengers, and Forensic Auditor.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Footage Survey & Prior Scope Mapping | 7 processed files verified, 7 prior clips mapped to zero-overlap exclusion zones | M0 | Survey |
| 2 | Resolve Environment & Media Pool Check | Active project `tygarina_2026-09-30`, 60 fps, media item IDs cataloged | M0 | Survey |
| 3 | Highlight Candidate Discovery (21 clips) | 3 distinct 55s clips per file with Thai titles, timestamps, and objective rationale | M1 | Survey |
| 4 | Resolve Timeline Construction (21 timelines) | Construct 21 timelines named `{ชื่อคลิปภาษาไทย}_{ชื่อเกม}-vdo` via MCP | M2 | Request R2/R3 |
| 5 | Frame Accuracy & Zero Offline Media | Confirm 55.0s (3300 frames) duration, zero offline media, exact in/out frames | M3 | Request R3/Verification |
| 6 | Non-Destructive Storage Invariant | Verify 0 files modified, deleted, or transcoded in SynologyDrive | M3 | Safety |
| 7 | Forensic Integrity Audit | Independent verification of authenticity, unmocked Resolve API, Project.db | M3 | Integrity Mode |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M0 | Survey & Scope Mapping | Catalog footage, Resolve state, map prior exclusion zones | None | DONE |
| M1 | Deep Footage Analysis & Candidate Selection | 21 highlight candidates (3/file) with Thai-only names & objective rationale | M0 | DONE |
| M2 | DaVinci Resolve Timeline Construction | Construct 21 highlight timelines in active Resolve project via MCP | M1 | DONE |
| M3 | Verification, QC & Forensic Audit | Reviewers, Challengers, and Forensic Auditor gate checks | M2 | DONE |

## 21 Highlight Candidates Specification (All 21 Timelines Verified)
| # | Source File | MediaPool ID | Game Tag | Start (s) | End (s) | Duration | Start Frame | End Frame | Target Timeline Name | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4` | `4462a5cf-dad7-4499-ab4d-20a999ba2b59` | `REPO` | 4588.0s | 4643.0s | 55.0s | 275280 | 278580 | `วิ่งหนีปีศาจแทบไม่ทัน_REPO-vdo` | VERIFIED |
| 2 | `Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4` | `4462a5cf-dad7-4499-ab4d-20a999ba2b59` | `REPO` | 9578.0s | 9633.0s | 55.0s | 574680 | 577980 | `จังหวะเอาชีวิตรอดเฉียดฉิว_REPO-vdo` | VERIFIED |
| 3 | `Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4` | `4462a5cf-dad7-4499-ab4d-20a999ba2b59` | `REPO` | 350.0s | 405.0s | 55.0s | 21000 | 24300 | `เปิดตี้แจกความฮากับเพื่อน_REPO-vdo` | VERIFIED |
| 4 | `ปืนเขาที่เราหมดแรง @KRATOI_26...mp4` | `3ebbdd92-9aa6-4738-b586-956bf85f35d6` | `Climbing` | 4296.0s | 4351.0s | 55.0s | 257760 | 261060 | `เหลือสองชีวิตเกาะหน้าผาไว้_Climbing-vdo` | VERIFIED |
| 5 | `ปืนเขาที่เราหมดแรง @KRATOI_26...mp4` | `3ebbdd92-9aa6-4738-b586-956bf85f35d6` | `Climbing` | 5020.0s | 5075.0s | 55.0s | 301200 | 304500 | `จังหวะกระโดดข้ามหุบเหวสุดเสียว_Climbing-vdo` | VERIFIED |
| 6 | `ปืนเขาที่เราหมดแรง @KRATOI_26...mp4` | `3ebbdd92-9aa6-4738-b586-956bf85f35d6` | `Climbing` | 238.0s | 293.0s | 55.0s | 14280 | 17580 | `แกล้งเพื่อนตั้งแต่จุดสตาร์ท_Climbing-vdo` | VERIFIED |
| 7 | `IB - สำรวจโลกภาพวาด P1.mp4` | `7a4e9419-b627-4b4f-87db-9a0d7af59fe2` | `Ib` | 4158.0s | 4213.0s | 55.0s | 249480 | 252780 | `เจอตัวละครใหม่ตกใจจนร้องลั่น_Ib-vdo` | VERIFIED |
| 8 | `IB - สำรวจโลกภาพวาด P1.mp4` | `7a4e9419-b627-4b4f-87db-9a0d7af59fe2` | `Ib` | 2088.0s | 2143.0s | 55.0s | 125280 | 128580 | `ประตูมิติชวนขนหัวลุก_Ib-vdo` | VERIFIED |
| 9 | `IB - สำรวจโลกภาพวาด P1.mp4` | `7a4e9419-b627-4b4f-87db-9a0d7af59fe2` | `Ib` | 7614.0s | 7669.0s | 55.0s | 456840 | 460140 | `ไขปริศนาภาพวาดมรณะ_Ib-vdo` | VERIFIED |
| 10 | `After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4` | `9ae1c0ee-6b90-482e-ac71-a5aac9a6f262` | `DnD` | 4382.0s | 4437.0s | 55.0s | 262920 | 266220 | `เล่าวินาทีบอสแพ้แบบอนาถ_DnD-vdo` | VERIFIED |
| 11 | `After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4` | `9ae1c0ee-6b90-482e-ac71-a5aac9a6f262` | `DnD` | 4780.0s | 4835.0s | 55.0s | 286800 | 290100 | `ฉากโรลเพลย์สุดกาวในห้องน้ำ_DnD-vdo` | VERIFIED |
| 12 | `After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4` | `9ae1c0ee-6b90-482e-ac71-a5aac9a6f262` | `DnD` | 3490.0s | 3545.0s | 55.0s | 209400 | 212700 | `ทอยเต๋าพลาดจนแผนพังยับ_DnD-vdo` | VERIFIED |
| 13 | `Gartic phone - ไทกะสกิลวาดรูป 999999.mp4` | `88c9437b-cf33-48e5-98d5-5faf4844742d` | `GarticPhone` | 2630.0s | 2685.0s | 55.0s | 157800 | 161100 | `เฉลยภาพวาดจนเพื่อนอึ้งทั้งห้อง_GarticPhone-vdo` | VERIFIED |
| 14 | `Gartic phone - ไทกะสกิลวาดรูป 999999.mp4` | `88c9437b-cf33-48e5-98d5-5faf4844742d` | `GarticPhone` | 834.0s | 889.0s | 55.0s | 50040 | 53340 | `ลืมปิดไมค์วาดรูปไฟลนก้น_GarticPhone-vdo` | VERIFIED |
| 15 | `Gartic phone - ไทกะสกิลวาดรูป 999999.mp4` | `88c9437b-cf33-48e5-98d5-5faf4844742d` | `GarticPhone` | 2248.0s | 2303.0s | 55.0s | 134880 | 138180 | `วาดรูปเพี้ยนจนกลายเป็นมีม_GarticPhone-vdo` | VERIFIED |
| 16 | `Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4` | `e56002ed-9d9e-4cc4-97c9-fd191a631f5e` | `FreeTalk` | 1734.0s | 1789.0s | 55.0s | 104040 | 107340 | `ตอบแชทเรื่องสู้เสือด้วยมือเปล่า_FreeTalk-vdo` | VERIFIED |
| 17 | `Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4` | `e56002ed-9d9e-4cc4-97c9-fd191a631f5e` | `FreeTalk` | 1946.0s | 2001.0s | 55.0s | 116760 | 120060 | `จำลองเหตุการณ์ถ้าเจอเสือของจริง_FreeTalk-vdo` | VERIFIED |
| 18 | `Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4` | `e56002ed-9d9e-4cc4-97c9-fd191a631f5e` | `FreeTalk` | 1518.0s | 1573.0s | 55.0s | 91080 | 94380 | `อ่านคอมเมนต์สุดกาวขำจนตัวโยก_FreeTalk-vdo` | VERIFIED |
| 19 | `เมื่อไทกะคือความชิบหายในครัว!.mp4` | `407b877a-89c8-42b1-bc6d-71fbcd5fb6d1` | `Overcooked` | 430.0s | 485.0s | 55.0s | 25800 | 29100 | `เปิดครัววันแรกก็วุ่นวายซะแล้ว_Overcooked-vdo` | VERIFIED |
| 20 | `เมื่อไทกะคือความชิบหายในครัว!.mp4` | `407b877a-89c8-42b1-bc6d-71fbcd5fb6d1` | `Overcooked` | 3850.0s | 3905.0s | 55.0s | 231000 | 234300 | `ออเดอร์ล้นครัวสั่งความวิกฤต_Overcooked-vdo` | VERIFIED |
| 21 | `เมื่อไทกะคือความชิบหายในครัว!.mp4` | `407b877a-89c8-42b1-bc6d-71fbcd5fb6d1` | `Overcooked` | 9030.0s | 9085.0s | 55.0s | 541800 | 545100 | `จานตกน้ำหมดครัวนาทีสุดท้าย_Overcooked-vdo` | VERIFIED |

## Interface Contracts
- API Route:
  1. MediaPool current folder: `Master` (`media_pool.set_current_folder("Master")`)
  2. For each candidate 1..21:
     Call `media_pool.create_timeline_from_clips` with:
     - `name`: Target Timeline Name
     - `clip_infos`: `[{"clip_id": MediaPool_ID, "start_frame": Start_Frame, "end_frame": End_Frame, "record_frame": 0}]`
  3. Save project via `project_manager.save_project`
  4. Verify timeline count in project is 28 (7 prior + 21 new)
