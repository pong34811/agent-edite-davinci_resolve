---
name: resolve-trim-to-length
description: Use when shortening Resolve timelines to a target length.
version: 0.1.0
platforms: [windows]
---

# Trim Resolve timelines to a target length

No MCP action or scripting call trims an item's end in place or razors, so the
recipe is DuplicateTimeline -> DeleteClips -> AppendToTimeline with a reduced
`endFrame`. Implemented in repo `scripts/p2_trim_tail_150s.py <idx...> [--apply]
[--seconds N]` (dry-run by default). Follow repo AGENTS.md (MCP first; state an
`MCP-GAP:` line; connect via `scripts/resolve_common.connect_resolve`). Related:
`resolve-edit` (same pattern as `p2_trim_bad_gif_tail.py`).

## Steps
1. Read-only audit: for every timeline, `(GetEndFrame-GetStartFrame)/timelineFrameRate`; list over-length ones. Never eyeball.
2. Resolve ambiguity with ONE clarify before editing: target ("2.50 min" = 2:30 or 2:50?) and cut location (head / tail / user-chosen). Recommended default: tail trim into a `<name>_150s` variant, originals untouched.
3. `backup_drp.export_verified` a .drp, then `src.DuplicateTimeline(name+"_150s")`, make it current. Sleep ~1.3s between mutations (rapid ops crash Resolve).
4. In the duplicate: DeleteClips items starting at/after the cut; delete subtitle cues touching the cut (DeleteClips works on subtitle items; cues cannot be re-timed); delete straddling video/audio items and re-append the same media pool item with `mediaType` 1/2, same `trackIndex`/`recordFrame`, reduced `endFrame`.
5. Restore transform/crop/opacity (video) and Volume/Pan (audio) via SetProperty; read back; assert the new item ends exactly at the cut.
6. Verify per track: expected = original items clipped at the cut, compared on start/end/Zoom/Pan/Crop; variant length == target; originals unchanged; timeline count = old + N. On failure delete the partial duplicate with `MediaPool.DeleteTimelines`. SaveProject.
7. Report deleted subtitle cues/SFX past the cut, and that the cut is mechanical (not on a sentence end).

## Traps
- `GetSourceStartFrame/EndFrame` are in the SOURCE clip's fps, not the timeline's (30 fps source on a 60 fps timeline is half). Scale the reduction by `(se-ss)/(e-s)` or the clip lands short.
- Re-append drops grades, Fusion comps and links not copied; tell the user to eyeball the variant. No render/visual QC was done unless you do it.
- Do not trust a verify script that counts trimmed items as tail items; compare against the clipped expectation.
- Scratch scripts must live under the Hermes scratch dir by native path (`C:/Users/<user>/AppData/Local/hermes/cache/scratch`); bash `$TMPDIR` is not a native-Python path.
