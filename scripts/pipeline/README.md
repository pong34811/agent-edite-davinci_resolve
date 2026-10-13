# Batch project pipeline (Thai VTuber clips)

Scripts used to take every project in a Resolve folder from "clips only" to subtitled, enriched, and 9:16 versions
(FreeTalk_3/4, Fallout4, Overcooked, GarticPhone, Climbing, LoL, Ib, DnD, REPO, Oct 2026, Resolve Studio 21.1.0.17).
They write to the live project: use them only after the user authorizes that project, and follow
`.agents/skills/resolve-video-enrichment/references/batch-project-pipeline.md` for the order, gates and pitfalls.

## Environment
- `TMPDIR` = this folder (scripts import `rlib.py` / `rlib_apply.py` from it).
- `PW` = per-project work dir (inventory, `offs.json`, `asr/`, `plan_T*.json`, `final_T*.json`, `ids.json`).
- `SFX_DIR`, `GIF_DIR`, `BGM_DIR` = asset library folders; `FFMPEG` / `FFMPEG_DIR` = ffmpeg binary / bin folder;
  `EXPORT_DIR` = where `.drp` backups go (absolute path); `PROJECT_FOLDER` = Resolve project-manager folder name.
- Resolve scripting uses `ResolvePython`'s module path (set by `rlib.py`); ASR needs `faster-whisper`, `pythainlp`,
  `numpy` and the CUDA wheels (run with `uv run --with ...`).

## Order
| Step | Script |
|---|---|
| 1 backup + read-only inventory (`proj/<name>/inventory.json`) | `inv_proj.py <project>` |
| 2 source ranges per timeline (`offs.json`) | `offs.py <project>` |
| 3 ASR -> `asr/T<N>.srt` (Whisper large-v3, VAD, Thai tokenizer, 3-word/14-char/1.5 s cues) | `asr3.py [N ...]` |
| 4 rule check (also flags U+FFFD and repetition loops) | `check_srt.py <asr dir>` |
| 5 import SRT to an empty subtitle track, read back text/count/frames | `subimp.py N ...` |
| 6 subtitle preset | `../load_subtitle_preset.py` (use an absolute `--backup-dir`) |
| 7 `timelines.json` + second backup | `dump_timelines.py` |
| 8 cue files + library lists | `prep_cues.py` |
| 9 plans (`plan_T<N>.json`, one per timeline; empty lists allowed) | subagents or by hand |
| 10 validate plans, measure loudness, pick BGM, write `final_T<N>.json` | `prep_final.py` |
| 11 `ids.json` | `make_ids.py <work dir>` |
| 12 place BGM/SFX/GIF with protected-range check | `apply_enrichment.py N orig` |
| 13 GIF preset | `../apply_vdo_preset.py --apply` |
| 14 9:16 copies | `../convert_talk_9x16.py` (talk-only) or `../convert_game_9x16.py` (game + facecam) |
| 15 vertical presets | `../apply_vdo_preset.py --preset short --timeline <id>...`, `../load_subtitle_preset.py --orientation vertical` |

`../delete_9x16.py` removes only the `<name>_9x16` timelines of the given indexes (name + id + raster checked).
