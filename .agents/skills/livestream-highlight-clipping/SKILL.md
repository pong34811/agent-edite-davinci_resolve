---
name: livestream-highlight-clipping
description: Use when cutting stream VOD highlights into timelines.
---

# Livestream Highlight Clipping

> **In this repo:** pipeline code is `scripts/highlight/` (was `work/*.py`), tests `tests/highlight/`, job folders `work/highlight/<channel>/<job>/` (`HIGHLIGHT_JOB` points at its `job.json`), job prompt template `docs/highlight/prompt-template.md`, wiki `docs/highlight/wiki/`. Older wording that says `work/`, `prompt.md` or `llm_wiki/` means these paths.

Class of task: a folder of multi-hour stream VODs -> inventory -> 30s-3min highlight candidates (gameplay, fun, meme) -> one DaVinci Resolve timeline per clip. Funnel pipeline: cheap audio scoring, shortlist-only transcription, parallel review, then timelines. User communicates in Thai; write the final report in Thai. Deliverable is assembled timelines only (see `resolve-rough-cut`: no titles/captions/music/effects/grading unless asked).

## Order of work

1. **Look at Resolve first, read-only.** `project_manager snapshot`, `media_pool probe_media_pool`. The user often already has the project open with footage imported at the right fps. Reuse it: do not create a project, set frame rate, or re-import. Imported durations matching ffprobe show an AV1 file decodes; still check offline flags with `probe_clip_properties` before building.
2. **Inventory with ffprobe** (codec, fps, duration, rotation) via `pathlib` globbing. Stream filenames carry Thai text, full-width bar and slash characters: never hand-type paths, pass list args to subprocess, open text as UTF-8.
3. **Ask every open question once, up front** (single clarify): aspect (16:9 vs vertical), clips per VOD, approval checkpoint vs automatic. Do not interleave questions through the run.
4. **Extract audio to a 16 kHz mono wav ONCE per VOD** and reuse that wav for scoring, transcription and silence detection. Repeated demuxing of multi-GB AV1 files is the main avoidable cost.
5. **Pass A, cheap, all footage:** score sliding windows from the wav (loudness, peaks, quiet-then-spike jumps for scares/shouts, sustained-loud plateaus for laughing fits; demote windows with little speech). Merge overlapping windows.
6. **Pass B, shortlist only:** transcribe just the shortlisted windows (padded) with faster-whisper (`language="th"`, `vad_filter=True`). Smoke-test the GPU on a 60 s clip first; new GPU generations can break the CTranslate2 build.
7. **Boost audio only for the transcription copy** (high-pass ~80 Hz + `loudnorm`, optionally `dynaudnorm`), cut from the wav. NEVER normalize the wav used for scoring: it erases the loudness differences the shortlist relies on.
8. **Pass C, judgement:** one subagent per VOD (parallel) reads a packet of transcript + one small contact sheet per window and writes a candidate JSON. Validate their files with a pytest schema check (length 30-180 s, end <= duration, no overlaps, allowed categories) instead of trusting their summaries.
9. **Snap cut points to silence** (`ffmpeg ... silencedetect=n=-35dB:d=0.4`) so clips do not start or end mid-word.
10. **Show the candidate table and get approval** before creating timelines.
11. **Build timelines** per `resolve-rough-cut`: `set_current_folder` to the clips' bin, `create_timeline_from_clips` with `end_frame` exclusive, then `detect_gaps_overlaps` = 0 and duration check. If source fps == timeline fps (both 60) there is no mixed-fps flooring issue.

## Pitfalls

- Avoid Resolve `analyze_bin` for shot finding on hours of 1080p+: it extracts full-res frames. Use small ffmpeg contact sheets with input-seek (`-ss` before `-i`).
- Plain loudness ranking surfaces BGM stingers; combine it with jump and speech-ratio features.
- Long jobs (transcription) run as background processes with notify and resumable per-span output, never as a foreground call.
- Execution split: script-writing tasks are tightly coupled, do them natively; use subagents only for the parallel review pass.
- Overlaps heavily with `long-video-highlight-clipping`, which carries the tested details (batched Whisper, Windows CUDA DLL fix, shortlist sizing, repeated-char hallucination cleanup, tooling pitfalls). Load that one first; this file is the shorter order-of-work view. Feature weights and loudnorm settings are starting points to tune.
