# Changelog

## v0.6.0

### Added
- `scripts/pipeline/`: the batch pipeline used on 10 projects (inventory + `.drp` backup, ASR with Whisper large-v3, SRT import and read-back, cue files, plan validation + loudness-based gains, enrichment placement with protected-range check) with a README; `check_srt.py` (caption contract, U+FFFD, repeats, hallucination loops) and `make_ids.py`. Paths are env-driven (`PW`, `TMPDIR`, `SFX_DIR`, `GIF_DIR`, `BGM_DIR`, `FFMPEG`, `FFMPEG_DIR`, `EXPORT_DIR`, `PROJECT_FOLDER`).
- `scripts/convert_talk_9x16.py` (talk-only: face crop fills 1080x1920, bottom status bar cropped) and `scripts/convert_game_9x16.py` (game panel on top + facecam panel on a new V3; `--scale/--cx/--top/--game-scale/--game-cx`), `scripts/delete_9x16.py` (remove only exact `_9x16` copies).
- `scripts/video_presets.json`: preset `short` (vertical GIF placement: Zoom 0.42, Position 0 / 403.2).
- `tests/test_convert_9x16_layout.py`: offline tests for the face-crop and facecam-panel maths and the SRT checker.
- `resolve-video-enrichment/references/batch-project-pipeline.md` (new); additions to `vertical-9x16-conversion.md` (variants A/B, presets, checks) and `horizontal-gif-placement.md` (`short`, raster-dependent Pan/Tilt); `resolve-video-enrichment` 0.2.0 and `thai-subtitles-resolve` 0.4.0 (batch ASR notes); new rows in `docs/OPERATING-NOTES.md`.

### Run (live, Resolve Studio 21.1.0.17, folder of 2026-09-30 projects)
- FreeTalk_3, FreeTalk_4, Fallout4, Overcooked, GarticPhone, Climbing, LoL, Ib, DnD, REPO: subtitles (`Mitr Font`) and enrichment on 66 horizontal timelines, then 66 `_9x16` copies with `Mitr-short-001` and GIF `short`; protected V1/A1/subtitle ranges compared on every timeline, repeat dry runs of both presets report 0 changes, `.drp` backups exported before each project.
- Two 9:16 samples from FreeTalk_3 were rendered with burn-in and checked frame by frame.

### Scope
- ASR text is unproofed (no listening QC). Skipped for lack of usable speech: FreeTalk_3 T5, GarticPhone T1, LoL T2, Ib T3, REPO T8; REPO T1 imports only the clean part after ~30 s; FreeTalk_3 T6 and FreeTalk_4 T2 each lost one corrupted cue. LoL T3-T5 use a VP9 source that is Media Offline in Resolve, so those clips (and their verticals) were not viewed. Facecams at the frame edge (Overcooked, Ib) cannot be centred in 9:16. FreeTalk_3 T4/T5 speech is ~20 dB quieter than the other clips and was not normalized.
- `tests/test_skill_bundle.py` still fails as before v0.6.0 (core skill count 17 on disk vs 16 expected, manifest not refreshed); not changed here.

## v0.5.0

### Added
- `scripts/apply_vdo_preset.py` + `scripts/video_presets.json`: applies the Inspector Video preset "vdo" to GIF items on the V2 REACTIONS track. Resolve 21.1 has no API for Inspector > Video Presets > Load Preset and `User.db` does not expose the preset body, so the script writes captured property values (Zoom 0.42 gang, Pan 0, Tilt 32.28, others default) with `SetProperty`. Dry run by default; `--apply`, `--timeline`, `--only-originals`, `--track-name`, `--capture NAME` (captures from the clip under the playhead).
- `resolve-video-enrichment/references/horizontal-gif-placement.md`: 16:9 GIF placement, the measured Pan/Tilt-to-pixel model (X shift = Pan*fitted_w/1920, Y shift = Tilt*fitted_h/1080), GIF import timing (Resolve 25 fps normalization, 1.5s minimum), per-timeline loudness-based BGM/SFX levels.

### Updated
- Synced `resolve-video-enrichment` with the live Hermes copy (also brings the previously unsynced `katy404-channel-study.md`, `vertical-9x16-conversion.md`, `assets/` and edits to `asset-library-and-cues.md`, `automation-safety.md`, `illustration-assets.md`).

### Verified
- Live on Resolve Studio 21.1.0.17, project `tygarina_2026-09-30_FreeTalk_1`: preset applied to 63 of 64 GIF items (10 originals + 10 `[ENHANCED]` copies; 1 already matching), 0 failures, repeat dry run reports 0 changes, active timeline/playhead/page restored.
- Enrichment of the same 10 timelines (SFX/BGM/GIF added to originals and copies, protected V1/A1/subtitle ranges unchanged) was read back; a 3-timeline pixel check confirmed GIF bounding boxes before the preset was applied.

### Scope
- Not a real Load Preset: the preset values are a captured clone; re-capture if "vdo" changes. No listening QC, no render, and no per-file license check of the BGM/SFX/GIF assets was done.
- `tests/test_skill_bundle.py::test_bundle_structure_references_and_checksums` was already failing before this release (core skill count 16 vs 18 and an out-of-date file manifest); `docs/skills-manifest.json` was not refreshed here.

## v0.4.0

### Added
- `scripts/load_subtitle_preset.py`: loads a saved Subtitle track preset (Inspector > Load Preset) by script. Resolve 21.1 has no preset API, so it copies the preset bytes (`User.db` `SubtitlePresetsBA`) into each target track's `EffectFiltersBA` in `Project.db`. Dry run by default; `--apply` saves, exports a `.drp`, closes the project, snapshots `Project.db`, writes one transaction, reopens, restores timeline/playhead/page and verifies blobs and cue counts.
- `--orientation horizontal|vertical` selects timelines by resolution (Mitr Font for 16:9, Mitr-short-001 for 9:16 in the user's library).
- `tests/test_load_subtitle_preset.py`: offline tests for blob parsing/round-trip and exact-row database writes.

### Verified
- Applied `Mitr Font` to 10/10 subtitle tracks of project `tygarina_2026-09-30_FreeTalk_1` (8 changed, 2 already matching); cue counts unchanged; repeat dry run reports 0 changes. The vertical path is dry-run tested only.

## v0.2.0

### Added
- `resolve-video-enrichment/references/adjustment-focus.md`: using the user's selected Adjustment Clip as a protected template (selection readback, copy rather than move, per-timeline templates) and a 9-point per-cue VTuber framing checklist (subtitle association, new-track placement, prominence, centering, head-to-chest/hands, headroom, no crop, caption/HUD overlap, scope audit).
- `resolve-video-enrichment/references/illustration-assets.md`: planning, rights, organization, import, placement, and QC of still-image overlays.
- KT404 enrichment tooling: `scripts/enrichment_assets.py`, `scripts/enrichment_engine.py`, `scripts/run_pilot.py`, with tests, plus the design spec and implementation plans under `docs/superpowers/`.
- Working references and QC evidence under `reference/` and `scratch/`.

### Updated
- Synced `resolve-video-enrichment` with the live Hermes copy: per-timeline `timelineFrameRate` for record/source conversions, full-length BGM and 1.5–2.5s GIF holds, and new Thai trigger phrases.
- Bundle manifest checksums and counts refreshed for the release contents.

### Scope
- No claim of live Resolve verification for the new guidance; the pilot tooling's own results are recorded in `WORKLOG.md`.

## v0.1.0

First versioned release of the DaVinci Resolve editing skill bundle. The bundle version is independent of Resolve, the upstream MCP server, and individual archived skill versions.

### Added
- Thai VTuber editorial guidance: selecting self-contained highlights, truthful hooks, comic timing, and preserving the creator's personality.
- On-demand chapters for Resolve editing, Thai captions/audio/framing, YouTube packaging/feedback, and delivery/rights, with primary-source references.
- A reusable edit brief, cutlist, experiment plan, and acceptance-record template.

### Updated
- Expanded `resolve-video-enrichment` into a lean core with 11 reference chapters and one template, retaining the existing enrichment/recovery workflows.
- Clarified native subtitles versus burned-in pixels, evidence-led cue placement, measured audio versus scripting capability, source-frame timebases, and approval-gated repair/cleanup.
- Preserved the project's native Subtitle-track workflow and Thai short-form limits: three short words/about 14 Thai characters, at most 1.5 seconds, and no spaces between Thai words except appropriate Latin boundaries.
- Refreshed bundle provenance/checksums and validation evidence for the release contents.

### Fixed
- Bundle validation now accepts Git's LF/CRLF conversion for UTF-8 text while still rejecting content changes and preserving exact binary checksums; regression tests cover both newline directions and binary changes.

### Scope
- Skills, documentation, and bundle-validation release only: no MCP implementation, Resolve project, source media, or live editing behavior was changed.
- No claim of proven audience growth, channel-specific analytics, or live Resolve verification.
- Unrelated local editing plans, worklogs, scratch reports, media, and project backups are not part of this release change.
