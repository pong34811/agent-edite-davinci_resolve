# Original User Request

## 2026-10-01T10:03:04Z

Convert all 30 existing 16:9 horizontal edited timelines in DaVinci Resolve project `KT404_2026-09-29` into vertical 9:16 (1080x1920) short-form timelines (`<OriginalName>_9x16`) optimized for TikTok, YouTube Shorts, and Reels using a Split Screen layout (Game top + VTuber bottom), full-screen VTuber focus moments, and repositioned reaction GIFs, while strictly locking subtitle tracks, cut durations, and audio mixes.

Working directory: `C:\Users\warit\Desktop\agent-edite-davinci_resolve`
Integrity mode: development

Reference paths & Project Context:
- DaVinci Resolve Project: `KT404_2026-09-29` (Project ID: `7c38045b-c9ae-426c-8b4c-2e2d726d88ff`)
- Assets & Backup location: `G:\My Drive\Projects\Katy404\2026-09-29`
- Editing rules & House style: `.agents/skills/house-style/SKILL.md`, `docs/OPERATING-NOTES.md`
- Total source timelines: 30 edited 16:9 timelines (e.g. `หนีฝ่าความหนาว_Minecraft-vdo`, `ขุดมั่วเจอเหล็กกองใหญ่_Minecraft-vdo`)

## Requirements

### R1. Non-Destructive Timeline Duplication & Project Backup
- Export and verify a full `.drp` project backup into `G:\My Drive\Projects\Katy404\2026-09-29` before performing any timeline mutations.
- Keep all 30 original 16:9 horizontal timelines completely untouched.
- Create new 9:16 vertical timelines named `<OriginalName>_9x16` configured at 1080x1920 with matching frame rates.

### R2. Vertical Visual Layout & Reframing
- Apply Split Screen layout to each 9:16 timeline:
  - Game action positioned in the upper portion of the frame.
  - VTuber avatar cropped and enlarged in the lower portion, keeping head, face, hands, and headroom safely framed.
- For intervals corresponding to existing V3 Adjustment Clips (VTuber Focus), switch composition to a full-screen 9:16 VTuber close-up for the duration of that cue.
- Reposition V2 reaction GIFs to safe vertical screen positions without covering the avatar's face or the subtitle area, keeping their original timing and durations.
- Do not add new header bars, unrequested title cards, or extra SFX.

### R3. Strict Preservation of Locked Editorial Elements
- Subtitle track: Keep the native Subtitle track untouched — exact text, timing, cue count, and styling must be preserved 1:1.
- Audio: Preserve all audio tracks, dialogue balance, BGM, SFX, and volume levels without alteration.
- Cuts & Pacing: Retain 100% of existing cuts and clip durations without shortening or retiming.

### R4. Pilot Verification & Staged Execution
- Execute end-to-end on 1 sample timeline first (e.g. `หนีฝ่าความหนาว_Minecraft-vdo_9x16`).
- Save project via `ProjectManager.SaveProject()` and verify timeline integrity, visual framing, caption placement, and Resolve stability before processing the remaining 29 timelines.
- Deliverables are strictly the verified timelines in DaVinci Resolve (no video file export required).

## Acceptance Criteria

### Project Safety & Non-Destructive Invariants
- [ ] Fresh `.drp` backup file exists and passes integrity check in `G:\My Drive\Projects\Katy404\2026-09-29` prior to editing.
- [ ] All 30 original 16:9 timelines remain bit-for-bit / property-for-property identical to their preflight baseline.

### Vertical Timeline Specifications & Integrity
- [ ] 30 new vertical timelines exist, each following the naming convention `<OriginalName>_9x16`.
- [ ] Each vertical timeline is configured to 1080x1920 (9:16) with timeline frame rate matching its source 16:9 timeline.
- [ ] Zero "Media Offline" items across all tracks.

### Visual Composition & Framing
- [ ] Gameplay video occupies upper canvas; VTuber avatar occupies lower canvas with visible face and headroom.
- [ ] V3 Adjustment Clip intervals display full-screen 9:16 VTuber close-up.
- [ ] V2 reaction GIFs are positioned cleanly within 9:16 safe areas without obscuring face or subtitles.

### Editorial & Subtitle Preservation
- [ ] Subtitle track cue counts, text strings, and start/end timecodes in each `_9x16` timeline match the original 16:9 timeline exactly.
- [ ] Audio tracks, waveforms, and volume levels in each `_9x16` timeline match the original 16:9 timeline exactly.
- [ ] Total timeline duration in frames in each `_9x16` timeline equals the original 16:9 timeline.

### Save & Cleanup
- [ ] `ProjectManager.SaveProject()` confirmed.
- [ ] Active project, playhead position, and page states are cleanly restored.


## 2026-10-02T02:21:27Z

# Teamwork Project Prompt — Draft

> Status: Launched
> Goal: Craft prompt → get user approval → delegate to teamwork_preview
> Requested team: [none — teamwork routes from the description]

Analyze all video footage in `C:\Users\warit\SynologyDrive\Tygarina\2026-09-30` to identify highlight moments (gaming, fun, and memes) between 30 seconds and 3 minutes in length, and automatically construct individual short-clip timelines for each selected moment in the currently active DaVinci Resolve project.

Working directory: C:\Users\warit\SynologyDrive\Tygarina\2026-09-30
Integrity mode: benchmark

## Requirements

### R1. Footage Analysis
Analyze the provided video files to find interesting segments suitable for short clips. Target specific moments: gaming action, fun/amusing interactions, and meme-worthy events. 

### R2. Timeline Creation
For each identified clip, construct a new separate timeline containing the selected segment in the active DaVinci Resolve project using the Resolve MCP server.

### R3. Safe Handling
Do not modify, transcode, or delete the original source video files. All timeline manipulation must happen non-destructively through the DaVinci Resolve API.

## Acceptance Criteria

### Analysis Quality
- [ ] Analysis produces a verifiable list of clip candidates categorized by type (gaming, fun, meme).
- [ ] Every selected clip duration is strictly between 30 seconds and 3 minutes.
- [ ] An objective log or report shows the rationale (e.g. transcript snippet, audio spike) for each chosen segment.

### Resolve Integration
- [ ] A programmatic check of the Resolve project via MCP confirms that the new timelines exist.
- [ ] The programmatic check confirms that the timelines contain the correct source footage and match the exact expected durations.


## 2026-10-02T03:01:39Z

# Teamwork Project Prompt — Draft

> Status: Launched
> Goal: Craft prompt → get user approval → delegate to teamwork_preview
> Requested team: [none — teamwork routes from the description]

Conduct a deeper analysis of the video footage in `C:\Users\warit\SynologyDrive\Tygarina\2026-09-30` to find additional interesting short clips (30s - 3m). Extract exactly 3 highlight moments per video file (footage). Construct new timelines for these clips in DaVinci Resolve, naming them strictly using the format `{ชื่อคลิปภาษาไทย}_{ชื่อเกม}-vdo`.

Working directory: C:\Users\warit\SynologyDrive\Tygarina\2026-09-30
Integrity mode: benchmark

## Requirements

### R1. Deep Footage Analysis
Analyze the source footage to extract exactly 3 new interesting short clips from each video file. Exclude the 7 clips already extracted in the previous run to avoid duplicates.

### R2. Strict Naming Convention
Name each created timeline using the exact format: `{Thai_Clip_Name}_{Game_Name}-vdo`.
Example: `จังหวะตกใจสุดขีด_REPO-vdo`. The `{Thai_Clip_Name}` part must be in Thai only.

### R3. Timeline Creation
Construct these new timelines in the active DaVinci Resolve project using the Resolve MCP.

## Acceptance Criteria

### Naming & Quantity
- [ ] Exactly 3 new timelines are created for each processed source video file.
- [ ] Every timeline name strictly follows the `{ชื่อคลิปภาษาไทย}_{ชื่อเกม}-vdo` format.
- [ ] The `{ชื่อคลิปภาษาไทย}` portion contains no English characters.

### Resolve Integration
- [ ] A programmatic check verifies the existence and exact naming of the new timelines in the active Resolve project.


## 2026-10-02T04:11:27Z

# Teamwork Project Prompt — Draft

> Status: Launched
> Goal: Craft prompt → get user approval → delegate to teamwork_preview
> Requested team: [none — teamwork routes from the description]

Analyze the full library of 32 footage files in `C:\Users\warit\SynologyDrive\Tygarina\2026-09-30` (with emphasis on expanding coverage to the 25 previously untouched files as well as finding peak moments across all files) to discover and construct exactly 60 new highlight clip timelines in the active DaVinci Resolve project. Naming must strictly follow `{ชื่อคลิปภาษาไทย}_{ชื่อเกม}-vdo`.

Working directory: C:\Users\warit\SynologyDrive\Tygarina\2026-09-30
Integrity mode: benchmark

## Requirements

### R1. Target Quantity & Broad Coverage
Extract exactly 60 new highlight clip segments (durations strictly between 30s and 3m) across the 32 source video files, prioritizing files that have not yet had clips extracted, while also capturing peak highlights across all footage.

### R2. Non-Overlap & Exclusion
Do not overlap with any of the 28 existing timelines currently in the project. Each new highlight must be a distinct, unique segment.

### R3. Strict Thai Naming Convention
Every created timeline must strictly adhere to the naming format: `{ชื่อคลิปภาษาไทย}_{ชื่อเกม}-vdo`.
The `{ชื่อคลิปภาษาไทย}` portion must contain 100% Thai Unicode characters (zero English/Latin letters).

### R4. Resolve Timeline Construction & Non-Destructive Invariant
Construct all 60 new timelines directly in active project `tygarina_2026-09-30` via Resolve MCP. Source media files must remain 100% read-only and unmodified.

## Acceptance Criteria

### Highlight Extraction & Naming
- [ ] Exactly 60 new timelines are created in DaVinci Resolve.
- [ ] Every timeline duration is strictly within 30 seconds to 3 minutes (e.g. 50s-70s).
- [ ] 100% of the new timeline names match the regex pattern for `{ชื่อคลิปภาษาไทย}_{ชื่อเกม}-vdo` with 0 Latin characters in the Thai title part.
- [ ] 0.00s overlap with any of the 28 pre-existing highlight timelines.

### Project Verification
- [ ] A programmatic check verifies that 60 new timelines exist in the project (bringing the total project timeline count to 88).
- [ ] 0 offline media items across all created timelines.
- [ ] Project is cleanly saved using `ProjectManager.SaveProject()`.
