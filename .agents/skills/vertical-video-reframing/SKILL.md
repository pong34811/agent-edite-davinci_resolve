---
name: vertical-video-reframing
description: Use when reframing edited landscape video to portrait.
---

# Reframe an existing cut for portrait delivery

This is a **reframing** workflow, not the raw-footage assembly covered by `resolve-rough-cut`. For Resolve-specific edit operations also load `resolve-edit`; for media reads follow the repo's source-media safety rules. Do not treat a marketing example or a source-file contact sheet as proof that a Resolve timeline renders correctly.

## Procedure

1. **Inventory before deciding.** Read the current project/build, timeline names and IDs, source and target frame rates/resolutions, duration, track structure and current output state. Check whether the intended portrait timeline or a project backup already exists; inspect an existing target instead of duplicating its name or overwriting it. Record which subtitle, audio, cut-point, GIF and graphic tracks are protected, and whether rendering is requested.
2. **Study the actual picture.** Inspect representative frames at the opening, middle, focus/reaction passages and ending. Map record frames to source frames using each item's reported `source_fps`; ffprobe the source and decode review frames only into session scratch or an analysis root. Do not assume a clip titled for a game actually shows gameplay throughout: it may show a slide, chat, an illustration or a full-face reaction instead. When useful, inspect Resolve-rendered frames too; source frames cannot prove the composite, subtitles, effects or grade.
3. **Choose a content-aware layout.** Fit legible *primary content* (gameplay, slide, illustration or conversation) in one region and make the avatar large enough for expressions in the other. Reassess at scene changes rather than imposing a game-only template. Compare a stacked composition against a scaled-full-frame/blur-fill alternative on the actual footage. Check platform UI occlusion and the unchanged subtitle zone before finalizing the crop. Favor an avatar close-up at a reaction beat only when the actual picture and timing support it. Treat a reaction GIF's name or active interval as an overlay cue, not evidence of the avatar's expression. If no separate focus clip is found, report which frames and animation surfaces were inspected; sparse still samples cannot rule out a brief baked-in or keyframed focus passage. Do not add new focus beats under an instruction to preserve existing ones.
4. **If reference clips are requested, inspect them as clips.** Find relevant local-language and broader-niche examples, examine more than a thumbnail with temporally spaced frames, and separate observed composition from creators' or vendors' claims. If the user delegates the artistic choice, make one recommendation with reasons rather than returning an undecided menu. The optional capture recipe is in `references/reference-study.md`.
5. **Make a visual proposal before editing when requested.** Build a scratch mockup from an actual source frame, label it as an analysis illustration, and state what it cannot show (motion, subtitle layout, overlays, Resolve effects). Compare the opening and an existing reaction/overlay beat side by side; supply individual target-raster images as well as comparison sheets so the design can be judged at mobile size. Identify a baked-in avatar explicitly: enlarging it also enlarges its original background, not an independently keyed character. If subtitle position/style cannot be established, do not draw invented captions or certify overlay clearance; carry subtitle collision as an unresolved composite-QC gate. A placeholder-only mockup is a fallback, not evidence that the crop works. When using subagents, require independent spec compliance first, visual quality review second, then human approval; a mockup passing review is not authorization to mutate Resolve. Show the selected design and resolve the approval gate before changing the project.
6. **Protect the original and implement one sample.** Export a fresh project backup to an authorized safe destination before mutation, duplicate or resume only the explicitly scoped target timeline, and make framing-only changes first. Preserve locked/protected tracks; do not introduce cuts, title bars, SFX or a render destination just to make a vertical version. Stop after the first sample when the user wants to review it before the rest.
7. **Verify the rendered result, not just settings.** Read back the target's name, portrait settings, duration and track inventory; compare representative rendered frames against the original and check subtitle/GIF placement at actual timestamps. Compare protected track item timing/text/audio properties before and after. Confirm Resolve remains responsive before moving to the next timeline. Clearly distinguish a scratch mockup, a Resolve timeline and a finished render in the handoff.

## Resolve conversion mechanics (the API layer)

- **The resolution write is gated.** `Timeline.SetSetting("timelineResolutionWidth")`
  returns False while the timeline inherits project settings
  (`useCustomSettings == "0"`). Set `useCustomSettings = "1"` first, then width
  (1080), then height (1920); each `SetSetting` returns a bool you must check —
  a `False` does not throw.
- **Verify the duplicate structurally, not by eyeballing frames.** Compare
  per-track `(name, start, end, enabled)` tuples and end-frame equality against
  the source for every audio/subtitle track plus the V1 video track; overlay
  tracks may legitimately differ.
- **Overlay transforms do not carry across the aspect change.** A 16:9 `Pan` of
  ~2000 pushes an inset off a 1080-wide canvas. Still images (`.jpg`/`.png`) →
  center + enlarge (`Pan=0`, `Zoom=1.0`). Reaction GIFs / short inserts → shrink
  to a corner (`Zoom≈0.38`, `Pan≈-250`, `Tilt≈+1250` = upper-left). Resolve sign:
  positive `Tilt` moves up, positive `Pan` moves right.
- **Full-frame 16:9 clips letterbox in a 9:16 timeline.** Budget a per-clip crop
  pass over gameplay segments instead of imposing a one-size template.

## Decision boundaries

- An unspecified maximum duration is **not** permission to shorten an existing cut; preserve it until a duration is supplied or a cut is approved.
- If the user requests only a timeline, do not invent a codec or output path. A render is a separate deliverable.
- Preserve the original file and its chain of custody. Temporary review stills and external reference clips belong only in session scratch/analysis storage and are never imported as replacement source media.
- A source crop may make a slide readable while the subtitle or GIF still collides at runtime. Do not claim the layout is done until Resolve-rendered frames verify those layers together.
