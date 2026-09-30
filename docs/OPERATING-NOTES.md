# Resolve operating notes for this project

These rules reconcile the imported skills; they preserve previously observed behavior and are not new live tests on the current Resolve session. Read before an edit. Current user instructions take precedence for scope.

## Local skills and activation

Core editing skills live under `.agents/skills/`. Hermes officially supports this project-local directory, with project > profile-local > external precedence. The repository must be trusted before automatic discovery. From this directory, the supported command is `hermes skills trust`; then start a new session. Trust was intentionally not changed by the collection task. Reading a local SKILL.md with `read_file` works without pretending that it is already registered. No global skills/configuration or other profiles were modified.

The backend remains the existing `davinci-resolve-mcp` installation. This repository includes skills, manuals and the source-safe contact-sheet helper, not `src/server.py`, its Python environment, Node server or MCP credentials. A command in an imported backend manual must be run from the backend installation, not assumed available here. Probe the actual attached MCP tool catalog or Resolve scripting bridge before any live use.

## Reconciled rules

| Topic | This project's rule | Why |
|---|---|---|
| Thai cue duration | At most 1.5s, three short words / about 14 Thai characters | Current house style is stricter than the imported subtitle skill's generic 2.2s example. |
| Thai typography | No inter-word spaces; preserve only appropriate Latin boundaries | Token grouping is for timing, not displayed spacing. |
| SRT placement | Empty subtitle track, bare mediaPoolItem payload | Extra placement fields can shift cues to timeline-end plus SRT offsets. |
| Corrected SRT | Remove stale pool cache entry before re-import, then verify style as well as cues | Same-path ImportMedia can reuse old parsed text. |
| Mutation rate | Start with ~1.2s between structural edits, save and verify | A historical 0.35–0.45s append-only delay is not a reliable DeleteTrack/AddTrack/Append batch policy. |
| Backup cleanup | Retain and report archives; delete only with explicit approval and a new verified backup | The rough-cut source said to clean archives automatically; other workflows correctly require permission. |
| Playback FPS | Read separately from timeline FPS; set in verified Resolve UI if necessary | Playback frame rate is not script-settable in the observed build. |
| API methods | Exact build, installed README/typed stub, then a read-only or isolated probe | Older manuals' blanket API gaps may be stale; do not treat absence from a catalog as proof. |
| Audio level | AudioVolume in dB on observed builds; enumerate/read back actual properties | Volume/Gain/Level guesses can return False silently. |
| Caption QC | Viewer screenshot or short burn-in render | ExportCurrentFrameAsStill can omit subtitle overlays. |
| Native captions | Subtitle track only; migrate only exact authorized targets | A creation preference does not authorize modifying protected legacy timelines. |
| User-owned styling | If the user handles fonts/styles, verify insertion and report legibility separately | Older font plans or easier SQL styling cannot override the current scope. |
| Playhead readback | Activate each timeline before GetCurrentTimecode; capture fresh state on resume | Inactive timeline reads can return the active timeline's playhead. |
| Page restoration | Serialize live calls; wait and read GetCurrentPage after OpenPage | A True return can precede completion of the page switch. |
| Adjustment Clip | Scripted pilot; lock all original video/audio/subtitle tracks; full range audit and rendered frames | Generator insertion can ripple other track types even when V1 looks unchanged. |

## Transform and offline-media traps

- Set transform floats (e.g. `0.25`), not strings. A setter immediately after append can return False while the value is already correct; wait/read back before another write.
- `ZoomGang=True` links ZoomX and ZoomY. Probing one can change the other.
- Fit overlays using their actual source raster and Media Pool FPS/Frames. Compare Resolve-rendered pixels, not only Inspector numbers.
- An offline overlay can replace the whole composite with Media Offline while V1 is online. Inspect overlay tracks first.
- If an offline item's GetMediaPoolItem() is None, there is no pool entry to relink. Re-import/re-place only after approval, preserving record frames, tracks, source ranges and transforms.

## Database boundaries

Subtitle track style has no supported scripting setter in the observed workflow. A style-copy database operation must export/verify `.drp`, save and close the project, take a SQLite backup, update only exact subtitle-track rows, reopen, then verify cue text/frames and style blob equality. Do not guess Inspector size from QFont pointSize. Prefer an already-matching live style and leave the database unchanged when it matches.

## Evidence and scope

For legacy subtitle migration, read the Thai subtitle skill's native-caption
migration reference. Preserve exact words and absolute frames; disable only a
verified captions-only legacy track after native cues pass. Preserve unrelated
titles/overlays and protected horizontal versions. Recheck live state before
repeating interrupted mutations. Caption insertion, publication legibility,
listening QC and DRP restore are separate verdicts.

`docs/skills-manifest.json` records original paths, source SHA-256s, copied files, local amendments, and bounded historical usage anchors. Only the current default Hermes history was examined. A load in a session mentioning Resolve is evidence of loading, not proof that the skill was used on every clip or completed an edit. No footage, render, SRT deliverable, project DB, secret, or entire conversation transcript was copied.

The current portable `.agents` source was chosen over older worktree versions. Distinct historical versions are retained under `docs/skill-variants/`; the old house-style variant lacks the newer Thai rules. A Codex-specific media-analysis wording variant was archived; the active local copy is agent-neutral.

The bundle validator checks file coverage under `.agents/`, `docs/`,
`resolve-advanced/`, `scripts/`, and `tests/`, plus the declared integration
documents. It excludes its manifest, generated validation report and Python
bytecode caches. `PLAN.md`, `WORKLOG.md`, `reference/` and `.mcp.json` are
separate editing-work context, not evidence that this collection completed any
live edit. Check those tasks independently; do not rewrite their progress from
bundle tests. Checksums detect drift against the local manifest, not malicious
changes to both a file and the manifest; they are not signed provenance.

Archive validation checks the discovered names/paths and upstream frontmatter.
Tests use `TMPDIR` when supplied, otherwise `HERMES_HOME/cache/scratch` or
the platform's default Hermes home; no system-temp fallback is needed.
The `superpowers-` directory prefix is an archive namespace, not part of the
upstream skill name. Archive scripts and all archive links are not execution-
tested by core validation; these files remain inactive historical references.

In the separate editing plan, keep the sample-approval gate authoritative.
`PLAN.md` Task 2's all-timeline font heading must not be used to bypass Task 3's
explicit sample approval. Review/reorder that plan with its owner before any
batch writes; this skill-package review does not approve the remaining clips.

## Imported references that are not prerequisites

Generic references to global `colorist`, `colorist-assistant`, `editor`, `assistant-editor`, `online-editor`, `post-supervisor`, `deliverables-knowledge`, `quality-control`, and `qc-domain` do not prove those skills are installed here. No copies were found in the inspected primary skill roots. Use the included craft guides and actual task requirements instead of pretending to load unavailable skills. Related workflow archives may also reference their parent plugin; they are preserved context, not a claim of a configured plugin.

Official Hermes reference: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills#project-local-skills
