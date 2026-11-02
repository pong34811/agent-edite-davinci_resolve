---
name: timeline-naming-convention
description: Use when naming highlight timelines or changing the naming format of timeline builders.
---

# Timeline naming

- Current user-requested format (Sakuyako-Cheris job, 2026-10-05): `{ชื่อคลิป}-vdo`. Earlier jobs used `{ชื่อคลิป}-{ชื่อเกม}-vdo`. Always follow the format in the live brief; the format is per job, so check `job.json`/`prompt.md` rather than assuming.
- `{ชื่อคลิป}` is a concise Thai title from source-verified event content, not from ASR alone or the filename. No source/candidate IDs or category prefixes in the name; keep them in metadata.
- If two names collide, stop and ask; do not silently append a suffix.
- `scripts/highlight/build_timelines.py` builds `{title}-{game}-vdo`. Changing prompt text or `job.json` does not change its output. To support a new format, change the generator with tests first (RED then GREEN) and only then claim support.
- Renaming existing timelines: follow the serialized `set_current` then `set_name` procedure in `long-video-highlight-clipping`.
