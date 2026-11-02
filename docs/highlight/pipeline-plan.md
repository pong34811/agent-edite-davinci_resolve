# Highlights from Long Videos -> Resolve Timelines — Implementation Plan v2 (channel-agnostic; supersedes 2026-10-04_010000-hoshi-highlight-timelines.md)

> **ย้ายมาจาก repo `agent-seacrh-virus-cut` (2026-11-02):** โค้ด `work/*.py` อยู่ที่ `scripts/highlight/`, เทสที่ `tests/highlight/`, ข้อมูลงาน (`WORK_DIR`) ที่ `work/highlight/<CHANNEL>/<JOB>/`, spec คือ `docs/highlight/prompt-template.md`. แผนนี้คือบันทึกการออกแบบเดิม; คำสั่งปัจจุบันอยู่ใน `AGENTS.md` และ skill `long-video-highlight-clipping`


> **For agentic workers:** Execution split (see "Execution Strategy"): Tasks 0-6 and 8-10 NATIVE via superpowers:executing-plans (tightly coupled, sequential). Task 7 (review) via superpowers:subagent-driven-development / `delegate_task` (4 parallel). Load skills `resolve-rough-cut`, `resolve-media-pool`, `resolve-session` before Task 0 step 3 and Task 9. Steps use checkbox syntax.

**Goal:** Inventory every video in `INPUT_DIR`, find highlights of `CLIP_MIN_S`-`CLIP_MAX_S` seconds in the `CATEGORIES` (default gameplay / fun / meme), and build one Resolve timeline per approved clip. All parameters are defined in `prompt.md` (variables table); this plan never hardcodes a channel, path or file list.

**Architecture:** Three-pass funnel so expensive work touches the minimum footage. Pass A (cheap, all footage, audio-only, parallel): loudness/dynamics features over ~10.5 h of audio -> shortlist. Pass B (GPU, shortlist only, ~25% of runtime): Whisper Thai transcripts. Pass C (LLM judgement, parallel subagents): read transcript + one low-res contact sheet per shortlisted window, pick clips. A script then turns approved clips into Resolve `clip_infos`. Source files are never modified or transcoded; video is never fully decoded.

**Tech Stack:** ffmpeg/ffprobe 9.0.1 (`C:\Users\warit\AppData\Local\hermes\tools\ffmpeg-9.0.1-win32-x64\bin`; has libdav1d and av1_cuvid), Python venv with numpy, faster-whisper, pillow, pytest; Resolve MCP (`D:\davinci-resolve-mcp`).

**Spec:** `docs/highlight/prompt-template.md` (variables table + rules; it wins over this plan on any conflict).

## What changed vs v1 (and why)

1. Transcribe the shortlist only, not 10.5 h (about -75% GPU time). Machine: RTX 5060 Ti 16 GB, 20 cores. A Blackwell GPU may not work with the pinned CTranslate2 build, so a 2-minute GPU smoke test is now Task 0.
2. Audio-only scoring (no AV1 video decode). Demux each VOD ONCE to `work/audio/<id>.wav` (16 kHz mono pcm_s16le, ~1.2 GB total, level-untouched) and reuse it for scoring, transcription and silencedetect (v2 draft streamed to numpy and would have re-demuxed AV1 three times). all videos run in parallel. Whisper is not needed for the first filter.
2b. Transcription input is a boosted/normalized COPY of only the shortlist spans (high-pass 80 Hz + `loudnorm`), cut from the wav. NEVER normalize the scoring wav: it would erase the loudness differences the shortlist depends on.
3. New features "quiet-then-spike" and "sustained loudness plateau" (jumpscares in horror games, laugh fits in chatty streams). v1's plain loudness would mostly surface BGM stingers.
4. All questions go to the user ONCE up front (single `clarify`, Task 0) instead of blocking mid-run.
5. AV1 gate moved to Task 0 and uses ONE probe (import one AV1 file). Full import happens only after approval, and only for VODs with approved clips.
6. Contact sheets: 6 frames per window, 320 px wide, fast input-seek (`-ss` before `-i`) — far cheaper than Resolve `analyze_bin`, which pulls full-res frames. Do NOT use `analyze_bin`.
7. Subagents only for Pass C. Script tasks run natively (no fresh context + reviewer per 20-line script). Quality gates are pytest, not reviewer subagents.
8. One entry point `python work/pipeline.py <stage>` with output caching (skip when output is newer than inputs), so retuning costs seconds.
9. Cut points snapped to silence with `silencedetect`, so the editor does not have to trim.

## Global Constraints

- `INPUT_DIR` is READ-ONLY. All output under `WORK_DIR` (= `work\highlight\<CHANNEL>\<JOB>`); EVERY `work/` path in this plan means `WORK_DIR`. Gitignore `audio/ frames/ transcripts/ scores/ proxy/ .venv/` inside it.
- Clip length `CLIP_MIN_S`..`CLIP_MAX_S` (default 30..180, target 45-120). Categories exactly those in `CATEGORIES` (default `gameplay`, `fun`, `meme`).
- Timelines are assembly only: no titles, captions, music, effects, grading. Timeline fps and resolution = footage fps (from `inventory.json`; if files differ, ask the user) and `ASPECT`.
- Final report to the user in Thai.
- Filenames may contain `【】`, Thai, full-width `｜` and `⧸`. Discover paths via `pathlib.Path.glob` over `INPUT_DIR` (extensions .mp4 .mkv .mov .webm .ts .m4v, no subfolders). Assign `source_id` = `v01`, `v02`, ... by sorted filename and record the mapping in `inventory.json`; never match substrings of filenames. Pass paths as list args to `subprocess` (no shell); open text files with `encoding="utf-8"`.

## Parameters

All values come from the variables table in `prompt.md`: `INPUT_DIR`, `CHANNEL`, `JOB`, `WORK_DIR`, `CLIP_MIN_S`, `CLIP_MAX_S`, `CATEGORIES`, `CLIPS_PER_VIDEO`, `ASPECT`, `LANGUAGE`, `APPROVAL`. `work/config.py` reads them from `WORK_DIR/job.json` (written once at Task 0 from the table) so no script hardcodes them. Footage facts (count, codec, fps, duration) are never written in this plan: read them from `inventory.json`. N below means the number of videos found.

## Review Focus (each has a test in its owning task)

1. Overlapping/adjacent shortlist windows merge, not duplicate (Task 3).
2. Windows with no speech (BRB screen, music) are demoted (Task 3).
3. Cut points land in silence, not mid-word (Task 2 `snap_to_silence`, Task 7).
4. Candidate with end beyond video duration, or <30 s or >180 s, is rejected (Task 7 schema test).
5. AV1 offline in Resolve is detected before building (Task 0).

## File Structure

- `work/config.py` paths, limits, source_id mapping
- `work/inventory.py` ffprobe -> `inventory.json`, `inventory.md`
- `work/windows.py` pure functions: `merge_windows`, `clamp_duration`, `snap_to_silence`
- `work/features.py` Pass A audio features -> `scores/<id>.features.npz`
- `work/shortlist.py` scoring + merge -> `scores/<id>.top.json`
- `work/transcribe.py` Pass B -> `transcripts/<id>.json`
- `work/contact_sheet.py` -> `frames/<id>_<start>.jpg`
- `work/pipeline.py` stage runner with caching (stages: features, shortlist, transcribe, sheets, packets)
- `work/review/<id>.packet.md` input and `work/review/<id>.json` output per VOD; `work/candidates.json` merged
- `work/build_timelines.py`
- `work/tests/test_inventory.py test_windows.py test_shortlist.py test_candidates_schema.py test_build.py`

`candidates.json` item: `{"id":"v01-01","source_id":"v01","start_s":1234.5,"end_s":1320.0,"category":"fun","title_th":"...","reason":"...","score":0.0-1.0}`

## Tasks

### Task 0: Preflight and ask everything once (about 10 min)

- [ ] Step 1: Create venv: `python -m venv work/.venv && work/.venv/Scripts/pip install numpy faster-whisper pillow pytest`. Expected: installs without error.
- [ ] Step 2: GPU smoke test. Make a 60 s wav with `ffmpeg -t 60 -i <any vod> -vn -ac 1 -ar 16000 scratch.wav`, then transcribe with `WhisperModel("large-v3", device="cuda", compute_type="float16")`. Expected: Thai text printed in <60 s. On CUDA error try `compute_type="int8_float16"`, then `pip install -U ctranslate2`; last resort `device="cpu", model="small"` (still OK because only the shortlist is transcribed).
- [ ] Step 3: Resolve + codec gate (read-only, live): follow the "Resolve" section of `prompt.md` (`runtime_mode`, `get_current`, `list`, `snapshot`, `probe_media_pool`). Reuse the open project only if its name is `JOB` and its Media Pool already holds the `INPUT_DIR` files; otherwise follow the new-job branch there. Check each clip for offline status via `media_pool probe_clip_properties`; for AV1 files offline or zero-length, STOP and ask about H.264 proxies (`h264_nvenc`, approved-clip ranges only, in `work/proxy/`). Save `{source_id: clip_id}` read live to `work/resolve_clips.json` (ids are state, not constants).
- [ ] Step 4: ONE `clarify` call, asking only variables from `prompt.md` still at default and unconfirmed: `ASPECT`, `CLIPS_PER_VIDEO`, `APPROVAL`, and the Resolve series-vs-new-project question when relevant. Save answers in `work/decisions.md` and update the variables table in `prompt.md`. Commit.

### Task 1: Inventory (TDD)

**Files:** `work/config.py`, `work/inventory.py`, `work/tests/test_inventory.py`.
**Interfaces:** `inventory.probe(path: Path) -> dict` (keys `file, source_id, codec, width, height, fps:int, duration_s:float, size_bytes:int`); `inventory.build() -> list[dict]`.

- [ ] Step 1: failing test (uses a tiny fixture folder built in `tmp_path` with 2 short ffmpeg-generated mp4 files named with Thai and `【】` characters): `rows = inventory.build(tmp_path); assert [r["source_id"] for r in rows] == ["v01","v02"]; assert all(r["fps"] > 0 and r["duration_s"] > 0 for r in rows)`. `inventory.build(input_dir: Path | None = None)` defaults to `config.INPUT_DIR`.
- [ ] Step 2: `work/.venv/Scripts/python -m pytest work/tests/test_inventory.py -v` -> FAIL (ImportError).
- [ ] Step 3: implement using `ffprobe -v error -show_entries format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate -of json`; `__main__` writes `inventory.json` and a markdown table `inventory.md` (this is the footage list deliverable).
- [ ] Step 4: pytest -> `1 passed`; `python work/inventory.py` prints one row per video.
- [ ] Step 5: commit `feat: footage inventory`.

### Task 2: Window utilities (TDD)

**Files:** `work/windows.py`, `work/tests/test_windows.py`.
**Interfaces:** `merge_windows(ws: list[tuple[float,float,float]], gap_s: float = 15) -> list[tuple[float,float,float]]` (score = max); `clamp_duration(start: float, end: float, min_s: float = 30, max_s: float = 180) -> tuple[float,float]` (grow/shrink symmetrically about the centre; never start<0); `snap_to_silence(t: float, silences: list[tuple[float,float]], radius: float = 3.0) -> float` (midpoint of nearest silence within radius, else t).

- [ ] Step 1: tests: `merge_windows([(0,40,.5),(35,80,.9),(200,240,.3)]) == [(0,80,.9),(200,240,.3)]`; `clamp_duration(100,110) == (90,120)`; `e-s == 180` for `clamp_duration(0,500)` and `s >= 0` for `clamp_duration(5,10)`; `snap_to_silence(100,[(101,101.6)]) == 101.3`; `snap_to_silence(100,[(110,111)]) == 100`.
- [ ] Step 2: run -> FAIL. Step 3: implement. Step 4: run -> `5 passed`. Step 5: commit.

### Task 3: Pass A — features and shortlist (audio only, parallel)

**Files:** `work/features.py`, `work/shortlist.py`, `work/tests/test_shortlist.py`.
**Interfaces:** `features.extract_wav(source_id: str) -> Path` runs `ffmpeg -y -v error -i <file> -vn -ac 1 -ar 16000 -c:a pcm_s16le work/audio/<id>.wav` (skip if wav exists and is newer than source; verify duration within 1 s of inventory). `features.extract(source_id: str) -> Path` reads that wav with numpy, computes per-second RMS dB and peak dB, writes `scores/<id>.features.npz` (`rms`, `peak`). `shortlist.score_windows(rms, peak, win: int = 60, hop: int = 30) -> list[tuple[float,float,float]]`. `shortlist.top(source_id: str, per_hour: int = 14) -> list[tuple[float,float,float]]` (top-N by score then `merge_windows`).

Per-window features, z-scored within the VOD: `loud` (mean RMS), `peak` (max peak), `jump` (max of RMS[t] minus median RMS[t-10..t-2]), `plateau` (fraction of seconds above the VOD 85th-percentile RMS). Score = 0.3 loud + 0.15 peak + 0.3 jump + 0.25 plateau, min-max to 0-1. `speech_ratio` = fraction of seconds above VOD 30th-percentile RMS; if <0.2, score *= 0.3.

- [ ] Step 1: failing tests on synthetic arrays: (a) 600 s quiet noise + 10 s burst at t=300 -> top window contains 300; (b) two bursts 20 s apart -> `top()` returns one merged window; (c) a constant-loud 300 s stretch scores below a burst in normal speech; (d) the same burst scores lower inside a silent stretch (speech_ratio<0.2) than inside a speech-level stretch.
- [ ] Step 2: pytest -> FAIL. Step 3: implement. Step 4: `pytest work/tests/test_shortlist.py -v` -> `4 passed`.
- [ ] Step 5: `python work/pipeline.py features` (all videos via `ThreadPoolExecutor(min(N, 8))`). Expected: N npz files, a few minutes total. `python work/pipeline.py shortlist` -> each `top.json` has ~14 non-overlapping windows per hour of video (script asserts no overlap).
- [ ] Step 6: commit.

### Task 4: Pass B — transcribe shortlist only (GPU)

**Files:** `work/transcribe.py`.
**Interfaces:** `transcribe.run(source_id: str) -> Path` writes `transcripts/<id>.json` = `[{"start": float, "end": float, "text": str}]` with absolute timestamps, covering the union of shortlist windows padded +-60 s (merged). Each span is cut from `work/audio/<id>.wav` (not the video) and boosted with `ffmpeg -ss <s> -t <len> -i work/audio/<id>.wav -af "highpass=f=80,loudnorm=I=-16:TP=-1.5:LRA=11" -ac 1 -ar 16000 -f f32le -` into memory (add `dynaudnorm=f=150:g=15` after loudnorm only if quiet speech still drops out); one `WhisperModel` instance; `language="th"`, `vad_filter=True`, `beam_size=1`. Append finished spans to `<id>.partial.json` so reruns skip them.

- [ ] Step 1: test: `transcribe.segments_for_span` on a 20 s synthetic sine returns `[]` without error; and `transcribe.boost(samples)` on a 0.01-amplitude 440 Hz-modulated noise returns RMS at least 6 dB higher than the input.
- [ ] Step 2: run in background with notify (never foreground): `python work/pipeline.py transcribe`. Expected: ~10-20 min for ~2.5 h of audio on this GPU.
- [ ] Step 3: verify `python -c "import json,glob;[print(f,len(json.load(open(f,encoding='utf-8')))) for f in sorted(glob.glob('work/transcripts/*.json'))]"` -> N files (one per video), each with >20 segments per hour of video (fewer only if the video has little speech). Commit scripts.

### Task 5: Contact sheets (run while Task 4 transcribes: CPU vs GPU)

**Files:** `work/contact_sheet.py`.
**Interfaces:** `contact_sheet.make(source_id: str, start_s: float, end_s: float, n: int = 6) -> Path` — 3x2 grid of 320x180 tiles, timestamp burned on each tile with Pillow; frame grab `ffmpeg -ss <t> -i <file> -frames:v 1 -vf scale=320:-1 -f image2pipe -vcodec png -`.

- [ ] Step 1: test: `make("v01", 100, 160)` returns an existing jpg of size 960x360. Fail -> implement -> pass.
- [ ] Step 2: `python work/pipeline.py sheets` for every shortlist window (parallel). Commit.

### Task 6: Review packets

- [ ] Step 1: `python work/pipeline.py packets` writes `work/review/<id>.packet.md`: per shortlist window — window id, hh:mm:ss range, score and features, transcript lines (+-60 s), contact sheet path. One file per VOD so each subagent reads exactly one file.
- [ ] Step 2: verify `ls work/review/*.packet.md | wc -l` -> `N`.

### Task 7: Pass C — parallel review (4 subagents)

- [ ] Step 1: `delegate_task` calls with one task per `source_id`, at most 8 per call. Each context must include verbatim: Global Constraints; category definitions copied from `prompt.md` for `CATEGORIES`; the candidate schema; and these instructions: "Read only `work/review/<id>.packet.md`. Open at most one contact sheet per window with `vision_analyze`. Pick the clip count from `work/decisions.md` (`CLIPS_PER_VIDEO`), spread across the stream (no two within 5 min unless clearly different beats). Extend or trim to a complete beat. Snap start/end with `ffmpeg -ss <t-5> -t 10 -i <file> -vn -af silencedetect=n=-35dB:d=0.4 -f null -` and `windows.snap_to_silence`. Write Thai `title_th` and `reason`. Write ONLY `work/review/<id>.json`." Children cannot ask questions.
- [ ] Step 2 (parent verifies; child summaries are self-reports): `python -m pytest work/tests/test_candidates_schema.py -v`. The test loads `work/review/*.json` (not packets) and asserts: required keys, category in allowed set, `CLIP_MIN_S <= end_s-start_s <= CLIP_MAX_S`, `end_s <= duration_s` from inventory, no overlaps within a source, unique ids. Expected: all pass; redo only the failing VOD.
- [ ] Step 3: merge to `work/candidates.json` ordered by source then start, ids `<source_id>-NN`. Commit.

### Task 8: Approval checkpoint (skip only if Task 0 chose automatic)

- [ ] Print table (id, source, hh:mm:ss range, duration, category, title_th); ask in Thai: approve / drop ids / nudge times. Apply edits, re-run schema test, commit.

### Task 9: Build timelines

**Files:** `work/build_timelines.py`, `work/tests/test_build.py`.
**Interfaces:** `to_clip_infos(c: dict, clip_id: str, fps: float) -> list[dict]` returning `[{"clip_id": clip_id, "start_frame": round(c["start_s"]*fps), "end_frame": start_frame + round((c["end_s"]-c["start_s"])*fps), "record_frame": 0}]` (end exclusive; source fps equals timeline fps, so no mixed-fps floor issue).

- [ ] Step 1: failing test with fps=60: start_s=10, end_s=70 -> `start_frame==600, end_frame==4200, record_frame==0`. Run -> FAIL; implement; run -> PASS. Commit.
- [ ] Step 2: Resolve setup per the "Resolve" section of `prompt.md`: reuse the open project only when its name is `JOB` and the Media Pool holds the `INPUT_DIR` files; otherwise ask series-vs-new, set `timelineFrameRate` to the footage fps BEFORE the first timeline, create a bin named `JOB`, `set_current_folder` to it, THEN import. Before each `create_timeline_from_clips`, `set_current_folder` to the folder holding the clips. The Playback frame rate UI setting cannot be verified via API: ask the user to confirm Project Settings (gear, bottom-right) -> Master Settings -> Playback frame rate equals the footage fps, quoting that path exactly. If `ASPECT` is 9:16, set timeline resolution before the first timeline (it may lock after creation; check `resolve_control api_truth "timeline"`).
- [ ] Step 3: per candidate: `set_current_folder` to the bin, then `media_pool create_timeline_from_clips` named `<id>_<category>_<title_th>` (<=60 chars) with `to_clip_infos`. If vertical was chosen: timeline 1080x1920 at creation, scale/position per item (centre crop unless the user gave a focus).
- [ ] Step 4: verify all timelines: `timeline detect_gaps_overlaps` -> 0 gaps, 0 overlaps; item duration frames == `round(dur*fps)`; timeline count == number of candidates; delete any `*_archived_vNN`; save project.
- [ ] Step 5: spot-check the first frame of 3 timelines with `timeline_frame` (non-black).

### Task 10: Report (Thai)

- [ ] Footage list (`inventory.md`), candidate table, timeline names, what was skipped (no captions/music/grading, no renders), tuning knobs (`per_hour`, weights in `shortlist.py`).

## Execution Strategy

- Native (`superpowers:executing-plans`): Tasks 0-6, 8-10 — small, sequential, shared interfaces; subagents would only add overhead.
- Subagents (`superpowers:subagent-driven-development`, one per video, max 8 parallel): Task 7 only — independent, judgement-heavy, token-heavy; parent verifies with pytest.
- Long jobs (features, transcribe) run as background terminal processes with `notify=true`.
- Estimated wall-clock: preflight 10 min, scripts+tests ~40 min, features ~5 min, transcription ~15 min, review ~10 min, timelines ~10 min.

## Risks

- CTranslate2 on Blackwell (RTX 50xx) may fail -> Task 0 smoke test and fallbacks.
- Loudness shortlist can miss quiet deadpan memes. Mitigation: raise `per_hour` to 24 (cost: more transcription only), or let reviewers request extra windows from transcript keyword hits.
- Fun/meme judgement is subjective; Task 8 is the quality gate.
- AV1 in Resolve: handled in Task 0.
