# Studying short-form video references

Use this only when a requested layout decision depends on published examples. Cite the actual clips examined and say whether the evidence was full playback or sampled frames.

1. Search for both local-language creators and international examples of the same clip type. Sample different editorial styles, not just different creators using one template.
2. Fetch metadata before downloading. `yt-dlp --simulate --no-playlist --print '%(title)s | %(duration)s | %(id)s' URL` checks that the target is a real short. If automatic format selection fails, inspect `yt-dlp --list-formats URL` and choose a separate video stream plus the **original-language** audio stream by the IDs actually returned; `--merge-output-format mp4` joins them. Keep reference files in session scratch.
3. Inspect time, not only the cover: for a brief clip, `ffmpeg -i REF.mp4 -vf 'fps=1/5,scale=270:480,tile=6x1' -frames:v 1 CONTACT.png` provides a quick sequence of frames for visual comparison. Adjust the interval/tile count to the actual duration; frames alone do not establish spoken timing or exact transitions.
4. Note which region holds gameplay or other content, the avatar's readable size, text position, switches to face-focused shots, and UI-safe negative space. A two-panel example shows an option, not a universal rule about which panel must always contain gameplay.
5. When developing a project-specific crop, seek the source using the item `source_start/source_fps` plus a record-relative offset; inspect different record points. `ffprobe` dimensions/fps first. Keep FFmpeg stills/mockups in scratch, label them as source-based illustrations, and verify later with a frame rendered by the target editor.

A third-party service page may document a layout, but it cannot substitute for observing the linked video. Likewise a video thumbnail can support only a claim about that one frame, not a claim about the full edit.