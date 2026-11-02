---
name: resolve-smart-edit
description: Use when assembling, cutting, or editing video clips end-to-end in DaVinci Resolve — including media ingest, audio/visual analysis, dead-air removal, filler-word trimming, review gating, or assembling non-destructive variant timelines.
---

# DaVinci Resolve Smart Clip Edit

End-to-end intelligent clip editing pipeline in DaVinci Resolve. Bridges raw footage to an assembled, verified, non-destructive variant timeline.

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

## End-to-End Workflow

```
[ Raw Media ] ──> [ 1. Ingest & Prep ] ──> [ 2. Multimodal Analysis ]
                                                       │
[ 5. Verification ] <── [ 4. Variant Assembly ] <── [ 3. Review Gate ]
```

### Phase 1: Ingest & Project Setup
1. **Probe Media Before Importing:**
   Check frame rates and rotation with `ffprobe`:
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
   Tile extracted frames for token-efficient visual inspection:
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
   - `end_frame` is **exclusive**: `end_frame = start_frame + duration`.
   - `record_frame` is in **timeline frames** and accumulates sequentially:
     ```python
     record = 0
     for clip_id, start_sec, dur_sec in approved_cuts:
         start_f = round(start_sec * fps)
         dur_f = round(dur_sec * fps)
         clip_infos.append({
             "clip_id": clip_id,
             "start_frame": start_f,
             "end_frame": start_f + dur_f,  # exclusive
             "record_frame": record,
         })
         record += dur_f
     ```

### Phase 5: Verification & Handover
1. **Gaps & Overlaps Check:**
   ```python
   gaps = timeline(action="detect_gaps_overlaps")
   # Must return 0 gaps and 0 overlaps
   ```
2. **Audio Mirror Verification:**
   Verify `readback.after.clip_count` reflects both video and mirrored audio tracks.
3. **Report Handover:**
   Provide the editor with the new variant timeline name, final duration, and notes on any soft retakes that require human editorial judgment.

---

## Critical Traps & API Truths

| Trap | Symptom | Invariant Fix |
|---|---|---|
| **Exclusive `end_frame`** | 1-frame gap between every clip, audio clicking | Always calculate `end_frame = start_frame + duration` |
| **`ImportMedia` current folder** | Clips land in root bin or wrong folder | Call `media_pool(action="set_current_folder")` **before** importing |
| **Locked `timelineFrameRate`** | Project fps cannot be changed | Set project frame rate before creating the first timeline |
| **WAV Source Rate Freeze** | Audio item source start drifts by minutes | Audio items take project rate at import. Divide by reported `source_fps`, never hardcode 24 |
| **Mixed-FPS Floor** | Variant is 1 frame short on 24 vs 23.976 | Compute floored conversion: `floor(src_frames * timeline_fps / source_fps)` and extend 1 frame if short |
| **Multi-track Overwrite** | Stacked V1/V2 drops secondary video on tighten | Tighten handles analyzed layer; append offset secondary tracks with `record_frame_mode="absolute"` |

---

## Common Mistakes

- **Mutating the original timeline:** Never alter the source cut directly. Always output a variant timeline.
- **Over-cutting pacing:** Aggressive silence thresholds cut natural breathing and speaking rhythm. Default to `tightness="generous"`.
- **Blind execution:** Skipping the review gate and cutting without reporting largest lifts.
- **Inventing UI paths:** Do not guess menu coordinates or UI buttons; refer to Blackmagic manuals if manual interaction is needed.
