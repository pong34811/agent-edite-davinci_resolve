# Verification, safety, and the batch pipeline

Source: `AGENTS.md`, `docs/guides/native-drt-authoring.md` (verification
checklist), `docs/guides/headless-edit-loop.md`, `scripts/README.md` references,
`.agents/skills/resolve-*` safety sections.

## The one rule that covers everything

**Every silent failure in this domain returns success.** A call that reports
`success` can have appended nothing, re-imported the wrong timeline, or produced a
timeline that reads back perfectly and renders black. So: **verify structure, not
return values** — read item counts and each item's `GetLeftOffset()` back and
compare against what you intended.

## The verification ladder

| Level | Check | Catches |
|---|---|---|
| 1. Return value | `_operation.status` | almost nothing — see above |
| 2. Structure | item count, `GetLeftOffset()`, `detect_gaps_overlaps`, `source_range_report` | gaps, overlaps, wrong frames kept |
| 3. Frames | viewer captures / marker contact sheets | wrong content, black, flash |
| 4. Render | frame luma at cut boundaries, dissolve midpoints, retime windows; RMS per audio window | media without pool descriptors (black), silent audio, inert transitions |

- `_operation.verification.status` = `contradiction` is the one to **stop** on:
  Resolve reported success and the readback disagrees. `unverified` means no
  evidence was reported, not that it was checked and found clean.
- **Render is truth** for anything authored offline. Structural readback cannot
  detect a black or silent timeline.
- For renders generally: require `Complete` status, a nonempty output, `ffprobe`
  video/audio verification, and visual QC. **Native still export can omit
  subtitles** — use viewer captures or an authorized burn-in preview for caption
  legibility.

## Safety and recoverability

- **Never overwrite source media.** Edit operations reference existing Media Pool
  items; they never transcode, render, proxy, relink, or create derivatives.
  `ffprobe`/`ffmpeg` are permitted for read-only analysis and render QC only.
- **Export a verified `.drp` backup before batch operations**
  (`scripts/backup_drp.py` → `export_verified`).
- **Work in recoverable variants** (`_focus_variant`, `_bak`, `_150s`) and only
  update original master timelines on explicit user instruction.
- **Preserve state around mutations** — wrap Resolve Python in
  `preserved_state(resolve)`; at the end of every session put Resolve back on the
  project and folder the user was working in (root → owner folder → year folder →
  `LoadProject`) and **report which project you left open**. An ad-hoc read-only
  audit script that calls `LoadProject` still moves the user's session.
- **Sleep ~1.2-1.3 s between structural mutations** — rapid operations crash
  Resolve.
- **Never call `SaveProject()` on the never-saved `Untitled Project`** — it blocks
  the application. Teardown order is `CloseProject` → `LoadProject(named)` →
  `DeleteProject`.
- Treat generated probe reports and analysis artifacts as local scratch, never
  committed files.

## Tool selection: MCP first, scripting second (mandatory)

1. Check the `davinci-resolve` MCP catalog and its tool schema.
2. Execute via MCP when a tool/action covers the task — probe read-only first.
3. Fall back to the Resolve Python scripting API **only** when no matching MCP
   tool exists, or an MCP call fails on a recorded build limitation.
4. State the mandatory line before writing any script:
   `MCP-GAP: <tool/action checked> -> <result/reason for script fallback>`
5. Scripts live in `scripts/`, connect through
   `scripts/resolve_common.py:connect_resolve`, wrap mutations in
   `preserved_state(resolve)`, and read back and verify every modification.
6. If neither path supports the feature, mark the task `BLOCKED` with evidence.
   **Never invent method names.**

**Strictly prohibited:** screenshots/GUI automation, keystroke macros, browser
automation, non-Resolve editors. The only exceptions that are not Resolve control:
`ffprobe`/`ffmpeg` for read-only media analysis and render QC, and last-resort
offline SQLite inspection/patching when Resolve is fully closed and a verified
`.drp` backup exists.

## The DRT transfer pattern for safe track injection

Direct API insertion (`InsertGeneratorIntoTimeline`) can misplace clips across
track indices on complex timelines. The verified pattern:

1. Export the timeline to DRT:
   `timeline.Export(drt_path, resolve.EXPORT_DRT, resolve.EXPORT_NONE)`
2. Parse and inject the target track/clips with `scripts/drt_focus_track.py`
3. Import back: `media_pool.ImportTimelineFromFile(drt_path)`
4. Read back and verify all original tracks against the baseline

## Batch pipeline scripts (p2) — when the edit is production work

- `scripts/p2_9x16_*.py` — build/convert/verify vertical timelines;
  `p2_9x16_gif_relayout.py` keeps V2 GIFs inside the game panel above the avatar
  seam (V3 draws over V2).
- `scripts/p2_trim_tail_150s.py` — `<name>_150s` variant cut at 150 s.
- `scripts/p2_export_final.py` — final export of every p2 timeline to the Drive
  `vdo` folder with the `H.264 Master` preset (preset loaded per job, vertical gets
  a temporary cover frame, dry-run unless `--apply`).
- `scripts/drt_focus_track.py`, `scripts/focus_frame_qc.py`,
  `scripts/deploy_climbing_focus.py`, `scripts/cleanup_and_rename_timelines.py` —
  focus-track injection, framing QC, and safe timeline cleanup/renaming.
- Subtitle/enrichment: `asr_words_th.py`, `build_dynamic_srt.py`,
  `verify_srt_on_timeline.py`, `caption_lint.py`, `apply_vtuber_zoom.py`,
  `apply_enrichment_d22.py`, `apply_vdo_preset.py`.

## Interrupting a batch safely

Kill the process, then clean up **before** re-running: read the queue, delete only
job ids you created, delete every `__cover_tmp` timeline you made, delete the
partial outputs already written, `SaveProject()`, and confirm
`IsRenderingInProgress()` is False. Never re-run on top of your own leftover jobs
and copies — the resumed run's "skipping existing outputs" count then hides the
files written with the bad settings.

Kill by **PID, never by command-line match**: a filter like
`CommandLine -match '<script>.py'` also matches the wrapper shell running the
filter, so the kill command kills itself and you cannot tell whether the target
died. Resolve the PIDs first, print them, then stop those exact ids in a second
call. Kill the parent python before its children (spawned ffprobe processes
respawn until their parent dies).
