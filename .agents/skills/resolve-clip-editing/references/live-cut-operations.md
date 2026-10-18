# Live cut operations — the edit kernel

Source: `docs/kernels/timeline-edit-kernel.md`, `.agents/skills/resolve-edit/SKILL.md`,
`docs/SKILL.md` (Common Workflows 3-4, Reading A Result).

Live boundary validated on Resolve Studio 20.3.2.9: 255 supported, 4 partially
supported, 138 unsupported, 4 version/page dependent.

## Duplication and relocation

`timeline(action="duplicate_clips")` re-appends the same Media Pool item with the
same source trim via `MediaPool.AppendToTimeline([{clipInfo}])`.

Placement modes: `same_time` | `offset` | `at_playhead` | `track_above` |
`after_source` | `next_gap`.

Controls: `clip_ids` (timeline item unique IDs), `selected=True`,
`target_track_index`, `track_offset`, `record_frame`, `record_frame_offset`.

- `copy_clips` is an **alias** for duplication.
- `move_clips` duplicates first, then deletes the original source items.
- `include_linked=True` duplicates linked audio alongside the video item and
  restores the video/audio link state.

```
timeline(action="duplicate_clips", params={
  "clip_ids": ["<timeline-item-uuid>"], "target_track_index": 2, "record_frame_offset": 120
})
timeline(action="duplicate_clips", params={
  "selected": True, "placement": "track_above", "include_linked": True,
  "copy_properties": ["transform", "crop", "composite", "audio", "dynamic_zoom",
                      "scaling", "stabilization", "clip_color", "markers", "enabled"],
  "copy_keyframes": True
})
```

## Range operations

- `copy_range` / `duplicate_range` — copy exact video/audio source segments from
  explicit `start_frame`/`end_frame` or the current mark in/out; destination via
  `record_frame` + optional track targeting.
- `overwrite_range` — deletes whole destination items overlapping the destination
  range, then appends the copied range.
- `lift_range` — deletes whole timeline items in a range.

```
timeline(action="copy_range", params={
  "start_frame": 110, "end_frame": 130, "record_frame": 900,
  "track_types": ["video", "audio"], "target_track_index": 2
})
```

**Partial overlaps in `lift_range` are blocked by default** because Resolve has
no public razor/split primitive. `allow_partial_item_delete=True` confirms
deletion of whole overlapping items — it does **not** perform a partial trim.

## Copyable item state

Groups: `transform`, `crop`, `composite`, `audio`, `retime`, `dynamic_zoom`,
`scaling`, `stabilization`, `clip_color`, `markers`, `flags`, `enabled`, `cache`,
`voice_isolation`, `fusion`, `grades`, `takes`, `keyframes`.

`copy_properties=True` copies all supported groups; a list or comma-separated
string scopes it; `copy_keyframes=True` adds the `keyframes` group.

Partially supported in practice: audio properties (some `SetProperty` calls
return false), dynamic zoom/scaling/stabilization, edit-page title and generator
text, cache and voice isolation, and keyframe interpolation fidelity.

## Reading the build before offering a surface

| Surface | Needs | If absent |
|---|---|---|
| `Timeline.GetSelectedClips` | 21.0.4 | No selection readback — identify clips by track/index or id; the repo's selection helper duck-probes three names and degrades to "no selection" |
| `TimelineItem.SetName` | 20.2 | Clip names are read-only from a script |

An empty `unavailable_on_this_build` means **nothing recorded is missing**, not
that everything exists. Probe with `name in dir(obj)` — **never `hasattr`**: on a
Resolve object `hasattr` returns `True` for every name, real or invented.

Distinguish **gated** (arrives with a newer build) from **absent** (never does).

## What the API cannot do (blocked by Resolve, not by MCP plumbing)

- **Razor/split edits** — no direct public timeline split primitive.
- **True partial lift** — no safe partial-item delete without a split primitive.
- **Clip speed / retime values** — `set_retime` sets retime *quality* only
  (`RetimeProcess`, `MotionEstimation`) and returns `True` for doing so, which
  reads as if the retime succeeded. `SetProperty('Speed'|'PlaybackSpeed'|
  'RetimeSpeed'|'ClipSpeed')` returns `False` and the matching `GetProperty`
  returns `None` on every build measured. Setting a %, reversing, and speed ramps
  are unreachable — route the user to Resolve's own retime controls.
- **Transition cloning** — no public timeline-item transition clone/read/write API.
- **Source-less item cloning through append** — titles, generators, Fusion comps
  and subtitles can exist on a timeline, but have no Media Pool item to clone.
- **Deep speed-ramp semantics** — opaque ramp curves are not independently
  inspectable.

**Never improvise UI geography** when handing off. Say what the operation is and
that you cannot see their screen. A UI pointer that already exists in this repo's
skills was authored deliberately — quote it verbatim; otherwise point at
Blackmagic's manual. An invented location costs the user more than "I don't know
where it is on your build" ever does, because everything else you said was
measured.

## Append semantics — the silent-failure zone

```
media_pool(action="append_to_timeline", params={"clip_ids": ["<uuid>", ...]})
media_pool(action="append_to_timeline", params={"clip_infos": [
  {"clip_id": "<uuid>", "start_frame": 0, "end_frame": 100, "record_frame": 1200, "track_index": 4}
]})
```

- When Resolve answers `AppendToTimeline` with None/False/[], the call fails with
  `APPEND_TO_TIMELINE_FAILED` (not `success` with `count: 0`) and keeps
  `verified_operation` (item count before/after) on the error.
  `error.retryable` is true **only** when that readback shows nothing was
  appended — otherwise inspect the timeline before retrying or the clips land twice.
- **`end_frame` exclusivity is build/layer dependent.** Measured on Studio 21.0
  the MCP `clip_infos` contract is **exclusive** (`end_frame = start_frame +
  duration`; otherwise a 1-frame gap between every clip, with matching audio
  gaps). Measured on 19.1.3.7 the raw `AppendToTimeline` `endFrame` is
  **inclusive of the last frame**. Verify with `detect_gaps_overlaps` instead of
  trusting either from memory.
- **Do not build a repeated clip with `CreateTimelineFromClips([clip] * n)`.** It
  deduplicates identical MediaPoolItem references: fifteen copies produced a
  one-copy timeline, returned a valid Timeline, and reported no error. Use
  `AppendToTimeline` with one dict per instance and assert the frame count.
- Positioned append is also the way to rebuild a row after `delete_clips`.

## Reading a result: the operation envelope

Every compound tool return carries `_operation`: `status` (`success` | `partial`
| `blocked` | `failed`), `verification.status` (`passed` | `failed` | `partial`
| `contradiction` | `unverified`), `changes`, `warnings`, `execution_id`.

- **`contradiction` is the one to stop on** — Resolve reported success and the
  readback disagrees.
- **`unverified` means no evidence was reported**, not that the operation was
  checked and found clean.
- **A missing `changes` means "not reported", never "nothing changed".**
- `blocked` means a confirm gate is waiting; the payload still carries
  `confirm_token` and `preview`.

## Show the gaps before cutting them

- **`plan_dead_space_markers(timeline_name?, tightness?)`** — the review gate.
  Same calibrated detection as `plan_silence_ripple` but proposes **markers**
  instead of assembling a variant, so a human sees every gap before agreeing to
  lose it. Red = confident, Yellow = the gate only just cleared its separation
  floor. Nothing is written. Use this whenever the ask is "mark the dead space so
  I can review and approve" — that is a request for this verb, not a tighten.
- **`tightness`**: `generous` (default) | `balanced` | `tight`. The default is
  deliberately loosest: a first assembly is *supposed* to be long, because
  trimming a generous cut is fast and visible while recovering material the
  machine already discarded is slow and invisible. Move to `tight` only when the
  editor asks.
- Guard bands are floored regardless of tightness — a removed gap always leaves
  frames before it (the outgoing word's decay) and after it (the incoming word's
  attack). **`tight` removes more gaps, never more speech.**
- **`plan_transcript_tighten(clip_ref)`** — word-level: fillers, false starts and
  long pauses, emitting the same `keep_ranges` shape the variant assembler takes,
  with a stated reason per removal. False starts are a flagged heuristic (tight
  repeats only, so "no, no, no" as emphasis survives).
- **`search_spoken_content(query, mode)`** — `phrase` | `all_words` | `regex`
  across every transcribed clip, returning timestamped hits with context plus
  `selects` (in/out with handles), in deterministic order (clip name, then time).
  It is the lexical axis; `find_similar` is the semantic-visual one.
- Both transcript actions need `transcript_words`: run transcription, then
  strata backfill. They say so rather than returning an empty plan.
