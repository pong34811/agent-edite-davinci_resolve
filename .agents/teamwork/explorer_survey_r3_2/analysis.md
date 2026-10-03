# Technical Analysis: DaVinci Resolve Live Environment Survey

**Agent**: Explorer 2 (`explorer_survey_r3_2`)  
**Mission**: Survey live DaVinci Resolve environment, active project, timeline frame rate, existing timelines, Media Pool items, and verify timeline creation mechanics with Thai Unicode names and exact 60 fps frame ranges.  
**Date**: 2026-10-02T03:11:00Z  

---

## 1. Executive Summary

A comprehensive survey of the live DaVinci Resolve environment was conducted using both DaVinci Resolve MCP tools and the native `DaVinciResolveScript` Python API:
1. **Environment & Active Project**:
   - DaVinci Resolve Studio version is **21.1.0.17** (clears all 68 known version gates).
   - Active Project is **`tygarina_2026-09-30`** (Unique ID: `c0d08784-1fd9-4675-921b-d77a6b5cccdf`).
   - Project `timelineFrameRate` is configured to **60.0 fps** at **1920x1080** (16:9 horizontal).
2. **Existing Timelines**:
   - Exactly **7 highlight timelines** from the previous run exist in the project, all in valid 100% online state, with durations strictly between 55.0s and 65.0s.
3. **Media Pool Inventory (`Master` folder)**:
   - Contains **39 items**: 32 source `.mp4` video files located in `C:\Users\warit\SynologyDrive\Tygarina\2026-09-30` and 7 timeline references.
   - The 7 source video files utilized in the previous run have been mapped to their exact `media_pool_item_id` values.
   - The remaining 25 candidate video files are fully online and indexed.
4. **Timeline Creation Mechanics & Thai Unicode Validation**:
   - Live creation testing verified that `media_pool.create_timeline_from_clips` natively supports Thai Unicode timeline names formatted as `{ชื่อคลิปภาษาไทย}_{ชื่อเกม}-vdo` on DaVinci Resolve Studio 21.1 on Windows without text corruption or encoding issues.
   - Verified that created timelines have **zero "Media Offline"** items (status: `Online`).
   - Verified that frame conversion at 60 fps ($t \times 60$) maps 1:1 to timeline record frames without rounding drift.
   - The test timeline was cleanly deleted, returning the project to its baseline of 7 timelines.

---

## 2. Active DaVinci Resolve Project & Environment Inspection

### 2.1 Build & Application Verification
- **MCP Tool**: `resolve_control.get_version`
- **Native Python API**: `resolve.GetVersion()`, `resolve.GetProductName()`
- **Product Name**: `DaVinci Resolve Studio`
- **Version Array**: `[21, 1, 0, 17, ""]`
- **Version String**: `21.1.0.17`
- **MCP Server Version**: `4.8.23`
- **API Support Status**: Clears all 68 known version gates; fully supports advanced multi-track manipulation, positioned clip insertion, and Unicode timeline names.

### 2.2 Active Project Properties
- **MCP Tool**: `project_manager.get_current`, `project_settings.get_setting`
- **Native Python API**: `pm.GetCurrentProject()`
- **Project Name**: `tygarina_2026-09-30`
- **Project ID**: `c0d08784-1fd9-4675-921b-d77a6b5cccdf`
- **Total Timelines**: 7
- **Timeline Frame Rate (`timelineFrameRate`)**: `60.0` fps
- **Playback Frame Rate (`timelinePlaybackFrameRate`)**: `24` fps (Resolve GUI playback rate, read-only API limitation; does not affect timeline rendering or frame positioning)
- **Timeline Resolution**: `1920` x `1080` (Standard 16:9 Full HD)

---

## 3. Enumeration of Existing Timelines (Prior Run)

All 7 highlight timelines constructed during the previous run are present and verified in the active project:

| Index | Timeline Name | Unique ID | Duration (Frames) | Duration (Seconds) | Source Video File | Source Frame Range [Start..End] |
|:---:|:---|:---|:---:|:---:|:---|:---:|
| 1 | `Highlight_Gaming_REPO_Jumpscare` | `d27a0b25-f0d2-40b9-bd8b-63d1382f56df` | 3900 | 65.0s | `Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4` | 403,200 .. 407,100 |
| 2 | `Highlight_Gaming_Climbing_Clutch` | `2855ef77-dbe2-43ee-a5d9-0b1338158e67` | 3600 | 60.0s | `ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4` | 351,300 .. 354,900 |
| 3 | `Highlight_Gaming_Ib_Horror` | `3aa2003a-846b-4f47-92f0-63b9f2705b2c` | 3300 | 55.0s | `IB - สำรวจโลกภาพวาด P1.mp4` | 268,500 .. 271,800 |
| 4 | `Highlight_Fun_DnD_Bard` | `8cdd0c49-f569-45f3-a6c9-1150c5eb1ef9` | 3300 | 55.0s | `After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4` | 58,800 .. 62,100 |
| 5 | `Highlight_Meme_GarticPhone_Art` | `29ce2285-67a7-44bc-a2dc-a177cd87e67a` | 3900 | 65.0s | `Gartic phone - ไทกะสกิลวาดรูป 999999.mp4` | 150,600 .. 154,500 |
| 6 | `Highlight_Meme_FreeTalk_Tiger` | `4acb6f81-c870-4d3e-b82a-6e971a3a4af8` | 3600 | 60.0s | `Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4` | 134,100 .. 137,700 |
| 7 | `Highlight_Fun_Overcooked_KitchenFire` | `c62ea0c3-79dd-4bd4-835b-82d487e5717a` | 3900 | 65.0s | `เมื่อไทกะคือความชิบหายในครัว!.mp4` | 458,400 .. 462,300 |

### Structural Invariants Observed
- Each timeline possesses exactly **1 Video Track** and **1 Audio Track** (stereo).
- `start_frame` is `0` (timecode `00:00:00:00`).
- Timeline item durations match timeline total durations exactly (no gaps, no tail clips).
- Subtitle tracks: currently 0 on all 7 timelines.

---

## 4. Media Pool Inspection (`Master` Folder)

The Media Pool root (`Master`) contains 39 items:
- 32 Video Clips (`.mp4` source files).
- 7 Timeline references corresponding to Timelines 1–7.

### 4.1 The 7 Processed Video Files from Prior Run
These 7 files correspond to the clips already extracted. When executing the new requirement ("Extract exactly 3 highlight moments per video file (footage)... Exclude the 7 clips already extracted in the previous run to avoid duplicates"):

| Video File Name | MediaPoolItem ID | Duration (TC) | FPS | Resolution | Codec | Prior Highlight Range Excluded |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| `Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4` | `4462a5cf-dad7-4499-ab4d-20a999ba2b59` | 02:50:59:18 | 60.0 | 1920x1080 | H.264 High L4.2 | 6720.0s .. 6785.0s (403200..407100) |
| `ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4` | `3ebbdd92-9aa6-4738-b586-956bf85f35d6` | 01:55:45:04 | 60.0 | 1920x1080 | H.264 High L4.2 | 5855.0s .. 5915.0s (351300..354900) |
| `IB - สำรวจโลกภาพวาด P1.mp4` | `7a4e9419-b627-4b4f-87db-9a0d7af59fe2` | 02:26:08:18 | 60.0 | 1280x720 | H.264 High L3.2 | 4475.0s .. 4530.0s (268500..271800) |
| `After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4` | `9ae1c0ee-6b90-482e-ac71-a5aac9a6f262` | 02:30:53:24 | 60.0 | 1280x720 | H.264 High L3.2 | 980.0s .. 1035.0s (58800..62100) |
| `Gartic phone - ไทกะสกิลวาดรูป 999999.mp4` | `88c9437b-cf33-48e5-98d5-5faf4844742d` | 02:20:35:12 | 60.0 | 1280x720 | H.264 High L3.2 | 2510.0s .. 2575.0s (150600..154500) |
| `Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4` | `e56002ed-9d9e-4cc4-97c9-fd191a631f5e` | 02:08:24:01 | 60.0 | 1280x720 | H.264 High L3.2 | 2235.0s .. 2295.0s (134100..137700) |
| `เมื่อไทกะคือความชิบหายในครัว!.mp4` | `407b877a-89c8-42b1-bc6d-71fbcd5fb6d1` | 03:23:35:08 | 60.0 | 1280x720 | H.264 High L3.2 | 7640.0s .. 7705.0s (458400..462300) |

### 4.2 Complete Inventory of All 32 Video Clips in Media Pool

| # | Status | Video File Name | MediaPoolItem ID | FPS | Duration (TC) | Resolution |
|:---:|:---:|:---|:---|:---:|:---:|:---:|
| 1 | Candidate | `บอสทำไรตอนตี 2？？.mp4` | `68b3833d-61bf-4b7c-b8eb-95c2b970ab8a` | 60.0 | 00:55:46:42 | 1920x1080 |
| 2 | Candidate | `ฝึกเล่น LoL.mp4` | `12a09f5f-b6b0-47fc-8e1f-41ba5c009ab4` | 60.0 | 01:43:30:08 | 1280x720 |
| 3 | Candidate | `เสืออยากคุย [qZVnCXIjfzo].mp4` | `00cc01c1-f3cc-4666-a40c-197214ba162e` | 60.0 | 02:12:49:02 | 1920x1080 |
| 4 | Candidate | `สอนไทกะเล่น LoL ที.mp4` | `35d91ae8-0efc-474b-8034-21b09eb5cc3a` | 59.94 | 02:31:22:05 | 1280x720 |
| 5 | Candidate | `เสืออยากคุย [VqELVP2u2oU].mp4` | `d9d8a666-c3f9-4dc8-b037-68d887eab4dd` | 60.0 | 02:17:23:02 | 1920x1080 |
| 6 | **Prior Processed** | `IB - สำรวจโลกภาพวาด P1.mp4` | `7a4e9419-b627-4b4f-87db-9a0d7af59fe2` | 60.0 | 02:26:08:18 | 1280x720 |
| 7 | Candidate | `รายการ ： Q&A คุยกับนกแก้ว.mp4` | `fc777b1b-0b4c-4176-8805-05a65110b206` | 60.0 | 01:47:30:12 | 1280x720 |
| 8 | Candidate | `R.E.P.O @ballkarozumar1238 @F4RC14  @momomewmoi @Mikhail_Cerise.mp4` | `a1af7fdd-bf9d-4166-b15a-7108d7a3ece7` | 60.0 | 03:07:58:45 | 1280x720 |
| 9 | Candidate | `เสืออยากคุย [ns0I3EihIUI].mp4` | `b04b6312-022f-44a4-be57-9ff9e0c14661` | 60.0 | 03:17:21:40 | 1920x1080 |
| 10 | Candidate | `Free Talk ：สอนไทกะเป็นโจรสลัดที.mp4` | `58c86277-78be-4d93-9ecc-258f9a8723b5` | 60.0 | 01:29:46:00 | 1280x720 |
| 11 | Candidate | `R.E.P.O @Luche_Sinclair @Kungphaokung @RahhatemPSM @Salika_SaharasCh.mp4` | `b3fdb6ac-e495-45b7-9bce-5ff92b809fd7` | 60.0 | 02:00:40:16 | 1280x720 |
| 12 | **Prior Processed** | `Gartic phone - ไทกะสกิลวาดรูป 999999.mp4` | `88c9437b-cf33-48e5-98d5-5faf4844742d` | 60.0 | 02:20:35:12 | 1280x720 |
| 13 | Candidate | `ฉลอง 800 ซับ! วงล้อเสี่ยงท้าย!!.mp4` | `03273e5a-487f-4a23-a3fb-a56ba1ce4a3f` | 60.0 | 01:24:00:12 | 1280x720 |
| 14 | Candidate | `Free Talk： ลูกน้องไม่ตอบก็จะคุย!.mp4` | `c483d870-8c4f-494a-9ca7-61631f47608c` | 60.0 | 01:26:41:06 | 1280x720 |
| 15 | Candidate | `R.E.P.O @ballkarozumar1238 @F4RC14  @momomewmoi @mitsuki_mayu@NANOZEROO.mp4` | `56e2c71f-976c-4cbd-9d23-b4d2834c19df` | 60.0 | 03:05:50:24 | 1280x720 |
| 16 | Candidate | `ไลฟ์นี้จะเล่น Fallout 4 Nuka-world P1.mp4` | `8d711ef7-b6fc-444e-8f07-281d928da30d` | 60.0 | 06:34:56:47 | 1920x1080 |
| 17 | Candidate | `IB - สำรวจโลกภาพวาด P2 @caramellatte710.mp4` | `dcb04276-39a9-41f0-9cdd-53b1bafc5752` | 60.0 | 03:59:05:40 | 1280x720 |
| 18 | **Prior Processed** | `Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4` | `e56002ed-9d9e-4cc4-97c9-fd191a631f5e` | 60.0 | 02:08:24:01 | 1280x720 |
| 19 | Candidate | `Free Talk - ปิดคาสิโนแล้วบอสไปทำไรต่อ.mp4` | `b3931d4e-7ce5-452b-9cc9-2a667e5607fd` | 60.0 | 01:13:18:03 | 1280x720 |
| 20 | Candidate | `Free Talk ： จีบ 10 ปี แถมฟรีหนี้ 200 ล้าน.mp4` | `99bf4a6d-245e-4a9a-8889-10b1d6b40203` | 60.0 | 02:17:10:05 | 1280x720 |
| 21 | **Prior Processed** | `Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4` | `4462a5cf-dad7-4499-ab4d-20a999ba2b59` | 60.0 | 02:50:59:18 | 1920x1080 |
| 22 | **Prior Processed** | `After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4` | `9ae1c0ee-6b90-482e-ac71-a5aac9a6f262` | 60.0 | 02:30:53:24 | 1280x720 |
| 23 | Candidate | `Free Talk ：เมื่อได้เป็นตัวโดนประจำตี้.mp4` | `aa7e9833-0b07-4cad-9951-b7dd0b15c607` | 60.0 | 01:43:52:00 | 1920x1080 |
| 24 | **Prior Processed** | `เมื่อไทกะคือความชิบหายในครัว!.mp4` | `407b877a-89c8-42b1-bc6d-71fbcd5fb6d1` | 60.0 | 03:23:35:08 | 1280x720 |
| 25 | Candidate | `ไลฟ์คุยไปเรื่อยแบบเสือขี้เบื่อ.mp4` | `1e4a373c-80b2-41f3-840b-9a04b12ae218` | 60.0 | 02:07:33:11 | 1920x1080 |
| 26 | **Prior Processed** | `ปืนเขาที่เราหมดแรง @KRATOI_26  @Mixzy21PM  @Pleiades_Frontier.mp4` | `3ebbdd92-9aa6-4738-b586-956bf85f35d6` | 60.0 | 01:55:45:04 | 1920x1080 |
| 27 | Candidate | `ใช้ชีวิตไปกับไทกะ 101 (ไม่ชินกล้องเลย).mp4` | `12371e44-432d-45d1-b9d2-fe3c1017b2f8` | 60.0 | 02:05:29:10 | 1920x1080 |
| 28 | Candidate | `MEET BOSS ： บอสเราเจอผู้หญิงไม่ได้เลย.mp4` | `4600079c-dfb7-41ca-9ce8-284f1d9161c7` | 60.0 | 03:06:16:25 | 1280x720 |
| 29 | Candidate | `After DnD EP.4 ตอน เมื่อไทกะนอนไม่หลับเพราะความรัก.mp4` | `33bd05cc-6238-469a-acf1-74e6bac5270e` | 60.0 | 01:23:32:09 | 1280x720 |
| 30 | Candidate | `After DnD ： หลอนครั้งแรกแต่จบดาร์กขั้นสุด.mp4` | `4d96b4b6-8a58-4182-bb68-308f7a2dae3d` | 60.0 | 02:23:50:17 | 1280x720 |
| 31 | Candidate | `Free Talk ：เมื่อไทกะเล่น เกย์กับชายใน DnD โดยไม่รู้ตัว.mp4` | `b4196bbd-e94a-401b-abe3-eca5d6e056f4` | 60.0 | 02:15:27:16 | 1280x720 |
| 32 | Candidate | `Free Talk ติดเกาะกับเธอ จ้างเท่าไหร่ก็ไม่ออก.mp4` | `6d94e629-b683-43ee-894a-ac94c805c736` | 60.0 | 04:43:22:42 | 1280x720 |

---

## 5. Timeline Creation Mechanics & Thai Unicode Validation

### 5.1 Verification Test Design
To prove that DaVinci Resolve Studio 21.1 on Windows can create and manage timelines named strictly using `{ชื่อคลิปภาษาไทย}_{ชื่อเกม}-vdo`, an empirical end-to-end test was performed:
1. Target Name: `ทดสอบการตัดต่อ_TEST-vdo` (conforming to `{ชื่อภาษาไทย}_{ชื่อเกม}-vdo`).
2. Source Clip: `บอสทำไรตอนตี 2？？.mp4` (MediaPoolItem ID: `68b3833d-61bf-4b7c-b8eb-95c2b970ab8a`).
3. Positioned Clip Specification:
   - `start_frame`: 0
   - `end_frame`: 1800 (exactly 30.0s at 60 fps)
   - `record_frame`: 0
4. MCP Execution:
   ```json
   {
     "action": "create_timeline_from_clips",
     "params": {
       "name": "ทดสอบการตัดต่อ_TEST-vdo",
       "clip_infos": [
         {
           "clip_id": "68b3833d-61bf-4b7c-b8eb-95c2b970ab8a",
           "start_frame": 0,
           "end_frame": 1800,
           "record_frame": 0
         }
       ]
     }
   }
   ```

### 5.2 Verification Findings
1. **Creation Response**:
   - `success`: `true`
   - `name`: `"ทดสอบการตัดต่อ_TEST-vdo"`
   - `id`: `"1e23a44b-0187-460d-8a17-d9c89e8ff72d"`
   - `created_new`: `true`
2. **Readback via `timeline.get_current`**:
   - Name read back identically as `"ทดสอบการตัดต่อ_TEST-vdo"`.
   - `start_frame`: 0, `end_frame`: 1800.
3. **Structure & Media Status Probe via `timeline.probe_timeline_structure`**:
   - Video Track 1: 1 item, `start`: 0, `end`: 1800, `source_start`: 0, `source_end`: 1800, `source_fps`: 60.0.
   - Audio Track 1: 1 item, `start`: 0, `end`: 1800, `source_start`: 0, `source_end`: 1800, `source_fps`: 60.0.
   - **`file_exists`**: `true`
   - **`media_status`**: `"Online"` (100% verified online, zero offline media).
4. **Cleanup & Invariant Preservation**:
   - The test timeline was deleted using `media_pool.delete_timelines` with `confirm_token` (`d8a88a4d18d24237b621df3564c17821`).
   - Project timeline count cleanly returned from 8 to 7.
   - Verified via `timeline.list` that all 7 baseline timelines remain intact and unchanged.

### 5.3 Frame Range Calculations ($t \times 60$)
Since the project `timelineFrameRate` is configured to `60.0`:
- 1 second = 60 frames.
- Frame calculations are 100% deterministic integer multiples:
  $$\text{start\_frame} = \text{round}(t_{start} \times 60)$$
  $$\text{end\_frame} = \text{round}(t_{end} \times 60)$$
  $$\text{duration\_frames} = \text{end\_frame} - \text{start\_frame} = \text{round}((t_{end} - t_{start}) \times 60)$$
- Valid duration window: 30 seconds to 180 seconds = 1,800 frames to 10,800 frames.

---

## 6. Recommendations for Downstream Workers & Orchestrator

1. **Naming Format Compliance**:
   - Use `{ชื่อคลิปภาษาไทย}_{ชื่อเกม}-vdo`.
   - Ensure the prefix contains only Thai Unicode glyphs (U+0E01..U+0E5B) and Thai spaces/punctuation, strictly avoiding English letters (A-Z, a-z).
   - Resolve Studio 21.1 on Windows handles Thai UTF-8 strings natively in timeline names without issue.
2. **Timeline Creation Tool**:
   - Use `media_pool.create_timeline_from_clips` with positioned `clip_infos`:
     `[{'clip_id': <media_pool_item_id>, 'start_frame': <start>, 'end_frame': <end>, 'record_frame': 0}]`.
   - This method creates the timeline and populates Video 1 and Audio 1 tracks simultaneously in a single atomic transaction.
3. **Save Project After Creation**:
   - Always call `project_manager(action='save')` to persist created timelines to the project database.
