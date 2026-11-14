---
name: vtuber-cover-batch-pipeline
description: Use when making covers for a whole Resolve project.
---

# VTuber cover batch pipeline (Resolve project -> 16:9 + 9:16 JPGs)

Recipe for building covers for every timeline of an open Resolve project in the separate agent-thumbnail repository. Design rules live in `davinci-thumbnails`, `vtuber-thumbnail-layout`, and `vtuber-thumbnail-qc`; repository-specific requirements live in that repository's `AGENTS.md`. Its referenced implementation is external and is not bundled here.

## External dependency and project rules

This bundle does not include the agent-thumbnail repository, its CLI, assets,
or scripts. Locate that repository and read its `AGENTS.md` before using this
workflow; verify every referenced file exists there. If the dependency is
unavailable, stop before mutation and report the missing prerequisite.

For Resolve operations in this repository, follow its `AGENTS.md`: inspect
Resolve through MCP first and use Python only after a documented `MCP-GAP:`
with the shared Resolve helpers. Do not use screenshots or GUI automation.

## Steps
0. Check for an existing batch first: `ls outputs/<ch>/*`, `reports/<ch>/*/delivery-manifest.json`, `projects/*/mapping.py`, `.hermes/plans/`. If the open project's timeline names already equal a mapping's `name`/`tl_short` set and every `<name>.jpg` exists, do NOT rebuild: re-run `cli.verify`, report, and move to QC/fixes. Prompt typos (folder name, character name) are resolved against what is actually on disk (`ls` the folder; character = the asset set in `1.picture`), and the assumption is stated in the report.
1. `python -m cli.doctor`; if numpy/Pillow are missing, install `requirements.txt` into the interpreter behind `python`.
2. Inventory the CURRENTLY OPEN project read-only (no save, no project switch): per timeline `name, res, frames, fps, src (File Path of first video item), srcstart (GetLeftOffset), subs [(start - tl_start, text)]` -> `reports/<ch>/<date>/timeline-inventory*.json`. Landscape = width 1920. The 9:16 twin's name already ends in `_9x16`, so the twin check is `name in portrait_names`, never `name + '_9x16'`.
3. Take timeline names from the live inventory, never from OCR of a UI screenshot (vision garbles Thai). If the user says hooks follow the Timeline name, shorten the inventory name to 1-4 words; never put ASR profanity on a cover.
4. Coverage check: distinct `src` in the inventory vs mp4s in the footage folder vs existing `projects/*/mapping.py`.
5. Generator script: dict `id -> (hook, sec, frame_tl_sec, model_no, talk, evidence, flag)`; assert counts and that every model number exists on disk; write `projects/<name>/mapping.py` + `__init__.py`; flag rows whose subtitle does not back the title.
6. Extract one frame per timeline at `src_start + frame_tl` (ffmpeg `-ss` before `-i`; sources are multi-GB, run in background) for local, read-only review. Do not upload source frames to an external provider unless the user explicitly authorizes that transfer. Make a contact sheet, review menu / inventory / black / loading / dark frames, re-sample those clips at ~6 offsets on one sheet, update `frame_tl`. A shop/inventory screen is acceptable only when it is the clip's subject; flag it.
7. Measure each source's stream-overlay layout (below), build all, `python -m cli.verify`, QC sheets (<=25 covers per sheet, landscape and Shorts separately), fix, FULL rebuild, verify, write `reports/<ch>/<date>/qc-summary.md`, `cli.package`, `python -m cli.organize` (re-syncs `_LATEST`; `cli.open` alone leaves it on the previous batch), `cli.open <channel>`.

## Delivery to a user-named folder
When the user wants `Thumbnails/` split by orientation, COPY (never move) from `outputs/<ch>/<date>/` into `<project>/Thumbnails/Horizontal_16x9` and `Vertical_9x16` (split on the `_9x16.jpg` suffix), check sizes with Pillow (1920x1080 / 1080x1920) and md5-compare against `outputs/`. After every later rebuild re-copy ONLY the changed filenames and re-run the md5 compare, otherwise the user's folder silently holds stale covers.

## Parallel QC and fix (subagents)
- Full-size QC fans out well: 3-4 read-only reviewers by game/source group (<=14 covers each, 1 group also doing the cross-set repetition check), each running `qc_previews.py` and writing `reports/<ch>/<date>/qc-full/group-X.md`. Forbid them from editing covers/mapping.
- Fixes go to ONE implementer (shared mapping + build script, so parallel fixers conflict): require a scratch backup of `outputs/<ch>/<date>` first, a FULL rebuild, `cli.verify`, `pytest`, and a `fix-report.md`. Re-verify yourself afterwards (verify, pytest, md5 vs the user's folder, open 1-2 fixed covers).
- Reviewer vision output is a hypothesis: scores come back unreliable (e.g. 100/100) and claims such as 'hair cut by a straight vertical edge' or 'avatar fragment at the edge' failed pixel checks. Measure (alpha bbox, row scans) before touching the engine; only poses wider than the canvas truly overflow.
- When a hook is not backed by any frame (no lava/zombie/diamond in the clip), flag it in the mapping rather than rewording; wording changes are the user's call.

## Pitfalls
- Full-frame VTube Studio captures (transparent 3840x2160 bust plus props) make the compositor shrink the face: crop to a bust box around the face before passing `avatar_image`. Stream frames also carry the streamer's own overlay avatar/mascots: crop the background to the game box (an exact 16:9 sub-rectangle, e.g. 960x540 of 1280x702) so the cover has one character, and for clips where the model fills the frame, take an empty-scene frame from the same stream (Armigon 2026-11-12).
- agent-thumbnail `render_thai_lines(align="center")` draws each line from x before shifting it to centre, so on Shorts (x=540) any hook wider than ~540 px is clipped at the canvas edge and comes out cut (e.g. `สิ้นใจทุก`). Import order is not the cause. Without touching that repo: wrap it to render on a canvas three widths wide at x+W and crop the middle (`scripts/scratch/armigon_shorts_202610/build_covers.py`, Armigon 9:16 covers 2026-11-12). Check every Shorts cover's hook ends inside the frame.
- Calling the agent-thumbnail engine from a script outside that repo: import `src.engine.text_thai` before anything that pulls in `PIL.ImageFont`/`ImageDraw`. Importing Pillow first gives `RuntimeWarning: libraqm is unavailable` and misplaced Thai vowels/tone marks even though `cli.doctor` reports OK (Aomi-mama flood covers, 2026-11-09).
- Aomi-mama talk covers: `composite_landscape(is_gameplay=False, blur_radius=46)` matches the approved 2026-10 look only for the background and text; its avatar is small and sticker-outlined with a flat bottom cut. Pass `avatar_image=None` and paste the model yourself: crop to the alpha bbox, scale so the top sits at y~75 and it bleeds off the bottom, no outline, soft drop shadow.
- Unblurred (sharp) talk-cover background: use `composite_landscape(is_gameplay=True, blur_radius=0)` (light dim + left text gradient, no blur). A sharp stream frame also shows the stream's own VTuber avatar; when it sits outside the area your pasted model covers you get two avatars, so take the background from a frame or day where the stream avatar sits behind your model (Aomi-mama flood covers: user asked for no blur, 2026-11-09).
- A clip can sit on one non-game screen for its whole length (stream loading loop, a text slide). Sample ~7 offsets per suspicious clip; if every offset is a text slide, take a character frame from another clip of the same stream, because slide text competes with the hook.
- `TimelineItem.GetLeftOffset()` is in TIMELINE frames, not source frames: with a 24 fps timeline on 60 fps media, source seconds = (GetLeftOffset + tl_frame) / 24. Check it once against `GetSourceStartFrame()/src_fps` (or the MCP's `source_start_seconds`) before extracting frames; dividing by the source fps lands at ~40% of the real time and still yields plausible-looking frames (Armigon 2026-10: all 48 cover backgrounds had to be redone).
- Frames to reject when sampling: inventory/menu screens, Minecraft F3 debug overlay (shows server name and coordinates; if it covers the whole range, add an absolute-source-time field such as `frame_abs` since `frame_tl` must be >= 0), end-of-mission banners that contradict the hook, Steam/File Explorer desktop shares showing username or a stray window (use per-id crop boxes), near-black dungeon frames, and calm game-start frames for fight hooks.
- Shorts avatar mouth/chin sits below y1440 on many covers; raising it needs a ~19% taller avatar that clips the sides, so treat it as a layout decision to report, not a silent engine change.
- Different OBS scenes per source: game shrunk to a corner, room panel on one side, teal bar at the bottom, stream avatar in the OTHER corner. A fixed crop leaves a small avatar next to the big one. Find the game box from the strongest column/row gradients (4:3 vs 16:9 aspect fixes the box), detect the scene from a bottom-row pixel colour, and give desktop/Steam/Explorer screen-shares per-timeline override boxes (draw a labelled coordinate grid on the raw frame and let vision read the box).
- Fit crops by cover-fit (scale to cover, centre-crop). Resizing a non-16:9 box to 16:9 stretches the game.
- `ShortsLayout.TEXT_MAX_WIDTH` defaults to 940; set 700 in the build script so centred text stays within x<=918. Verify numerically: render hook+sec on a black canvas without avatar and measure the non-black bbox for every row (Shorts x in 162..918). Check landscape text vs the avatar alpha mask (include the sticker outline from `apply_avatar_separation`); loose pixel tolerances only give false alarms.
- Vision on contact sheets is screening, not proof: low-res sheets yield wrong claims (a crop that starts below the text reads as 'text cut off', the big avatar reads as 'duplicate'). Confirm on a full-res crop that actually contains the region (measure the real text rows first) before changing anything.
- The build script rewrites `delivery-manifest.json` from the rows it built, so `--only N` truncates the manifest. Always finish with a full rebuild before verify/package.
- Red hook on red/brown footage is IMPORTANT, not CRITICAL (stroke keeps it readable); the compositor has no hook-colour parameter.
- Landscape hook wider than `TEXT_MAX_WIDTH` (850 px) at `fit_text` min size 120 is drawn centred at x=505 and runs off the LEFT edge (`ของขวัญจาก Lovely` lost its first letter). Pass the hook as two lines (`["ของขวัญจาก", "Lovely"]`) instead of shortening a name (Hoshi 2026-09-01 covers, 2026-11-14).
- Editor-added red circles/arrows in the source frame end up behind or around the pasted model and read as a second focus; pick a frame without them or blur the background.
