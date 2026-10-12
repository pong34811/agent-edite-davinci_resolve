---
name: resolve-folder-cover-batch
description: Use when making covers for a whole Resolve folder.
version: 1.0.0
author: Hermes
metadata:
  hermes:
    tags: [VTuber, Thumbnails, DaVinci, Resolve, Batch, Subagents]
---

# Resolve Folder Cover Batch

Turn a Resolve Project Manager folder (many projects, each with landscape + `_9x16` timelines) into 16:9 and 9:16 YouTube covers in the agent-thumbnail repo. Companion to the repo skills `davinci-thumbnails` (design rules), `vtuber-thumbnail-layout`, `vtuber-thumbnail-qc` (mandatory QC) and the repo `AGENTS.md` (output/handover protocol). Reply to the user in Thai.

## Working scripts (repo: `.agents/skills/davinci-thumbnails/scripts/`)

`tygarina_0930_inventory.py`, `gen_tygarina_0930_mapping.py`, `tygarina_0930_extract_frames.py`, `build_tygarina_0930_covers.py` — copy and rename module/channel for a new set (same shape as the `aomi_p2` trio).

## Procedure

1. **Environment (Windows):** use `py`, not `python` (the default interpreter may lack numpy/pytest). Run `py -m cli.doctor` and `py -m pytest tests/` first; work on a new branch; do not commit unless asked.
2. **Scope = projects, not timelines.** Names in a Project Manager screenshot are Resolve *projects*; each holds N landscape + N `_9x16` timelines. Count with `pm.GetProjectListInCurrentFolder()` and say the real total (pairs x 2) before building. Read names from the live folder, not the screenshot (OCR-like misreads, e.g. `Ib` vs `lb`).
3. **Inventory via API:** import `DaVinciResolveScript` from `C:/ProgramData/Blackmagic Design/DaVinci Resolve/Support/Developer/Scripting/Modules`. Per project: `SaveProject` -> `CloseProject` -> `LoadProject` (sleep ~1.2-1.5s each). Per timeline record name, frames, fps, resolution, source path (`GetMediaPoolItem().GetClipProperty('File Path')`), `GetLeftOffset()` as source start, subtitle cues (`GetStart()-timeline start`, text). Reload the originally open project at the end. Resolution settings come back as strings; cast before comparing. Pair landscape/portrait by name (`+ '_9x16'`) from data and verify every landscape has a twin.
4. **Split hook planning across 5 subagents** by project, balanced by pair count. Write a shared `BRIEF.md` into `reports/<channel>/<date>/` BEFORE dispatching and point every child at it (inputs, hook rules, evidence rule, output schema). Each child writes only its own `hooks_<G>.json` (hook, sec, frame_tl, talk, model, evidence, flag) and never edits mapping or git. Hooks come from subtitle cues only; ASR is often garbled, so children set `flag` (`subs doubtful` / `title-only`) instead of inventing text.
5. **Merge in the controller:** assert row count, unique names, `tl_short` exists in the inventory, no duplicate hooks, hook <= 2 lines and sec present.
6. **TDD the mapping:** add a test (count, unique names, hook/sec shape, `tl_short == name + '_9x16'`), watch it fail, generate `projects/<module>/mapping.py` with a generator script, watch it pass. Add a NEW `channels.json` entry instead of repointing an existing channel's module.
7. **Check assets before the full build:**
   - Open the avatar PNGs. Files named in a Channel Kit `CHECKLIST.md` as placeholder are coloured boxes: never ship them; substitute real renders from earlier dated folders and report the limited poses.
   - Count source-frame sizes (`Counter(Image.open(f).size ...)`). Sources can mix 1920x1080 and 1280x720; resize every frame to 1920x1080 before the fixed crop boxes, otherwise crops run off the frame and half the cover is black.
   - Full-body renders: crop to bust (`crop_bottom`) and clear faint uncoloured line-art alpha regions.
   - Wide bust crops: cap width to the target height so the avatar never reaches the hook; place the avatar by its real height, not a constant.
8. **Build 2-3 covers, then all**, then spot-check contact sheets (12 landscape + 12 Shorts) with `vision_analyze`. Confirm vision claims such as black bars numerically (frame size, mean brightness) before changing code. Warm blurred talk scenes make the red hook vanish: brightness ~0.5, blur ~28, extra dark left gradient.
9. **Verify + QC:** `py -m cli.verify --jpg-dir outputs/<channel>/<date> --manifest reports/<channel>/<date>/delivery-manifest.json`, then QC in 5 parallel subagents (~35 covers each, `QC_BRIEF.md` written first, outputs `qc_part_N.md`, read-only). Controller merges into `qc-summary.md`, fixes every CRITICAL (rebuild with `--only`), re-verifies, then package and `py -m cli.open <channel>`; final message carries the clickable `_LATEST` link from AGENTS.md.

## Pitfalls

- Write brief files before dispatching subagents; a child that starts before its brief exists wastes a round.
- Never run subagents that edit the same file in parallel; give each its own output file and merge centrally.
- Do not report counts from the screenshot as done; report reconciled counts and flagged rows (title-only / doubtful subs) in the handover.
- Missing real emotion PNGs is a known-limitation to disclose, not something to paper over with placeholders.
