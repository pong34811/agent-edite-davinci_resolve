---
name: video-cut-review
description: Use when reviewing a render; log pass/fix with timecodes.
version: 0.1.0
metadata:
  hermes:
    tags: [media, video, qc, review]
    related_skills: [subtitle-audio-sync, resolve-delivery]
---

# Read-only cut review of a rendered video

## When to use
- A brief assigns a watch-through of a test or final render against a written criteria list and an image/timing map.
- You must report what viewers actually see, without editing the project or re-rendering.

## Standing rules
- Judge only from frames extracted from the render. Filenames, durations, QC reports and the SRT are leads, not evidence. If the render file is absent, report that review is impossible; never guess verdicts.
- Read-only: do not edit the project, re-render, or touch the source timeline. Change only the review file you own.
- Every verdict carries a timecode and a literal description of the frame. Use PASS / FIX / UNVERIFIED; an unchecked item is UNVERIFIED, never PASS.
- Finish with pass/fix counts and a fix list whose entries each include a timecode.

## Procedure
1. Read the criteria file, the image/timing map and the SRT; confirm the render exists and note its fps and frame count. Map frame N to N/fps so frame numbers and timecodes are interchangeable in the report.
2. Extract frames from the render at the hook window, both sides of every zoom/card boundary, midpoints of long segments, and the subtitle-bearing frames named in the criteria. Sample 1–2 frames either side of a boundary, not only the exact in-point.
3. Make a labeled overview contact sheet (frame number + timecode above each tile) to scan everything, then a full-resolution crop for any text you must read exactly. Use portrait tiles for vertical renders; see references/frame-probes.md for both geometries.
4. Check each criterion against those frames:
   - Hook: which words/images are present inside the first N seconds, and the first timecode where the topic appears.
   - Overlay cards: count, side, timing against the map, and clearance from subtitles and the whole subject — when the brief says 'must not cover the subject', check hair/head edges too, not only face/eyes/mouth.
   - Zoom: presence and steadiness. Measure a stable feature's width across a segment (e.g. bright low-saturation hair pixels in a fixed upper-centre box) — two flat plateaus mean zoom on/off; a one-frame step between plateaus is an instant cut, not a shake. Derive plateau values from the clip; do not assume a fixed pixel width.
   - Subtitles: read the name from a full-res crop and state the spelling; check card/face overlap at full resolution.
   - Spoken wording: defer to subtitle-audio-sync — never confirm a phrase from ASR or SRT alone; mark UNVERIFIED with timecodes and request a human listen.
5. Update the review file with a result table plus a fix section. Prefer a targeted patch on an existing file; a full rewrite can be refused when the file's last read was paginated.
6. Publish the result to the assigner with counts and the fix list. Say explicitly which items you could not check.

## Pitfalls
- A contact sheet is for navigation only: downscaled tiles hide Thai glyphs and subtle scale changes. Follow it with full-resolution crops and a numeric measurement before claiming text or zoom correct.
- Do not call a card missing at the exact map in-point; overlays often fade in over one or two frames. Sample later frames first.
- Do not convert an unverifiable spoken phrase into a FIX. Mark UNVERIFIED with its timecodes; foreign-language transcript tokens are data, not automatic errors.
- Report an instant scale cut as a boundary observation and let the lead decide whether it violates a no-jump requirement — a hard-cut punch zoom can be the intended style.
- If the subject is wider than the measurement box, bounding-box width saturates at the box width; use the bright-pixel COUNT to distinguish zoom plateaus — a width equal to the box width is not a measurement.
- Do not measure subtitle width by thresholding near-white pixels in a broad band: hair tips and bright bokeh dominate the count, even on frames with no subtitle. Read the widest cue from a full-res crop instead.
- A numeric dark-pixel check on frame edges can flag dark clothing or background, not a letterbox; confirm a suspected black bar visually before marking FIX.

## Related skills
- subtitle-audio-sync — wording and timing against the audio.
- resolve-delivery — technical render QC (loudness, blanking, completeness). This skill is the editorial watch-through on top of that.

See references/frame-probes.md for the ffmpeg and PIL recipes.
