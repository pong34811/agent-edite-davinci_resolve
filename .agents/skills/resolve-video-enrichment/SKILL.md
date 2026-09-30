---
name: resolve-video-enrichment
description: "Use when enriching existing Resolve timelines with assets."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [davinci-resolve, video-editing, delivery]
    related_skills: [video-footage-review]
---

# Resolve Video Enrichment

Use this workflow when an existing Resolve project needs sound effects, background music, reaction GIFs/illustrations, or a finished render. The goal is a recoverable project change and a deliverable proven to contain the requested additions.

## When to Use

Use this skill for existing Resolve timelines that need external SFX, BGM, GIF/illustration overlays, media relinks after a folder move, or a verified render. Use `video-footage-review` first when the main deliverable is a cutlist or content review rather than a Resolve project change.

## Always-on rules

- Never modify, transcode, proxy, replace, or relink camera originals unless the user explicitly requests that exact operation. Resolve project edits and rendered derivatives are separate from source-media writes.
- Inspect the existing timeline before adding anything. If the requested SFX, BGM, or GIF coverage already exists, preserve it instead of stacking duplicates.
- For this user's Resolve adjustment-clip/VTuber-focus work, write and run Resolve scripting rather than driving the Edit page with Computer Use. Escalate to UI only when the user explicitly changes that preference and the required operation cannot be scripted; verify the actual rendered frame either way.
- Preserve original timeline IDs by default with `[ENHANCED]` variants. Only when the user explicitly asks to update original timelines may approved cues be promoted: export and verify a fresh `.drp` backup first, copy only active approved cues and base `AudioVolume`, and leave original video, source-audio cuts, and subtitle items intact. Keep enhanced copies through original-timeline readback; if the user explicitly requests deleting them, export a second fresh backup of the fully promoted project before cleanup and follow the unique-ID removal/readback sequence in `references/asset-coverage.md`. Never treat a pre-promotion backup, render output, or asset bin as the cleanup target.
- Activate the target timeline and verify `GetCurrentTimeline().GetUniqueId()` before using `GetIsTrackEnabled`, `AppendToTimeline`, `DeleteClips`, or state-dependent track readback; these operations can depend on which timeline is current.
- Size GIF insertions from the Media Pool item's actual `FPS` and `Frames`, not an assumed planned frame rate; compare the inserted duration with the approved variant. See `references/asset-coverage.md` for the exact promotion/readback sequence. GIFs commonly report 25 or 50 fps even in a 60 fps timeline, so a 60 fps assumption stretches or halves every hold.
- Derive overlay Pan/Tilt from the source raster, never as one constant per batch. Resolve fits each source inside the timeline canvas BEFORE Inspector Zoom, and Pan/Tilt displace that fitted raster, so the visible shift is `Pan * fitted_w / canvas_w` and `-Tilt * fitted_h / canvas_h`. One Tilt that centres a square GIF pushes a tall one off the top edge. Invert the model per item: `fit = min(canvas_w/w, canvas_h/h)`, then solve Pan/Tilt for a fixed on-canvas centre. Measure it rather than trusting the model: capture the same viewer frame with the overlay track disabled and enabled, and diff the two PNGs offline for a true bounding box; `Timeline.SetTrackEnable("video", n, state)` toggles it and the prior state must be read back before exit.
- Read the overlay transform off the project's OWN existing overlay items before choosing a corner. Do not derive a "safe" corner geometrically: gameplay captures usually have a streamer facecam/avatar composited bottom-right, and a corner that is empty in the raw game feed is not empty in the recorded frame. Copy the existing `ZoomX`/`Pan`/`Tilt` verbatim when the project already places overlays **at the same raster**. For a 16:9-to-9:16 variant, `DuplicateTimeline` first, set `useCustomSettings=1` then its timeline width/height, and read back both the duplicate's output raster and the original's unchanged raster. Inspector Pan/Tilt values from the horizontal timeline cannot be transplanted: their readback/render coordinates change when the active timeline's raster changes. Calibrate crop/position on the new timeline using Resolve-rendered frames; observed crop distance scales with Zoom, while Tilt's visible displacement may not equal its property value.
- Screen out unusably short reaction media before planning cues. A GIF library routinely holds 1-3 frame files that probe at 0.1-0.8s; they register as a valid placement and a passing readback while being invisible in playback. Filter on probed duration (>= ~0.9s) when building the candidate pool.
- Verify a music bed covers the FULL timeline before selecting it. Assert `source_duration >= timeline_duration` and fall back to a longer mix rather than appending a bed that runs out mid-clip.
- Treat loudness normalization applied after Resolve rendering as a separate export step; it does not become a normalization setting on the Resolve timeline.
- Keep dialogue and game audio legible: inspect existing clip volumes and preserve a working mix rather than blindly adding or normalizing every asset.
- Plan the mix as flat per-item levels. `SetProperty('AudioVolume', dB)` is the only working level key (`Volume`/`Gain`/`Level`/`ClipVolume` return False silently) and there is no keyframe, fade, or ducking API, so a music bed can never dip under speech — pick a bed level low enough to sit under dialogue for the whole clip instead of promising automation.
- Enrichment on a project that already contains a finished exemplar timeline is BOUNDED work under `superpowers:brainstorming`: inventory read-only, present a short in-chat design (cue sources, track map, levels, counts, what stays untouched), then STOP for an explicit yes. Reading the project is allowed before approval; appending, importing, or adding tracks is not.
- Use exact asset basenames for coverage checks before any fuzzy matching; a successful name match is not proof of a source path.
- Distinguish empty track containers from actual coverage: enumerate timeline items and exact source paths, including subtitle items. A subtitle track count alone does not prove captions exist, and a single base audio item can already contain baked-in music/effects that must be reviewed before adding more.
- Save through `ProjectManager.SaveProject()` and verify its return value. Do not assume `Project.Save()` is callable.
- After a verification loop that switches current timelines, explicitly restore and read back the captured active timeline, timecode, page, and Media Pool folder before final assertions/save; if that timeline was intentionally removed, use its surviving paired original at the same timecode. A loop can leave Resolve focused on its last inspected timeline.
- Diagnose a red `Media Offline` composite at a reaction cue from V2 first: an offline overlay can cover an online V1 source, so inspect the active overlay and render a cue frame before relinking original footage. An offline overlay does not merely vanish — it replaces the WHOLE composited frame with the red card, so a missing corner GIF still ruins the render.
- When an offline timeline item's `GetMediaPoolItem()` returns `None`, its pool entry is gone and **Relink Media cannot fix it** — there is no item to repoint. Do not promise a relink; re-import and re-place. See `references/offline-media-repair.md` for the delete/re-place/restore-transform sequence.
- Space timeline mutations out and `SaveProject()` between them: rapid `AppendToTimeline` / `AddTrack` / `DeleteTrack` sequences crash Resolve because the previous project save is still in flight. After any crash, dismiss the modal "Problem Report" window (Ignore — never send a report on the user's behalf; it blocks the scripting bridge so calls hang instead of erroring), then run `PRAGMA integrity_check` on `Project.db` and read the affected timeline back before redoing work.
- A render is not complete until Resolve reports the job complete, the output exists, and `ffprobe` confirms the required video and audio streams. For a batch, extract and visually review a known overlay frame from every output; one output's frame does not validate the batch. For caption QC, native `ExportCurrentFrameAsStill` omits subtitle overlays, so render a scratch preview with documented `ExportSubtitle=True`, `SubtitleFormat="BurnIn"`, then inspect its frames. On a measured Resolve build, `ExportCurrentFrameAsStill` returned False on the Deliver page; restore the Edit page before still capture, and restore the original page again after a render (including after save). Rendering also MOVES the playhead: capture the timecode first and restore it with `SetCurrentTimecode`, rather than asserting it never changed.

## Procedure

### State and QC boundaries

- Activate each timeline before reading its playhead: an inactive `Timeline.GetCurrentTimecode()` can return the active timeline's timecode on observed 21.1.0.17. Capture fresh state when resuming, not stale state from an earlier session.
- Serialize live Resolve calls. `OpenPage()` may return True before the page switch completes; wait and read back `GetCurrentPage()` before saving/asserting restoration. Never launch a render and export/save in parallel against one project.
- Migration success is not publication-legibility approval. Compare every cue's text and frames separately from checking contrast, frame margins, chat/face overlap and glyph rendering in burn-in previews. Report deferred user-owned style work without applying it.
- AAC renders can decode to different PCM despite unchanged timeline audio. Report unequal hashes honestly; compare timeline audio properties independently, and never treat a numerical comparison as listening QC.
- Reuse an existing preview only after a fresh content/settings audit proves that it still represents the current timeline. Otherwise rerender within authorization. A DRP ZIP/hash check is not a restore test.

### 1. Establish scope and preserve state

1. Identify the Resolve project, target timelines, asset directories, and output directory.
2. Record the current timeline and playhead timecode so the UI state can be restored.
3. Ask the open scope questions in ONE round, after the inventory and before any edit, so the design is presented once: which timelines (including whether partly-enriched ones get topped up), `[ENHANCED]` variants versus editing originals with a verified `.drp` backup, cue density per minute, and whether a render is wanted. Asking these one message at a time on a 12-timeline batch burns the user's turn budget for no extra signal.

### 2. Verify media after moves or relinks

1. List the new source directory and each requested asset directory.
2. From the live Resolve project, read each primary clip's `GetClipProperty("File Path")` and check `os.path.exists(path)`.
3. If a project still points at an old location, report the missing path and ask for explicit relink authorization before editing or rendering. Relink only when the user has requested that exact operation; changing the render output directory does not fix offline media.
4. On Windows, prefer Resolve's bundled `ResolvePython.exe` when calling `DaVinciResolveScript`, because it carries the runtime compatible with Resolve's scripting bridge. It lives in a subdirectory, not beside `Resolve.exe`: `C:/Program Files/Blackmagic Design/DaVinci Resolve/ResolvePython/ResolvePython.exe`. Scripts must `sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")` before importing. Pass the script as a full forward-slash native path — it is a native program, so a relative name plus a shell `cd` resolves against the process's own temp/cwd and fails with "can't open file".
5. Batch the whole probe into ONE script that walks every timeline, dumps the inventory to a JSON file in scratch, and restores the captured timeline/timecode/page at the end. Each `ResolvePython.exe` launch reconnects to the bridge, so per-question invocations are slow and each one leaves Resolve focused on whatever it last inspected.

### 3. Inventory current enrichment

For every target timeline, read video and audio track counts, track names, item names, start/end frames, and clip volume properties. Compare item basenames against the SFX, BGM, and illustration folders.

- Treat a timeline item name as usable coverage evidence even when `GetMediaPoolItem()` is unavailable for a source-less overlay; use track, name, and frame placement together.
- Report coverage per timeline before changing anything: existing BGM, existing SFX, existing GIF/overlay count, and missing categories.
- Import only the selected missing assets into a traceable bin; do not import an entire large sound library just to use one file.

### 4. Apply only the missing enrichment

1. Offer the recoverable-variant choice explicitly rather than assuming it; do not silently duplicate into `[ENHANCED]` when the user would rather have the originals updated behind a verified backup. If they choose variants, duplicate each changed timeline into an `[ENHANCED]` copy. If the user explicitly asks to edit the original timeline IDs, follow the promotion workflow in `references/asset-coverage.md` and keep variants until every original passes readback; if the user also explicitly asks to remove them, follow the post-promotion cleanup there. Do not replace original picture, source-audio, or subtitle tracks.
2. Follow the project's existing track convention after inspecting it: dialogue/game audio on the base audio track, SFX on the SFX track, BGM on the BGM track, and overlays on a dedicated video track such as V2.
3. Place assets at content cues or reviewed frame references. Do not use evenly spaced blind placements when timing can be read from markers, subtitles, transcript cues, or visual review. On a subtitled timeline the existing subtitle items are the highest-quality cue source available: their text gives the emotional beat and their frames are already exact.
4. Assign each emotional beat from a POOL of interchangeable assets rather than a single file per category, and enforce a minimum re-use gap (~25s). A one-file-per-emotion mapping produces the same sting four times in one short and reads as broken, not as a running joke. Order classification rules most-specific first and put broad negations ("not", "don't") LAST, or one generic pattern swallows most cues.
5. Order the batch smallest-first and prove ONE timeline end-to-end -- placement, levels, transform, and a rendered frame -- before running the rest. A transform mistake caught on the first clip costs one rerun; caught at the end it costs twelve.
6. Make the placement script idempotent by skipping any (source path, record frame) pair already on the target track. Reruns after a fix then correct properties without stacking duplicate cues. On a subtitled timeline the subtitle track IS the cue map — `GetItemListInTrack("subtitle", i)` returns every line's text with exact start/end frames, so emotion and punchline timing can be read straight off it with no extra analysis pass. See `references/asset-library-and-cues.md` for mapping cue text to an asset.
4. Set overlay transform, scale, position, and opacity so the game footage remains readable; verify on a rendered frame rather than trusting structural placement alone.
5. Leave already-correct BGM/SFX/GIF material unchanged.

### 5. Prepare a pinned render

1. Probe the live render matrix with `GetRenderFormats()`, `GetRenderCodecs(format_id)`, and `GetRenderResolutions()` before selecting a format/codec.
2. Load an explicit render preset before setting output fields. Resolve applies `SetRenderSettings` on top of inherited preset state.
3. Set the current format and codec explicitly, then set `TargetDir`, `CustomName`, `SelectAllFrames`, `ExportVideo`, `ExportAudio`, and the intended raster/frame rate.
4. If `SetRenderSettings` returns false, test the settings in small groups and remove only the rejected key; do not queue a job on an unknown inherited state.
5. Keep the output directory separate from the source directory and use a deterministic filename.
6. Add exactly the intended render job, start only that job, and read its final status.

### 6. QC and close out

1. Confirm the job status is `Complete` and the output file has non-zero size.
2. Run `ffprobe` and assert the expected container, video codec, width/height, frame rate, duration, and an audio stream.
3. Extract a frame at the new overlay's timestamp and use visual inspection to confirm the game image and overlay are both visible.
4. Save with `ProjectManager.SaveProject()`, restore the original timeline/playhead, save again if the active-state restoration changed the project, and read back the final state.
5. Report the exact output path, what changed, what was intentionally not duplicated, and any remaining deliverables such as additional renders.

See `references/asset-coverage.md` for the coverage/readback checklist, `references/asset-library-and-cues.md` for asset-library layout and cue-to-asset mapping, `references/adjustment-focus.md` for script-only adjustment-clip placement and Fusion framing, and `references/render-qc.md` for the Windows ResolvePython render and ffprobe recipe.
