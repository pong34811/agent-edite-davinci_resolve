---
name: resolve-still-qc-capture
description: Use when capturing still frames from Resolve timelines for QC of clip in/out points.
---

# Resolve still capture for QC

- Capturing stills changes the project render format. Before capture, read back `render.get_format_and_codec` and record it.
- JPG / YUV420_8 stills need a delivery preset selected first; capture failed to restore the original format in the Hoshi job.
- After capture, try to restore the original format and read it back. Read every `timeline_frame` capture warning; a new project's original format may be mov with an empty codec that cannot be restored. If so, disclose the remaining jpg setting instead of silently choosing a delivery codec.
- Restoring the playhead is separate from restoring the timeline: set and read back the handoff timeline and playhead intentionally.
