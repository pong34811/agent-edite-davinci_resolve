---
name: resolve-highlight-batch-production
description: Use when running 16:9->9:16 highlight batches in Resolve.
version: 0.1.0
author: Warit (pong34811), Antigravity
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [DaVinci-Resolve, Highlight, Batch, Vertical, VTuber, Descript, Subtitles]
user-invocable: true
---

# Livestream Highlight Batch Production (16:9 → Descript → 9:16 + V3 Full-Screen Zoom)

End-to-end production playbook verified on `KT404 Highlights 2026-11` (`14` streams, `56` clips, `112` timelines = `56` horizontal `16:9` + `56` vertical `9:16` @ `1080x1920 60fps`). Connects existing domain skills (`long-video-highlight-clipping`, `resolve-video-enrichment`, `vertical-video-reframing`, `resolve-mitr-subtitle-presets`, `thai-subtitles-resolve`) without duplicating their rules.

## When to Use

- Converting a batch of approved highlight timelines from raw `16:9` assemblies into finished `16:9` + `9:16` multi-track deliverables in DaVinci Resolve Studio (`21.1+`).
- Replacing `9:16` V3 `VTuber Zoom (off)` 16:9 Adjustment Clips with real full-screen portrait VTuber punch-ins while preserving `Mitr-short-001`, `V1`/`V2`/`V4`, and audio tracks.
- Coordinating multi-agent prep vs single-writer Resolve execution (see `.agents/roles/README.md`).

## Prerequisites & Safety Gates

1. Follow `AGENTS.md` start-of-task checklist (`davinci-resolve` MCP probe first; log `MCP-GAP:` when falling back to Python `scripts/resolve_common.py`).
2. Only **one Resolve writer** at a time; other agents stay read-only (`mode=ro` SQLite, offline frame/audio analysis, SRT prep).
3. Export a verified `.drp` (`scripts/backup_drp.py:export_verified`) before every batch stage, keep work reversible before promoting originals, and never modify source footage.

## 6-Stage End-to-End Pipeline

### Stage 1: Raw 16:9 Highlight Assembly
- Create project with explicit media location (`pm.CreateProject(name, media_dir)`), confirm playback FPS (`60`), and assemble `{hook}-{Game}-vdo` clips via `long-video-highlight-clipping`.
- Never call `SaveProject()` while `"Untitled Project"` is open (dialogs block Resolve IPC).

### Stage 2: 16:9 Enrichment & Peak-Safe Audio
- **Per-stream avatar geometry**: Probe every distinct live VOD (`windows.json`); group identical layouts, measure bottom letterbox rows, keep `ahoge` headroom (`5–8%`) and `window_cx <= 1 - h/2`.
- **Track layout (`16:9`)**: `V1` base clip, `V2` `VTuber Zoom` (Adjustment Clips), `V3` `REACTIONS` GIFs using Inspector preset `vdo` (`Zoom=0.42, Pan=0, Tilt=32.283865` from `scripts/video_presets.json`, NOT corner-calculated fallback slots), `A1` dialogue (`Dialogue Leveler` on + per-clip `AudioVolume`), `A2` `SFX` (`-10 dB` baseline), `A3` `BGM` (`-21 dB` baseline, fade `12/48`).
- **Peak control**: Simulate mix offline with `ffmpeg` (`ebur128=peak=true`) and apply uniform per-clip offset so true peak stays `<= -1 dBTP` (API has no Fairlight Main bus Limiter; report final LUFS gap transparently).
- Promote `<name>_edit` to `{hook}-{Game}-vdo` cleanly with one `MediaPool.DeleteTimelines([...])` call (avoids MCP `_archived` copies).

### Stage 3: Descript Thai Subtitles & Safe Track Swap
- Export audio-only AAC (`ffmpeg -vn -ac 1 -ar 16000 -> aac 96k`), batch-import to Descript (`language="auto"`), split exported SRT back per clip, and keep **only audio-evidenced Thai speech** (`house-style`: drop unverified/foreign hallucinations rather than guessing).
- Map candidate IDs to timelines **by exact timeline name**, never by list index (`swap_subs` DRT round-trips append timelines to the end and shift `timeline_ids.json` indices).
- Pre-escape `ListMgt::LmVersionTable` (`::`) before XML parsing and restore before DRT serialization.
- Never run two `swap_subs` processes concurrently.

### Stage 4: Stacked 9:16 Conversion (`1080x1920`)
- Duplicate or build `<name>_9x16` with `RASTER`: `V1` `Game Top` (`0..960`, cropped left of avatar column, anchored appropriately for RoV letterbox streams), `V2` `VTuber Bottom` (`960..1920`, anchored at raw bottom `y=1080` rather than game letterbox so avatars hanging below letterbox do not clip; adjust `TOP` per stream group so ahoge has headroom), `V3` `VTuber Zoom (off)` (`Flags=2` initially), `V4` `REACTIONS` GIFs with `short` preset (`Zoom=0.42, Pan=0, Tilt=655.261544`).

### Stage 5: Vertical Subtitle Preset (`Mitr-short-001`)
- Apply `"Mitr-short-001"` to all `_9x16` tracks via explicit user-approved offline `Project.db` patch (`Sm2TiTrack.FieldsBlob` -> `EffectFiltersBA`, verified SQLite backup first while Resolve is completely closed), leaving horizontal `16:9` tracks at `"Mitr Font"`.
- Verify style bytes read-only against `User.db` presets (`Mitr-short-001` vs `Mitr Font`), and remember `ExportCurrentFrameAsStill` omits Subtitle tracks — subtitle QC requires a burn-in render (`H.264 Master` -> `.mov`).

### Stage 6: 9:16 V3 Full-Screen VTuber Zoom (No DRT Round-Trip)
- **Why not scale V2 / Adjustment Clip `Pivot=(0.5,0)`**: Scaling a pre-cropped V2 (`CropTop>0`) crops sides severely and a `Pivot=(0.5,0), Center=(0.5,0.5)` Transform lifts the bottom edge into a half-screen black void; DRT round-trips also risk dropping `Mitr-short-001` `EffectFiltersBA`.
- **Verified method**:
  1. Read exact zoom intervals `[(r0, r1), ...]` from the untouched `16:9` original `V2` track.
  2. Switch to Edit page (`r.OpenPage("edit")`) — `Timeline.DeleteClips` deterministically fails on other pages in `21.1.0.17` — and clear old V3 Adjustment Clips with readback retries.
  3. Append raw **uncropped** (`CropTop=0`) source clip segments (`mediaType=1`, `trackIndex=3`, `recordFrame=r0`, `src_offset + r0 .. src_offset + r1`) via `mp.AppendToTimeline`.
  4. Apply per-group full-screen properties (`1080x1920`, bottom `y_src=1080` aligned at `1920`, horizontal `cx_src` centered) so **eyes stay below `Mitr-short-001` (`y ≈ 974..1090`)**, full ahoge/hair/shoulders/mic/hands stay inside `0..1080`, and zero black edges appear. Example calibrated groups on `KT404 Highlights 2026-11`: Group A (`k_full=2.50`, `40` clips) and Group B (`k_full=2.15`, `16` clips for taller framing).
  5. Assert `it.GetFusionCompCount() == 0` (catches leftover or competing writers' Fusion Transforms), compare protected tracks (`V1`, `V2`, `V4`, Audio, Subtitle, fps, range) against pre-edit baseline, and `pm.SaveProject()`.
  6. Ensure `V3` is named `"VTuber Zoom"` and enabled (`Flags=0` in `Project.db`; if `GetIsTrackEnabled` returns `False` right after `SetTrackEnable`, verify `Flags=0` offline and reload/re-verify).
  7. Verify all timelines without activating every single one in UI (avoids `~24 GB` RAM bloat and `~45s/timeline` switch lag): read `V1..V4` items/properties inactive in one pass + activate diverse per-game pilot samples for live `GetIsTrackEnabled` + burn-in `H.264 Master` render QC (`ffprobe` + inspected `normal`/`zoom`/`after` frames).

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Overlapping Resolve writers corrupt clips or leave Fusion comps (`fc=1`) | Enforce single writer turn; require `GetFusionCompCount() == 0` in idempotent target check |
| `DeleteClips` returns `False` silently | Call `r.OpenPage("edit")` before deleting and loop with readback confirmation |
| Mapping clips by `timeline_ids.json` row order breaks after DRT swaps | Key every script by stable timeline name or `GetUniqueId()` |
| `GetIsTrackEnabled("video", 3)` reads `False` on inactive timelines or pre-reload `Flags=2` | Activate timeline before calling `GetIsTrackEnabled`; clear `Flags=2 -> 0` offline + reload |
| Burn-in QC missed because stills omit subtitles | Render short `H.264 Master` `.mov` (`ExportSubtitle=True, SubtitleFormat="BurnIn"`) across zoom boundary |
