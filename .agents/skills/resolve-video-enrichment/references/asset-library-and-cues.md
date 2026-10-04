# Asset library layout and cue-to-asset mapping

How to turn a subtitled gameplay timeline into a placement plan without guessing timings.

## Read the cue map off the subtitle track

A timeline with native editable subtitle items provides a useful frame-addressed cue map. For each subtitle track index, `GetItemListInTrack("subtitle", i)` yields text through `GetName()` and timeline frames through `GetStart()`/`GetEnd()`. Burned-in pixels alone do not expose these items, and a subtitle track is not proof of complete or correct transcription.

Use captions to shortlist emotional beats, then verify the actual speech, action, and reaction before placing an asset. Caption appearance can precede or span the punchline; it is not automatically the accent frame. Visual-only surprises, pauses, and avatar expressions require performance review, not keyword matching.

Game-specific cues deserve game-specific SFX — a Minecraft death, a MOBA ace, and a boss despawn each have an idiomatic sound in a large library. Match the game named in the timeline name before reaching for a generic meme sound.

## Asset library conventions (user's Google Drive)

| Kind | Root | Scale | Naming |
|---|---|---|---|
| SFX | `G:\My Drive\Projects\2.1_sfx` | ~1.7k files, flat | Free-form; mixed Thai/English meme and game names |
| BGM | `G:\My Drive\Projects\1.bgm` | ~10 files, flat | Free-form; mostly no-copyright/NCS gaming mixes |
| Reaction GIF | `G:\My Drive\Projects\3.gif` | ~165 files, flat | `<Thai emotion> - <slug>.gif`, plus a few `.mp4` |

The GIF folder is pre-categorised by the Thai emotion prefix before the dash: เศร้า (sad), โกรธ (angry), ขำ (laughing), งง (confused), ดีใจ (happy), ตกใจ (shocked), ทักทาย (greeting), ปฏิเสธ (refusing), หิว (hungry), อาย (shy), คิดหนัก (thinking), เท่ (cool), เบื่อ (bored), plus animal sets หมา / กระต่าย / คาปิบารา. Caption text maps onto that prefix directly, so pick the emotion first and any slug within it second.

Treat these paths and counts as historical examples, not live inventory or license evidence. Discover the current authorized library with `search_files`, persist a manifest through `write_file`, and search that manifest rather than re-enumerating per cue. Never import the whole library into the Media Pool to use a handful of files. A filename or folder label such as no-copyright/NCS does not prove permission; verify each selected asset's current license and attribution requirements.

## Track convention on this user's shorts projects

`V1` gameplay · `V2` reaction overlays · `A1` dialogue/game audio · `A2` SFX · `A3` BGM · `ST1` Thai subtitles. Inspect an already-finished timeline in the same project to confirm the names before creating tracks — an existing exemplar timeline is the spec.

## Project-specific placement starting points

These are historical exemplar settings, not universal audience preferences or required quotas. Use current scope, the actual performance, and the approved exemplar; omit an asset that has no editorial job.

- Density around 5 SFX cues per minute reads as "punchy but not spammy" for gameplay shorts; 8-10/min is a deliberate comedy-edit choice, not a default.
- One BGM per clip, trimmed to the full timeline length, rotated so neighbouring clips in a batch do not share a bed. After activating and ID-verifying each target, use that Timeline's `GetSetting("timelineFrameRate")` as record FPS; a Project-level frame-rate setting can differ. Read source `Duration` and `FPS` separately with named `GetClipProperty` calls, compute required source frames from the per-timeline record span and source FPS, and verify both source and record ranges after append. Fail before appending if no approved candidate covers the whole timeline; do not assume a short source loops or layer a second bed to hide a duration mismatch.
- For SFX, plan record duration using the target Timeline's FPS, read each asset's source FPS and available duration, then convert that duration to source frames; do not pass record-frame counts as source `endFrame` values. Cap to the source's available frames and derive the actual record end from the same source/timeline FPS ratio.
- Call `GetClipProperty("FPS")` and `GetClipProperty("Frames")` separately on each GIF MediaPoolItem; Resolve may return scalar values rather than a dictionary. Skip missing/malformed metadata and GIFs shorter than the approved minimum.
- Plan a nominal two-second GIF hold in record frames using the target Timeline's own FPS, then convert to source frames with the actual source/timeline FPS ratio (Resolve floors source-to-record conversion). Cap to available `Frames` only if the resulting record duration remains within 1.5–2.5s, and verify the inserted source and record ranges with timeline readback.
- On resume, identify an existing GIF by target track, record start, and asset; then validate its actual duration is within the approved range and timeline bounds. Do not require an exact planned end as the identity key, because source FPS conversion can change record duration; reject duplicate or out-of-range matches before appending.
- Leave `V1`, `A1` source ranges, and the subtitle track untouched; enrichment is additive.

## Build-measured metadata and source-end guards

- On Studio 21.1.0.17, imported MP3 `Frames` can be empty while `FPS` and
  `Duration` are populated. Read the pool's own FPS and duration timecode to
  derive available source frames; validate its timebase first. Do not cast an
  empty Frames string to float or assume a WAV/MP3 always follows timeline FPS.
- Verify source-end convention with an isolated approved placement before a
  batch. On this build an MP3 append with startFrame=0, endFrame=10377 produced
  10377 record frames; endFrame=10378 produced the intended 10378-frame bed.
  Historical inclusive-end guidance is not proof on the current build. Compare
  GetStart(True)/GetEnd(True), source start/end and actual conformed duration;
  require BGM to cover the exact approved timeline, not merely within one frame.
- Probe GIF alpha by inspecting the actual Resolve composite. Some GIFs retain
  transparency on this build; neither a historical alpha-loss observation nor
  a Media Pool Alpha mode label proves current pixel behavior.

## Batch recipe for talk/chat (non-gameplay) timelines

Proven order for "add SFX + BGM + GIF to every timeline, copies first, then originals":

1. Export a `.drp` backup, then dump each timeline's ID, FPS, range, V1 range, and subtitle cues (start/end/text) to scratch files; write the SFX and GIF filename lists to scratch too.
2. Fan out `delegate_task` planners (read-only, file toolset, two timelines each) that write `plan_T<N>.json` (`frame` = a real cue start, exact filenames). Subagents finish in seconds with little verification, so validate every plan in code: files exist, frames are real cue starts, spacing, first/last limits, no duplicates within a timeline.
3. Filter the GIF library to usable items before accepting plans: Resolve duration >= 1.5s and >= 8 frames (hold target 2s must stay inside 1.5-2.5s). Swap rejected picks for a same-emotion-prefix GIF not already used in that timeline.
4. Set levels per timeline, not globally: source speech loudness varied by ~20 LU between timelines of one batch. Measure speech from the V1 source file at `GetLeftOffset()/fps` with ffmpeg `ebur128`; BGM gain = speech LUFS - 20 - BGM LUFS (clamp -60..0); SFX gain = speech LUFS - 3 - SFX LUFS, capped at 0 dB. `ebur128` reports -70 for very short files; use `loudnorm=print_format=json` (`input_i`) for SFX.
5. `DuplicateTimeline(name + " [ENHANCED]")` on the activated original; the copy is appended at the END of the timeline list, so list indices of originals stay valid, but still resolve targets by stored ID + expected name.
6. Append with `{mediaPoolItem, startFrame, endFrame, mediaType, trackIndex, recordFrame}`: audio source frames equal seconds x timeline FPS (60 here); BGM `endFrame` = timeline length; SFX trimmed to <= 3s with `SetFades({FadeOut: 9})`; GIF `endFrame = n-1` where `n = min(Frames, round(2*FPS))` from Resolve's own properties. Lock V1/A1/subtitle tracks first and restore their previous lock state in a `finally`.
7. Overlay slot on a centered-avatar + right-chat facecam layout: the user's own Inspector Video preset (named `vdo`: Zoom 0.42 gang, Position 0 / ~32.3, all else default) is the approved GIF placement and overrides any slot you compute. A computed top-left slot (40 px margin, at most 420x300) is only a fallback that clears face, hair, chat and captions. Prove placement with the overlay-on/off pixel diff, not Inspector numbers.
   - Resolve has no scripting call for Inspector > Video Presets > Load Preset (`Project.SetPreset`/`GetPresetList` are project-settings presets) and the preset body is not readable in `User.db` (`VideoPresetsBA` shows no preset names). Reproduce a preset by capturing `TimelineItem.GetProperty()` from a clip the user loaded it onto and re-applying the transform/composite keys with numeric `SetProperty` (readback + one retry, ~0.45s apart).
   - Repo tool: `scripts/apply_vdo_preset.py` (dry run by default; `--apply`, `--only-originals`, `--timeline`, `--capture NAME` stores the clip under the playhead into `scripts/video_presets.json`). It only touches GIFs on the `REACTIONS` track and restores timeline/playhead/page.
   - A fixed centered zoom covers the face for tall (portrait) GIFs; flag that to the user instead of silently moving them.
8. Pilot one timeline end to end (copy), fix calibration, run the remaining copies 2-4 per call (~30s each), then promote to originals with the same idempotent function and a full readback comparison against the pre-edit dump and against the copy.
9. Finish by restoring the captured active timeline, playhead (re-set after any still export, which moves it), page and Media Pool folder.
