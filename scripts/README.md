# scripts/

Fallback tools for work the `davinci-resolve` MCP does not cover. Order of use (AGENTS.md): MCP, then `python scripts/resolve_preflight.py --need <tool[.action]>`, then a script.

| Group | Scripts |
|---|---|
| Shared plumbing | `resolve_common.py` (`connect_resolve`, `require_resolve`, `preserved_state` — restores project, timeline, playhead, Media Pool folder, page and warns on stderr when a step cannot be restored, `api_has_method`), `backup_drp.py` (`export_verified`, `verify_drp`), `resolve_preflight.py` (`--need`, `--list-tools`, `--probe-api`) |
| Subtitles / style | `caption_lint.py` (offline Thai caption rule check), `load_subtitle_preset.py`, `apply_video_style.py`, `apply_vdo_python.py`, `apply_vdo_preset.py`, `video_presets.json` |
| Enrichment | `enrichment_engine.py`, `enrichment_assets.py`, `enrich_timelines_python.py`, `run_pilot.py`, `apply_offline_enrichment_pilot.py`, `render_enrichment_pilot.py`, `build_offline_*.py`, `review_enrichment_readonly.py`, `anomaly_sweep.py` |
| Review / contact sheets | `contact_sheet.py`, `render_review_previews.py`, `analyze_review_previews.py`, `verify_review_resume.py` |
| Focus / framing | `focus_apply_batch.py`, `focus_tune.py` (run from the repo root as `python -m scripts.focus_apply_batch`, or directly) |
| Project operations | `promote_drafts_to_originals.py`, `cleanup_backups.py` (dry-run unless `--confirm`; never deletes rollback archives) |
| Bundle upkeep | `verify_skill_bundle.py`, `refresh_skill_manifest.py` |

New scripts connect through `resolve_common` (never a private `get_resolve()`), wrap session changes in `preserved_state(resolve)`, and read back every write. Retired one-off scripts live outside the repo in `Desktop/_archive-davinci-cleanup-2026-10-09/` (`scripts/` and `scripts-review-2026-10-09/`). Tests that need a running Resolve (`tests/test_m1_*`) are skipped unless `pytest --live` is passed.
