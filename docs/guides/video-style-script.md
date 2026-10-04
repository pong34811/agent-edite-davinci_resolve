# Native Python video-style helper

`python scripts/apply_video_style.py --help`

## What it does

Capture constant, exposed video properties from an approved timeline clip and
apply them to explicitly identified video clips through Resolve's Python API.
It supports a reusable JSON style, dry run by default, verified DRP backup before
writes, per-property readback, rollback on failed application, protected timeline
snapshot comparisons, SaveProject and UI state restoration.

**This is not a loader for native named Video Presets.** On observed Studio
21.1.0.17 no public `LoadVideoPreset` API is present. A JSON captured from a clip
is not proof that the native preset named `vdo` was loaded. It does not copy OFX,
Fusion graphs or keyframes, does not rename/save native presets, and does not
read/write Resolve databases. Do not silently use another saved name such as
`short` when the user requests `vdo`.

## Prerequisites

- Windows Resolve with external Python scripting enabled and a working bridge.
- Run from this repository root; the helper reuses `connect_resolve` from
  `scripts/load_subtitle_preset.py`, without invoking its database workflow.
- Discover the current project/timeline and video-item unique IDs first.
- Obtain approval for the source clip and exact targets. Do not assume an
  instruction to write a helper authorizes applying it to every timeline.
- Keep source media untouched. No importing, track creation, deletion, timing
  edits, rendering, GUI actions or SQLite patches are performed by this helper.

## Capture and preview

Use `terminal` with the following command, replacing every placeholder with a
verified live ID/path. Repeat `--target-clip-id` for additional authorized clips:

```bash
python scripts/apply_video_style.py --source-clip-id "<source-video-item-id>" --target-clip-id "<target-video-item-id>" --project-id "<project-id>" --timeline-id "<timeline-id>" --capture-style "<new-style-json-path>"
```

This reads Resolve state and writes only the explicitly requested JSON file.
`--capture-style` refuses to overwrite an existing file. The current project and
active timeline must match the supplied IDs; the script never switches targets
by names or guessed selection. Targets must be video timeline items.

## Apply an approved style

First run without `--apply` and inspect matched/changed counts:

```bash
python scripts/apply_video_style.py --style-json "<captured-style-json>" --target-clip-id "<target-video-item-id>" --project-id "<project-id>" --timeline-id "<timeline-id>"
```

Then apply within the same explicit scope:

```bash
python scripts/apply_video_style.py --style-json "<captured-style-json>" --target-clip-id "<target-video-item-id>" --project-id "<project-id>" --timeline-id "<timeline-id>" --backup-dir "<approved-backup-directory>" --report "<result-json>" --apply
```

`--apply` requires a backup directory. Source/reference mode also supports
`--apply`, but a captured JSON makes the approved values inspectable and stable.
For the current clip workflow, `presets/video/approved-gif-style.json` contains
properties from an approved reference, not a decoded/native preset `vdo`. The public
example omits the live clip ID and filename; capture a fresh JSON from the exact
approved source clip when its provenance must be recorded.

## Verification and limits

- Every requested target must match the captured properties after application
  and save. False setter returns are judged by actual property readback.
- A repeat dry run must report changed_count = 0; source clips and already
  matching targets are no-ops.
- Timing, source trims/paths, clip IDs/enabled state/fades, unrelated properties,
  audio, subtitle text/frames, track states and timeline format are compared
  before/after. Only selected video-style properties may differ.
- Coupled zoom axes are temporarily unlinked while copying, then restored.
- Snapshot/DRP archive checks are not a restore test or visual/listening QC.
- Same numeric style on different GIF rasters can produce different pixel sizes.
  Inspect each GIF with the relevant subtitle visible; do not adjust the approved
  captured values silently to make a different framing judgment.
- Preserve captured properties separately from named-preset/GUI/SQL workflows.
  Loading a native preset through a database workaround requires separate
  explicit authorization and a proven format/target mapping.

Offline tests (no Resolve connection):

```bash
python -m unittest discover -s tests -p test_apply_video_style.py -v
```

Tests cover capture boundaries, dry run, readback after false setters, idempotent
re-runs, partial-failure rollback, invalid styles/targets, preservation checks,
and the real CLI help subprocess. Live verification must be reported separately.
