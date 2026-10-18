---
name: resolve-clip-editing
description: Cut, trim, and assemble clips in DaVinci Resolve.
version: 0.1.0
author: Hermes
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [Resolve, Editing, Timeline, Interchange]
---

# Cutting Clips in DaVinci Resolve

The craft and the tool mechanics of building, trimming, restructuring, and
round-tripping a Resolve timeline: what the edit kernel can and cannot do, how
frame math actually resolves, which interchange format to pick, and how to
verify a cut. It does NOT cover grading, Fairlight mixing, Fusion authoring, or
rendering as ends in themselves, and it never authorizes touching source media.
Distilled from this repo's own verified sources (`docs/kernels/`,
`docs/guides/`, `.agents/skills/resolve-*`); stdlib-free prose, no runtime deps.

## When to Use

- "ตัดต่อคลิป" / cut, trim, assemble, tighten, or restructure a Resolve timeline
- "make me a rough cut / first cut / assembly" from a folder of footage
- "remove the dead air", "tighten this recording", "cut it to 2:30"
- Duplicating or moving clips, copying a range, building a variant timeline
- Choosing an interchange format, or asking "what changed between v3 and v4"
- Any question about razor/split, clip speed, retime, or selection readback

## Prerequisites

- The `davinci-resolve` MCP (live, drives a running Resolve) and/or
  `davinci-resolve-advanced` (offline: authors `.drp`/`.drt`/`.drx` and reasons
  over interchange with **no Resolve open**). Node never drives Resolve.
- The edit page for timeline/track operations:
  `resolve_control(action="open_page", params={"page": "edit"})`
- In this repo: connect through `scripts/resolve_common.py`
  (`connect_resolve`, `preserved_state`) and preflight with
  `python scripts/resolve_preflight.py --need <tool[.action]>`
- Build-specific gates are real — read
  `resolve_control get_version` → `build.unavailable_on_this_build` first

## How to Run

1. Read the reference chapter for the job (index in Quick Reference) with
   `skill_view(name="resolve-clip-editing", file_path="references/<file>")`.
2. Confirm the build and the page before promising a capability — the scripting
   API changes per **patch** release.
3. Drive Resolve through the MCP; invoke any repo script through the `terminal`
   tool. Write a Python script only behind a stated
   `MCP-GAP: <tool/action checked> -> <reason>` line.
4. Read every modified item back, then verify with `detect_gaps_overlaps` and
   `source_range_report`.

## Quick Reference

| Load | When |
|---|---|
| `references/resolve-timeline-model.md` | Frames, timebase, pages, clip IDs, track architecture |
| `references/live-cut-operations.md` | Duplicate/move/range/copy-properties, append semantics, what the API cannot do |
| `references/interchange-and-drt.md` | Format choice, round-trip traps, offline `.drt` authoring |
| `references/assembly-and-tightening.md` | Rough cut, tighten, trim-to-length, headless loop |
| `references/editorial-craft.md` | Where to cut, coverage pre-flight, sound first, house style |
| `references/verification-and-safety.md` | Read-back, render-is-truth, backups, batch pipeline |

Flat command list (all via the MCP):

```
timeline(action="get_items", params={"track_type": "video", "index": 1})
timeline(action="duplicate_clips", params={"clip_ids": [...], "placement": "next_gap"})
timeline(action="copy_range", params={"start_frame": 110, "end_frame": 130, "record_frame": 900})
timeline(action="detect_gaps_overlaps")
timeline(action="source_range_report")
timeline(action="probe_timeline_structure")
timeline(action="export", params={"path": "C:/tmp/cut.fcp7xml", "type": "FCP_7_XML"})
media_pool(action="append_to_timeline", params={"clip_infos": [{"clip_id": "<uuid>", "start_frame": 0, "end_frame": 100, "record_frame": 1200, "track_index": 4}]})
resolve_control(action="api_truth", params={"topic": "timeline"})
```

## Procedure

1. **Establish state.** `timeline(action="list")`, `get_current`,
   `probe_timeline_structure`, `source_range_report`. Confirm the timeline's own
   `Timeline.GetSetting("timelineFrameRate")` — the project setting is not a
   substitute. Note the start frame: many timelines start at `01:00:00:00`
   (frame 108000 at 30 fps, 86400 at 24 fps).
2. **Bound the deliverable.** An assembly is not a finished piece: a rough-cut
   request does not imply titles, transitions, music, grading, or a render.
3. **Gather evidence before choosing frames.** For cut/pacing/shot questions,
   lead the answer with `media_analysis(action="coverage_report")`'s
   `evidence_base` line before any creative recommendation.
4. **Plan in timeline frames**, not source frames — mixed-fps sources floor on
   conversion (see `references/live-cut-operations.md`).
5. **Work in a variant.** Back up first, prefer `_variant`/`_150s` copies over
   editing a master, and keep source media untouched.
6. **Execute through the MCP** — `duplicate_clips` / `copy_range` /
   `append_to_timeline` with explicit `clip_ids` and record positions.
7. **Read back every target**, then `detect_gaps_overlaps` +
   `source_range_report`, then look at representative frames.
8. **Save and restore**: `ProjectManager.SaveProject()`, then put the original
   project/timeline/playhead/page back.

## Pitfalls

- **There is no razor/split primitive and no clip-speed API on any build.**
  `lift_range` blocks partial overlaps unless `allow_partial_item_delete=True`
  (whole-item delete, not a trim); `set_retime` sets retime *quality* only and
  returns `True` while a speed % change is unreachable. Say so and name the
  operation the user must do in Resolve's own retime controls.
- **Never improvise UI geography.** A UI path that already exists in this repo's
  skills (e.g. Project Settings (gear, bottom-right) → Master Settings → Playback
  frame rate) is authored and reviewed — quote it verbatim. Anything else: say
  what to do, say you cannot see their screen, point at Blackmagic's manual.
- **`hasattr` lies on Resolve objects** — it returns `True` for every name, real
  or invented. Probe with `name in dir(obj)`.
- **Selection readback is best-effort**: `Timeline.GetSelectedClips` is 21.0.4+,
  so never build a destructive op on "the selected clips" without reading back
  what you actually got.
- **`end_frame` exclusivity differs by layer/build** — the MCP `clip_infos`
  contract measured exclusive on Studio 21.0, the raw `AppendToTimeline` measured
  inclusive-of-last-frame on 19.1.3.7. Verify with `detect_gaps_overlaps` rather
  than trusting either from memory.
- **`SaveProject()` on the never-saved `Untitled Project` blocks the whole
  application** and needs a force-kill. Check the project name first.
- **A repeated `timelineName` silently stops working** — the second import
  returns `None` with no error.
- Generated probe reports and analysis artifacts are scratch, not committed files.

## Verification

After any cut: `timeline(action="detect_gaps_overlaps")` plus
`timeline(action="source_range_report")`, then compare the item count and each
item's `GetLeftOffset()` against what you intended — **every silent failure in
this domain returns success**. For an assembled or imported cut, a render probe
(frame luma at cut boundaries, RMS for audio) is the only proof it is not black
or silent.
