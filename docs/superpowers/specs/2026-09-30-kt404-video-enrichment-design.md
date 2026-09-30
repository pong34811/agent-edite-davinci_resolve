# Design Specification: KT404_2026-09-29 Video Enrichment

**Date:** 2026-09-30  
**Project:** KT404_2026-09-29  
**Platform:** DaVinci Resolve Studio 21.1.0.17 on Windows  
**Scope:** Enrich all 30 timelines with SFX, BGM, and GIF/Meme overlays.

---

## 1. Context & Objectives

The project `KT404_2026-09-29` contains 30 pre-cut gameplay highlight timelines from VTuber Katy404 across 4 games (Minecraft, Terraria, Monster Hunter World, and Soul Walker). Each timeline currently features:
- **Video 1 (V1):** Source gameplay footage + Katy404 VTuber camera (bottom-right).
- **Audio 1 (A1):** Original game audio and dialogue.
- **Subtitle 1 (Sub 1):** Thai subtitles for spoken dialogue.

The goal is to enhance entertainment value and viewer engagement across all 30 timelines by adding:
1. **Sound Effects (SFX)** from `G:\My Drive\Projects\2.1_sfx`
2. **Background Music (BGM)** from `G:\My Drive\Projects\1.bgm`
3. **Illustrations & Reaction GIFs** from `G:\My Drive\Projects\3.gif`

---

## 2. Global Constraints & Core Rules

1. **Aspect Ratio & Resolution:** 1920×1080 (16:9 widescreen, 60 fps). Do NOT convert to 9:16 or alter native raster.
2. **Original Media Safety:** Never alter or overwrite original game footage or audio.
3. **Pre-flight Backup:** Export a verified `.drp` archive before making any modifications.
4. **VTuber & Caption Clearance:**
   - Katy404 avatar is at bottom-right.
   - Subtitle cues are at bottom-center.
   - All GIF overlays must be centered in the frame with scale ~0.50–0.65 to ensure zero obstruction of avatar and subtitles.
5. **Pilot Approval Gate:** Timeline 1 (`ขุดมั่วเจอเหล็กกองใหญ่_Minecraft-vdo`) must be completely enriched and verified first as a pilot. Batch operations on Timelines 2–30 only proceed after pilot review.

---

## 3. Architecture & Track Layout

Each timeline will maintain a standardized track hierarchy:

| Track | Type | Name | Content / Purpose |
|---|---|---|---|
| **V1** | Video | `Main Video` | Original gameplay + VTuber overlay (untouched) |
| **V2** | Video | `GIF Overlays` | Reaction GIFs / Meme pop-ups (centered) |
| **A1** | Audio | `Original Audio` | Original dialogue and game sound (untouched) |
| **A2** | Audio | `SFX` | Sound effects for comedic punchlines & reactions (-10 dB to -12 dB) |
| **A3** | Audio | `BGM` | Background music bed (-22 dB to -24 dB, 0.5s fade-in, 1.0s fade-out) |
| **Sub 1** | Subtitle | `Subtitles` | Existing Thai subtitle cues (untouched) |

---

## 4. Audio Engineering & Cue Detection

### 4.1 Subtitle-Driven Cue Detection
Subtitles on `Sub 1` provide precise timestamps for comedic beats, shocks, and reactions:
- **Comedic / Punchline / Blunder:** Keywords like "555", "ฮ่าๆ", "อ้าว", "เอ้า", "แป๊บ", "ไม่ได้"
  - *SFX:* `1_ตลกตบมุก_1.mp3`, `2.ตบมุก.mp3`, `3.ตบมุก.mp3`
- **Shock / Panic / Sudden Boss Event:** Keywords like "เห้ย", "ว๊าก", "ไม่นะ", "ตาย", "ระเบิด"
  - *SFX:* `(mafioso) scream.mp3`, `3.ฟ้าผ่า.mp3`, `_RUN_ vine effect sound.mp3`
- **Cute / Win / Aha Moment:** Keywords like "อ๋อ", "เยี่ยม", "สวย", "รอดแล้ว"
  - *SFX:* `3. WINK _DING_.mp3`, `_Click_ Nice.mp3`, `_Wow!_ (anime voice accent).mp3`

### 4.2 BGM Mood Mapping by Game
- **Minecraft (Timelines 1–10, 26):** Cute / relaxing / cheerful.
  - *Tracks:* `NCSน่ารัก.mp3`, `FREE BGM 4 LOOP.wav`, `2025-02-04_-_Wishing_Well_-_www.FesliyanStudios.com_.mp3`
- **Terraria (Timelines 13–18):** Boss encounters, Pumpkin Moon, Moon Lord. Energetic / EDM.
  - *Tracks:* `Top 50 NoCopyrightSounds Songs 2025...mp3`, `Gaming Music 2023...mp3`, `ncs_mix_2025_resolve.wav`
- **Monster Hunter World (Timelines 19–24):** Upbeat hunting action.
  - *Tracks:* `payday.mp3`, `ncs_mix_2025_resolve.wav`, `Gaming Music 2023...mp3`
- **Soul Walker (Timelines 11–12, 25, 27–30):** Fast-paced anime action & bosses.
  - *Tracks:* `YEAT - DISRESPECTFUL...`, `Gaming Music 2023...mp3`, `aphextwin.m4a`

### 4.3 Levels & Dynamics
- **A1:** 0 dB (Dialogue clarity is top priority).
- **A2 (SFX):** -10 dB to -12 dB.
- **A3 (BGM):** -22 dB to -24 dB with smooth 0.5s fade-in at head and 1.0s fade-out at tail.

---

## 5. Visual Enrichment (GIF / Meme Overlays)

### 5.1 Placement & Scaling
- **Position:** Screen Center (`Pan=0, Tilt=0`).
- **Scale:** Zoom `0.50` to `0.65` (maintains clear visibility without covering background gameplay or overlapping VTuber model at bottom-right or subtitles at bottom-center).
- **Duration:** 1.5 to 2.5 seconds per pop-up.
- **Frequency:** 1 to 3 pop-ups per timeline, timed to the strongest emotional or punchline beat.

### 5.2 Reaction Matching
- **Surprise / Shock / Confusion:** `Anime - Shocked Reaction.gif`, `Reaction - What Confused Minion.gif`, `Reaction - OMG No Funny.gif`
- **Laughter / Teasing:** `Reaction - Iconic Laugh.gif`, `Reaction - Laughing Pointing.gif`, `Reaction - Well Done Laughing.gif`
- **Cute / Celebration:** `Cute - Dancing Cat.gif`, `Cute - Happy Dancing Cat.gif`, `Anime - Thumbs Up.gif`
- **Frustration / Anger:** `Anime - Angry Chibi.gif`, `Thai Meme - Clenched Fist Angry Cute.gif`

---

## 6. Execution Workflow & Verification Plan

1. **Safety Backup:** Export `.drp` before touching Resolve project.
2. **Media Pool Organization:** Create bins `Enrichment_SFX`, `Enrichment_BGM`, `Enrichment_GIF` and import required assets.
3. **Pilot Timeline 1 Execution:**
   - Add tracks V2, A2, A3.
   - Insert BGM, set volume and fades.
   - Place 2-3 SFX and 1-2 centered GIFs on cue.
   - Read back timeline structure and verify track counts, item counts, and audio levels.
   - User review & approval of pilot.
4. **Batch Execution (Timelines 2–30):**
   - Iterate through each timeline.
   - Apply BGM matching game theme.
   - Detect subtitle cue peaks; insert corresponding SFX and centered GIFs.
   - Save project after each batch.
5. **Final Audit & QC:**
   - Verify all 30 timelines have expected tracks and media coverage.
   - Save final project via `ProjectManager.SaveProject()`.
