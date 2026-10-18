# Assembly and tightening recipes

Source: `.agents/skills/resolve-rough-cut/SKILL.md`,
`.agents/skills/resolve-tighten-recording/SKILL.md`,
`.agents/skills/resolve-trim-to-length/SKILL.md`,
`docs/guides/headless-edit-loop.md`.

## Pick the recipe by direction

| Recipe | Direction | Input | Output |
|---|---|---|---|
| Rough cut | **additive** | a folder of many clips | an assembled timeline |
| Tighten recording | **subtractive** | one long single-take recording | a tightened variant |
| Trim to length | **mechanical** | over-length timelines | a `<name>_150s` copy |
| Build from scratch | positional | Media Pool items | an exact cut via `AppendToTimeline` |

## Rough cut (additive)

**Deliverable contract:** deliver an assembled timeline. Do **not** add titles,
captions, text cards, effects, transitions, music, or grading unless explicitly
asked — editors who ask for a rough cut want shot selection and pacing; styling
is theirs, and added graphics are work that gets thrown away.

1. **Probe before importing.** `ffprobe` every clip for `r_frame_rate`,
   `avg_frame_rate`, and `rotation` — two of those routinely differ from what the
   filenames and Resolve suggest.
2. **For a series, add a timeline to the existing project — don't create a new
   one.** Check `project_manager list` first: one project per series keeps bins,
   analysed clips and settings together; one per episode scatters them.
3. **On a NEW project, set BOTH frame rates before any timeline exists.**
   `timelineFrameRate` locks once a timeline exists
   (`project_manager safe_set_project_settings`); `timelinePlaybackFrameRate`
   cannot be set through the API at all, so ask the user to set it in the UI
   during setup, quoting the authored path verbatim:
   > Project Settings (gear, bottom-right) → Master Settings → Playback frame rate
4. **Find shots at scale by tiling, not by reading frames one at a time.**
   `media_analysis` extracts frames at full source resolution (a 35-minute 4K clip
   yields 80 frames at 2160x3840; `commit_vision` costs ~1,100 tokens each, and a
   four-clip shoot exceeds 250 frames). `scripts/contact_sheet.py` burns frame
   index, timestamp and `selection_reason` onto each tile — roughly a 15x saving
   with no loss of coverage. It needs Pillow and hard-fails without it rather than
   silently producing nothing. Use a fresh scratch output dir per run; the helper
   refuses existing `sheet_*.jpg` destinations. If a pending `visual.json` frame is
   missing, re-extract it — never filter missing frames and renumber the rest,
   which would misattribute `commit_vision` findings to the wrong frame.
5. **Assemble** with a flat `clip_infos` list: source `start_frame`/`end_frame`
   plus a cumulative `record_frame`.

```python
shots = [(clip_id, start_sec, duration_sec), ...]
infos, record = [], 0
for clip_id, start, dur in shots:
    # compute source frames from the clip's own rate, then record positions
    infos.append({"clip_id": clip_id, "start_frame": sf, "end_frame": ef,
                  "record_frame": record})
    record += duration_in_timeline_frames
```

### Verified traps (each silently produces a wrong result, not an error)

| Trap | Confirmed on | Symptom | Fix |
|---|---|---|---|
| `clip_infos` `end_frame` is **exclusive** | Studio 21.0 | 1-frame gap between every clip, with matching audio gaps | `end_frame = start_frame + duration` |
| **Mixed-fps duration floor** | Studio 21.0 (MCP v2.71.1) | Source fps ≠ timeline fps → Resolve **floors** the conversion, so a range planned to fill an exact record slot lands one frame short | Plan in timeline frames: `floor(src_frames * timeline_fps / source_fps)`; extend `end_frame` by one source frame and re-check |
| **Audio item source frames are in the media's rate** | Studio 21.0.3.7, corrected 19.1.3.7 | `source_start: 56871` for a WAV on a 29.97 timeline read as 1897.6 s but counting at 24 gives 2369.6 s — out by 7m52s | Read the `source_fps` the probe reports beside every item; never the timeline rate, never a hard-coded 24 |
| `create_timeline_from_clips` needs the current folder | Studio 21.0 | Bare `Failed to create timeline from clip_infos` with valid clip_ids | `media_pool set_current_folder` to the clips' bin first |
| `ImportMedia` has no destination parameter | Studio 21.0 (MCP v2.71.1) | Clips land in whatever folder is current; an unrecognized destination arg is silently ignored | `set_current_folder` **before** importing |
| Phone footage carries a `rotation` flag | Studio 21.0 | Stored 3840x2160, displays 2160x3840 | Resolve honours it — **do not reframe**, it is already vertical |
| Phone footage is **VFR** | Studio 21.0 | `avg_frame_rate` differs per clip and from `r_frame_rate` | Match the timeline to what Resolve conforms to, not `r_frame_rate` |
| `timelinePlaybackFrameRate` is read-only | Studio 21.0.2 | `set_setting` returns False for every value form, before and after a timeline exists | No API path — ask the user to set it in Master Settings during setup |
| An API-built Fusion comp on a media clip renders only when `MediaOut` has a path from `MediaIn` | Studio 19.1.3.7 | A `MediaOut` fed by a tool with no source does not merely get bypassed — the render job comes back `Failed` | Wire the graph so `MediaOut` descends from `MediaIn`; for text over picture insert a Fusion **title** as its own clip and set its `Text+` via `fusion_comp set_text_plus` |

Every row states the build it was confirmed on. The scripting API changes per
patch release, so a trap confirmed on one build is only a **prior** on another —
re-confirm before relying on an older row. Query them at runtime with
`resolve_control api_truth "timeline"` (or `"media-pool"`, `"fusion"`).

### Common mistakes

- Reframing vertical-flagged footage into a vertical timeline — double-rotating
  or cropping material that already fits.
- Setting the timeline frame rate **after** creating the timeline; it is ignored.
- Trusting `detect_gaps_overlaps` alone — also confirm total duration and inspect
  representative frames.
- Reporting a render as the deliverable when the timeline is what was asked for.

## Tighten a recording (subtractive)

**Deliverable contract:** a tightened **variant** timeline, plan → review →
confirm. No grading, captions, or additions. The variant runs generous on purpose.

1. **Lift the analysis caps for long media** —
   `media_analysis set_caps_preset {preset: "unlimited"}`; the standard preset
   carries a 90-second wall clock and multi-hour material dies on it. Restore
   `standard` when done.
2. **Transcribe** — `media_analysis start_batch_job` with
   `{clip_id, vision: false, transcription: {enabled: true, ...}}`, then
   `run_batch_job_slice {job_id}`. Two traps in one pair: **batch jobs do not
   advance themselves** (the job sits in `queued` until a slice call drives it),
   and `run_batch_job_slice` **blocks until the slice completes** — budget roughly
   4-7x realtime for local whisper (28.5 min of speech in 5m14s via mlx_whisper)
   and run it from a background process, not the main conversation.
3. **Plan → review → execute.** `plan_silence_ripple` / `plan_tighten` for
   silence, `plan_transcript_tighten` for fillers and false starts; to let a human
   approve first, use `plan_dead_space_markers` (see
   `references/live-cut-operations.md`).

### The coordinate trap — the trap that assembles the wrong content

The plan and the execute response describe ranges in **different coordinate
systems**, and both look like plausible frame pairs:

| Field | Coordinate system | Verified |
|---|---|---|
| plan `keep_ranges` `start_frame`/`end_frame` | **Source** frames, `end_frame` exclusive (duration = end − start) | frame-exact against `clip_where` readback |
| `structural_diff.added` `in_frame`/`out_frame` | **Record** (timeline) frames of the variant | matches variant item record spans, not source spans |
| variant record positions | cumulative sum of keep-range durations | `record[i] = Σ(end−start)(j<i)`, frame-exact |

### What silence-driven tightening cannot hear

`plan_tighten` measures the microphone, not the meaning. Three classes survive
every threshold and each needs a different instrument: **audible fillers and tight
restarts** (`plan_transcript_tighten` covers these at word level), pauses that are
part of the performance, and meaning carried by silence. Do not treat "the
waveform was flat" as "nothing was said here that mattered".

### Multi-layer recordings (V1 camera + V2 screen capture)

`execute_tighten` assembles only the **analyzed** source; the other layer is
dropped from the variant, silently. To rebuild it:

1. Establish the constant offset between the two layers and verify it by **audio
   cross-correlation** between the two source files (extract matching windows with
   ffmpeg, correlate; residual under 50 ms passes). Eyeballing waveforms does not
   survive a 20-minute assembly.
2. Take the plan's `keep_ranges` (source frames), add the offset, and append with
   `media_pool append_to_timeline` clip_infos:
   `{clip_id, start_frame, end_frame, record_frame, record_frame_mode: "absolute",
   track_index: 2, media_type: 1}` (`media_type: 1` = video only; keep the
   analyzed layer's audio).
3. Verify counts and first/middle/last placements before trusting it.

### Common mistakes

- Trusting `detect_gaps_overlaps` alone — it proves the assembly is gapless, not
  that the right frames were kept. The duration check and spot placement reads are
  part of verification, not extras.
- Verifying audio by "the response said success" — **count the variant's audio items**.

## Trim a timeline to a target length

1. **Read-only audit:** for every timeline,
   `(GetEndFrame-GetStartFrame)/timelineFrameRate`; list over-length ones. Never
   eyeball.
2. **Resolve ambiguity with ONE clarify before editing**: the target ("2.50 min" =
   2:30 or 2:50?) and the cut location (head / tail / user-chosen). Recommended
   default: tail trim into a `<name>_150s` variant, originals untouched.
3. `backup_drp.export_verified` a `.drp`, then `src.DuplicateTimeline(name+"_150s")`,
   make it current. Sleep ~1.3 s between mutations (rapid ops crash Resolve).
4. In the duplicate: `DeleteClips` items starting at/after the cut; delete subtitle
   cues touching the cut (`DeleteClips` works on subtitle items; **cues cannot be
   re-timed**); delete straddling video/audio items and re-append the same media
   pool item with `mediaType` 1/2, same `trackIndex`/`recordFrame`, reduced
   `endFrame`.
5. Restore transform/crop/opacity (video) and Volume/Pan (audio) via `SetProperty`;
   read back; assert the new item ends exactly at the cut.
6. Verify per track: expected = original items clipped at the cut, compared on
   start/end/Zoom/Pan/Crop; variant length == target; originals unchanged; timeline
   count = old + N. On failure delete the partial duplicate with
   `MediaPool.DeleteTimelines`. `SaveProject`.
7. Report the deleted subtitle cues/SFX past the cut, and that the cut is
   mechanical (not on a sentence end).

Ready-made: `scripts/p2_trim_tail_150s.py <index> [--apply] [--seconds 150]` makes
a `<name>_150s` copy via DuplicateTimeline + DeleteClips + AppendToTimeline with a
reduced `endFrame` — items past the cut are deleted, subtitle cues starting at/after
or straddling the cut are deleted (not re-timed), originals untouched. Same pattern
as `p2_trim_bad_gif_tail.py`.

Traps: **re-append drops grades, Fusion comps and links** not copied — tell the
user to eyeball the variant; do not trust a verify script that counts trimmed items
as tail items; scratch scripts must use a native path
(`C:/Users/<user>/AppData/Local/hermes/cache/scratch`), not bash `$TMPDIR`.

## Build a cut from scratch through the API

`AppendToTimeline` with explicit `clipInfo` dicts is frame-exact and needs no
interchange format at all:

```python
clips = resolve.GetMediaStorage().AddItemListToMediaPool(paths)
timeline = pool.CreateEmptyTimeline("CUT_v001")
project.SetCurrentTimeline(timeline)
pool.AppendToTimeline([
    {"mediaPoolItem": clips[0], "startFrame": 0,  "endFrame": 191},
    {"mediaPoolItem": clips[1], "startFrame": 24, "endFrame": 71},
])
```

**`CreateTimelineFromClips([clip] * n)` deduplicates identical MediaPoolItem
references** — fifteen copies produced a one-copy timeline, returned a valid
Timeline and reported no error. Use one dict per instance and assert the frame count.
