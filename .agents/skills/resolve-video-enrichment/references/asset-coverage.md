# Asset coverage and Resolve readback

Use this reference before adding SFX, BGM, or illustration media to an existing batch of timelines.

## Coverage table

For each timeline, record:

| Field | Readback |
|---|---|
| Timeline name | `GetName()` |
| Video/audio tracks | `GetTrackCount("video"/"audio")` |
| Track labels | `GetTrackName(type, index)` |
| Items | `GetItemListInTrack(type, index)` |
| Placement | `GetName()`, `GetStart()`, `GetEnd()`, `GetDuration()` |
| Mix | Read `GetProperties().get("AudioVolume")` on builds whose shipped API documents it; probe `GetProperty("AudioVolume")` on older builds. Check the installed scripting README/stub and read back the value after setting it. |
| Source existence | `GetMediaPoolItem().GetClipProperty("File Path")` when available, then `os.path.exists()` |

Compare exact `GetName()` basenames to `os.listdir()` results in the requested asset directories. Count matching SFX, BGM, and GIF items per timeline. Treat missing `GetMediaPoolItem()` as incomplete provenance, not as proof that the timeline item is absent.

## Cue-level offline diagnosis

When Resolve shows `Media Offline` at a reaction cue but the V1 source reports online, inspect the active V2-or-higher item before relinking gameplay media. An unavailable overlay can replace the composite even though the camera/gameplay source is valid. In a recoverable variant, restore the named overlay from its exact asset path and prove the repair with a rendered frame at that cue.

## Decision table

| Finding | Action |
|---|---|
| BGM already spans the timeline | Keep it; do not add another full-length BGM. |
| SFX already lands on reviewed cues | Keep the cue and mix; add only a genuinely missing cue. |
| GIF/overlay track exists and has relevant items | Do not duplicate it. |
| One category is missing | Create a recoverable enhanced variant and add only the missing category. |
| Source path moved | Verify every primary path exists before editing/rendering; report missing paths and obtain explicit authorization before any relink. |
| Timing is uncertain | Review markers/subtitles/frames first; do not place assets by uniform spacing. |

## Safe variant pattern

- Original: `project timeline name`
- Variant: `project timeline name [ENHANCED]`
- Put selected GIFs on the dedicated overlay track and selected SFX/BGM on the named audio tracks.
- Save via `ProjectManager.SaveProject()` and restore the user's active timeline after mutation.

## Promote approved enrichment to original timelines

Use this only after the user explicitly asks to apply reviewed work to the original timeline IDs. Otherwise keep the recoverable `[ENHANCED]` copies as the edit deliverable.

1. **Snapshot and back up.** Record current timeline ID/timecode, page, and Media Pool folder. Compare each original's video/audio source ranges and subtitle items with its approved variant. Export the current project with `ProjectManager.ExportProject(project_name, backup_path, True)`; require a true return, a non-empty `.drp`, and keep the enhanced timelines as a second recovery path.
2. **Build the cue source list.** On each enhanced timeline, activate it and verify its unique ID before reading track-enabled state. Collect only items whose clip is enabled on an enabled track; match exact asset path and record frame, and read back gain, fades, transform, source range, and duration. This excludes disabled obsolete overlays retained for recovery.
3. **Promote without replacing the edit.** Activate the original by `GetUniqueId()` before every timeline mutation. Preserve V1, A1 source ranges, and subtitle track/items; add dedicated V2 `REACTIONS`, A2 `SFX`, and A3 `BGM` only when absent. Copy the approved active GIF/SFX/BGM cues to empty tracks at their reviewed record frames, and set the original A1 `AudioVolume` to the approved variant's exact value. Before appending, match existing path+record-frame pairs so a retry cannot stack duplicates.
4. **Use actual GIF media timing.** Read `FPS` and `Frames` from the GIF's `GetMediaPoolItem().GetClipProperty()`. Reproduce the insertion frame count with `min(source_frames, max(1, int(round(duration_s * source_fps))))`, using the actual media `FPS` (fallback to the cue rate only if Resolve has no FPS value). A cue's planned FPS can differ from the imported GIF's real FPS and halve/double its duration. After insertion, require timeline duration, fades, and transform to match the active enhanced item before committing that timeline.
5. **Commit or roll back per active timeline.** Save each completed timeline through `ProjectManager.SaveProject()` and read it back before proceeding. If an assertion fails, activate each affected timeline before calling `DeleteClips`; remove only items on tracks created by the failed transaction, restore its prior base `AudioVolume`, then delete only those now-empty tracks in reverse order. Save and verify the rollback, or stop with the pre-edit `.drp` path; never delete against an inactive timeline or blindly replay a partial batch.
6. **Verify the actual originals.** For every original, compare V1/A1 source in/out and all subtitle names/placements to the pre-edit baseline. Confirm track labels, enabled states, cue counts, exact paths, record frames, volume/fades, GIF transforms, and GIF durations against the enhanced reference. Export a still from the actual original timeline at each GIF cue midpoint with `Project.ExportCurrentFrameAsStill()` and inspect it for offline media, overlap, and legibility; enhanced-timeline frames alone do not prove the original was updated correctly.
7. **Restore, optionally remove copies, and report.** Normally retain `[ENHANCED]` references. Remove them only when the user explicitly asks, and only after every promoted original passes step 6 and the project is saved. Export a second fresh `.drp` of the fully promoted project with `ProjectManager.ExportProject(project_name, backup_path, True)`; require a true return and a non-empty file, because a pre-promotion backup does not contain the promoted originals. Re-read the live project and map originals/copies by stable timeline IDs; define the exact deletion set from those IDs, confirm names/pairs and expected pre-delete IDs, and capture the current UI state. If the active timeline is in the deletion set, switch to its paired surviving original at the same timecode first. Call `MediaPool.DeleteTimelines(target_objects)`, save, then enumerate timelines again: require all original IDs to remain, only the requested copy IDs to be absent, and the complete remaining-ID set/count to match the precomputed expectation; do not trust the deletion return value alone. Recheck original cue counts/paths, cuts, subtitles, and the asset bin. Do not delete Media Pool assets or rendered files when the request is only to remove timeline copies. After any verification loop that switches timelines, restore the chosen surviving timeline/timecode before asserting the active state and final save; otherwise the last inspected timeline can cause a false failure. Finally restore the page/folder, save, and read back. Report original count, cues promoted, whether copies were retained or removed, the post-promotion backup path, unchanged cuts/subtitles, and any separate post-render mastering step; do not imply that post-render LUFS is embedded in the Resolve timeline.
