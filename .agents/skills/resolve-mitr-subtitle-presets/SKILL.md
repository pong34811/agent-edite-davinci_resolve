---
name: resolve-mitr-subtitle-presets
description: "Apply Mitr subtitle presets to 16:9 and 9:16 Resolve tracks."
version: 0.1.0
author: Hermes
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [DaVinci-Resolve, Subtitles, Fonts, Thai, Presets]
---

# Mitr Subtitle Presets for Horizontal and Vertical Timelines

Loads the user's saved Subtitle *track* presets (Inspector > Load Preset) onto
DaVinci Resolve subtitle tracks by script, picking the exact approved preset by timeline
orientation: landscape 16:9 vs portrait 9:16 Shorts. It does NOT create cues,
retime captions, or invent styles. It only copies an existing preset. Uses the
stdlib plus Resolve's own scripting bridge. Resolve has no preset API, so the
write goes into the disk-database `Project.db` while the project is closed.

## When to Use

- "load preset Mitr Font ให้ทุก timeline", "ใส่ฟอนต์ Mitr ให้ซับ"
- "จัดการ font mitr แนวนอน / แนวตั้ง", "ซับ shorts ใช้ Mitr-short-001"
- Batch-applying one subtitle style across many timelines without clicking
  Inspector > Load Preset per track.

## Prerequisites

- Windows, Resolve Studio running (verified on 21.1.0.17), project open, on a
  **Disk** database (`pm.GetCurrentDatabase()['DbType'] == 'Disk'`).
- Python 3.10+ (`python`). Python 3.14 `compression.zstd` (or `pip install
  zstandard`) is optional and only used for the `--list` font summary.
- The preset must already be saved in Resolve (Inspector > Save Track as Preset).
- Scripting paths used: `C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting`
  and `C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll`.
- For any future write-enabled implementation: a verified `.drp` backup and
  explicit user approval after showing the dry-run plan and exact affected
  timeline/track list. Merely naming a preset or timeline is not authorization.
- Resolve must be fully closed before any offline `Project.db` patch. If the
  helper cannot guarantee that condition, do not run `--apply`; use a supported
  Resolve action or stop as `BLOCKED` and report the limitation.

## How to Run

Use only the repository helper `scripts/load_subtitle_preset.py`, after checking
the Resolve MCP catalog and recording an `MCP-GAP:` if it lacks preset loading.
The nested skill copy is a compatibility wrapper, not an independent database
writer. Always dry-run first and present the exact plan. `--apply` remains
blocked unless the approved backup and fully-closed Resolve requirements above
are satisfied.

## Quick Reference

Preset mapping in the user's library (verified on project KT404_2026-09-29:
30 tracks of 1920x1080 used Mitr Font, 30 tracks of 1080x1920 `_9x16` used
Mitr-short-001):

| Orientation | Raster | Preset | Font in preset |
|---|---|---|---|
| horizontal (แนวนอน) | 1920x1080 | `Mitr Font` | Mitr SemiBold, default position |
| vertical (แนวตั้ง) | 1080x1920 | `Mitr-short-001` | Mitr Bold + custom position |
| (unused/basic) | any | `mitr`, `mitr-short` | Mitr Regular, identical bytes |

```
python load_subtitle_preset.py --list
python load_subtitle_preset.py --preset "Mitr Font" --orientation horizontal
python load_subtitle_preset.py --preset "Mitr-short-001" --orientation vertical
python load_subtitle_preset.py --preset "Mitr Font" --all-timelines
python load_subtitle_preset.py --preset "Mitr Font" --timeline "TL name" --timeline "TL 2"
```

`--apply` currently exits before writing any database bytes. Use this helper
for read-only discovery and dry-run planning only.

Other flags: `--user` (default guest), `--project-db`, `--user-db` overrides.
No target flag = current timeline only.

## Procedure

1. `--list` and confirm the exact preset name. Preset names are case- and
   punctuation-sensitive. If the user's requested name differs from the saved
   name (for example `Mitr-Font` vs `Mitr Font`), do not silently substitute;
   show both names and ask which exact preset they intend.
2. Dry run per orientation. Output lists every subtitle track and
   `already_matches`, then `N of M subtitle track(s) would change.`
   A mixed project (16:9 + `_9x16` copies) needs **two** runs: horizontal with
   `Mitr Font`, vertical with `Mitr-short-001`. Never `--all-timelines` one
   preset over a mixed project.
3. Treat `--apply` as unavailable: it deliberately stops before writing because
   it cannot verify that Resolve fully exited. A future writer must be updated
   and reviewed to enforce that condition, and must create and verify a durable
   `.drp` backup, save/close the project, confirm no Resolve process holds the
   database, and verify every changed row. Never bypass this gate by calling
   the nested copy or a direct SQLite command.
4. Report `verified_tracks`, `changed_tracks`, cue counts, backup dir; ask the
   user to eyeball one horizontal and one vertical timeline in the viewer.

How it works (for debugging): presets live in
`<library>\Resolve Projects\Users\guest\User.db`, `SM_User.FieldsBlob`, key
`SubtitlePresetsBA`. A styled track stores the identical bytes under
`EffectFiltersBA` in `Sm2TiTrack.FieldsBlob`. Library path comes from
`%APPDATA%\Blackmagic Design\DaVinci Resolve\Preferences\dblist.conf` (drive
colon stripped, e.g. `G\My Drive\...`). Orientation comes from
`Timeline.GetSetting("timelineResolutionWidth"/"timelineResolutionHeight")`.

## Pitfalls

- `No target timeline has a subtitle track (orientation=vertical)` is normal
  for a project with only 16:9 timelines. It's not a bug.
- `DB has N subtitle tracks but Resolve reports M`: unsaved new tracks. Save in
  Resolve and rerun.
- A track added by SRT import has no `EffectFiltersBA` (unstyled stub). The
  script appends the key, which reproduces Resolve's own bytes exactly.
- Re-importing an SRT (DeleteTrack/AddTrack) resets the track style. Reapply
  the preset afterwards.
- Projects sit in nested folders (`Projects\Tygarina\2026-09-30\<name>`). The
  script globs recursively and requires the DB to contain the target timeline IDs
  (`GetUniqueId()` == `Sm2Timeline_id`).
- Never write while the project is open; the script refuses if Save/Export/Close
  fails. Don't hand-edit `pointSize` to change Inspector Size (8.14286 is the
  descriptor, not the UI size). Save a new preset in the UI instead.
- Running with a preset that already matches is a no-op (`Nothing to do`).
- Any future approved writer must snapshot each target timeline (cue text and frames, video/audio items, track states, range) and diff after. The current helper is dry-run only and has no live-write verification.
- This agent cannot reliably read Inspector/viewer screenshots and viewer capture is prohibited by the repo rules; ask the user to eyeball one vertical timeline at a stated cue timecode.
- In this repo the SQLite write needs explicit approval after the dry-run plan is shown (house-style); naming the preset alone is not enough.

## Verification

For the current helper, preserve the dry-run report and state that the preset
was not applied. A later implementation must define and verify its own
post-write acceptance checks before enabling database mutation.
