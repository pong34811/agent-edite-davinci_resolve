# Batch pipeline: many projects, each with several short clips

Use when the user authorizes the same treatment for a whole folder of Resolve projects (observed: 10 projects, 66 clips of 55-65 s, Oct 2026, Resolve Studio 21.1.0.17). Scripts live in `scripts/pipeline/` (see its README for env vars and order); converters are `scripts/convert_talk_9x16.py` and `scripts/convert_game_9x16.py`. Authorization is per project: "do the rest" from the user covers the projects they named, not other folders.

## Order per project (stop and read back after each step)
1. `inv_proj.py` saves, loads the project, exports `<project>_pre-update.drp`, writes the inventory. Look at one frame per clip (ffmpeg contact sheet at 480x270) to classify the source: talk-only (VTuber + chat, full frame), game + facecam, or collab with several facecams. Probe codecs (`ffprobe`): a VP9-in-mp4 source came up **Media Offline** in Resolve while ffmpeg decoded it; AV1 and H.264 were fine. Report offline sources; do not transcode or relink without authorization.
2. ASR (`offs.py`, `asr3.py`) on the exact source range of V1 (offset from `GetLeftOffset()`), not the whole file. Cues follow the Thai caption contract.
3. `check_srt.py` the output, then read the cue text. Remove, do not guess:
   - ASR **hallucination loops** (one phrase repeated for 20+ s on lobby/ambient noise, e.g. "เฮ้ยเฮ้ยเฮ้ย" x37): import only the clean later part and say so. A cue with a repeated tail ("หาๆๆๆๆๆ") is shortened to the contract limit.
   - U+FFFD cues: re-transcribe the window once; if the real words cannot be recovered, delete the cue after import (`Timeline.DeleteClips([item], False)` on the subtitle item works) and report it. Never leave a replacement glyph on screen.
   - Clips with no speech get no subtitle track and a BGM-only plan; sparse clips (2-5 cues) get 0-2 SFX/GIFs.
4. `subimp.py` (empty track, bare `{"mediaPoolItem": item}`), then `load_subtitle_preset.py --orientation horizontal --all-timelines --backup-dir <ABSOLUTE path>`. A relative `--backup-dir` failed the `.drp` export ("nothing written"). `CloseProject failed; nothing written` has happened: Resolve then restarted to an Untitled project; reopen the project, verify nothing changed, run again (it succeeded on the second attempt each time).
5. `dump_timelines.py` (second backup `<project>_pre-enrich.drp`), `prep_cues.py`, plans, `prep_final.py`, `make_ids.py`, `apply_enrichment.py N orig` per timeline, then the GIF preset (`apply_vdo_preset.py --apply`). Plans: subagents write `plan_T<N>.json` from the cue files (one agent per 2-4 timelines); `prep_final.py` validates in code (frames = real cue starts, SFX >= 420 and GIF >= 600 frames apart, first/last bounds, no repeats, files exist) and sets gains from measured speech loudness. Empty plans are valid; the validator must guard empty lists.
6. Vertical copies (`references/vertical-9x16-conversion.md`, variants A/B), GIF preset `short`, subtitle preset `Mitr-short-001`.
7. Read back every timeline (resolution, subtitle count, GIF/SFX/BGM counts), compare protected V1/A1/subtitle ranges, `SaveProject()`, restore the user's project, timeline, timecode and page.

## Resolve behaviours that cost time
- `TimelineItem.GetProperty/SetProperty` for Pan/Tilt are scaled by the **active timeline's raster**: reading a 1080p timeline's Pan while a 1080x1920 timeline is current returns 1.78x values, and a write lands differently. Activate the target timeline before reading or writing transforms, and compare readings only inside one timeline.
- Property setters can return False if called too fast; space writes ~0.45 s, structural edits ~1.2 s, and read back each value.
- After ~8-10 duplicate-and-edit cycles Resolve may stop responding: create vertical copies in batches of 3-4 with a 20-30 s pause, verify each batch.
- `DuplicateTimeline` appends the copy; to remove a half-built copy use `MediaPool.DeleteTimelines([copy])` after activating the original, only for the exact `<name>_9x16` + id + 1920 raster (`scripts/delete_9x16.py`).
- A facecam track appended with `endFrame = offset + duration - 1` came back one frame short; use `offset + duration` and compare start/end with V1.
- Burned-in subtitles need `SetRenderSettings({"ExportSubtitle": True, "SubtitleFormat": "BurnIn"})`; without it a render and a still export show no subtitle. Render QC changes project render settings (target dir, name, size): turn `ExportSubtitle` off again, delete your jobs from the queue, and tell the user the other settings changed. Preview files were large `.mov` from the user's H.264 preset.
- Source frames may be 1280x720; Resolve fits them to the 1920x1080 timeline, so all layout maths use timeline coordinates (scale ffmpeg frames to 1920x1080 before measuring).

## Limits to state in the final report
ASR text is unproofed and sometimes wrong; subtitle styles/positions come from the user's presets; renders were checked on a sample only; offline sources and skipped no-speech clips are listed per project.
