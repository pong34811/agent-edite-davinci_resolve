# Resolve automation safety and enrichment decision rules

## Provenance and authority
- Consolidated from this skill's established enrichment workflow and the project's operating notes, not a new live API test.
- Historical observations include Studio 21.1.0.17; discover the exact running build and verify its installed API before relying on them.
- Current user scope and local `AGENTS.md`/house style override old examples, levels, render rasters, and mutation delays.
- Test fakes must mirror the native Resolve object's method owner and exact argument/result shape; check the installed API reference and use a read-only probe when ambiguous, because a convenient mock can green-test calls Resolve rejects.
- Existing detailed references remain authoritative for their narrow recipes; the guards here apply before running any example.

## Source and project boundaries
- Never alter, proxy, transcode, replace, or relink originals without approval for that exact operation.
- Read existing coverage before importing anything; a track container is not evidence of actual items.
- Base audio can already contain music/SFX; listen before stacking more.
- Keep original timeline IDs intact using approved variants; promotion to originals requires explicit approval and a fresh verified `.drp`.
- Promote only approved cues and base `AudioVolume`; preserve picture cuts, source audio ranges, and subtitle items.
- Keep enhanced copies through original readback. Deleting archives requires separate approval and a second fresh post-promotion backup.
- Do not mistake renders or asset bins for backup/cleanup targets.
- Name matching is not source verification: prefer exact asset basename, full media path, item ID, track, and frame range.
- Source-less overlays may still be inventoried by item name, track, and position, but do not claim a verified media path.

## Python CLI invocation
- From the repository root, run the exact documented `--help` or dry-run command in a subprocess test before relying on a Resolve automation CLI. Direct file execution sets `sys.path[0]` to the script directory, so imports such as `from scripts...` can fail before argument handling; either bootstrap the repository root deliberately or invoke the module with `python -m`, and test the chosen form.

## Active-state discipline
1. Capture fresh active project, timeline ID, playhead, page, folder, and track enable/lock states on entry or resume.
2. Activate the target and verify `GetCurrentTimeline().GetUniqueId()` before state-dependent reads or mutations.
3. Call `GetCurrentTimecode()` and `SetCurrentTimecode(timecode)` on the active Timeline, not Project; these methods belong to the Timeline API. Read the playhead only while that timeline is active, because inactive reads have returned the active timeline's timecode. After attempting `SetCurrentTimecode`, always read back the timecode even if the setter returns `False` or raises; treat restoration as successful only when the active Timeline reads back the exact requested value, because the return/exception alone cannot prove whether the state changed. Put these methods on fake Timeline objects in tests too, so a test double cannot hide a wrong API owner or skip the readback contract.
4. Serialize all bridge calls; never render while a second worker changes, exports, or saves the same live project.
5. Begin structural changes at roughly 1.2-second spacing; save and read back between batches.
6. A False transform setter immediately after append may already have applied: wait and reread before retrying.
7. Use `ProjectManager.SaveProject()` and check its return; do not assume `Project.Save()` exists.
8. Restore the captured active timeline/timecode/page/folder/track states and reread each at exit.
9. Wait for `GetCurrentPage()` after `OpenPage()`; a True return can precede the visible page switch.
10. If an explicitly removed active variant no longer exists, restore its surviving paired original at the captured timecode and report the substitution.

## Enrichment plan and pilot
- Existing exemplars make the task bounded: inventory, propose cue sources/counts/tracks/levels, obtain approval, then mutate.
- Ask independent scope decisions together: targets, variants versus originals, density, render deliverables.
- Import only selected missing assets into a traceable bin, not an entire library.
- Existing native subtitle text and exact frames make a useful emotional cue map; verify meaning rather than keyword-match blindly.
- Use specific emotion rules before generic negations; broad words such as "not" must not swallow every other category.
- Vary interchangeable assets; roughly 25 seconds between reuses is an editorial starting point, not a universal law.
- Skip existing `(source path, record frame)` placements on the intended track; a rerun must not duplicate cues.
- Before a batch, prove one representative timeline end to end and record its exact target ID/name, protected-item baseline, inserted item paths/record frames/ranges, property readbacks, successful save, and visual/audio QC.
- For overlay-clearance approval, inspect a rendered/viewer frame while the relevant subtitle cue is actually visible; a native still that omits subtitles or a frame with no active cue cannot prove caption clearance.
- Resolve each batch target by stable timeline ID plus expected exact name, not list index alone; baseline protected source ranges and subtitle text/frames before editing, and verify/save each target before advancing so a partial batch can stop and resume without duplication.
- Require every new cue's end inside the intended timeline; a valid start alone can append black-tail time.

## GIF and overlay timing
- Read Media Pool `FPS` and `Frames`; do not assume GIF/source FPS matches timeline FPS.
- Compare the inserted duration with the approved cue; conforming can stretch or halve a guessed hold.
- Screen out very short/degenerate GIFs before cue selection; around 0.9 seconds minimum is a usable library-filter starting point.
- Tiny or single-frame GIFs may behave like multi-second stills; verify Resolve's actual inserted range.
- Do not assume GIF alpha survives import; render-check the composite for opaque backgrounds.

## Framing and adjustment clips
- Use Resolve scripting for approved adjustment-clip/VTuber-focus changes; UI is an explicit exception, not the default route.
- Lock protected video/audio/subtitle tracks, run a pilot, and compare every underlying range afterward.
- Generator/adjustment insertion can ripple a different track even when V1 appears unchanged.
- Use numeric transforms, e.g. `0.25`, never the string `'0.25'`; `ZoomGang=True` couples ZoomX/ZoomY.
- Start from the project's own existing overlay placement, not an assumed empty corner of gameplay.
- Copy transforms directly only at the same raster; an approved aspect-ratio variant needs new calibration.
- With explicit reformat approval, duplicate first, set `useCustomSettings=1` and the intended timeline dimensions, then reread both original and duplicate rasters.
- Fit model for source `w,h` on canvas `W,H`: `fit=min(W/w,H/h)`; fitted raster is `w*fit,h*fit`.
- Historical transform model: visible X shift is `Pan*fitted_w/W`, visible Y shift is `-Tilt*fitted_h/H`; calculate per source, not one batch constant.
- The model is a calibration aid, not proof; Zoom/raster changes can alter apparent crop and displacement.
- Verify rendered head, face, hands, headroom, caption overlap, HUD and game evidence.
- When needed, capture the same viewer frame with overlay off/on and diff scratch images for a measured bounding box; restore the track state afterward.

## Audio capability boundaries
- Enumerate actual item properties; observed level key is `SetProperty('AudioVolume', dB)`.
- `Volume`, `Gain`, `Level`, and `ClipVolume` have silently failed on observed builds; do not guess equivalents.
- Resolve 21.1 exposes native `TimelineItem.SetFades`/`GetFades` for clip-edge fades; verify the installed build and read back through `GetFades()` (not generic `GetProperty("FadeIn")`). This does not provide keyframed music ducking: a flat `AudioVolume` level is not automated ducking.
- Fairlight UI may support operations the scripting bridge does not. Verify the current route rather than claiming Resolve itself cannot mix dynamically.
- Without approved/verified automation, choose a conservative flat music bed and listen through every loud phrase.
- Verify the chosen music source covers the full timeline; a short bed must not silently run out.
- Post-render loudness normalization is a separate derivative export, not a saved timeline mix setting.
- Equal/different decoded hashes are preservation evidence only. AAC can change PCM samples without an audible edit; hashes never substitute for listening.

## Offline media and crashes
- A missing V2 reaction overlay can turn the entire composite red while V1 is online; inspect overlays before diagnosing the original source.
- If `GetMediaPoolItem()` is None, no pool entry exists to relink; approved re-import/re-placement must preserve original record frame, track, ranges, and transforms.
- Follow `references/offline-media-repair.md`; do not silently replace sources as part of delivery.
- After a crash, a blocking Problem Report modal may prevent bridge calls; do not send a report on the user's behalf.
- Use a read-only integrity check and timeline readback before retrying the interrupted batch; success logs from earlier calls are not a live inventory.
- Never patch an open database. Direct SQL is a separately authorized last resort: verified export, close, database backup, exact rows, transaction, reopen, readback.

## Pinned render and per-output evidence
1. Discover `GetRenderFormats()`, `GetRenderCodecs(format_id)`, and `GetRenderResolutions()`.
2. Load a verified named preset, then explicitly set approved format/codec, raster/FPS, target directory, basename, range, video, and audio.
3. If a setter rejects a payload, isolate the rejected field under saved/restorable preset state; never queue on unexplained False.
4. On an observed build `SelectAllFrames=False`, `ReplaceExistingFilesInPlace=False`, and certain `VideoQuality` values failed; do not generalize their availability.
5. Queue only the intended job and wait for Complete; verify a nonempty output and video/audio streams with `ffprobe`.
6. Inspect a known overlay/caption frame from every output, plus critical first/last/cut frames; one output cannot validate the batch.
7. Native `ExportCurrentFrameAsStill` may omit subtitles; use the viewer or an authorized scratch burn-in render with documented `ExportSubtitle=True`, `SubtitleFormat="BurnIn"`.
8. A measured build refused still export on Deliver; switch to the verified capture page and restore the original page afterward.
9. Rendering can move the playhead; restore it explicitly with `SetCurrentTimecode` and reread it.
10. Reuse a preview only after a fresh content/settings audit proves it still represents the target.
- For frame-index extraction on newer FFmpeg, use the supported `-fps_mode passthrough` route instead of removed `-vsync` syntax.

## Exported-state comparisons
- DRP inspection may require recognized zstd decompression and UTF-16BE/UTF-16LE decoding as well as ASCII/UTF-8.
- A stored font name is not proof of the rendered font; check glyph appearance in the approved UI/render.
- Allow transform-state differences only for exact approved item IDs; native Inspector data can live in `EffectFiltersBA`.
- Verify non-transform properties independently so an approved framing change does not conceal another effect change.
- Normalize C++ XML class tags only in an in-memory parse copy; never rewrite object IDs or archives just to make a parser pass.
- DRP archive/hash validation is not a restore test; state precisely which check was performed.

## Final gate
- Every changed target must match scope and manifest, preserve protected material, pass visual/listening checks required by scope, save successfully, and leave the user's captured working state restored.
- Separate insertion success, publication legibility, listening QC, and restore-test status in the handoff.
