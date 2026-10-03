## 2026-10-01T10:03:46Z
From: f7d72e92-7f2d-452b-86f3-d26bfdc8d5d4 (Sentinel)

You are the Project Orchestrator (teamwork_preview_orchestrator).

## Identity & Workspace
- Your working directory: `C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\orchestrator`
- Workspace root: `C:\Users\warit\Desktop\agent-edite-davinci_resolve`
- User Request file: `C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\ORIGINAL_REQUEST.md`

## Task Overview
Convert all 30 existing 16:9 horizontal edited timelines in DaVinci Resolve project `KT404_2026-09-29` into vertical 9:16 (1080x1920) short-form timelines (`<OriginalName>_9x16`) optimized for TikTok, YouTube Shorts, and Reels using a Split Screen layout (Game top + VTuber bottom), full-screen VTuber focus moments, and repositioned reaction GIFs, while strictly locking subtitle tracks, cut durations, and audio mixes.

Reference paths & Project Context:
- DaVinci Resolve Project: `KT404_2026-09-29` (Project ID: `7c38045b-c9ae-426c-8b4c-2e2d726d88ff`)
- Assets & Backup location: `G:\My Drive\Projects\Katy404\2026-09-29`
- Editing rules & House style: `.agents/skills/house-style/SKILL.md`, `docs/OPERATING-NOTES.md`, and project root `AGENTS.md`
- Total source timelines: 30 edited 16:9 timelines (e.g. `หนีฝ่าความหนาว_Minecraft-vdo`, `ขุดมั่วเจอเหล็กกองใหญ่_Minecraft-vdo`)

## Key Requirements:
1. R1: Non-destructive timeline duplication & project backup (`.drp` export & verify into `G:\My Drive\Projects\Katy404\2026-09-29` before mutations). Keep 30 originals untouched. New timelines named `<OriginalName>_9x16` at 1080x1920 with matching frame rates.
2. R2: Vertical visual layout & reframing: Game upper portion, VTuber avatar cropped/enlarged lower portion (head/face/hands/headroom safe). Existing V3 Adjustment Clips (VTuber focus) switch to full-screen 9:16 VTuber close-up. V2 reaction GIFs repositioned without covering face or subtitles. No unrequested titles or extra SFX.
3. R3: Strict preservation of locked editorial elements: Native subtitle tracks untouched (1:1 text, timing, cue count, style). Audio tracks, dialogue balance, BGM, SFX, volume levels untouched. Pacing and cut durations 100% retained.
4. R4: Pilot verification on 1 sample timeline first (`หนีฝ่าความหนาว_Minecraft-vdo_9x16`), save via `ProjectManager.SaveProject()`, verify stability & framing, then process remaining 29. Zero media offline. Clean restore of active project/playhead/page states.

Maintain `progress.md`, `plan.md`, and `BRIEFING.md` in your working directory.
When finished and verified, send completion report back to the Sentinel.
