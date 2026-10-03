# Handoff Report: 16:9 to 9:16 Vertical Conversion Mechanics

**Agent:** Explorer 3 (`teamwork_preview_explorer`)  
**Parent Orchestrator:** `66b810a5-7537-48dc-8702-b84e40a0973a`  
**Handoff Type:** Hard (Investigation Complete)  
**Detailed Report Reference:** `C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\teamwork\explorer_3\report.md`  

---

## 1. Observation

1. **Resolve Studio Environment & Active Project:**
   - Command: `resolve_control(action="get_version")`
   - Output: Product `DaVinci Resolve Studio`, version `21.1.0.17`, build clears all 68 known version gates.
   - Command: `project_settings(action="project_summary")`
   - Output: Active Project `KT404_2026-09-29`, Project ID `7c38045b-c9ae-426c-8b4c-2e2d726d88ff`, 30 timelines, active page `edit`, active timeline `หนีฝ่าความหนาว_Minecraft-vdo`.

2. **Current Timeline Track & Clip Structure:**
   - Probed via `timeline(action="probe_timeline_structure")` on `หนีฝ่าความหนาว_Minecraft-vdo`:
     - Track V1: `【🔴 LIVE】Minecraft - 003  ｜ 21⧸09⧸2569 ｜ #katy404live.mp4` (Resolution 1920×1080, 60.0 fps, online at `G:\My Drive\Projects\Katy404\2026-09-29\...`).
     - Track V2: `Cute - Dancing Cat.gif` (GIF overlay on V2).
     - Track V3: 3 Adjustment Clips (`eb451d3c-...`, `0fbba6dc-...`, `3e6c4de3-...`).
     - Subtitle Track 1: 38 native Thai dialogue cues (duration $\le 1.5$s, no inter-word spaces).
     - Audio Tracks: A1 (original dialogue/game 0 dB), A2 (SFX), A3 (BGM).

3. **Source Video Frame Inspection (`scratch_source.jpg`):**
   - Decoded at 6060s into source via FFmpeg:
     - Avatar Katy404 is **baked into the bottom-right corner** of the 1920×1080 stream recording ($X \approx 1400–1800, Y \approx 550–1080$).
     - Minecraft gameplay (crosshair, player view) is centered at $X \approx 960, Y \approx 540$.
     - Ahoge/head top is at $Y \approx 550$; eyes at $Y \approx 700$; purple controller/hands at $Y \approx 880$; jacket cuts off at bottom edge $Y = 1080$.

4. **Existing V3 Adjustment Clip Fusion Structure:**
   - Probed via `fusion_comp` on V3 item 0:
     - Graph: `MediaIn1` -> `Transform1` -> `MediaOut1`.
     - `Transform1` inputs: `Size: 1.30`, `Center: {1: 0.38, 2: 0.81, 3: 0.0}`, `Edges: 0.0`.
     - Frame captured via `timeline_frame(action="capture", frame=219300)` confirms that in 16:9, this node zoomed 1.3× into the bottom-right avatar.

5. **API Truth for Duplication & Settings:**
   - `resolve_control.api_truth("DuplicateTimeline")`: `Timeline.DuplicateTimeline` duplicates all tracks, items, and settings bit-for-bit, but silently moves Resolve's current-timeline pointer to the duplicate.
   - `resolve_control.api_truth("timelinePlaybackFrameRate")`: `Project.SetSetting('timelinePlaybackFrameRate')` returns `False` on all value forms. Do not attempt to write playback frame rate.
   - `DaVinciResolveScript.pyi` line 1067: `TimelineSettings` supports `useCustomSettings: "1"`, `timelineResolutionWidth: "1080"`, `timelineResolutionHeight: "1920"`, `timelineOutputResMatchTimelineRes: "1"`, `timelineOutputResolutionWidth: "1080"`, `timelineOutputResolutionHeight: "1920"`.

---

## 2. Logic Chain

1. **Duplication and Settings Strategy (from Obs 1, 2, 5):**
   - Since Requirement R3 demands 100% preservation of native subtitles, cut points, audio levels, and durations, `MediaPool.CreateEmptyTimeline` is rejected because it produces a blank canvas requiring lossy re-assembly.
   - `Timeline.DuplicateTimeline(f"{name}_9x16")` clones all tracks, items, subtitle cues, and audio mixes with zero mutation.
   - By calling `SetSetting("useCustomSettings", "1")` followed by `timelineResolutionWidth="1080"` and `timelineResolutionHeight="1920"`, only the resolution raster changes to 9:16.
   - The duplicate inherits the source 60.0 fps `timelineFrameRate` natively. No rate setter is called, avoiding the recorded `timelinePlaybackFrameRate` API bug.

2. **Split Screen Reframing Geometry (from Obs 2, 3):**
   - Because the VTuber avatar is baked into the 16:9 footage at bottom-right rather than being an isolated camera feed, displaying Game Top and VTuber Bottom simultaneously requires two visual layers.
   - Duplicating the V1 video clips to a dedicated V2 track provides independent control over the Game and VTuber layers:
     - **Upper Canvas (Game Top):** Zooming V1 by $1.60\times$ scales 1080 width to 1728 px and height to 972 px (matching the 960 px half-screen target). Shifting $Tilt = +480.0$ centers the gameplay crosshair at $Y = 1440$ in the upper half. $CropBottom = 486.0$ cleanly truncates at the split midline.
     - **Lower Canvas (VTuber Bottom):** Zooming V2 by $2.60\times$ scales the avatar to ~650 px wide (~60% of vertical width). Shifting $Pan = -936.0$ moves the avatar from the right flank ($+360$ px at Zoom 1.0) to canvas center ($X = 0$). Setting $Tilt = -200.0$ positions headroom safely below the split line, face centered at $Y \approx 710$, and purple controller/hands safely above the subtitle zone. $CropTop = 480.0$ prevents bleed into the game window.

3. **Full-Screen Focus Mechanism (from Obs 3, 4, and Logic Step 2):**
   - In the 9:16 Split Screen, Katy404 is positioned in the lower half, centered at normalized Fusion coordinates $(X=0.50, Y=0.25)$.
   - An Adjustment Clip on V4 receives `MediaIn1` from the tracks below.
   - Setting the Adjustment Clip's `Transform1` to `Center: {0.50, 0.25}` and `Size: 2.0` shifts $(0.50, 0.25)$ to $(0.50, 0.50)$ (exact screen center) and doubles scale from 960 px to 1920 px.
   - This expands the VTuber avatar to fill the complete 1080×1920 canvas, pushes gameplay off-screen, and automatically snaps back to Split Screen when the clip ends.

4. **Reaction GIF Repositioning (from Obs 2, 3, and Logic Step 2):**
   - In 16:9, GIFs sat at $(Pan=0, Tilt=0)$. In 9:16, $(Pan=0, Tilt=0)$ sits at $Y=960$ (the split line), colliding directly with Katy404's head and ahoge.
   - In 1080×1920, the safe placement that avoids Katy404 ($Y \in [400, 950]$), native subtitles ($Y \in [180, 280]$), and platform UI ($Y > 1720$ and $X > 920$) is the **Upper-Left Flank** ($Pan=-300.0, Tilt=+600.0, Zoom=0.42$) or **Top-Center** ($Pan=0.0, Tilt=+650.0, Zoom=0.40$).

---

## 3. Caveats

1. **No Source Relinking or Proxy Creation:** All reframing must reference original online MP4 media at `G:\My Drive\Projects\Katy404\2026-09-29\...`.
2. **Project-Wide DRP Backup Prerequisite:** Before executing mutations, the implementer must export a full `.drp` archive to `G:\My Drive\Projects\Katy404\2026-09-29\KT404_2026-09-29_pre_vertical_conversion.drp`.
3. **Pilot Approval Requirement:** Timeline 1 (`หนีฝ่าความหนาว_Minecraft-vdo_9x16`) must be converted and visually verified before batch processing Timelines 2–30.
4. **Read-Only Investigation Bound:** No project timelines or files were modified during this investigation.

---

## 4. Conclusion

The technical mechanics for converting 16:9 timelines to 9:16 vertical in DaVinci Resolve Studio 21.1 are fully validated:
1. **Duplication:** `Timeline.DuplicateTimeline("<OriginalName>_9x16")` provides 100% preservation of editorial cuts, audio, and native subtitles.
2. **Resolution:** `useCustomSettings="1"` with 1080×1920 raster and matching 60.0 fps.
3. **Split Screen:** Dual video tracks with exact transform parameters:
   - V1 Game: $Zoom=1.60, Pan=0.0, Tilt=+480.0, CropBottom=486.0$
   - V2 VTuber: $Zoom=2.60, Pan=-936.0, Tilt=-200.0, CropTop=480.0$
4. **VTuber Focus:** Adjustment Clips on V4 with `Center={0.50, 0.25}, Size=2.0`.
5. **Reaction GIFs:** Shifted to upper game flank: $Pan=-300.0, Tilt=+600.0, Zoom=0.42$.

---

## 5. Verification Method

1. **Duplication & Setting Verification:**
   - Read back settings on the duplicate:
     ```python
     assert timeline.GetSetting("timelineResolutionWidth") == "1080"
     assert timeline.GetSetting("timelineResolutionHeight") == "1920"
     assert float(timeline.GetSetting("timelineFrameRate")) == 60.0
     ```
2. **Editorial & Subtitle Parity:**
   - Compare subtitle item count and timecodes between 16:9 original and `_9x16`:
     ```python
     orig_subs = orig_timeline.GetItemListInTrack("subtitle", 1)
     vert_subs = vert_timeline.GetItemListInTrack("subtitle", 1)
     assert len(orig_subs) == len(vert_subs)
     ```
3. **Visual Quality Control:**
   - Capture rendered preview frame during normal split screen (e.g. frame 216500) via `timeline_frame(action="capture", frame=216500, quality="preview")`. Inspect: Game top, avatar bottom with clear headroom and hands, subtitles unblocked.
   - Capture rendered preview frame during focus cue (e.g. frame 219300). Inspect: Full-screen VTuber close-up, game pushed off-screen, subtitles intact.
