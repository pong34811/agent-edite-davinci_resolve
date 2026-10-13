# FreeTalk_2 Thai short-form subtitles — Plan

**Goal:** Native Subtitle-track Thai dynamic captions on all 10 timelines of Resolve project `tygarina_2026-09-30_FreeTalk_2`.

**Spec (user, binding):** transcribe Thai speech fully; fix ASR errors/spelling/proper nouns; never invent or change meaning; 1–4 words per cue split by phrase; 1–2 lines; start at the spoken phrase, end at phrase end; 0.8–1.8 s typical (0.6–1.0 fast, 1.5–2.0 slow), never uniform; no overlap, no cue before speech, no lingering after speech; font Mitr Bold, white, black outline, centered, large, lower-middle position clear of bottom UI.

**Global Constraints (project rules, override spec where stricter — see Ruling R1):**
- Thai cues: ≤3 short words / ≈14 Thai chars, ≤1.5 s; no spaces between Thai words; spaces only around Latin names.
- Native Resolve Subtitle track only; no Text+/Fusion. Empty subtitle track, bare `{"mediaPoolItem": item}` payload. Stale pool item removed before re-import of an SRT at same path.
- Never modify source footage. Scratch WAVs only. Timelines stay 1920x1080@60 (16:9, user-approved).
- Structural Resolve mutations spaced ≥1.2 s; save project and read back; numeric values numeric.
- Style via SQLite only after: verified `.drp` export, project saved and closed, SQLite backup, transaction on exact subtitle-track rows (Type=2), reopen, read back. User authorized this (scope: these 10 timelines). Never patch an open DB.
- Active project was switched from `tygarina_2026-09-30_FreeTalk_1` (saved first, active timeline id ce1494f1-1100-4830-8545-621bed9cc1bb, page edit) — restore that project/timeline/page at the very end. FreeTalk_2's own original active timeline: record it before mutating.

**Jobs** (all one continuous V1 clip + A1, 3300 frames @60 = 55 s (job 1 is 3600 frames = 60 s); durations are in jobs.json — never hard-code 55, source 60 fps, no retime, record start 0): see `jobs.json` in the workspace. WAV t=0 = source_start_frame/60; cue time = wav time.

## Task 1: Extract audio and draft ASR for 10 jobs
Per job: ffmpeg decode 55 s mono 16 kHz WAV from the source (read-only) into `<workspace>/audio/job<N>.wav` (also a voice-band filtered variant). faster-whisper (large-v3 or best available, CUDA; see thai-subtitles-resolve skill for DLL and transcribe settings) → `<workspace>/asr/job<N>.json` with segments and char-level time index; pick per job by avg_logprob. Output: draft transcript + flagged low-confidence spans per job. No SRT yet.

## Task 2: Curate transcripts and build SRTs
Review ASR drafts (listen via re-decode spot checks, contact frames only for context), correct misheard words, spellings, proper nouns (record uncertain terms). Segment into phrase-based cues per Global Constraints using pythainlp newmm + character timing; no dropped speech (flag instead). Write UTF-8 SRTs `<workspace>/srt/job<N>.srt` + a per-job curation log. A validator script asserts: consecutive indices, no overlap, ≥34 ms gap, ≤1.5 s, ≤3 words/≈14 chars, no foreign glyphs, first cue ≥ speech start, last cue ≤ 55 s.

## Task 3: Import SRTs into Resolve (unstyled), verify
After project `.drp` export backup. For each timeline: confirm 0 subtitle tracks, AddTrack("subtitle"), append bare media pool item, ≥1.2 s spacing, read back count/text/absolute frames vs SRT, save. Restore active timeline/page.

## Task 4: Style the 10 subtitle tracks (DB)
Mitr Bold, white, black outline (Outside Only), centered, large, lower-middle Y. Derive blob from a reference track styled live in the Inspector if scripting can't; follow the DB safety protocol in Global Constraints. Verify cues unchanged and style blobs equal across 10 tracks.

## Task 5: Final QC
Per timeline: re-check text vs audio (re-transcribe sample / listen windows), timing rules, no overlap, no linger, readback vs SRT, burn-in/viewer screenshots for legibility and position, report. Restore state.
