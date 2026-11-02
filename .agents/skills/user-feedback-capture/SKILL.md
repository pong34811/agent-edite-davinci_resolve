---
name: user-feedback-capture
description: Use after the user approves, rejects or corrects delivered clips, to record feedback in the wiki without guessing reasons.
---

# User feedback capture

1. Save the user's verbatim answer under `docs/highlight/wiki/raw/` (dated). Follow `docs/highlight/wiki/AGENTS.md`; raw files are immutable.
2. Record per-clip choices (select / reject / change request) using `docs/highlight/wiki/templates/clip-review.md`, tied to channel, job, source file and timestamps.
3. If no reason is given, write "reason not given". Never infer why a clip was liked or disliked.
4. Add a `house-style` rule only for a reusable preference the user states (Rule / Why / Trap). An approval of the whole set, or rejection of one clip, is not a rule.
5. Keep agent opinions separate from user answers. If YouTube metrics exist, store video id, publish date, collection date and window; never estimate numbers.
6. Update index, overview and append to `log.md`; check any hash or file claim before writing it.
