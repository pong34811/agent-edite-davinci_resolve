---
name: resolve-offline-media-repair
description: Use when Resolve media is offline though the file exists.
version: 0.1.0
platforms: [windows]
metadata:
  hermes:
    tags: [Resolve, Relink, Transcode]
---

# Resolve media offline although the file exists

Complements the project skill `resolve-conform` (repo `.agents/skills/`; copy it into the profile if `skill_view` cannot find it).

## Procedure

1. Confirm the path exists, then `ffprobe` it (codec, fps, duration) and compare with a sibling clip that is online. Resolve on Windows cannot decode VP9/Opus (YouTube/web-saved files): the clip goes offline with a correct path, so relinking to the same file never helps.
2. A "replaced" file with identical size + mtime is the same broken file (ctime changes on copy). Compare size, mtime and ctime before believing a replacement happened.
3. Transcode next to the original, never over it:
   `ffmpeg -nostdin -i SRC -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p -r <srcfps> -c:a aac -b:a 192k -movflags +faststart SRC_h264.mp4`
   Run it as a background terminal job with notify (about 25 min for a 2.5 h 720p60 file). ffprobe the result: codec H.264/AAC and duration equal to the source.
4. Swap with `MediaPoolItem.ReplaceClip(new_path)` inside `preserved_state(resolve)`; it keeps timeline instances, while `safe_relink`/`RelinkClips` match by file name and miss a renamed file. Read back File Path, Video Codec, Duration, then `SaveProject()`.
5. Re-run failed renders afterwards. `scripts/p2_export_final.py` skips outputs already Complete, so a re-run only redoes the failures; verify each with Complete status + ffprobe.

## Pitfalls

- Pool entries with an empty File Path are timelines, not offline media; do not relink them.
- Write Resolve probe scripts to the Hermes scratch dir via a native `C:/...` path; bash `$TMPDIR` is not a path native python can open.
- Transcoding is a derivative of source media: keep the original, name the copy `_h264`, and say so in the report.

## When the user says "continue" with no context

Do not ask or guess: run `session_search` (query by the filename/topic, sort newest) and read the matching prior session before acting. The user expects the previous session's goal (here: finish the batch export) to be recovered from history.
