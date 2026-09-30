# Asset library layout and cue-to-asset mapping

How to turn a subtitled gameplay timeline into a placement plan without guessing timings.

## Read the cue map off the subtitle track

A timeline with burned-in editorial captions already carries a complete, frame-exact cue list. For each subtitle track index, `GetItemListInTrack("subtitle", i)` yields items whose `GetName()` is the caption text and whose `GetStart()`/`GetEnd()` are timeline frames. Classify the text, place the asset at that frame.

This beats visual analysis for comedic timing: the punchline is the line of dialogue, and the caption already marks where it lands. Reserve frame rendering for checking that an overlay does not cover gameplay, not for finding the beat.

Game-specific cues deserve game-specific SFX — a Minecraft death, a MOBA ace, and a boss despawn each have an idiomatic sound in a large library. Match the game named in the timeline name before reaching for a generic meme sound.

## Asset library conventions (user's Google Drive)

| Kind | Root | Scale | Naming |
|---|---|---|---|
| SFX | `G:\My Drive\Projects\2.1_sfx` | ~1.7k files, flat | Free-form; mixed Thai/English meme and game names |
| BGM | `G:\My Drive\Projects\1.bgm` | ~10 files, flat | Free-form; mostly no-copyright/NCS gaming mixes |
| Reaction GIF | `G:\My Drive\Projects\3.gif` | ~165 files, flat | `<Thai emotion> - <slug>.gif`, plus a few `.mp4` |

The GIF folder is pre-categorised by the Thai emotion prefix before the dash: เศร้า (sad), โกรธ (angry), ขำ (laughing), งง (confused), ดีใจ (happy), ตกใจ (shocked), ทักทาย (greeting), ปฏิเสธ (refusing), หิว (hungry), อาย (shy), คิดหนัก (thinking), เท่ (cool), เบื่อ (bored), plus animal sets หมา / กระต่าย / คาปิบารา. Caption text maps onto that prefix directly, so pick the emotion first and any slug within it second.

The SFX folder is flat and huge. List it once into a file and grep, rather than re-listing per cue; never import the whole library into the Media Pool to use a handful of files.

## Track convention on this user's shorts projects

`V1` gameplay · `V2` reaction overlays · `A1` dialogue/game audio · `A2` SFX · `A3` BGM · `ST1` Thai subtitles. Inspect an already-finished timeline in the same project to confirm the names before creating tracks — an existing exemplar timeline is the spec.

## Placement defaults that survived review

- Density around 5 SFX cues per minute reads as "punchy but not spammy" for gameplay shorts; 8-10/min is a deliberate comedy-edit choice, not a default.
- One BGM per clip, trimmed to clip length, rotated so neighbouring clips in a batch do not share a bed.
- 2-3 reaction GIFs per clip, scaled small into a corner, roughly 1.5-2.0s each, sized from the media's real `FPS`/`Frames`.
- Leave `V1`, `A1` source ranges, and the subtitle track untouched; enrichment is additive.
