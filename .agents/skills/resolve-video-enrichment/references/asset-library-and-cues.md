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
