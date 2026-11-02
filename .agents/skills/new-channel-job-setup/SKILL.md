---
name: new-channel-job-setup
description: Use when starting a highlight job for a new channel or new footage folder, before running any pipeline stage.
---

# New channel / job setup

1. Read the user's brief and `docs/highlight/prompt-template.md`. List every variable still unanswered; ask them ONCE (aspect, clips per video, approval pause, Resolve project and folder, clip min/max seconds, categories). Skip anything already stated, and mark unconfirmed repo defaults as proposals.
2. Create `work/highlight/<channel>/<job>/job.json` (never hardcode channel, folder or file list in code). Export `HIGHLIGHT_JOB` as the absolute path before every stage.
3. Run `python inventory.py` from `scripts/highlight/`. Reconcile `inventory.json` with the live folder: count only video files (ignore `desktop.ini` and other non-footage); do not reuse counts from an old job or plan.
4. Read per-file fps/size from `inventory.json`. If fps or aspect differ across files, stop and ask for a timeline policy before creating a Resolve project.
5. Add a job-local `.gitignore` for `audio/ scores/ transcripts/ frames/`.
6. Footage folders are read-only; all artifacts go under the job folder.
