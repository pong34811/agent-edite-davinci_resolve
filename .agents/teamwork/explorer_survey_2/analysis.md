# DaVinci Resolve Environment & Media Survey Report

**Explorer**: Explorer 2 (Resolve Environment Explorer)  
**Date**: 2026-10-02  
**Status**: Completed  
**Working Directory**: `C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\explorer_survey_2`

---

## 1. Executive Summary

DaVinci Resolve Studio 21.1.0.17 is currently running in GUI mode and successfully connected via the `davinci-resolve` MCP server (v4.8.23). The active project is `tygarina_2026-09-30`.

Key conclusions:
1. **Source Footage is 100% Ingested**: All 32 video files present in `C:\Users\warit\SynologyDrive\Tygarina\2026-09-30` (totalling 78.85 hours and 69.50 GB) are **already imported** into the Media Pool root folder (`Master`). There are 0 missing clips and 0 extra clips. No media pool import step is required.
2. **Zero Timelines Currently Exist**: The project currently has 0 timelines (`timeline_count: 0`), meaning the project is clean and ready for timeline generation.
3. **Critical Frame Rate Mismatch**: All 32 source clips are recorded at **60.00 fps**. However, the active project's `timelineFrameRate` is currently set to **24.0 fps**. Because no timelines exist yet, project settings can be safely adjusted or timelines explicitly configured before any clip is placed.
4. **Timeline Creation API is Fully Operational**: The MCP server exposes `media_pool.create_timeline_from_clips` (with subclip `start_frame` and `end_frame`), `media_pool.create_timeline` (empty timeline), and `media_pool.append_to_timeline` (with `track_index` and frame offsets).

---

## 2. DaVinci Resolve & MCP Server Environment

Probed via `resolve_control`:

| Property | Value | Evidence / Tool Source |
|---|---|---|
| **Product** | DaVinci Resolve Studio | `resolve_control get_version` |
| **Resolve Build Version** | `21.1.0.17` (`[21, 1, 0, 17, ""]`) | `resolve_control get_version` |
| **Version Gate Status** | Clears all 68 recorded version gates | `build.unavailable_on_this_build: []` |
| **MCP Server Version** | `4.8.23` | `resolve_control get_version` |
| **Runtime Mode** | GUI Mode (`headless: false`) | `resolve_control runtime_mode` |
| **Process Path** | `C:\Program Files\Blackmagic Design\DaVinci Resolve\Resolve.exe` | `resolve_control runtime_mode` |
| **Connected Database** | Type: `Disk`, Name: `google drive` | `resolve_control runtime_mode` |
| **Current UI Page** | `cut` | `resolve_control get_page` |

---

## 3. Active Project Configuration

Probed via `project_manager get_current` and `project_settings get_setting`:

| Setting Key | Current Value | Notes |
|---|---|---|
| **Project Name** | `tygarina_2026-09-30` | Active project loaded in Resolve |
| **Project Unique ID** | `c0d08784-1fd9-4675-921b-d77a6b5cccdf` | Canonical UUID |
| **Timeline Resolution** | `1920 x 1080` | `timelineResolutionWidth` / `Height` |
| **Output Resolution** | `1920 x 1080` | Matches timeline resolution (1:1) |
| **Pixel Aspect Ratio** | `square` | Standard 1.0 PAR |
| **Timeline Frame Rate** | `24.0` | Default project timeline rate |
| **Playback Frame Rate** | `24` | `timelinePlaybackFrameRate` |
| **Color Science** | `davinciYRGB` | Rec.709 (Scene) / Rec.709 Gamma 2.4 |
| **Existing Timelines** | `0` | Probed via `timeline list` |

---

## 4. Media Pool & Footage Ingest Audit

### Ingest Status Comparison

A direct comparison between the physical directory `C:\Users\warit\SynologyDrive\Tygarina\2026-09-30` and the Media Pool `Master` bin was performed using `survey_clips.py`:

- **Physical Files on Disk**: 32 files (.mp4)
- **Clips in Media Pool Master Bin**: 32 clips
- **Missing in Pool**: 0
- **Extra in Pool**: 0
- **Ingest Conclusion**: **100% Complete**. No import operation is necessary.

### Comprehensive Footage Inventory

Technical verification via `probe_footage.py` and `ffprobe` (saved in `footage_specs.json`):

- **Total Video Count**: 32 files
- **Total Duration**: 78.85 hours (4,731 minutes)
- **Total Disk Size**: 69.50 GB
- **Frame Rate (all clips)**: **60.00 fps** (constant across 100% of footage)
- **Audio Specification (all clips)**: Opus codec, 48,000 Hz, 2 Channels (Stereo), 32-bit depth
- **Video Codecs**: H.264 High L4.2, VP9, AV1 (all recognized natively by Resolve Studio 21.1)
- **Resolutions**:
  - Full HD (1920x1080): 13 clips
  - HD (1280x720): 19 clips

#### Inventory Table

| # | Clip Name | Media Pool Item ID | Resolution | Duration (TC / min) | Video Codec | Size (MB) |
|---|---|---|---|---|---|---|
| 1 | บอสทำไรตอนตี 2？？.mp4 | `68b3833d-61bf-4b7c-b8eb-95c2b970ab8a` | 1920x1080 | 00:55:46:42 (55.8m) | h264 | 1,038.4 |
| 2 | ฝึกเล่น LoL.mp4 | `12a09f5f-b6b0-47fc-8e1f-41ba5c009ab4` | 1280x720 | 01:43:30:08 (103.5m) | h264 | 1,132.6 |
| 3 | เสืออยากคุย [qZVnCXIjfzo].mp4 | `00cc01c1-f3cc-4666-a40c-197214ba162e` | 1920x1080 | 02:12:49:02 (132.8m) | av1 | 2,672.8 |
| 4 | สอนไทกะเล่น LoL ที.mp4 | `35d91ae8-0efc-474b-8034-21b09eb5cc3a` | 1280x720 | 02:31:22:05 (151.4m) | h264 | 1,579.4 |
| 5 | เสืออยากคุย [VqELVP2u2oU].mp4 | `d9d8a666-c3f9-4dc8-b037-68d887eab4dd` | 1920x1080 | 02:17:23:02 (137.4m) | av1 | 3,120.3 |
| 6 | IB - สำรวจโลกภาพวาด P1.mp4 | `7a4e9419-b627-4b4f-87db-9a0d7af59fe2` | 1280x720 | 02:26:08:18 (146.1m) | av1 | 658.6 |
| 7 | รายการ ： Q&A คุยกับนกแก้ว.mp4 | `fc777b1b-0b4c-4176-8805-05a65110b206` | 1280x720 | 01:47:30:12 (107.5m) | h264 | 1,273.1 |
| 8 | R.E.P.O @ballkarozumar1238...Mikhail.mp4 | `a1af7fdd-bf9d-4166-b15a-7108d7a3ece7` | 1920x1080 | 03:07:58:45 (188.0m) | vp9 | 3,065.0 |
| 9 | เสืออยากคุย [ns0I3EihIUI].mp4 | `b04b6312-022f-44a4-be57-9ff9e0c14661` | 1920x1080 | 03:17:21:40 (197.4m) | av1 | 3,958.9 |
| 10 | Free Talk ：สอนไทกะเป็นโจรสลัดที.mp4 | `58c86277-78be-4d93-9ecc-258f9a8723b5` | 1280x720 | 01:29:46:00 (89.8m) | h264 | 1,102.8 |
| 11 | R.E.P.O @Luche...Salika.mp4 | `b3fdb6ac-e495-45b7-9bce-5ff92b809fd7` | 1920x1080 | 02:00:40:16 (120.7m) | vp9 | 1,756.2 |
| 12 | Gartic phone - ไทกะสกิลวาดรูป 999999.mp4 | `88c9437b-cf33-48e5-98d5-5faf4844742d` | 1280x720 | 02:20:35:12 (140.6m) | av1 | 577.8 |
| 13 | ฉลอง 800 ซับ! วงล้อเสี่ยงท้าย!!.mp4 | `03273e5a-487f-4a23-a3fb-a56ba1ce4a3f` | 1280x720 | 01:24:00:12 (84.0m) | h264 | 940.8 |
| 14 | Free Talk： ลูกน้องไม่ตอบก็จะคุย!.mp4 | `c483d870-8c4f-494a-9ca7-61631f47608c` | 1280x720 | 01:26:41:06 (86.7m) | h264 | 1,064.5 |
| 15 | R.E.P.O @ball...NANOZEROO.mp4 | `56e2c71f-976c-4cbd-9d23-b4d2834c19df` | 1920x1080 | 03:05:50:24 (185.8m) | vp9 | 2,839.4 |
| 16 | ไลฟ์นี้จะเล่น Fallout 4 Nuka-world P1.mp4 | `8d711ef7-b6fc-444e-8f07-281d928da30d` | 1920x1080 | 06:34:56:47 (395.0m) | vp9 | 10,082.9 |
| 17 | IB - สำรวจโลกภาพวาด P2...mp4 | `dcb04276-39a9-41f0-9cdd-53b1bafc5752` | 1280x720 | 03:59:05:40 (239.1m) | av1 | 1,324.4 |
| 18 | Free Talk ： หยุดเสือด้วยมือเปล่า？？.mp4 | `e56002ed-9d9e-4cc4-97c9-fd191a631f5e` | 1280x720 | 02:08:24:01 (128.4m) | h264 | 1,586.8 |
| 19 | Free Talk - ปิดคาสิโนแล้วบอสไปทำไรต่อ.mp4 | `b3931d4e-7ce5-452b-9cc9-2a667e5607fd` | 1280x720 | 01:13:18:03 (73.3m) | av1 | 428.6 |
| 20 | Free Talk ： จีบ 10 ปี แถมฟรีหนี้ 200 ล้าน.mp4 | `99bf4a6d-245e-4a9a-8889-10b1d6b40203` | 1280x720 | 02:17:10:05 (137.2m) | h264 | 1,401.4 |
| 21 | Collab R.E.P.O - เก็บของไว้ให้ไกลเสือ.mp4 | `4462a5cf-dad7-4499-ab4d-20a999ba2b59` | 1920x1080 | 02:50:59:18 (171.0m) | vp9 | 4,876.5 |
| 22 | After DnD ： เมื่อบาร์ดด่าจนมังกรตาย!.mp4 | `9ae1c0ee-6b90-482e-ac71-a5aac9a6f262` | 1280x720 | 02:30:53:24 (150.9m) | h264 | 1,762.8 |
| 23 | Free Talk ：เมื่อได้เป็นตัวโดนประจำตี้.mp4 | `aa7e9833-0b07-4cad-9951-b7dd0b15c607` | 1920x1080 | 01:43:52:00 (103.9m) | vp9 | 2,350.7 |
| 24 | เมื่อไทกะคือความชิบหายในครัว!.mp4 | `407b877a-89c8-42b1-bc6d-71fbcd5fb6d1` | 1920x1080 | 03:23:35:08 (203.6m) | vp9 | 2,834.3 |
| 25 | ไลฟ์คุยไปเรื่อยแบบเสือขี้เบื่อ.mp4 | `1e4a373c-80b2-41f3-840b-9a04b12ae218` | 1920x1080 | 02:07:33:11 (127.6m) | vp9 | 2,653.5 |
| 26 | ปืนเขาที่เราหมดแรง...Frontier.mp4 | `3ebbdd92-9aa6-4738-b586-956bf85f35d6` | 1920x1080 | 01:55:45:04 (115.8m) | vp9 | 2,955.3 |
| 27 | ใช้ชีวิตไปกับไทกะ 101 (ไม่ชินกล้องเลย).mp4 | `12371e44-432d-45d1-b9d2-fe3c1017b2f8` | 1920x1080 | 02:05:29:10 (125.5m) | vp9 | 2,772.3 |
| 28 | MEET BOSS ： บอสเราเจอผู้หญิงไม่ได้เลย.mp4 | `4600079c-dfb7-41ca-9ce8-284f1d9161c7` | 1280x720 | 03:06:16:25 (186.3m) | h264 | 2,176.4 |
| 29 | After DnD EP.4...เพราะความรัก.mp4 | `33bd05cc-6238-469a-acf1-74e6bac5270e` | 1280x720 | 01:23:32:09 (83.5m) | h264 | 953.2 |
| 30 | After DnD ： หลอนครั้งแรกแต่จบดาร์กขั้นสุด.mp4 | `4d96b4b6-8a58-4182-bb68-308f7a2dae3d` | 1280x720 | 02:23:50:17 (143.8m) | av1 | 489.5 |
| 31 | Free Talk ：เมื่อไทกะเล่น เกย์กับชาย...mp4 | `b4196bbd-e94a-401b-abe3-eca5d6e056f4` | 1280x720 | 02:15:27:16 (135.5m) | h264 | 1,645.8 |
| 32 | Free Talk ติดเกาะกับเธอ จ้างเท่าไหร่ก็ไม่ออก.mp4 | `6d94e629-b683-43ee-894a-ac94c805c736` | 1280x720 | 04:43:22:42 (283.4m) | h264 | 4,092.8 |

---

## 5. Critical Technical Findings & Architecture Risks

### 1. Frame Rate Alignment: 60 fps vs 24 fps
- **The Observation**: Every source file is 60.00 fps. The active project is set to `timelineFrameRate: 24.0`.
- **The Impact**: If a timeline is created at 24.0 fps from 60.0 fps source footage:
  - Frame rate conversion/drop-frame occurs.
  - Subclip `startFrame` and `endFrame` calculated from 60 fps media will be scaled or quantized if mapped to 24 fps record positions.
  - As documented in `api_truth`, source frame arithmetic across mismatched frame rates requires strict media-rate frame counting (`seconds = source_start / media_fps`).
- **Opportunity**: Because **0 timelines** exist in the project right now, `timelineFrameRate` can be updated in project settings (or custom timeline settings applied) before any timeline is created.

### 2. Multi-Resolution Handling (1080p and 720p)
- All files share the 16:9 aspect ratio (`timelinePixelAspectRatio: square`).
- Project setting `timelineInputResMismatchBehavior` is set to `scaleToFit`.
- 720p clips will cleanly scale to fit 1080p timelines without letterboxing/pillarboxing.

---

## 6. DaVinci Resolve MCP API Operations for Downstream Stages

The following methods are verified on this build (Resolve 21.1.0.17):

### A. Subclip Timeline Construction
1. **`media_pool.create_timeline_from_clips`**:
   - Signature: `create_timeline_from_clips(name, clip_infos, if_exists="version")`
   - `clip_infos` structure:
     ```json
     [
       {
         "clip_id": "68b3833d-61bf-4b7c-b8eb-95c2b970ab8a",
         "start_frame": 18000,
         "end_frame": 23400,
         "record_frame": 0
       }
     ]
     ```
   - **Critical Rule (api_truth)**: `media_pool.set_current_folder("Master")` must be confirmed before calling `create_timeline_from_clips`, or Resolve raises `FAILED_TO_CREATE_TIMELINE`.

2. **`media_pool.create_timeline` + `media_pool.append_to_timeline`**:
   - Creates an empty timeline, sets track structure, then appends subclips.
   - Recommended if multi-track placement or subtitle tracks are added.

3. **`timeline.create_variant_from_ranges`**:
   - Creates a timeline directly from source ranges with automatic handle and timecode management.

---

## 7. Next Steps & Recommendations for Implementation

1. **Clip Highlight Candidate Mapping**: Highlight detector (Explorer 1 / Analysis agent) should output candidate ranges with:
   - `file_name` (or `media_pool_item_id` matching Table in Section 4)
   - `start_seconds` and `end_seconds`
   - `start_frame` and `end_frame` at 60.00 fps
   - Highlight category (`gaming`, `fun`, `meme`)
   - Duration check: verify $30\text{s} \le \text{duration} \le 180\text{s}$ per Acceptance Criteria.

2. **Timeline Generation Sequence**:
   - Set current folder to `Master`: `call_mcp_tool(davinci-resolve, media_pool, {action: "set_current_folder", params: {path: "Master"}})`
   - Call `create_timeline_from_clips` for each approved highlight moment with a descriptive timeline name (e.g. `HL_01_Meme_ตีสอง`, `HL_02_Gaming_LoL_Steal`).
   - Run verification via `timeline.list()` and `timeline.get_items()` to confirm presence and duration.
   - Save project via `project_manager.save()`.
