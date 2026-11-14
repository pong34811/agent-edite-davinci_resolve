---
name: talking-avatar-vertical-copy
description: "Use when making a 9:16 copy of a solo VTuber Resolve clip."
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [Resolve, Vertical, VTuber, Overlays]
---

# Talking-Avatar Vertical Copy

Turns a 16:9 Resolve timeline whose V1 is **one avatar talking in a room (no gameplay)** into a `<name>_9x16` copy: avatar fills the frame, full-canvas alpha overlays move into the free chest band. Framing only: no cuts, subtitles and audio untouched. Uses the Resolve Python API through repo `scripts/resolve_common.py`; for gameplay + facecam layouts use `vertical-video-reframing` instead.

## When to Use
- "สร้าง timeline แนวตั้ง" / "make a vertical / 9:16 / Shorts version" and V1 is a single seated or standing avatar with no game panel.
- REACTIONS overlays are 1920x1080 alpha MOVs (`ffprobe` pix_fmt `yuva444p12le`) whose graphic sits on one side of the canvas.

## Prerequisites
- Resolve running with the project open; repo `AGENTS.md` start checklist done (MCP first; print the `MCP-GAP:` line before falling back to Python).
- `ffmpeg`/`ffprobe` on PATH, Pillow in the Python that runs `scripts/overlay_place.py`.

## Quick Reference
| Item | Value |
|---|---|
| Timeline RASTER (set in order, read back each) | `useCustomSettings=1`, `timelineResolutionWidth=1080`, `timelineResolutionHeight=1920`, `timelineOutputResMatchTimelineRes=1`, `timelineOutputResolutionWidth=1080`, `timelineOutputResolutionHeight=1920`, `timelinePixelAspectRatio=square`, `timelineInputResMismatchBehavior=scaleToFit`, `timelineOutputResMismatchBehavior=scaleToFit` |
| V1 fill-height zoom | `ZoomX=ZoomY=1920/607.5=3.1605`, Pan 0, Tilt 0 (shows source x 0.34–0.66) |
| Base scale of a 1920x1080 clip | `0.5625*Zoom`; Pan/Tilt are timeline pixels, +Pan right, +Tilt up |
| Overlay slot | centre y ~1180 of 1920 (under the chin, above burn-in subtitles); card panel height ~620, wide strip width ~1040 |
| Overlay values | `short` preset by default; chest-band proposal from `python scripts/overlay_place.py OVERLAY.mov --target-cy 1180 --target-h 620` (or `--target-w 1040`) |
| Duplicate | `orig.DuplicateTimeline("<name>_9x16")` (a **Timeline** method, not MediaPool) |

## Procedure
1. **Inventory (read-only).** Timelines with ID, start/end, resolution, fps; per track `(name, start, end, GetLeftOffset())`; V1/V3 file paths, current Zoom/Pan/Tilt. Stop if `<name>_9x16` exists.
2. **Look at V1.** Extract 5 spread frames to scratch, `vision_analyze` the sheet for the head/face extents (not shoulders).
3. **Fill the height.** Use Zoom 3.1605 when the **head, hair ornaments and visible hands** fall inside source x 0.34–0.66. Cropped shoulders/arms are expected. Lower the zoom only if the head or hands would be cut; never answer with a black band (house rule: full frame, no bands).
4. **Measure every overlay** with `scripts/overlay_place.py` (invoke through the `terminal` tool). It prints the alpha box over the whole clip and the Zoom/Pan/Tilt for the slot.
5. **Set overlays to house-style `short`** (`scripts/video_presets.json["short"]`: Zoom 0.42, Pan 0, Tilt 403.2) on every V3 item; it is the user's binding 9:16 rule and wins over any computed slot.
   - If an overlay's measured box is < 50% of the canvas width (a side panel on a full canvas), `short` leaves the graphic ~150 px wide and off-centre. Still apply `short`, then put the `overlay_place.py` chest-band values in the handoff as a proposal and apply them only after the user approves them for that channel.
   - A channel profile in `docs/channels/` that records approved chest-band values counts as that approval.
6. **Backup, then build** in one script, dry run first, `--apply` to write: `backup_drp.export_verified(pm, project, <scratch>.drp)`; inside `preserved_state(r)`: `SetCurrentTimeline(orig)` → `DuplicateTimeline` → sleep 1.25 s → compare the full track signature with the original → RASTER (0.3 s between) → `SetProperty` floats (retry 4x, 1 s, accept readback within 0.01) → re-compare signature → `SaveProject()`.
7. **Render QC.** Activate the copy, run `python -m scripts.focus_qc_frames --start 0 --end <end> --out <scratch> --name <n> --width 1080 --height 1920 --fps <timeline fps>`, restore the previous timeline in `finally`.

## Pitfalls
- Judging the fill by full-body width: the baseline agent rejected Zoom 3.16 over shoulders and shipped a 528 px black band. Judge by head/face/hands.
- Skipping the measurement: `short` is still applied, but only the measured box tells you whether the handoff needs a chest-band proposal.
- `import p2_9x16_build` for RASTER fails outside `python -m` (it imports `scripts.p2_9x16_common`); copy the list.
- `SetProperty` returns False for strings and right after timeline changes; pass floats and re-read before retrying.
- `focus_qc_frames` rejects an fps that differs from the timeline, and its render has no audio: it proves picture and subtitle placement only.
- The subtitle track keeps its 16:9 style; check burn-in width per cue and report if the channel has no 9:16 preset.

## Verification
`ffprobe -show_entries stream=width,height,nb_frames` on the QC render reports `1080,1920,<timeline length>`, and a 4-tile frame sheet at each overlay's middle shows head whole, no bands, overlay off the face and clear of subtitles; the copy's track signature equals the original's.
