# Resolve the user's target before editing

Merged on 2026-11-07 from the global `~/.agents/skills/davinci-resolve-workflow` skill (September 2026). Its tool-name tables used conceptual names that do not match the current community MCP, so only the rules below were kept. For real tool/action names, use the catalogue in `../SKILL.md`.

## Rules

- A name shown in Media Pool can identify a timeline, compound clip, or source file. Compare the current timeline and the project's timeline list before treating it as an insertable source. Never append the current timeline to itself.
- Interpret a short user reply naming a timeline as context for the preceding request, not as a request to generate a new video.
- Read the real project, timeline, frame rate, item positions, media identity, and destination track contents. A screenshot is context, not proof of media type or exact placement.
- If the user asks for an addition but has not identified what to add, inspect available context first, then ask only for that missing item. Do not invent a source or a placement (such as appending the full existing edit).
- Use `MediaPool.AppendToTimeline` only after checking its signature, source frame range, destination record frame and track index. Place video and audio separately when the API requires it.
- Preserve subtitles, BGM, SFX, source files and existing clip timing. Use a recoverable timeline copy for significant edits and keep the original target's identity.
- Validate an addition by reading destination items, identities, frame ranges and counts afterwards; a nonempty response is not verification. After an uncertain result, read current state before retrying so you do not add duplicates.
- Before `LoadProject`, beware the unsaved-project dialog; do not load another project when the task uses the one already open.

## Native read-only probe (Studio MCP `run_script`)

`run_script` supplies `resolve` and `project`; return JSON-compatible data in `result`.

```python
if project is None:
    result = {"connected": True, "project": None}
else:
    timeline = project.GetCurrentTimeline()
    result = {
        "project": project.GetName(),
        "timeline": timeline.GetName() if timeline else None,
        "tracks": {
            kind: [
                {"index": index, "count": len(timeline.GetItemListInTrack(kind, index) or [])}
                for index in range(1, timeline.GetTrackCount(kind) + 1)
            ]
            for kind in ("video", "audio", "subtitle")
        } if timeline else {},
    }
```

A failing browser or Computer Use session does not prove the Resolve MCP is down: try a read-only Resolve call before diagnosing the connection.

## Common mistakes

| Mistake | Instead |
|---|---|
| Placing items without checking track count | Read the track count first |
| Putting SFX on a track that already holds BGM | Read that track's items first |
| Rendering before setting format/codec | Set format and codec, then add the job |
| Applying a DRX/grade with the unchecked variant | Use the safe/guarded variant; DRX replaces the whole node graph |
| Importing a timeline without checking its media | Use the checked import, then read back media links |
