# HyperFrames animated illustration workflow for Resolve

Use this when generating animated graphics, alpha overlays, or full-frame
cutaways in HyperFrames and importing them into a DaVinci Resolve timeline.
Covers the Resolve-side placement traps and the HyperFrames-side render
settings that the session discovered. For static stills use
`illustration-assets.md` instead.

## 1. When to use HyperFrames vs static stills

- Use HyperFrames when the illustration needs motion: title reveals, ripples,
  dissolves, animated runes, scrolling text, or alpha-channel graphics.
- Use static stills (illustration-assets.md) for single-frame inserts that
  do not animate.
- HyperFrames renders to MP4 (opaque) or MOV with alpha (ProRes 4444). Resolve
  accepts both; choose alpha MOV when the graphic must composite over V1.

## 2. HyperFrames render settings for Resolve import

- Render at the timeline's exact raster and frame rate. A 1920x1052 60 fps
  project needs 1920x1052 60 fps output; mismatched rasters or fps cause
  conform drift or black bars.
- HyperFrames `check` must pass before render. Warnings about silent asset
  reels, short fades/holds, or optional sub-composition organization are
  acceptable when the reel is not a standalone narrated film.
- Alpha MOV: use ProRes 4444 with alpha. Verify the alpha channel survived
  render with ffprobe (`pix_fmt` contains `yuva` or `rgba`).
- Export keyframes natively (`hyperframes keyframes`) for the lore and
  graphics projects; the separate animation-map helper needs optional
  packages and may not certify.

## 3. Resolve import and placement

- Import through the Python API (`resolve_common.connect_resolve`), not the
  MCP, when the MCP lacks the needed action. State `MCP-GAP:` before
  scripting.
- Set the current Media Pool folder before import; `ImportMedia` has no
  destination parameter.
- **AppendToTimeline endFrame is exclusive on 60 fps timelines.** Passing
  `endFrame = sourceStart + duration - 1` produces one frame less. Pass
  `endFrame = sourceStart + duration` and read back the placed range before
  batching.
- Activate the target timeline before comparing track enable/lock state or
  reading `GetCurrentTimecode()`.
- Place full-frame cutaways on a dedicated video track (typically V2
  REACTIONS) and alpha graphics on the same track. Keep V1 (base footage),
  audio, and subtitle tracks untouched.
- For side graphics, verify the graphic does not overlap the avatar's
  face, hands, or subtitle area. Use actual rendered frames, not Inspector
  numbers.
- Read back every placed range (start, end, duration, source offset) and
  compare against the plan before batching the remainder.

## 4. QC sequence

1. Render a pilot range (e.g., the golem-origin segment) with subtitles
   and verify composite appearance.
2. If the pilot passes, batch the remainder using the same pattern.
3. After all placements: render a full preview, decode with ffmpeg (no
   warnings), ffprobe for raster/fps/frame count, and visually review
   extracted frames at cue start, midpoint, and end for every placement.
4. Restore original active project/timeline/playhead/page/folder/track
   states and read back.

## 5. Pitfalls

- **Source overlays in the original footage are not repaired by zoom or
  illustration placement.** If the source has a cropped head or a baked-in
  overlay, the illustration does not fix it; report it separately.
- **Keep the reel beside the footage.** Pass `illustration_reel.py --root`
  a folder next to the source media (e.g. `Z:/<channel>/<clip>/illustrations/`)
  and copy the reel + `placements.json` there before `baseline`. Reels kept only
  under `.hermes/projects/` went Media Offline twice when that folder vanished
  (Armigon intro/name, 2026-10-25/26).
- **Mixed rasters in one project.** The Armigon pilot used 1920x1052
  (not 1920x1080). Do not auto-convert to 1920x1080; preserve the
  approved aspect ratio.
- **HyperFrames CLI pin.** When `npx --no-install hyperframes` asks for a
  newer release, run the cached
  `npm-cache/_npx/<hash>/node_modules/hyperframes/bin/hyperframes.mjs`
  with `node` instead of downloading. Probe with
  `npx hyperframes@latest upgrade --project . --check` before the first
  render-affecting command.
- **Community MCP version mismatch.** The community MCP may be updated
  independently of the session. Run `scripts/check_mcp_update.py` at
  session start; if it reports UPDATE, read the upstream CHANGELOG, run
  `--apply`, and restart the session before continuing.