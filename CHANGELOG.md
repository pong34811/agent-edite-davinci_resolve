# Changelog

## v0.6.0

### Added
- `scripts/apply_video_style.py`: capture and apply exposed video properties from an approved reference clip to explicit timeline item IDs. Dry-run is the default; writes require a verified DRP backup and include property readback, rollback, protected timeline comparisons, and UI-state restoration. It is not a native named Video Preset loader and makes no Resolve database writes.
- Offline orchestration coverage for project/timeline ID refusal, invalid backup refusal, and successful save/readback/restoration. `docs/guides/video-style-script.md` and a sanitized example at `presets/video/approved-gif-style.json` contain no live project clip ID or filename.
- `.agents/skills/thai-subtitles-resolve/references/srt-insertion-and-presets.md` with SRT insertion, exact saved-preset discovery, database-write boundaries, and post-load verification.

### Updated
- `thai-subtitles-resolve` v0.4.0 now documents reuse of Media Pool SRT items, exact cue/frame readback, failure-safe append recovery, and approved saved font presets.
- House style, `resolve-edit`, `resolve-video-enrichment`, operating notes, and README clarify approved preset use and distinguish native APIs from database workarounds.

### Validation
- `python -m unittest discover -s tests -p test_apply_video_style.py -v` — 10 tests passed.
- The helper was live-verified against explicitly approved GIF items during development; this release preparation did not connect to or modify a Resolve project.

### Scope
- Editing-skill bundle and helper documentation only. No source media, Resolve project, or database was changed for this release. Caption/GIF visual review and listening QC remain separate checks.

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
