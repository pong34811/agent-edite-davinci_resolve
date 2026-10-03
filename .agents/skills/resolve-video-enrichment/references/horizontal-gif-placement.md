# Horizontal (16:9) GIF placement: Pan/Tilt model and the "vdo" preset

How to place reaction GIFs on a 1920x1080 timeline's V2 REACTIONS track, and how to reuse the user's Inspector Video preset ("vdo") from a script. Observed on Resolve Studio 21.1.0.17; re-verify on another build.

## 1. Inspector Video presets cannot be loaded by script
- `Project.SetPreset` / `GetPresetList` are project-settings presets, not Inspector > Video Presets > Load Preset. No TimelineItem method loads an Inspector preset.
- The preset body was not readable from `User.db` (`SM_User.FieldsBlob` has key `VideoPresetsBA`, but no "vdo" name was visible), unlike subtitle presets (`SubtitlePresetsBA`, see `scripts/load_subtitle_preset.py` in the project repo). Do not patch a DB for this.
- Working route: a preset is the set of Inspector values it copies. Capture them from a clip the user has already loaded the preset onto (`TimelineItem.GetProperty()` with no args returns a dict), store them in JSON, and write them with `SetProperty` (floats, never strings). Result is identical for stored transform/composite fields.
- Project-repo implementation: `scripts/apply_vdo_preset.py` + `scripts/video_presets.json`. Dry run by default; `--apply`, `--timeline`, `--only-originals`, `--track-name`, and `--capture NAME` (reads the clip under the playhead via `Timeline.GetCurrentVideoItem()`).
- Captured `vdo` (user-chosen layout): ZoomX/ZoomY 0.42 (gang), Pan 0, Tilt 32.28386473655701, rotation/anchor/pitch/yaw/flip/crop 0, Opacity 100, CompositeMode 0. It sits mid-frame and covers part of the avatar; the user confirmed this is intended. Do not "fix" it by moving clips off the face.
- Tell the user it is a captured-value clone, not a real Load Preset. If their preset changes, re-run `--capture vdo` on a clip that holds it, then `--apply`.

## 2. Pan/Tilt units depend on the fitted clip size (measured by pixel diff)
For a clip with Resolution rw x rh on a 1920x1080 canvas:
- fit = min(1920/rw, 1080/rh); fitted raster fw, fh = rw*fit, rh*fit; on-screen size = fw*Zoom, fh*Zoom.
- On-screen X shift (px) = Pan * fw / 1920. On-screen Y shift (px, + is up) = Tilt * fh / 1080.
- A landscape clip that fills the width has factor 1, which hides this. A portrait clip (e.g. 378x640, factor 0.33) lands in the wrong place if you pass raw pixel offsets.
- To place a box with top-left margin m: pan = (-960 + m + ow/2) * 1920/fw, tilt = (540 - m - oh/2) * 1080/fh, with ow, oh the on-screen size.
- Take rw x rh from `MediaPoolItem.GetClipProperty("Resolution")`, not ffprobe (a GIF's logical size can differ, e.g. 195x195 in Resolve vs 112x112 in ffprobe).
- Measure real placement: export a still with the V2 track enabled and disabled (`Timeline.SetTrackEnable`, `Project.ExportCurrentFrameAsStill`), diff, take the bounding box (alpha GIFs report only the visible content). Restore the track enable state.
- Preset values are copied raw, so Pan/Tilt in a preset do not rescale per clip aspect.

## 3. GIF import facts that broke earlier plans
- Resolve normalizes imported GIFs to 25 fps (`GetClipProperty("FPS")`, `"Frames"`); ffprobe fps/frames differ. Plan holds from Resolve's values: n = min(Frames, round(2.0 * FPS)); append with endFrame n-1; record length lands at about 1.75-1.95 s on a 60 fps timeline.
- Screen out GIFs under 1.5 s or under about 8 frames (single-frame stickers, 0.1-0.2 s loops); a hold must stay within 1.5-2.5 s. In one 158-file library only 80 qualified. Replace by same Thai emotion prefix (`ขำ`, `ตกใจ`, `งง`, ...).
- Append form that worked: `{"mediaPoolItem": c, "startFrame": 0, "endFrame": n-1, "mediaType": 1, "trackIndex": 2, "recordFrame": f}`, 0.5 s apart; add V2 first with `AddTrack("video")` and `SetTrackName`.

## 4. Related enrichment numbers measured in the same job
- Audio source frames use the timeline rate (audio clips report FPS 60 on a 60 fps timeline): SFX endFrame = int(min(dur, 3.0)*60)-1; BGM endFrame = timeline length.
- Source dialogue loudness varied from about -10 to -29.5 LUFS across timelines. Measure speech from the source file (offset from `GetLeftOffset()/fps`) with ffmpeg `ebur128`, and use `loudnorm=print_format=json` (`input_i`) for short SFX where `ebur128` returns -70. Set per-timeline AudioVolume: BGM about speech-20 LU, SFX about speech-3 LU, cap SFX at 0 dB.
- Lock V1/A1/subtitle tracks while appending, then restore the previous lock states; compare V1/A1/subtitle ranges before and after each timeline.
- `DuplicateTimeline(name)` appends the copy at the end of the timeline list, so indices 1..N stay the originals; still look targets up by `GetUniqueId()`.

## Procedure for a new project
1. Read-only inventory of timelines, tracks and subtitles; export a `.drp` before any write.
2. Plan cues (subagents may plan from per-timeline cue text files; validate their JSON in code: files exist, spacing, counts, no duplicates).
3. Build `[ENHANCED]` copies first, then promote the same plan to the originals only on explicit request.
4. Apply GIF layout (preset clone or the Pan/Tilt model), save, read back every item, then restore the active timeline, timecode and page.

## Pitfalls
- A set Pan that reads back correctly can still render elsewhere; verify pixels, not only `GetProperty`.
- Exporting stills moves the playhead and active timeline; restore both after QC.
- On Windows, an exported `PYTHONHOME` for the Resolve interpreter breaks other Python versions in the same shell (`SRE module mismatch`); set it per command.
- Do not call a reported layout "problem" if the user chose it; ask whether the preset layout is intended before proposing moves.
