# Resolve timeline model — frames, timebase, IDs, tracks

Source: `docs/SKILL.md` (Page Context, Clip ID Reference Pattern),
`docs/guides/editorial-decision-guide.md` (Edit Variant Safety),
`AGENTS.md` (track architecture).

## The object model

- **Project → Timeline → Track (video/audio/subtitle) → TimelineItem.** Items on
a timeline are *references* to Media Pool items; they never transcode, render,
proxy, or create derivatives of source media.
- A **Media Pool clip** is addressed by `clip_id` (its UUID).
- A **timeline item** is addressed two ways:
  - positionally: `track_type` + `track_index` + `item_index`
  - by identity: its unique ID, via
    `timeline_item(action="get_unique_id", ...)`

```
folder(action="get_clips")                    # -> [{name, id}, ...]  use id as clip_id
timeline(action="get_items", params={"track_type": "video", "index": 1})
                                              # -> [{name, id, start, end, duration}, ...]
```

## Pages are a precondition, not a detail

Resolve is page-based; page-sensitive calls fail with an unexplained `False`.

| Operation category | Required page | Switch with |
|---|---|---|
| Timeline editing, track operations | Edit or Cut | `resolve_control(action="open_page", params={"page": "edit"})` |
| Color grading, node graphs, CDL, LUT export | Color | `... params={"page": "color"}` |
| Gallery stills export, `grab_and_export` | Color + Gallery panel open | `resolve_control` + Workspace menu |
| Fusion compositions | Fusion | `... params={"page": "fusion"}` |
| Fairlight audio | Fairlight | `... params={"page": "fairlight"}` |
| Render / deliver | Deliver | `... params={"page": "deliver"}` |
| Media import, storage browsing | Media | `... params={"page": "media"}` |

**When a tool returns an unexpected `False`, check the page first.**

## Frame math — the four things that bite

1. **Source frames vs record (timeline) frames are different coordinate systems**
   and both look like plausible frame pairs. `start_frame`/`end_frame` are SOURCE
   frames; `record_frame` is a timeline position.
2. **Mixed-fps floors the conversion.** A source whose fps differs from the
   timeline's rounds DOWN, so a range planned to fill an exact record slot lands
   one frame short (24.0 or 29.97 source in a 23.976 timeline). Plan durations in
   **timeline** frames: `floor(src_frames * timeline_fps / source_fps)`, extend
   `end_frame` by one source frame if the floor misses, and finish with
   `detect_gaps_overlaps`.
3. **An audio item's source frames are in the media's rate, and a WAV freezes
   the project's rate at import.** Read the `source_fps` the probe reports beside
   every item and divide by that — never the timeline rate and never a hard-coded
   24. (A WAV imported while the project was at 29.97 has no mismatch at all; it
   reads 24 only if the project was at 24 at import.)
4. **`GetSourceStartFrame`/`GetSourceEndFrame` are in the SOURCE clip's fps**,
   while on an audio item `GetLeftOffset` counts in timeline frames. A reduction
   computed from source frames must be scaled by `(se-ss)/(e-s)`.

## Timeline origin

Many Resolve timelines start at `01:00:00:00` — frame `108000` at 30 fps,
`86400` at 24 fps. Template-authored timelines start at 86400. **Clips placed
before the origin are silently dropped by Resolve on import** — `startFrame` is
timeline-absolute. Check start frame and timecode before changing a variant.

## The two frame-rate settings

- `timelineFrameRate` — **locked once a timeline exists.** On a new project set
  it before creating any timeline (`project_manager safe_set_project_settings`).
- `timelinePlaybackFrameRate` — **read-only through the API on the measured
  builds**; `set_setting` returns False for every value form. Ask the user to set
  it during setup with this authored path, quoted verbatim:

  > Project Settings (gear, bottom-right) → Master Settings → Playback frame rate

- A project's `timelineFrameRate` may differ from an individual timeline's record
  rate. After activating and ID-verifying each target, read that timeline's own
  `Timeline.GetSetting("timelineFrameRate")`.

## Track architecture this project expects

**16:9 landscape** — V1 base footage (gameplay + VTuber webcam); V2 `VTuber Zoom`
(Adjustment Clip track with Fusion Transform); V3 `REACTIONS` (overlays, GIFs,
popups, illustrations); Subtitle 1 native Thai (always on top, unaffected by
Adjustment Clips).

**9:16 vertical** — V1 `Game Top` (cropped/panned gameplay); V2 `REACTIONS`;
V3 `VTuber Bottom` (framed avatar); V4 `VTuber Zoom` (Adjustment Clip zooming the
avatar); Subtitle 1 native Thai.

Preserve the project's approved aspect ratio — never auto-convert 16:9 to 9:16.

## Media-pool side notes that change an edit

- `ImportMedia` has **no destination parameter** — `import_media` lands in the
  CURRENT bin, so `set_current_folder` first.
- `create_timeline_from_clips` needs the current folder set to the clips' bin,
  or it fails with a bare `Failed to create timeline from clip_infos`.
- Phone footage may carry a **rotation** flag (stored 3840x2160, displays
  2160x3840). Resolve honours it — do not reframe it, it is already vertical.
- Phone footage is often **VFR**: `avg_frame_rate` differs per clip and from
  `r_frame_rate`. Match the timeline to what Resolve conforms to, not to
  `r_frame_rate`.

## Error recovery quick table (from `docs/SKILL.md`)

| Error | Cause | Fix |
|---|---|---|
| `Not connected to DaVinci Resolve` | Resolve not running / scripting disabled | `resolve_control(action="launch")`, wait, retry |
| `No project open` | none loaded | `project_manager(action="load", params={"name": "..."})` |
| `No current timeline` | no current timeline set | `timeline(action="set_current", params={"index": 1})` |
| `No item at index N` | `item_index` out of range | `timeline(action="get_items", ...)` first |
| `Clip not found` | stale/wrong `clip_id` | re-fetch via `media_pool get_selected` / `folder get_clips` |

A `{"success": False}` with no error key means the underlying Resolve API
returned `False` — usually a missing precondition (page, state, context).
