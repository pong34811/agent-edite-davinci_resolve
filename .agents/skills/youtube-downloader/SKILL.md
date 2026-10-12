---
name: youtube-downloader
description: "Download YouTube videos and playlists with yt-dlp."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [youtube, yt-dlp, downloader, playlist, queue]
---

# YouTube Downloader Workflow

## When to Use

Use when the user asks to download YouTube videos or playlists using the project `downloader.py` / `youtube_downloader` package. Triggers: "โหลดคลิป", "download youtube", playlist URL, resume download.

Use the project Python CLI for downloading individual YouTube videos with yt-dlp.

## Project conventions

- Entry points: `python downloader.py` (compatibility shim) and installed `download` command.
- Code lives in `youtube_downloader/` package; CLI is `youtube_downloader.cli.main`.
- Runtime dependency: `yt-dlp`. Python 3.10+.
- Output: MP4 merge, best video up to 1080p, saved under output folder.
- Batch limit: up to 22 unique HTTP(S) YouTube URLs per run; playlist URLs expand to individual videos before limit/dedup/queue.
- Queue state: `.download_queue.json` in working directory. `--resume` resumes pending/failed items in original output folder. See `references/queue-format.md` for schema.
- Cookies: uses local `cookies.txt` if present, otherwise attempts Microsoft Edge browser cookies, then retries without browser cookies.
- Playlists: `playlist?list=...` expands to individual videos before validation, queue creation, and batch limit.
- Output dir flag: `--output-dir <path>` sets queue output_dir.

## Procedure

1. Check for existing queue before starting a new batch.
   ```bash
   cat .download_queue.json
   ```
   If pending items exist, CLI prompts to resume. For non-interactive runs use `--resume`.

2. Expand playlists before validation.
   CLI does this internally via `_expand_urls` -> `is_playlist_url` -> `resolve_playlist`. Do not pre-filter URLs; let CLI expand.

3. Start download.
   ```bash
   python downloader.py [--no-update] [--resume] [--output-dir <path>] <URL...>
   ```
   For a playlist:
   ```bash
   python downloader.py https://www.youtube.com/playlist?list=PL...
   ```

4. Resume interrupted run.
   ```bash
   python downloader.py --resume
   ```
   Queue tracks per-item status `pending` / `completed` / `failed`. Completed items are skipped on resume.

5. Monitor progress.
   ```bash
   read_file .download_queue.json
   ```
   Or tail terminal output for `[OK]` / `[FAIL]` summary.

## Pitfalls

- Existing queue blocks new batch. CLI prompts "Found unfinished download session... Resume? [Y/n]". In headless mode, clear queue or use `--resume`. Clear by removing `.download_queue.json`.
- Long downloads time out terminal tool. CLI streams progress continuously; use generous timeout or background run. If timeout occurs, re-run `--resume` — queue persists and download resumes at byte offset.
- Playlist expansion happens before validation. Validation errors after expansion are per-video, not per-playlist URL.
- Video unavailable errors are permanent for that session. yt-dlp reports `ERROR: [youtube] <id>: Video unavailable`. Queue marks item `failed`. Re-trying will fail again unless video becomes available.
- Cookies extraction warnings are normal on Windows: `ERROR: Could not copy Chrome cookie database`. Downloader falls back to Edge cookies then no cookies. Never expose cookie contents.
- Output directory is stored in queue. Changing `--output-dir` on resume is ignored; output_dir comes from queue_data. To change destination, clear queue and start fresh.
- CLI updates yt-dlp by default. Use `--no-update` to skip update check.

## User preferences

- Reply in Thai for user-facing summaries, keep code/paths/literals in English.
- Report status as `path:line` style when referencing code, not full file dumps.
- Prefer continuous execution over repeated confirmation. If queue exists, assume resume unless user cancels.
- Announce queue progress in Thai and keep per-item URLs/status in English.
- When playlist is provided, expand via CLI automatically; do not manually list video IDs.
