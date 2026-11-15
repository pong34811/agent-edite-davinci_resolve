# Native-caption migration and interrupted-work verification

Use only for explicitly authorized legacy-caption targets. This reference is
not permission to edit a project, change fonts, render, or migrate other clips.

## Scope and baseline

- Discover the live project ID, timeline IDs, exact build, both frame rates,
  resolution, source paths, and complete video/audio/subtitle coverage.
- Work in approved recoverable variants or behind a fresh verified `.drp`
  when original edits are explicitly approved. Backup export does not prove restore.
- Capture current active timeline, playhead, page, folder, track states, render
  queue/presets/mode/format, project settings, and content invariants before work.
- Activate each timeline before reading its playhead. Inactive timecode reads
  can return another timeline's playhead on the observed build. Serialize live
  scripting calls; wait for asynchronous page switches and read them back.
- Reconcile live state on resume before importing, adding tracks, or disabling
  legacy captions. Already-correct cues need verification, not duplicate import.

## Extract and migrate

- Extract exact text and absolute start/end frames from each authorized legacy
  clip. Resolve Fusion titles can hold text in tools/settings rather than names.
  Inspect all relevant tracks/tools; never assume one named tool covers the set.
- If reading a `.drp` ZIP, work on a copy, inspect sequence identities, and
  normalize invalid `::` XML tag tokens only in the in-memory parsing copy.
  Never execute embedded expressions or scripts to recover caption text.
  Flag dynamic/ambiguous text instead of guessing. Do not write the archive/DB.
- Account for timeline start and its actual frame rate when converting frames
  to relative SRT timestamps. Assert order, duration, and every recovered cue.
- Do not shorten, drop words, split, or retime legacy cues merely to meet house
  style when the approved migration must preserve text and timing. Report
  overlong/overlength cues as exceptions. New authoring still follows house style.
- Import through an EMPTY Subtitle track using the bare
  `{"mediaPoolItem": item}` payload. Remove stale cached pool items before
  reimporting a corrected same-path SRT. Space structural mutations and save.
- Read back every cue's exact text and absolute start/end frames before
  disabling the legacy captions-only video track. Keep its clips recoverable;
  do not delete them. Never disable a mixed track containing unrelated overlays.
- Verify native track enabled, legacy captions-only track disabled, and no
  changes to protected horizontal timelines, other captions, video/audio
  ranges, transforms, cuts, project settings, source files, or render state.

## Styling and handoff

- If the user handles fonts/styles, do not resume an older font plan, copy a
  track style, or modify SQL. Insert/verify cues and report legibility issues.
  Direct SQL requires separate explicit authorization and a closed project.
- Keep separate verdicts for cue migration, publication legibility, full audio
  listening, backup ZIP/hash integrity, and tested restore. Do not collapse
  these into a single "passed" claim.
- Use viewer screenshots or a verified burn-in preview for glyphs, edge clipping,
  contrast, face/chat overlap, duplicate overlays, and caption coverage. Native
  still export can omit captions. Label sampled-frame QC as sampled, not complete.
- Reuse an existing preview only after a fresh content/settings audit proves it
  matches the current timeline; otherwise rerender within authorization.
- AAC decode hashes may differ without timeline audio changes. Audit timeline
  properties separately; hashes and numerical metrics are not listening QC.
- SaveProject, read back each modified target, restore the state captured at
  this continuation's start, and verify it after page switches settle. Record
  exact remaining exceptions and deferred user-owned work, not blanket completion.

## Resolve 21.1 "Subtitle as Text+" timelines (Laffy Yu-Gi-Oh, 2026-11-15)

When a timeline has a disabled Subtitle track plus a video track `Subtitle as Text+` (Fusion Title clips made from those cues), the native track usually still holds the same cues. Compare the Text+ clip names and start/end with the live `GetName()` and frames of the subtitle items (an MCP `clip_where` on the subtitle track is enough), then migrate by enabling the Subtitle track and disabling the Text+ track. Do not rebuild the cues.

- **Do not read Text+ `StyledText` live.** A `TextPlus.GetInput("StyledText")` loop over 61 clips hung Studio 21.1.0.17 (Not Responding, recovered with `resolve_recover.py`). Reading `Size` on the same tools had worked minutes earlier. A DRT does not help either: its `CompositionBA` for these clips holds only comp prefs, with no text.
- **The DRT `<Name>` of a subtitle cue can be stale.** The Name kept the long pre-split phrase (`อยากรู้ไหมคะว่าผมรู้จักยูกิโอได้ยังไง` on four cues), while `GetName()` gave the edited short cue. An unchanged DRT imported back gave all 61 live texts, so the round trip is safe. Never rewrite cue text from the DRT `<Name>`; test-import once and compare `GetName()` before trusting a DRT edit.
- **Preset through DRT:** `drt_set_subtitle_preset` (track 1) -> rename the old timeline `<name>_old` -> import -> rename to `<name>` -> enable ST1 and disable the Text+ track -> compare every track (items, offsets, V1-V3 transforms, audio volume) with the old dump. Keep `_old` until the user asks to delete it.
- **Width on 9:16:** `Mitr-short-001` renders about 101 px Mitr SemiBold, so a cue over ~1000 px (`ทุกวันเสาร์อาทิตย์เลยครับ`, `เรื่องนั้นคือเรื่อง Yuki-o`) runs past the 1080 frame. Estimate every cue with Pillow `getlength` at the calibrated size, then report the cues that run over and ask before splitting them.
