# scripts/

**Start with [`INDEX.md`](INDEX.md)** — it maps each task to a script and its scope. Throwaway scripts go in `scratch/` (gitignored); promote reusable ones here and add them to the index.

Fallback tools for work the `davinci-resolve` MCP does not cover. Order of use (AGENTS.md): MCP, then `python scripts/resolve_preflight.py --need <tool[.action]>`, then a script.

| Group | Scripts |
|---|---|
| Shared plumbing | `resolve_common.py` (`connect_resolve`, `require_resolve`, `preserved_state` — restores project, timeline, playhead, Media Pool folder, page and warns on stderr when a step cannot be restored, `api_has_method`), `backup_drp.py` (`export_verified`, `verify_drp`), `resolve_preflight.py` (`--need`, `--list-tools`, `--probe-api`) |
| Subtitles / style | `caption_lint.py` (offline Thai caption rule check), `load_subtitle_preset.py`, `apply_video_style.py`, `apply_vdo_python.py`, `apply_vdo_preset.py`, `video_presets.json` |
| Enrichment | `enrichment_engine.py`, `enrichment_assets.py`, `enrich_timelines_python.py`, `run_pilot.py`, `apply_offline_enrichment_pilot.py`, `render_enrichment_pilot.py`, `build_offline_*.py`, `review_enrichment_readonly.py`, `anomaly_sweep.py` |
| Review / contact sheets | `contact_sheet.py`, `render_review_previews.py`, `analyze_review_previews.py`, `verify_review_resume.py` |
| Focus / framing | `focus_apply_batch.py`, `focus_tune.py`, `drt_focus_track.py` (DRT track inject), `focus_frame_qc.py` (multi-frame visual & framing QC), `armigon_focus_pilot.py` (disposable Adjustment Clip pilot on a temp duplicate) |
| Project operations | `promote_drafts_to_originals.py`, `cleanup_backups.py`, `deploy_climbing_focus.py` (DRT timeline focus deployment), `cleanup_and_rename_timelines.py` (backup deletion and standard Thai naming) |
| p2 9:16 / publish | `p2_9x16_*.py` (build, convert, verify, `p2_9x16_gif_relayout.py` keeps V2 GIFs inside the game panel above the avatar seam), `p2_publish_*.py` / `p2_verify_*.py` (QC), `p2_fix_captions*.py` / `p2_apply_fixed_captions.py` (caption rules) |
| p2 render / export | `p2_render_vertical.py`, `p2_render_horizontal.py`, `p2_loudnorm_worker*.py` (two-pass loudnorm I=-14), `p2_trim_bad_gif_tail.py`, `p2_trim_tail_150s.py` (`<name>_150s` variant cut at 150 s, originals untouched), `p2_export_final.py` (final export of every p2 timeline to the Drive `vdo` folder with the `H.264 Master` preset; vertical copies get a temporary cover frame; dry-run unless `--apply`; tests in `tests/test_p2_export_final.py`) |
| Bundle upkeep | `verify_skill_bundle.py`, `refresh_skill_manifest.py` |

New scripts connect through `resolve_common` (never a private `get_resolve()`), wrap session changes in `preserved_state(resolve)`, and read back every write. Retired one-off scripts from 2026-10-09 were archived outside the repo in `Desktop/_archive-davinci-cleanup-2026-10-09/`; new throwaway scripts stay in `scratch/`, never outside the repository. Tests that need a running Resolve (`tests/test_m1_*`) are skipped unless `pytest --live` is passed.

`p2_export_final.py --prepend-cover-frames 30` adds a silent one-second cover to
30-fps vertical exports. `drt_prepend_cover.py` shifts record starts in exported
DRT files, including native subtitle and Adjustment Clip metadata; live readback
checks all source ranges, clip properties and cue text after import. Install
`zstandard` for DRT compression. The option is explicit; without it, prior batches
retain the one-frame cover overlay. `sakuyako_export_preflight.py` and
`sakuyako_export_final_audit.py` capture/compare the Sakuyako source timelines;
`sakuyako_export_qc.py` uses read-only ffmpeg analysis plus Pillow/NumPy to check
cover boundaries, silence, paired audio and produce visual review contact sheets.
