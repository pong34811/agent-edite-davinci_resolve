---
name: resolve-project-media-storage
description: Store edit assets beside footage to prevent Media Offline.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [Resolve, Media, Relink, Assets]
---

# Keep Edit Assets Beside the Footage

Every file a DaVinci Resolve timeline uses — illustrations/images, GIFs, BGM, SFX,
subtitle files, generated overlays — lives in the SAME folder tree as the footage
being edited, so the project never shows **Media Offline** after a cleanup or on
another machine. This skill decides where an asset goes before import and
consolidates an existing project. It does not edit timelines, transcode footage,
or delete originals.

Rule the user set (2026-11-22): "ใส่รูปภาพ bgm sfx ไฟล์งานที่ใช้งาน ให้เก็บไว้ที่เดียวกับ
footage" — goal: ไฟล์งานไม่หายจากโปรเจกต์ DaVinci.

## When to Use

- Adding images, GIFs, BGM, SFX, HyperFrames/emoji overlays or SRTs to a timeline
- "ไฟล์หาย", "Media Offline", "เปิดเครื่องอื่นแล้วไฟล์หาย"
- "เก็บไฟล์ไว้ที่เดียวกับฟุตเทจ", "ย้ายไฟล์ไป Google Drive"
- Before handing off or finishing any editing job in this repo

## Prerequisites

- Resolve Studio running with external scripting = Local; `davinci-resolve` MCP attached.
- Footage on a synced drive (this user: `G:/My Drive/Projects/<channel>/<job>/`).
- Repo tools: `scripts/consolidate_project_media.py`, `scripts/backup_drp.py`,
  `scripts/resolve_common.py`.

## How to Run

Audit, then consolidate an existing project — invoke through the `terminal` tool
from the repo root (dry-run first, then apply):

```
py -3.13 scripts/consolidate_project_media.py --dest "<footage folder>"
py -3.13 scripts/consolidate_project_media.py --dest "<footage folder>" --apply
```

`--apply` exports a verified `.drp`, copies files into kind subfolders, relinks
with `MediaPool.RelinkClips`, reads back every File Path and saves. Originals are
never deleted.

## Quick Reference

- Footage folder = folder of the V1 source clip (`GetClipProperty('File Path')`).
- Subfolders the script uses: `illustrations/` (png jpg webp mov psd), `gif/`,
  `bgm/`, `sfx/` (audio; bin/path containing bgm/music → bgm), `subtitles/`
  (srt vtt ass), `footage/`, `other/`.
- Relink one batch via MCP: `media_pool safe_relink {clip_ids, folder_path, dry_run}`.
- Allowed to stay outside: nothing that lives only on this machine — never the repo
  `.hermes/`, `scripts/scratch/`, Desktop, `%TEMP%` or Hermes scratch.

## Procedure

1. **Find the footage folder** before adding anything: read the V1 clip's File
   Path (MCP `timeline probe_timeline_structure` or `media_pool_item
   get_clip_property`). Confirm it is on the synced drive.
2. **New asset → write it there first.** Generated or downloaded files (emoji
   MOV, HyperFrames render, chosen BGM/SFX/GIF copy) go straight to
   `<footage folder>/<kind>/`, then `media_pool safe_import_media` from that path.
   Never import from the repo, Desktop or a temp folder "for now".
3. **Audit the project**: list every Media Pool File Path grouped by folder
   (`execute_code`/`terminal` with `resolve_common`), and flag any path that is not
   under the synced drive or does not exist.
4. **Consolidate**: run the dry-run, read the COPY/SKIP/MISSING lines, then
   `--apply`. A `MISSING SOURCE` blocks apply — recover or rebuild that file first
   (see `resolve-offline-media-repair`).
5. **Small batch alternative** (MCP-first): copy with SHA-256 check into
   `<footage folder>/<kind>/`, `.drp` backup via `project_manager export_project`,
   then `media_pool safe_relink` with `dry_run: true`, then `false`.
6. **Verify** (below), save, then remove only the duplicate local copies you made,
   after hashes match and nothing references them.
7. Record the asset location in `docs/channels/<channel>.md`.

## Pitfalls

- Files kept in the repo `.hermes/projects/...` or under a Desktop checkout went
  offline once the folder moved (Aomi-mama 2026-10: 17 emoji MOVs lost, rebuilt
  from Noto Emoji 3D and moved to `G:/My Drive/Projects/Aomi-mama/2026-10/illustrations/`).
- Shared libraries (`G:/My Drive/Projects/1.1 bgm`, `2.1_sfx`, `3.gif`) are online
  on Drive, but the user's rule is one tree per job: consolidate copies them beside
  the footage; never move or delete the shared originals.
- Stale SRT pool items pointing at deleted scratch paths show as missing on every
  machine; ask before deleting them from the pool.
- `safe_relink` matches by file name inside `folder_path`; keep the original names.
- A relink "success" is not proof Resolve decodes the file — render a short
  burn-in range over the relinked clip and inspect the frame with `vision_analyze`.
- The other machine must mount Drive at the same letter (`G:\My Drive`), or paths
  break again.

## Verification

Every Media Pool File Path exists and sits under the footage folder (or the agreed
synced tree), and every timeline video/audio item resolves to an existing file:

```
py -3.13 scripts/consolidate_project_media.py --dest "<footage folder>"
```

expects `dry-run: 0 to copy, N skipped, 0 missing`.
