---
name: resolve-smart-edit
description: Assemble and verify cuts in DaVinci Resolve Studio.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [Resolve, Editing, MCP, Python]
---

# Fast Editing in DaVinci Resolve Studio 21

Build a reviewable rough cut using Resolve MCP and, where necessary, the local Python Scripting API. Save time by reusing analysis and validating one representative edit before batching. Do not touch the original timeline or source media, automate the GUI, or render and publish outside the authorized scope.

- **Editorial craft:** See `docs/guides/editorial-decision-guide.md`
- **Additive rough cut assembly:** See `resolve-rough-cut`
- **Single-take subtractive dead-air pass:** See `resolve-tighten-recording`
- **Timeline kernel mechanics:** See `docs/kernels/timeline-edit-kernel.md`

---

## Non-Negotiable Safety Invariants (AGENTS.md)

1. **Source Media Safety:** Never modify, transcode, convert, proxy, relink, replace, or create derivatives of source media. All analysis artifacts go to session scratch or the configured analysis root.
2. **Non-Destructive Timelines:** Never overwrite or mutate the active user timeline. Smart edits always assemble into a **new variant timeline** (e.g., `<name>_smart_edit_v1`), leaving the original timeline completely intact.
3. **Mandatory Human Review Gate:** Present planned cuts, total time saved, and top lifts to the editor before assembling the variant cut.

---

## When to Use

- When asked to perform an end-to-end edit on a folder of clips or an unedited recording.
- When turning raw takes or vlogs into an assembled rough cut with dead air removed.
- When speech-driven editing (Whisper transcription) and visual sampling inform the cut.
- When a review gate (markers or report) is required before committing edits.

### When NOT to Use
- Pure additive montage across dozens of short clips without speech: use `resolve-rough-cut`.
- Single long screen recording/podcast needing dead-air ripple only: use `resolve-tighten-recording`.
- Direct manual trimming, clip duplication, or range copying on an existing cut: use `resolve-edit`.
- Color grading, audio busing, or visual effects: route to `resolve-color`, `resolve-audio`, or `resolve-fusion`.

---

## Prerequisites

- Use Resolve Studio 21 and the intended project on the same workstation. Record the full Resolve build and live MCP version. Read `AGENTS.md`, `docs/OPERATING-NOTES.md`, and `house-style` for project/channel rules.
- For the community `davinci-resolve` MCP, use the verified project server entry in `.mcp.json` with the active Hermes profile's `mcp_servers` configuration. Confirm attachment with a read-only call; a saved schema is not a connection.
- Built-in Studio MCP requires Studio 21.1+. Blackmagic documents **File → Setup AI Assistants** for supported clients; verify that Hermes actually discovers the tool. For same-host Python fallback, enable **Local** external scripting when required. No cloud credentials are required for these local routes. Read `docs/guides/resolve211-agent-guide.md` for runtime and build details.

## How to Run

Use the attached MCP schema for live actions. Through `terminal`, invoke `python scripts/resolve_preflight.py --need media_pool.append_to_timeline` for a read-only positioned-edit preflight. Stop on `BLOCKED`; don't start Resolve or switch projects implicitly. A passed preflight does not verify a write.

## Quick Reference

- Community: `resolve_control` → `get_version`, `check_version_support`, `api_truth`.
- Community: `media_analysis` → `coverage_report`, `summarize`, `get_report`.
- Community: `edit_engine` → `plan_dead_space_markers`, `plan_transcript_tighten`.
- Studio: `get_resolve_status`, `get_whats_new`, `search_scripting_api`, `get_scripting_api`, `get_scripting_docs`, `run_script`.
- Python: `MediaPool.AppendToTimeline`, `Timeline.GetItemListInTrack`, `ProjectManager.SaveProject()`.

## Procedure

1. **Confirm target and routes.** Read project/timeline IDs, start frame, resolution, distinct source/timeline/playback FPS, bins and track inventory. Try the community action first. If absent or demonstrably wrong, record `MCP-GAP: <tool/action checked> -> <reason>` and confirm the exact method in the installed Scripting API or Studio MCP before using sandboxed `run_script`. If that is unsuitable, use `read_file` on `scripts/INDEX.md` and `search_files` for a reusable helper. A new one-off goes in `scripts/scratch/` and uses `connect_resolve` and `preserved_state(resolve)` from `scripts/resolve_common.py`. No `run_script_unsafe` without explicit approval.
2. **Reuse evidence and cut for the story.** Check `coverage_report` and reuse current transcripts, markers and contact sheets; fill only gaps that affect the cut. For dialogue, establish premise → setup → turn → payoff in sound before choosing pictures. Judge cuts by whether a thought lands, a reaction adds meaning, and sound stays natural; confirm those beats in picture and audio. Do not remove pauses or retakes unless authorized; Thai caption text follows `house-style`.
3. **Review before applying.** Present the cut list, reasons, largest removals, runtime estimate and uncertain points. For a review-only request, propose markers instead of cutting. Record source IDs, `[IN, OUT)` at source FPS, absolute record frames at timeline FPS, and target tracks. Validate an existing draft through `terminal`: `python scripts/edit_workflow.py validate scratch/edit-review/edit_decisions.json`. See `docs/EDIT-WORKFLOW.md` for the plan and QC receipt format.
4. **Pilot, then batch.** Verify the `.drp` backup (`scripts/backup_drp.py`, `export_verified`) before batch writes. Apply to a new variant after approval. Pilot the hardest case first (e.g. mixed FPS, nonzero timeline start, linked audio). Read back both source and record ranges, then apply serially. If the result differs, stop and inspect before retrying; reuse completed work only when it matches the plan. No pytest in the live run–inspect–fix loop.

### Execution recipes

```
[ Raw Media ] ──> [ 1. Ingest & Prep ] ──> [ 2. Multimodal Analysis ]
                                                       │
[ 5. Verification ] <── [ 4. Variant Assembly ] <── [ 3. Review Gate ]
```

### Phase 1: Ingest & Project Setup
1. **Probe Media Before Importing:**
   Invoke through `terminal` to compare the reported frame rates with `ffprobe`:
   ```bash
   ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate,avg_frame_rate -of default=noprint_wrappers=1 <file>
   ```
2. **Project Settings:**
   On a new project, verify `timelineFrameRate` via `project_manager(action="safe_set_project_settings")`. Note: Resolve permanently locks `timelineFrameRate` once any timeline is created.
3. **Bin Isolation:**
   Create an episode/sequence bin in Media Pool and set it as current **before** importing:
   ```python
   # Mandatory: ImportMedia always deposits into current folder
   media_pool(action="set_current_folder", params={"folder_id": target_bin_id})
   media_storage(action="import_media", params={"paths": [clip_path]})
   ```

### Phase 2: Multimodal Analysis
1. **Whisper Speech Transcription:**
   ```python
   job = media_analysis(action="start_batch_job", params={
       "clip_id": hero_clip_id,
       "vision": False,
       "transcription": {"enabled": True}
   })
   # Drive batch job to completion
   media_analysis(action="run_batch_job_slice", params={"job_id": job["job_id"]})
   ```
2. **Visual Contact Sheet Sampling:**
   Invoke through `terminal` to tile already-sampled frames for visual inspection:
   ```bash
   python3 scripts/contact_sheet.py <clip_dir> <scratch_out_dir>
   ```

### Phase 3: Editorial Planning & Human Review Gate
1. **Silence & Dead-Air Detection:**
   ```python
   plan = edit_engine(action="plan_tighten", params={
       "timeline_name": source_timeline_name,
       "tightness": "generous",
       "min_pause_seconds": 1.2
   })
   ```
2. **Word-Level Trimming (Fillers & False Starts):**
   ```python
   word_plan = edit_engine(action="plan_transcript_tighten", params={"clip_ref": hero_clip_id})
   ```
3. **Mark Timeline for Visual Inspection:**
   ```python
   edit_engine(action="plan_dead_space_markers", params={
       "timeline_name": source_timeline_name,
       "tightness": "generous"
   })
   ```
4. **Human Review Gate (Halt & Confirm):**
   Report to the user:
   - Estimated runtime reduction (e.g. original `18m 20s` -> `13m 45s`, saved `4m 35s`).
   - Total number of planned cuts / keep ranges.
   - Largest lifts (any silent segment > 15s must be verified to prevent cutting silent on-screen demonstrations).
   *Wait for user confirmation before proceeding to Phase 4.*

### Phase 4: Non-Destructive Variant Assembly
1. **Assemble Variant Timeline:**
   Feed the verified keep ranges to `create_timeline_from_clips`:
   ```python
   media_pool(action="create_timeline_from_clips", params={
       "timeline_name": f"{source_timeline_name}_smart_edit_v1",
       "clip_infos": clip_infos
   })
   ```
2. **Coordinate Rules:**
   - `start_frame` / `end_frame` are in **source clip frames**.
   - Plan `end_frame` as exclusive. Convert to the live action's convention and confirm it on the variant.
   - `record_frame` is in **timeline frames**; confirm the action's relative/absolute mode. Use actual timeline start and frame rate, not zero or the source rate by default.

### Phase 5: Verification & Handover
1. **Gaps & Overlaps Check:**
   ```python
   gaps = timeline(action="detect_gaps_overlaps")
   # Compare to the plan; no unintended gaps or overlaps.
   ```
2. **Audio Mirror Verification:**
   Verify `readback.after.clip_count` reflects both video and mirrored audio tracks.
3. **Report Handover:**
   Provide the editor with the new variant timeline name, final duration, and notes on any soft retakes that require human editorial judgment.

---

## Pitfalls

| Trap | Symptom | Invariant Fix |
|---|---|---|
| **End-frame convention** | One frame missing after append | Verify the wrapper and item type. Half-open ranges matched tested video/audio appends on 21.1.0.17; verify the current build on a pilot. |
| **`ImportMedia` current folder** | Clips land in root bin or wrong folder | Call `media_pool(action="set_current_folder")` **before** importing |
| **Locked `timelineFrameRate`** | Project fps cannot be changed | Set project frame rate before creating the first timeline |
| **WAV Source Rate Freeze** | Audio item source start drifts by minutes | Audio items take project rate at import. Divide by reported `source_fps`, never hardcode 24 |
| **Mixed FPS** | Success reported but variant is short | Keep FPS as a rational value, calculate planned record duration separately, and verify the actual range instead of blindly extending the source. |
| **Analyzed layer only** | A tighten removes secondary video or linked audio | Verify planned coverage on all affected tracks. Do not reuse a single-layer plan as a whole-timeline edit. |
| **Misleading API probe** | `hasattr` says a nonexistent method is available | Use `name in dir(obj)`; compare the installed vendor docs, attached action, and actual runtime results separately. |
| **Unsupported retime or trim** | Quality settings mistaken for speed or guessed razor calls | Inspect `SetSpeed`/`set_speed` on the specific build. Constant speed does not establish ramp support; never invent setters. |

---

## Common Mistakes

- **Mutating the original timeline:** Never alter the source cut directly. Always output a variant timeline.
- **Over-cutting pacing:** Aggressive silence thresholds cut natural breathing and speaking rhythm. Default to `tightness="generous"`.
- **Blind execution:** Skipping the review gate and cutting without reporting largest lifts.
- **Inventing UI paths:** Do not guess menu coordinates or UI buttons; refer to Blackmagic manuals if manual interaction is needed.

## Verification

Compare the saved variant's live track inventory with the approved decision list and the original baseline: source ID and bounds, record start/end, track, linked audio, subtitles, and duration. Check picture and sound at each changed join for sync, complete dialogue and unintended gaps; confirm audio does not extend the picture tail. Restore the original active state. Report the variant ID, measured duration, route used and any unverified result. For reusable discoveries, record build, item type and readback evidence via `project-learning`.
