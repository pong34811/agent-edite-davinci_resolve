---
name: resolve-batch-export
description: Use when batch-exporting Resolve timelines with a preset.
version: 0.1.0
platforms: [windows]
---

# Batch export Resolve timelines with the user's preset (+ cover frame)

Repo implementation: `scripts/p2_export_final.py [--project NAME] [--covers DIR] [--out DIR] [--preset NAME] [--require-cover] [--apply] [--only a,b] [--limit N] [--verify]`
(dry-run by default; one project per invocation, so loop a bash `for` over projects, each its own process, state in `exports/final-export/<project>/`; pure planning helpers are unit-tested in `tests/test_p2_export_final.py`).
Follow repo AGENTS.md (MCP first, state an `MCP-GAP:` line, connect via
`scripts/resolve_common.connect_resolve`, `.drp` backup before `--apply`).
Related: `resolve-delivery` (render/QC essentials), `resolve-trim-to-length`.
Depth: `references/provenance-audit.md` (five read-only proofs for "which timeline produced this file?").

## Delivery conventions (this user)
- Deliverables land in the job folder beside their covers, flat: `G:\My Drive\Projects\<owner>\<year-month>\<job>\vdo-N\`.
  Each clip ships as a pair with a matching `.jpg` cover — horizontal `<timeline-name>.jpg`, vertical
  `<timeline-name>_9x16.jpg` — and the render output carries the same stem as its timeline. Do not invent a second
  naming scheme or a subfolder per aspect ratio.
- Vertical clips carry the cover as the first frame; horizontal clips do not get a cover. The cover goes on a
  temporary copy of the timeline so the original is untouched.
- Captions are burned into the picture, never shipped as a separate sidecar file. A batch whose captions came out as
  `.ttml` instead of on-screen text must be re-rendered — check a pilot frame that has a live cue before queuing the
  rest, because a clean-looking `.mov` with no `.ttml` is not by itself proof the text is on screen.

## Steps
1. Read-only preflight: `GetRenderPresetList()` contains the user's named preset; target folder
   has no existing output for the names (Resolve would suffix them); covers/assets exist.
2. Ask once about ambiguities: which timelines when a trimmed `_150s` variant exists (default:
   render the variant under the ORIGINAL name), container (follow the preset), burn-in subs,
   loudnorm, cover length/position.
3. Do NOT hardcode settings from a screenshot or an older batch script — but DO honour what the user
   asked for in that screenshot. `LoadRenderPreset(name)` before every job pins the base state, then
   override `SelectAllFrames`, `TargetDir`, `CustomName` AND every setting the user explicitly asked
   for that the preset does not guarantee (overriding only those three shipped a whole batch with
   captions as sidecar files — see the subtitle trap). Start only your own job ids. The preset carries
   more state than the keys you pass and `GetRenderSettings` cannot be read back to check it, so the
   pilot frame is the only real verification.
4. Cover for vertical clips: render a `DuplicateTimeline` copy named `<name>__cover_tmp`, add a
   top video track, lay the jpg on it at the first frame (nothing shifts), render, then
   `MediaPool.DeleteTimelines` the copy once Complete. Originals stay untouched.
5. A still ignores `startFrame/endFrame` in `AppendToTimeline` and lands as 300 frames, hiding the
   opening. Set `poolItem.SetMarkInOut(0, N-1, "video")`, append with no start/end frames, then
   `ClearMarkInOut("all")`; assert the item spans exactly N frames and the other tracks' item
   counts are unchanged.
6. Pilot one horizontal + one vertical first; ffprobe each (video+audio streams, 1920x1080 or
   1080x1920, duration vs timeline) and compare frame 0 of verticals to the jpg (ffmpeg `ssim`
   >= 0.9) before queuing everything. Then `--verify` over all outputs.
7. On any failure mid-loop, delete the render jobs and `__cover_tmp` copies you created and
   `ClearMarkInOut` the pool stills; sleep ~1.3s between mutations (rapid ops crash Resolve).

## Multi-project runs
- Select jobs by cover presence (`--require-cover`): export only timelines with a `<out_name>.jpg`; report the rest as skipped, never render silently. Dry-run all projects first and check the total equals the cover count and out_names are unique across projects (all land in one flat folder).
- Switch projects with `ProjectManager.SaveProject` -> `CloseProject` -> `LoadProject` (skip Save for an "Untitled" project, it can open a name dialog); wrap in `preserved_state`. `LoadProject` only sees the folder/library open in Project Manager: probe `GetCurrentDatabase/GetProjectListInCurrentFolder` first; never `SetCurrentDatabase` yourself.
- Foreground commands over 600s are auto-backgrounded; run long loops with `terminal(background=true, notify=true)`, log to a file, wait via `process_manage`.
- Resuming a run killed earlier (e.g. by the user, or a session that ended): re-issue the EXACT same per-project `for` loop over ALL projects, including ones already finished — `_find_output` makes each project idempotent (`skipping existing outputs: N` / `nothing to do`), so there is no need to compute which projects or jobs remain by hand. Recover the exact prior command/flags with `session_search` (role_filter `tool,assistant`, query on literal tokens like the project-name prefix or script module name) rather than reconstructing flags from memory.
- Before resuming, the project that was open at kill-time can be mid-cleanup: a `for n in range(1,trackcount+1)` kill can land inside the script's own "delete this job's `__cover_tmp`" loop. Check it: list timelines containing `__cover_tmp` and read every queued `GetRenderJobStatus(id)['JobStatus']` — only call `DeleteAllRenderJobs()` once every status is terminal (`Complete`/`Failed`/`Cancelled`), then `MediaPool.DeleteTimelines` each leftover tmp timeline (sleep ~1.3s between each per the mutation-pacing trap below) and `SaveProject()` before restarting the loop.

## Provenance audit: "which timeline did this file come from?"
When asked whether exported files came from a reserve/backup timeline, do NOT judge by filename alone (a same-named
reserve project is common). Collect these five independent proofs, strongest first, all read-only:
1. **Render-job queue** — `project.GetRenderJobList()` returns per job: `TimelineName`, `OutputFilename`, `TargetDir`,
   `PresetName`. Join on `OutputFilename` and you have direct project+timeline attribution. Read the whole queue for
   EVERY candidate project (`GetRenderJobStatus(id)` for status). A project with 0 jobs cannot be the source.
2. **Timeline inventory per project** — walk every project in the database tree (`GetFolderListInCurrentFolder` /
   `OpenFolder` / `GotoParentFolder` / `GetProjectListInCurrentFolder`) and compare timeline names against the files.
   Report `timelines with no output file` and `output files with no timeline`. Beware `LoadProject` returning None:
   retry ~3x with a sleep; it is flaky on a large Drive-backed database, not a missing project.
3. **Track structure as a fingerprint** — a reserve/rough-cut timeline is typically `(video 1, audio 1, subtitle 0)`
   with 0 cues, while an enriched deliverable is `(video 2-4, audio 3, subtitle 1)` with tens of cues. Compare the
   SAME-named timelines between candidate projects; the structure tells you which one the file matches.
4. **Exact frame count, not duration** — `ffprobe -select_streams v:0 -count_frames -show_entries stream=nb_read_frames`.
   Deliverable lengths cluster on round values (55/60/65 s), so duration ties and proves nothing; frame count
   separates a 3300-frame rough cut from a 3316-frame finished timeline. `-count_frames` is slow (minutes over 176
   files on Drive) — run it backgrounded and only on the ambiguous files.
5. **Sidecar artefacts** — a `<name>_Subtitle 1.ttml` next to the output proves the timeline had a subtitle track and
   that the job was queued with subtitle "As separate file" instead of BurnIn. Absence of .ttml + a subtitle track in
   the source means the captions are burned in.
Also confirm the reserve project CANNOT be the source on its own merits: 0 vertical timelines means every `_9x16`
file came from elsewhere, regardless of name collisions.

## Traps
- Interrupting a running batch (the user says stop, or you spot a wrong setting): kill the process, then clean up
  BEFORE re-running. Read the queue, `DeleteRenderJob` only the ids you created, delete every `__cover_tmp` timeline
  you made (~1.4s sleep each), delete the partial outputs already written, `SaveProject()`, and confirm
  `IsRenderingInProgress()` is False. Never re-run on top of your own leftover jobs and copies: the resumed run's
  `skipping existing outputs` count then hides the files written with the bad settings, and you end up reconciling
  two generations of output. Deleting and re-queuing is the cheaper path.
- Kill by PID, never by command-line match. A filter like `CommandLine -match '<script>.py'` also matches the wrapper
  shell that is running the filter, so the kill command kills itself (exit code 4294967295) and you cannot tell
  whether the target died. Resolve the PIDs first, print them, then `Stop-Process` those exact ids in a second call.
  Child processes spawned by your loop (e.g. ffprobe) respawn until their parent python dies — kill the parent first,
  then the children.
- An ad-hoc read-only audit script that calls `LoadProject` still moves the user's session; `preserved_state` only
  wraps scripts that use it. At the end of every audit, put Resolve back on the project and folder the user was
  working in (root -> owner folder -> year folder -> `LoadProject`) and report which project you left open. Loading
  a dozen projects to compare them and walking away leaves the user on the wrong timeline.
- Subtitles are NOT guaranteed by the preset: `LoadRenderPreset` + overriding only `SelectAllFrames/TargetDir/CustomName`
  silently produced a separate `.ttml` sidecar (no captions in the picture) even though the user expected burned-in text.
  When the user asks for captions in the file, pass `ExportSubtitle: True, SubtitleFormat: "BurnIn"` in the same
  `SetRenderSettings` call. Verify on a PILOT frame with a live cue (`ffmpeg -ss <sec> -i f.mov -map 0:v:0 -frames:v 1`)
  via vision, not by absence of `.ttml` alone.
- A disabled Subtitle track still renders burned-in captions — do NOT "fix" a timeline whose subtitle track reads
  `GetIsTrackEnabled('subtitle', n) == False`; check a real rendered frame before reporting missing subtitles.
- `GetTimelineCount()` transiently returns `None` immediately after a long render batch (and `GetCurrentTimeline()` can
  read as an Untitled project). Using it as an arithmetic operand raises `TypeError: unsupported operand ... 'NoneType'
  and 'int'` and aborts the whole cleanup phase, leaving every `__cover_tmp` timeline behind. Guard every count read
  (`n = p.GetTimelineCount() or 0`) and skip `None` timelines. If cleanup did abort, recover read-only: reload the
  project, list `__cover_tmp` names, `DeleteTimelines` each with ~1.4s sleep, `SaveProject()`.
- On a Failed job read `GetRenderJobStatus(id)['Error']` first; an offline-cover error means check the pool clip's `File Path` (a bug once produced `{}\\name.jpg` from a variable shadowing the covers folder). Then delete your job, the `__cover_tmp` timeline, the pool clips and the partial output file before retrying (resume skips any existing output; ImportMedia is path-cached).
- ffprobe on .mov also shows a `data` timecode stream and repeats stream groups; judge by video/audio `codec_type`. Extract frames with `-map 0:v:0 -fps_mode passthrough` (`-vsync` is rejected by current ffmpeg).
- Bash `$TMPDIR` is `/tmp` for MSYS: pass native python `"$(cygpath -w "$TMPDIR/x.py")"`.
- The scratch dir for ad-hoc scripts must be a native path (`C:/Users/<user>/AppData/Local/hermes/cache/scratch`); bash `$TMPDIR` is not.
- `pytest` may be absent from the interpreter: run `uv run --with pytest python -m pytest ...`.
- Pool `ImportMedia` is path-cached; reuse existing pool clips from the `P2 Covers` bin instead of re-importing.
- `Error decoding full resolution media for <file> at <tc>` on a Failed job, at a deep timecode into a long source (tens of minutes in), is usually Resolve's own decoder choking on that region, not a corrupt or offline file — confirm with a read-only probe (`ffmpeg -ss <seconds> -i "<path>" -frames:v 1 -fps_mode passthrough -update 1 out.jpg`; needs `-update 1` for a single still, not a `%03d` pattern) before assuming the source is bad. The unreadable region can be a wide contiguous band (tens of minutes, not one GOP): a 1-frame or 1-second nudge of the clip's source in-point does NOT dodge it, and sequential forward decode from a known-good point into the band fails at the same offset too (it's not seek-related). If you need the actual boundary, bisect with short test renders (`SelectAllFrames: False, MarkIn/MarkOut` a 10-frame window on a throwaway duplicate timeline) at several source offsets rather than guessing a small shift will clear it. Retrying the render job reproduces the identical failure at the identical offset — it is not transient, so don't burn a second attempt hoping it clears. There is no scripting-API call to generate Optimized/Proxy media (it is UI-only: right-click the clip > Generate Optimized Media); when the probe confirms the source is readable, stop and ask the user to generate optimized media for that clip in the Resolve UI, then retry — don't invent a transcode workaround outside Resolve.
- When the user reports they fixed a decode-failed clip (relinked, re-exported, replaced the source), verify the bytes actually changed before spending another render cycle: `os.stat()` the file and compare size AND mtime AND ctime to the pre-fix values. Size+mtime alone can lie: ordinary copy tools (Explorer copy, robocopy /COPY:DAT) preserve the source's mtime, so a user who copies the SAME broken file back onto itself again shows an unchanged mtime but a bumped ctime (ctime only proves *a copy operation happened just now*, not that the content differs) — identical size with either timestamp unchanged means it is still the same bytes, full stop. Also do not assume a chat "[User attached file: <path>]" notice put new bytes on disk: in a plain CLI/terminal session there is no inbound attachment channel, so that line is usually just the path the user picked in their file browser, not an upload — `stat` the referenced path yourself before trusting it changed, and if it still matches the broken file's stat, say so plainly and ask them to actually overwrite the file on disk (not re-attach it in chat). A relink to a copy of the identical file (same size/mtime) reproduces the identical error — tell the user the relink didn't change the content instead of re-running the same failing render.
- To force Resolve to re-acknowledge a file at a path after a real replace (or to clear a transient "Media Offline" after any file-level change at the same path), call `mediaPool.RelinkClips([clip, ...], folderPath)` — it works even when `GetClipProperty('Online Status')` already reports `Online`, and is the scripted equivalent of right-click > Relink Selected Media; `SaveProject()` after.
- A Failed job still writes a small partial output file (tens/low-hundreds of KB, not the expected multi-MB clip) — `_find_output`-based resume treats its mere existence as "already rendered" and silently skips it. After any Failed status, check the output file size (or just delete it) before trusting a resume's "skipping existing outputs" count.

## Reporting a finished batch
Lead with the verdict in one line — done or not done, plus the file count — then the evidence. A long report that
opens with QC detail makes the user ask "is it finished?" again; the yes/no goes first, every time. When something
was left in a non-obvious state (jobs still queued, a project left open, a file skipped), say it in that same first
block rather than at the end of the detail.
