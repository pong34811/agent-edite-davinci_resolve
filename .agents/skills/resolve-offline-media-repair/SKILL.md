---
name: resolve-offline-media-repair
description: Use when Resolve media is offline though the file exists.
version: 0.1.0
platforms: [windows]
metadata:
  hermes:
    tags: [Resolve, Relink, Transcode]
---

# Resolve media offline although the file exists

Complements the project skill `resolve-conform`. Follow the repository's
`AGENTS.md`: inspect the live MCP catalog first, use the scripting API only
after recording an `MCP-GAP:` line, and keep any script under `scripts/` using
`scripts/resolve_common.py` and `preserved_state(resolve)`.

## Procedure

1. Confirm the path exists, then use `ffprobe` read-only (codec, fps, duration) and compare with a known-online sibling. A correct path does not prove Resolve can decode the media; diagnose the exact clip and codec before proposing a change.
2. If a replacement is reported, compare content hashes (and file size as a quick check) against the original. Timestamps, including ctime, do not prove that bytes changed.
3. Do not transcode with FFmpeg or replace source media through an external editor. First check the Resolve MCP for a supported relink/repair action. If the MCP lacks it, record the required `MCP-GAP:` and use only a verified Resolve scripting-API method under the repository rules. Never invent `ReplaceClip` or other methods; check the installed API stub and probe read-only first.
4. If recovery requires optimized/proxy media that the supported MCP/API cannot create, stop with `BLOCKED` and ask the user to generate it in Resolve. Do not use GUI automation or bypass the tool mandate.
5. Resume exports only after the batch exporter confirms a prior `Complete` job and validates the corresponding output. A failed/cancelled job or an unexplained existing file is not proof of a usable export.

## Pitfalls

- Pool entries with an empty File Path are timelines, not offline media; do not relink them.
- Keep Resolve scripting-API probe or mutation scripts under this repository's `scripts/`, connect through `scripts/resolve_common.py`, and use `preserved_state(resolve)` for mutations. Do not put Resolve mutation scripts in Hermes scratch.
- `ffprobe` and `ffmpeg` are permitted here only for read-only media analysis or render-QC checks; they are not an editing/transcode path.

## When the user says "continue" with no context

Do not ask or guess: run `session_search` (query by the filename/topic, sort newest) and read the matching prior session before acting. The user expects the previous session's goal (here: finish the batch export) to be recovered from history.
