# Source Timelines Enumeration & Deep Dive Report

**Project**: `KT404_2026-09-29` (Project ID: `7c38045b-c9ae-426c-8b4c-2e2d726d88ff`)  
**Investigator**: Explorer 2 (`teamwork_preview_explorer`)  
**Date**: 2026-10-01  
**Integrity Mode**: Read-Only Preflight Inspection  

---

## 1. Executive Summary

A comprehensive, non-destructive audit of DaVinci Resolve project `KT404_2026-09-29` was conducted via the DaVinci Resolve MCP bridge and Python Scripting API (`DaVinci Resolve Studio 21.1.0.17`).

Key findings:
1. **Total Timelines**: Exactly **30 edited source timelines** exist in the project, all residing in Media Pool bin `Master/Shorts_2026-09-29/Fun`.
2. **Aspect Ratio & Resolution**: **100% (30 of 30) are horizontal 16:9 timelines** configured at `1920x1080` raster.
3. **Start Timecode**: Uniform across all 30 timelines (`01:00:00:00`).
4. **Frame Rates**:
   - **29 timelines** operate at **60.0 FPS** (Start frame: `216000`).
   - **1 timeline** (Index 25: `บอสมังกร_Soul Walker-vdo`, ID: `454c59dd-6b7e-4ee4-96fd-c829f001bde1`) operates at **30.0 FPS** (Start frame: `108000`). *Crucial note for 9:16 duplicate creation.*
5. **Universal Video Layout**:
   - `V1`: Exactly 1 item — Base gameplay / live stream recording.
   - `V2`: 1 to 2 items — Reaction GIF / Illustration overlays.
   - `V3`: Exactly 3 items — Native Resolve `Adjustment Clip`s for VTuber Focus with Fusion comps (`MediaIn1 -> Transform1 -> MediaOut1`, `Size=1.3`, `Center=(0.38, 0.81)`).
6. **Native Subtitle Tracks**: Every timeline possesses 1 native Subtitle track (`Sub1`, named `TH` or `Subtitle 1`), containing between 29 and 127 cues.
7. **Audio Track Architecture**:
   - `A1`: Original stream audio (Stereo across all 30).
   - `A2`: SFX (Mono with `-11.0 dB` in Timelines 1–25; Stereo with `0.0 dB` in Timelines 26–30).
   - `A3`: BGM (Mono with `-23.0 dB` and 30-frame fade-in / 60-frame fade-out in Timelines 1–25; Stereo with `0.0 dB` and 0-fade in Timelines 26–30).
8. **Media Status**: **Zero offline media items**. Every referenced file exists on disk at its recorded path under `G:\My Drive\Projects\...`.

---

## 2. Complete Enumeration of All 30 Source Timelines

| Index | Timeline Name | Unique ID | Start TC | End TC | Duration (Frames) | Duration (TC) | FPS | Resolution | 16:9? |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | ขุดมั่วเจอเหล็กกองใหญ่_Minecraft-vdo | `67402c28-d713-4383-8e5e-f4a77b782e95` | 01:00:00:00 | 01:01:50:00 | 6600 | 00:01:50:00 | 60.0 | 1920x1080 | Yes |
| 2 | คุยกับเพื่อนตั้งนาน ลืมเอาเสียงเข้าไลฟ์_Minecraft-vdo | `1890f171-5727-4b23-ab56-35a09b1c83aa` | 01:00:00:00 | 01:01:32:00 | 5520 | 00:01:32:00 | 60.0 | 1920x1080 | Yes |
| 3 | ลืมเสบียง จนต้องกินเนื้อซอมบี้_Minecraft-vdo | `f838a8b1-9c7a-46cc-b0b1-f974b56af4ce` | 01:00:00:00 | 01:01:54:00 | 6840 | 00:01:54:00 | 60.0 | 1920x1080 | Yes |
| 4 | ครีปเปอร์ระเบิดข้างกรง แต่กรงยังรอด_Minecraft-vdo | `c69f0411-082d-4c4f-8e07-884e41837676` | 01:00:00:00 | 01:01:20:00 | 4800 | 00:01:20:00 | 60.0 | 1920x1080 | Yes |
| 5 | เห็นแร่จนสงสัยว่าตัวเองมีเอกซเรย์_Minecraft-vdo | `ad24db80-bcd5-4d6e-98e5-04941ffb5ac1` | 01:00:00:00 | 01:00:44:00 | 2640 | 00:00:44:00 | 60.0 | 1920x1080 | Yes |
| 6 | ออกหาตัวละคร วนกลับมาบ้านตัวเอง_Minecraft-vdo | `2a0ede66-757f-456c-8ca9-312e0dcb8779` | 01:00:00:00 | 01:01:20:00 | 4800 | 00:01:20:00 | 60.0 | 1920x1080 | Yes |
| 7 | ต้องพายเรือ หรือหิ้วเรือขึ้นเขา_Minecraft-vdo | `9cc3753a-2112-44ca-ac15-d5a74e982458` | 01:00:00:00 | 01:02:03:00 | 7380 | 00:02:03:00 | 60.0 | 1920x1080 | Yes |
| 8 | พาชาวบ้านกลับฐาน รอดมาได้ตัวเดียว_Minecraft-vdo | `2a240ed1-fe12-42a6-bb77-d8c3824794c6` | 01:00:00:00 | 01:02:18:00 | 8280 | 00:02:18:00 | 60.0 | 1920x1080 | Yes |
| 9 | ชวนชาวบ้านเพิ่มประชากร ขนมปังหายครึ่งกอง_Minecraft-vdo | `0f9c6773-8a5c-4130-ac6b-ea94d3e151a8` | 01:00:00:00 | 01:02:02:00 | 7320 | 00:02:02:00 | 60.0 | 1920x1080 | Yes |
| 10 | ทำฟาร์มในหิมะ น้ำแข็งจนต้องทำหลังคา_Minecraft-vdo | `e3dd6481-3ecf-4cf1-9968-c9df3e92b427` | 01:00:00:00 | 01:01:22:00 | 4920 | 00:01:22:00 | 60.0 | 1920x1080 | Yes |
| 11 | ชวนเพื่อนไม่ได้ เพราะเผลอแบล็กลิสต์กัน_Soul Walker-vdo | `9b5d48f6-b67b-497a-b150-8c363997a396` | 01:00:00:00 | 01:01:28:00 | 5280 | 00:01:28:00 | 60.0 | 1920x1080 | Yes |
| 12 | เสียงสะท้อนสยองขวัญ_Soul Walker-vdo | `6f32a58d-7b2f-482f-b88a-cc6c82de94e4` | 01:00:00:00 | 01:01:22:00 | 4920 | 00:01:22:00 | 60.0 | 1920x1080 | Yes |
| 13 | กองทัพโอลด์วัน_Terraria-vdo | `22b4148e-4a98-487f-8577-9c1deac5cdb0` | 01:00:00:00 | 01:01:00:00 | 3600 | 00:01:00:00 | 60.0 | 1920x1080 | Yes |
| 14 | แพ้มูนลอร์ด_Terraria-vdo | `f6f0bbec-5284-4369-a9c3-30a7de25bbd8` | 01:00:00:00 | 01:01:30:00 | 5400 | 00:01:30:00 | 60.0 | 1920x1080 | Yes |
| 15 | ปราบมูนลอร์ดได้ครั้งแรก_Terraria-vdo | `88805d14-956c-4779-976a-bc32bf38dced` | 01:00:00:00 | 01:01:35:00 | 5700 | 00:01:35:00 | 60.0 | 1920x1080 | Yes |
| 16 | ปราบมูนลอร์ดได้ครั้งที่สอง_Terraria-vdo | `ffb1e33d-7268-415f-a8a8-66618458ff28` | 01:00:00:00 | 01:01:50:00 | 6600 | 00:01:50:00 | 60.0 | 1920x1080 | Yes |
| 17 | คืนจันทร์ฟักทอง_Terraria-vdo | `fbefcba3-de86-4ba3-9d3f-a21568c99b56` | 01:00:00:00 | 01:01:30:00 | 5400 | 00:01:30:00 | 60.0 | 1920x1080 | Yes |
| 18 | ตัวละครโผล่ตอนสู้บอส_Terraria-vdo | `6f1418ba-61c1-4157-9793-7891ff51e050` | 01:00:00:00 | 01:01:40:00 | 6000 | 00:01:40:00 | 60.0 | 1920x1080 | Yes |
| 19 | สุ่มปี่สก็อตเหล็ก_Monster Hunter World-vdo | `0ce22811-d88c-4613-b62c-3c6924e1f6cf` | 01:00:00:00 | 01:01:57:00 | 7020 | 00:01:57:00 | 60.0 | 1920x1080 | Yes |
| 20 | เกรตจากราส_Monster Hunter World-vdo | `e35ac859-8b4a-478c-b74b-8b6dca82c79c` | 01:00:00:00 | 01:01:25:00 | 5100 | 00:01:25:00 | 60.0 | 1920x1080 | Yes |
| 21 | คูลูยาคู_Monster Hunter World-vdo | `f80c2653-4399-434a-a825-7f3d6e0cc33f` | 01:00:00:00 | 01:01:55:00 | 6900 | 00:01:55:00 | 60.0 | 1920x1080 | Yes |
| 22 | พูเคพูเค_Monster Hunter World-vdo | `9cdee07e-9c72-4181-95b9-dab9a2e16d41` | 01:00:00:00 | 01:01:45:00 | 6300 | 00:01:45:00 | 60.0 | 1920x1080 | Yes |
| 23 | บาร์รอธ_Monster Hunter World-vdo | `f37f103f-a3a9-4cec-9dbf-f8637c375efe` | 01:00:00:00 | 01:02:20:00 | 8400 | 00:02:20:00 | 60.0 | 1920x1080 | Yes |
| 24 | จูราทอดัส_Monster Hunter World-vdo | `a593dd7b-bbb2-4c73-a3a8-22dc815c92d5` | 01:00:00:00 | 01:02:40:00 | 9600 | 00:02:40:00 | 60.0 | 1920x1080 | Yes |
| 25 | บอสมังกร_Soul Walker-vdo | `454c59dd-6b7e-4ee4-96fd-c829f001bde1` | 01:00:00:00 | 01:04:30:00 | 8100 | 00:04:30:00 | **30.0** | 1920x1080 | Yes |
| 26 | หนีฝ่าความหนาว_Minecraft-vdo *(Pilot)* | `7dcaea9a-b19f-4fa4-ac24-9a4f8c12f3ff` | 01:00:00:00 | 01:01:38:00 | 5880 | 00:01:38:00 | 60.0 | 1920x1080 | Yes |
| 27 | ปราบโกเล็มสำเร็จ_Soul Walker-vdo | `d4b0f036-a62f-4afd-ba12-6683acda13fc` | 01:00:00:00 | 01:00:50:00 | 3000 | 00:00:50:00 | 60.0 | 1920x1080 | Yes |
| 28 | นับถอยหลังในห้องโล่_Soul Walker-vdo | `8018e46d-7e6d-496c-9136-965f8d31f66d` | 01:00:00:00 | 01:02:40:00 | 9600 | 00:02:40:00 | 60.0 | 1920x1080 | Yes |
| 29 | เคลียร์เมืองนรก_Soul Walker-vdo | `c76cc38b-a830-46b7-bd12-bb2c256e9c38` | 01:00:00:00 | 01:01:20:00 | 4800 | 00:01:20:00 | 60.0 | 1920x1080 | Yes |
| 30 | โดนบอสจับจนต้องใช้ท่าพิเศษสองครั้ง_Soul Walker-vdo | `98005c12-e4b5-48c7-ae32-f43bdacd3f0a` | 01:00:00:00 | 01:01:20:00 | 4800 | 00:01:20:00 | 60.0 | 1920x1080 | Yes |

---

## 3. Deep Dive: Pilot Timeline `หนีฝ่าความหนาว_Minecraft-vdo`

- **Timeline ID**: `7dcaea9a-b19f-4fa4-ac24-9a4f8c12f3ff`
- **Resolution**: `1920x1080` (16:9 horizontal)
- **Framerate**: `60.0 FPS`
- **Timecode Range**: `01:00:00:00` – `01:01:38:00` (Start Frame: `216000`, End Frame: `221880`, Duration: `5880` frames / 98.0s)

### 3.1 Video Tracks Breakdown

```
[V3] (VTuber Focus)       |--Adj 1--|           |--Adj 2--|      |--Adj 3--|
[V2] (Illustrations/GIF)              |--Dancing Cat.gif--|
[V1] (Gameplay Base)     |===================================================|
```

1. **Track V1: `Gameplay + original framing`** (1 item)
   - **Clip Name**: `【🔴 LIVE】Minecraft - 003  ｜ 21⧸09⧸2569 ｜ #katy404live.mp4`
   - **Span**: Record frames `216000` to `221880` (Duration: `5880` frames).
   - **Source In/Out**: `363300` to `369180` (Left offset: `363300`, Right offset: `69420`).
   - **Source File**: `G:\My Drive\Projects\Katy404\2026-09-29\【🔴 LIVE】Minecraft - 003  ｜ 21⧸09⧸2569 ｜ #katy404live.mp4`
   - **Transforms**: Default (`ZoomX: 1.0, ZoomY: 1.0, Pan: 0.0, Tilt: 0.0, Opacity: 100.0`).
   - **Visual Content**: 16:9 full frame with gameplay occupying the majority of screen, and VTuber avatar seated in the lower/right area.

2. **Track V2: `Illustrations`** (1 item)
   - **Clip Name**: `Cute - Dancing Cat.gif`
   - **Span**: Record frames `218621` to `218741` (Duration: `120` frames / 2.0s).
   - **Source File**: `G:\My Drive\Projects\3.gif\Cute - Dancing Cat.gif` (Resolution: `281x374`, 25 FPS).
   - **Transforms**: Default (`ZoomX: 1.0, ZoomY: 1.0, Pan: 0.0, Tilt: 0.0`).
   - **Timing Context**: Aligns exactly with subtitle cue 10 ("ถึงคืออิสรภาพ", frames `218621`–`218729`) and SFX track A2.

3. **Track V3: `VTuber Focus (Adjustment)`** (3 items)
   - All 3 items are native DaVinci Resolve **Adjustment Clips** (no media pool item).
   - Each adjustment clip has an active **Fusion Composition** containing:
     `MediaIn1 -> Transform1 -> MediaOut1`
   - **Transform1 Tool Settings**:
     - `Center`: `{X: 0.38, Y: 0.81}`
     - `Size`: `1.30` (130% zoom)
     - `Angle`: `0.0`, `FlipHoriz: 0`, `FlipVert: 0`
   - **Exact Cue & Frame Alignment**:
     - **Item 1**: Record frames `219265` – `219369` (Duration: `104` frames / 1.73s).
       *Directly matches Subtitle Cue 16*: `"เน้นอยู่ห้าร้อยห้าสิบ"` (frames `219265`–`219369`).
     - **Item 2**: Record frames `220076` – `220184` (Duration: `108` frames / 1.80s).
       *Directly matches Subtitle Cue 24*: `"ผมเอาไว้กล่องที่"` (frames `220076`–`220184`).
     - **Item 3**: Record frames `220690` – `220754` (Duration: `64` frames / 1.07s).
       *Directly matches Subtitle Cue 32*: `"ไว้นี้แล้วกันเอาไว้"` (frames `220690`–`220754`).

### 3.2 Native Subtitle Track Breakdown

- **Track Name**: `TH` (Index 1)
- **Total Cues**: **45 cues**
- **Format**: Native DaVinci Resolve Subtitle Track cues.
- **House Style Analysis & Flagged Legacy Exceptions**:
  Per `.agents/skills/house-style/SKILL.md`, short-form Thai captions standard:
  - Max hold: `1.5s` (90 frames at 60fps)
  - Max text: ~3 short words / ~14 Thai characters, no inter-word spaces.
  - *Audit Result*: 35 cues comply strictly. Exactly **10 legacy cues exceed 1.5s or 20 characters**:
    1. Cue 9: `"ถึงแล้วใช่ไหม"` (1.80s / 108 frames, 13 chars)
    2. Cue 10: `"ถึงคืออิสรภาพ"` (1.80s / 108 frames, 13 chars)
    3. Cue 12: `"ถึงเฮ้ออิสรภาพ"` (1.80s / 108 frames, 14 chars)
    4. Cue 14: `"คิมวายุคิโซะกล่าวว่า"` (1.80s / 108 frames, 20 chars)
    5. Cue 16: `"เน้นอยู่ห้าร้อยห้าสิบ"` (1.73s / 104 frames, 21 chars)
    6. Cue 23: `"ผมเอาเอาไว้ที่"` (1.52s / 91 frames, 14 chars)
    7. Cue 26: `"ส่งแล้วครับ"` (1.65s / 99 frames, 11 chars)
    8. Cue 27: `"ผมเอาไว้กล่องที่"` (1.80s / 108 frames, 16 chars)
    9. Cue 28: `"มันใกล้กับโต๊ะ"` (1.80s / 108 frames, 14 chars)
    10. Cue 40: `"แล้วก็เดี๋ยว"` (1.80s / 108 frames, 12 chars)
  *Parent Directive*: Under requirement R3, these cues must be preserved 1:1 without altering words or duration.

### 3.3 Audio Tracks Breakdown

1. **Track A1: `Original stream audio`**
   - **Subtype**: `stereo`
   - **Clips**: 1 item (`【🔴 LIVE】Minecraft - 003...mp4`), frames `216000` to `221880`.
   - **Clip Volume**: `0.0 dB`
   - **Fades**: In `0.0`, Out `0.0`
2. **Track A2: `SFX`**
   - **Subtype**: `stereo`
   - **Clips**: 1 item (`3. WINK _DING_.mp3`), frames `218621` to `218707` (Duration: `86` frames).
   - **Source File**: `G:\My Drive\Projects\2.1_sfx\3. WINK _DING_.mp3`
   - **Clip Volume**: `0.0 dB`
   - **Fades**: In `0.0`, Out `0.0`
3. **Track A3: `BGM`**
   - **Subtype**: `stereo`
   - **Clips**: 1 item (`NCSน่ารัก.mp3`), frames `216000` to `221880` (Duration: `5880` frames).
   - **Source File**: `G:\My Drive\Projects\1.bgm\NCSน่ารัก.mp3`
   - **Clip Volume**: `0.0 dB`
   - **Fades**: In `0.0`, Out `0.0`

---

## 4. Cross-Timeline Structural Comparison

Comparing across all 30 timelines revealed clear patterns and two distinct subgroup conventions:

| Architectural Component | Timelines 1 – 25 | Timelines 26 – 30 (incl. Pilot) |
|:---|:---|:---|
| **Video Track Count** | 3 (`V1`, `V2`, `V3`) | 3 (`V1`, `V2`, `V3`) |
| **V1 Item Count** | 1 (Stream Gameplay) | 1 (Stream Gameplay) |
| **V2 Items** | 1 to 2 Reaction GIFs (`ZoomX/Y: 0.55`) | 1 GIF (`ZoomX/Y: 1.0`) |
| **V3 Items** | Exactly 3 `Adjustment Clip`s | Exactly 3 `Adjustment Clip`s |
| **V3 Fusion Transform** | `Size=1.3, Center=(0.38, 0.81)` | `Size=1.3, Center=(0.38, 0.81)` |
| **Audio Track Count** | 3 (`A1`, `A2`, `A3`) | 3 (`A1`, `A2`, `A3`) |
| **A1 Type & Level** | Stereo, `0.0 dB` | Stereo, `0.0 dB` |
| **A2 (SFX) Type & Level** | **Mono**, **`-11.0 dB`** (1–3 cues) | **Stereo**, **`0.0 dB`** (1 cue) |
| **A3 (BGM) Type & Level** | **Mono**, **`-23.0 dB`** | **Stereo**, **`0.0 dB`** |
| **A3 BGM Fades** | **FadeIn: 30f, FadeOut: 60f** | **FadeIn: 0f, FadeOut: 0f** |
| **Subtitle Track** | 1 Native Subtitle Track (29–127 cues) | 1 Native Subtitle Track (32–108 cues) |

### Special Invariant: Timeline 25 Framerate
- **Timeline 25 (`บอสมังกร_Soul Walker-vdo`)** is the only timeline authored at **30.0 FPS** (Start frame: `108000`, End frame: `116100`, Duration: `8100` frames = 4m 30s).
- All duplicate creation operations for Timeline 25 must enforce `timelineFrameRate = 30.0` rather than the project default of `60.0`.

---

## 5. Media Pool Bins & Media Status Audit

### 5.1 Media Pool Bin Hierarchy

```
Master (8 items)
├── Archive (40 items: 39 Video, 1 Subtitle)
├── Enrichment_BGM (9 audio files)
├── Enrichment_SFX (9 audio files)
├── Enrichment_GIF (11 video/GIF files)
└── Shorts_2026-09-29
    ├── Gameplay (1 item)
    ├── Fun (61 items: 30 Source Timelines + 31 caption-overlay MOVs)
    └── Meme (0 items)
```

- **All 30 Source Timelines reside in**: `Master/Shorts_2026-09-29/Fun`.

### 5.2 Offline Media Verification: Zero Offline Media

A full scan of the Media Pool and every clip across all 30 timelines was performed:
- **Total Media Pool clips**: 139 items.
- **Clips with missing files**: **0**.
- **Offline items on timelines**: **0**.
- **File System Verification**: 100% of underlying files exist under `G:\My Drive\Projects\...`.

### 5.3 Shared Asset Inventory Across Timelines

1. **Source Stream Footage (7 long-form recordings)**:
   - `【🔴 LIVE】Minecraft - 002...mp4` (2h 31m)
   - `【🔴 LIVE】Minecraft - 003...mp4` (2h 01m)
   - `【🔴 COLAB】Terraria Skyblock กับเพือน...mp4` (2h 22m)
   - `【🔴 LIVE】Monster Hunter： World - 001...mp4` (2h 27m)
   - `【🔴 LIVE】Soul Walker - 003...mp4` (2h 37m)
   - `【🔴 LIVE】Soul Walker - 004...mp4` (3h 00m)
   - `【🔴 LIVE】Soul Walker - 005...mp4` (1h 55m)
2. **Reaction GIFs (5 distinct assets in `Enrichment_GIF`)**:
   - `Anime - Shocked Reaction.gif`
   - `Cute - Dancing Cat.gif`
   - `Cute - Happy Dancing Cat.gif`
   - `Reaction - Iconic Laugh.gif`
   - `Reaction - What Confused Minion.gif`
3. **SFX (4 distinct assets in `Enrichment_SFX`)**:
   - `(mafioso) scream.mp3`
   - `1_ตลกตบมุก_1.mp3`
   - `3. WINK _DING_.mp3`
   - `_Click_ Nice.mp3`
4. **BGM (6 distinct assets in `Enrichment_BGM`)**:
   - `Gaming Music 2023 ♫ 1 Hour Gaming Music Mix...mp3`
   - `NCSน่ารัก.mp3`
   - `Top 50 NoCopyrightSounds Songs 2025...mp3`
   - `YEAT - DISRESPECTFUL (PROD. SKY x KEENEX)...mp3`
   - `ncs_mix_2025_resolve.wav`
   - `payday.mp3`

---

## 6. Recommendations for Downstream 9:16 Conversion

1. **Non-Destructive Duplication**:
   - Duplicate each timeline into `<OriginalName>_9x16`.
   - Set resolution to `1080` x `1920`. Ensure `useCustomSettings = 1`.
   - Match the source timeline's frame rate explicitly (60 FPS for 29 timelines; 30 FPS for Timeline 25).
2. **Visual Layout Reframing**:
   - **Split Screen**: V1 Gameplay placed at top half; VTuber crop positioned at bottom half.
   - **VTuber Focus (V3)**: When V3 Adjustment Clips fire, expand VTuber to full-screen 9:16 close-up. Note that original V3 clips used Fusion comp with `Center=(0.38, 0.81)` and `Size=1.3` in 16:9 space.
   - **Reaction GIFs (V2)**: Maintain original start/end frames; reposition within 9:16 safe title boundaries so they do not obstruct avatar face or subtitle areas.
3. **Subtitles & Audio**:
   - Lock Subtitle track and do not mutate any of the text or timing.
   - Retain audio tracks A1, A2, A3 with exact track subtypes and volume levels matching their source timeline.
