# Orchestration Plan: Tygarina Footage Highlights & Timeline Construction

## Objective
Analyze all video footage in `C:\Users\warit\SynologyDrive\Tygarina\2026-09-30` to identify highlight moments (gaming, fun, memes) strictly between 30s and 3m, and construct individual timelines for each moment in the active DaVinci Resolve project via Resolve MCP server non-destructively.

## Phase 0: Survey (Parallel Exploration)
- Dispatch 3 parallel Explorers:
  - **Explorer 1**: Survey footage directory (`C:\Users\warit\SynologyDrive\Tygarina\2026-09-30`), list files, format, duration, audio channels, metadata.
  - **Explorer 2**: Survey DaVinci Resolve environment via Resolve MCP (`davinci-resolve` server: active project, frame rate, resolution, media pool structure).
  - **Explorer 3**: Survey highlight detection methodologies & available tools (audio analysis, transcripts, transcription/Whisper capabilities, scene detection).
- Merge survey findings into `PROJECT.md`.

## Phase 1: Milestone Decomposition & Architecture (PROJECT.md)
- Define milestones, interfaces, and deliverables.
- Setup E2E Testing track and Implementation track.

## Phase 2: Execution via Explorer → Worker → Reviewer → Challenger → Auditor Loops
- **Milestone 1**: Candidate Highlight Analysis & Selection
  - Identify highlight candidates with categories: gaming, fun, meme.
  - Enforce constraint: strictly between 30 seconds and 180 seconds.
  - Output structured report with objective rationale (transcript snippets, audio peaks, game action timestamps).
- **Milestone 2**: Resolve Ingest & Preparation
  - Ensure source footage is safely imported into Media Pool without transcoding or altering originals.
  - Capture media pool item IDs and properties.
- **Milestone 3**: Timeline Construction
  - For each approved highlight candidate, create a separate timeline named descriptively.
  - Place footage slice corresponding to [start_time, end_time].
  - Maintain timeline duration strictly matching highlight candidate duration.
- **Milestone 4**: E2E Verification & Forensic Audit
  - Verify all timelines exist in Resolve, have correct durations, and link cleanly to original media.
  - Run Reviewers, Challengers, and Forensic Auditor (`teamwork_preview_auditor`).
  - Pass gate and finalize victory report to Sentinel.
