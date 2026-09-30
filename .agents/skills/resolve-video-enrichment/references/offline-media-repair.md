# Repairing offline overlay / SFX / BGM items

For timeline items whose media-pool entry was deleted while the timeline item
survived. Symptom: `GetMediaPoolItem()` returns `None`, and Resolve's Relink
Media is useless because there is no pool item to repoint.

This is a project-database repair. It never touches source media — replacement
files are only read and imported. Snapshot `Project.db` (or export a `.drp`)
before the first write.

## 1. Record everything before changing anything

For each offline item capture, in one read-only pass:

- `GetStart()`, `GetEnd()`, `GetDuration()` (the record range)
- track kind and track index
- `GetLeftOffset()` — the SOURCE in-point, which is often NOT 0. A music bed
  trimmed to start 20 s into the file will silently restart from its head if
  you re-place it with `startFrame=0`.
- the full transform property dict via `GetProperty()` with NO arguments

Without the transform dict, a re-placed overlay comes back at 100% centred
instead of its intended corner scale/position.

Match replacement files by duration against the recorded item durations before
trusting a filename match.

## 2. Delete the dead item FIRST

`AppendToTimeline` onto a record range that is still occupied is **silently
dropped** — the existing item wins and the call reports success. Remove the dead
items with `Timeline.DeleteClips([items], False)`; the `False` keeps ripple off
so surviving clips do not shift.

## 3. Re-place at the recorded position

```python
info = {
    "mediaPoolItem": clip,
    "startFrame":   recorded_left_offset,
    "endFrame":     recorded_left_offset + recorded_duration - 1,
    "recordFrame":  recorded_start,
    "trackIndex":   recorded_track,
    "mediaType":    1,   # 1 video, 2 audio
}
```

Clamp `endFrame` to the source's own `Frames - 1` and report when you did, so a
short replacement file is visible rather than silently truncating.

Sleep ~0.45 s between appends — a tight batch of SFX/BGM/GIF appends crashes
Resolve, and the rate is the trigger, not any one file.

## 4. Restore the transform, then re-read it

`TimelineItem.SetProperty` returns `False` for roughly a second after the item is
appended, **even when the value is already correct** — Resolve is still settling
the new item. Always re-read with `GetProperty` before concluding a write
failed; retrying on the `False` alone leads you to "fix" a correct value.

Two more traps on the same call:

- It returns `False` for STRING values. Pass floats: `0.25`, not `"0.25"`.
- `ZoomGang` defaults to `True`, which LINKS `ZoomX` and `ZoomY`. Probing one by
  writing a test value silently changes the other — so a diagnostic write leaves
  the overlay the wrong size. Restore both after any zoom experiment.

## 5. Verify

Re-enumerate every track on the repaired timelines and assert zero items with
`GetMediaPoolItem() is None`, then diff each restored item's transform dict
against the values recorded in step 1 and report the mismatch count.

Finish with a rendered frame at a previously-broken timecode and look at it: the
structural check proves the item is online, only the pixels prove the red card
is gone and the overlay is framed where it belongs.
