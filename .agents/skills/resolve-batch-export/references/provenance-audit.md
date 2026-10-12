# Provenance audit — which timeline produced this rendered file?

Use when the user asks whether exported files came from a reserve/backup/duplicate timeline, or which project a
deliverable came from. A filename proves nothing: a same-named reserve project is common, and two projects will
gladly hold timelines that share every name.

Collect these five proofs, strongest first. All are read-only.

## 1. Render-job queue (direct attribution)

`project.GetRenderJobList()` returns one dict per job with `JobId`, `TimelineName`, `OutputFilename`, `TargetDir`,
`PresetName`, `VideoFormat`, `VideoCodec`, `FrameRate`, `MarkIn`/`MarkOut`, `RenderMode`. Join on `OutputFilename`
and you have project + timeline + destination for each file.

```python
p = pm.LoadProject(name); time.sleep(1.6)
for j in p.GetRenderJobList() or []:
    st = p.GetRenderJobStatus(j["JobId"]) or {}
    print(st.get("JobStatus"), j["TimelineName"], "->", j["OutputFilename"], j["TargetDir"])
```

Read the queue for EVERY candidate project. A project with 0 jobs cannot be the source — that single fact settles
the reserve-project question faster than any content comparison.

## 2. Timeline inventory per project

Walk the whole database tree and compare timeline names against the files on disk:

```python
def visit(path):
    for name in sorted(pm.GetProjectListInCurrentFolder() or []):
        p = pm.LoadProject(name)          # may return None; retry ~3x with a sleep
        ...
    for f in pm.GetFolderListInCurrentFolder() or []:
        if pm.OpenFolder(f):
            visit(f"{path}/{f}"); pm.GotoParentFolder()
pm.GotoRootFolder(); visit("")
```

Report both directions — `timelines with no output file` and `output files with no timeline`. Both should be empty
for a clean batch. `LoadProject` returning `None` on a large Drive-backed database is flakiness, not a missing
project: retry before reporting a load failure.

## 3. Track structure as a fingerprint

Describe each timeline as `(video tracks, audio tracks, subtitle tracks)` plus per-track item counts:

- reserve / rough-cut timeline: `(1, 1, 0)`, 0 cues, 1 item per track
- enriched deliverable: `(2-4, 3, 1)` with tens of cues on `subtitle1` and several overlay items on `video2+`

Compare the SAME-named timelines between candidate projects. The structure says which one the file matches, and it
costs nothing — no rendering, no ffprobe.

## 4. Exact frame count — never duration

```bash
ffprobe -v error -select_streams v:0 -count_frames \
        -show_entries stream=nb_read_frames,width,height,avg_frame_rate -of json "<file>"
```

Deliverable durations cluster on round values (55 / 60 / 65 s) in both the real and the reserve project, so duration
ties and proves nothing. Frame count separates them: a rough cut is exactly 3300 frames, the finished timeline is
3305 / 3316 / 3321.

`-count_frames` decodes the whole file — minutes for a hundred files on a network/Drive path. Run it backgrounded,
and only against the files the cheaper proofs could not settle.

## 5. Sidecar artefacts

A `<name>_Subtitle 1.ttml` beside the output proves (a) the source timeline had a subtitle track and (b) the job was
queued with subtitle format "As separate file" rather than "Burn into video". A reserve timeline with `subtitle: 0`
can never produce one. Conversely: no `.ttml` plus a subtitle track with cues in the source means the captions are
burned into the picture.

This is also the fastest way to find which outputs shipped WITHOUT burned-in captions in an otherwise uniform batch
— group the `.ttml` files by project and you have the re-render list.

## Disqualifying a reserve project outright

Before comparing content at all, check what the reserve project cannot possibly have produced:

- 0 vertical (`_9x16`) timelines ⇒ every vertical output came from somewhere else, however the names line up
- 0 render jobs ⇒ it never rendered anything to that folder
- `(1, 1, 0)` structure on every timeline ⇒ it cannot produce a file with overlays or burned-in captions

Any one of these ends the investigation.

## Restore the user's session

These scripts call `LoadProject`, so they move what the user sees. `preserved_state` only wraps scripts that use it.
Put Resolve back on the user's project and folder when the audit ends, and say which project you left open.
