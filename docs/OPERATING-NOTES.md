# Resolve operating notes for this project

These rules reconcile the imported skills; they preserve previously observed behavior and are not new live tests on the current Resolve session. Read before an edit. Current user instructions take precedence for scope.

## Local skills and activation

Active skills live under `.agents/skills/`: 17 curated core editing skills plus 29 supporting workflow/reference skills. The supporting set includes profile imports and namespaced Superpowers copies; their presence does not prove they were used for a Resolve edit. Hermes officially supports this project-local directory, with project > profile-local > external precedence. The repository must be trusted before automatic discovery. From this directory, the supported command is `hermes skills trust`; then start a new session. Trust was intentionally not changed by the collection task. Reading a local SKILL.md with `read_file` works without pretending that it is already registered. No global skills/configuration or other profiles were modified.

The backend remains the existing `davinci-resolve-mcp` installation. This repository includes skills, manuals and the source-safe contact-sheet helper, not `src/server.py`, its Python environment, Node server or MCP credentials. A command in an imported backend manual must be run from the backend installation, not assumed available here. Probe the actual attached MCP tool catalog first; use the Resolve scripting bridge only when the MCP is shown not to cover the task (see `AGENTS.md` "Tool selection" and `scripts/resolve_preflight.py`).

## Reconciled rules

When you learn a new rule, add a row here (see `.agents/skills/project-learning/SKILL.md`). Script catalogue: `scripts/INDEX.md`.

| Topic | This project's rule | Why |
|---|---|---|
| Tool selection | MCP catalog first; scripting-API script only after a stated `MCP-GAP:` line; shared `scripts/resolve_common.py` | Agents skipped the MCP and wrote ad-hoc scripts, each with its own copy of the connect code. |
| MCP updater path | If `scripts/check_mcp_update.py` reports the configured checkout is missing, verify the active install and correct `.mcp.json` before updating; do not clone or guess a replacement path | A stale Desktop path caused a `FileNotFoundError` before the updater could compare versions. |
| Offline intake and gates | Use `prepare_edit.py` and `edit_workflow.py`; see `docs/EDIT-WORKFLOW.md`. Prepared intake, valid plans and reconciled reviewer evidence are separate verdicts; never promote them to live audiovisual QC. | Reusing one manifest and explicit gate reduces repeated probes and prevents missing measurements being treated as passes. |
| Intake cache and coverage | Reject malformed cache/probe/receipt JSON; `--refresh` bypasses probe cache; fingerprint actual selected frame paths; skip Windows symlinks/junctions while allowing cloud placeholders; reject unparsed SRT blocks. | Review reproduced stale sheets for external frame paths, skipped broken cues and junction traversal outside the source tree. |
| Thai cue duration | At most 1.5s, three short words / about 14 Thai characters | Current house style is stricter than the imported subtitle skill's generic 2.2s example. |
| Thai typography | No inter-word spaces; preserve only appropriate Latin boundaries | Token grouping is for timing, not displayed spacing. |
| SRT placement | Empty subtitle track, bare mediaPoolItem payload | Extra placement fields can shift cues to timeline-end plus SRT offsets. |
| Corrected SRT | Remove stale pool cache entry before re-import, then verify style as well as cues | Same-path ImportMedia can reuse old parsed text. |
| Mutation rate | Start with ~1.2s between structural edits, save and verify | A historical 0.35–0.45s append-only delay is not a reliable DeleteTrack/AddTrack/Append batch policy. |
| Backup cleanup | Retain and report archives; delete only with explicit approval and a new verified backup | The rough-cut source said to clean archives automatically; other workflows correctly require permission. |
| Playback FPS | Read separately from timeline FPS; set in verified Resolve UI if necessary | Playback frame rate is not script-settable in the observed build. |
| API methods | Exact build, installed README/typed stub, then a read-only or isolated probe | Older manuals' blanket API gaps may be stale; do not treat absence from a catalog as proof. |
| Resolve 21.1 reference routing | Read `docs/guides/resolve211-agent-guide.md`; version-scope speed, transition, multicam and DCTL limits; distinguish documented APIs, attached actions and live validation | Older skills denied APIs that the 21.1 stub and current catalog expose; an empty version-gate list does not verify their behavior. |
| Vendor stub hashes | Compare raw bytes and CRLF-to-LF normalized bytes before declaring a stale reference; retain original provenance | The Windows 21.1 stub matched Studio MCP byte-for-byte; its raw CRLF hash differed from the recorded LF hash while normalized content matched. |
| Audio level | AudioVolume in dB on observed builds; enumerate/read back actual properties | Volume/Gain/Level guesses can return False silently. |
| Caption QC | Viewer screenshot or short burn-in render | ExportCurrentFrameAsStill can omit subtitle overlays. |
| Native captions | Subtitle track only; migrate only exact authorized targets | A creation preference does not authorize modifying protected legacy timelines. |
| User-owned styling | If the user handles fonts/styles, verify insertion and report legibility separately | Older font plans or easier SQL styling cannot override the current scope. |
| Playhead readback | Activate each timeline before GetCurrentTimecode; capture fresh state on resume | Inactive timeline reads can return the active timeline's playhead. |
| Page restoration | Serialize live calls; wait and read GetCurrentPage after OpenPage | A True return can precede completion of the page switch. |
| Adjustment Clip | Scripted pilot; lock all original video/audio/subtitle tracks; full range audit and rendered frames | Generator insertion can ripple other track types even when V1 looks unchanged. |
| Zoom Focus QC | ยืนยัน Armigon ทุกช่วง; ตรวจภาพเต็มเฟรม/ขอบดำ/blur; อ่าน `Center`/`Size` keyframe และ `MotionBlur`; เทียบเฟรมเดียวกันเมื่อเปิด/ปิด `Adjustment Clip` | ต้องแยก source crop หรือ overlay ที่บังอยู่เดิมออกจากผลของ zoom และห้ามสรุปว่า motion ไม่มีอาการสั่นจากภาพ still เพียงอย่างเดียว |
| Enrichment sequence | Draft on copies first, verify, then promote into originals; keep one idempotent apply path | Direct-to-original batch edits leave no reviewable stage and cannot be re-run safely. |
| Promotion identity | Match an existing placement by (asset name, record frame) and skip verified items | A rerun after a partial failure would otherwise duplicate clips. |
| GIF conform | Read the appended range and enforce 1.5–2.5s on the real range, allowing a few frames of conform drift | Resolve conformed a GIF 2 frames shorter than the requested hold and a strict equality check aborted a good promotion. |
| Subtitle items | Native subtitle items have no Media Pool entry; never flag them as offline | Treating a legitimate null as a media fault produced ~960 false "high" findings. |
| Thai cue length | Check every cue's end against the audio; numerals and digits-only cues need an explicit end | A "1,950" cue defaulted to 0.3 s while spoken for ~1.5 s. |
| MCP timeline mutators | Expect an auto-archived `Timeline N_archived_vNN` per mutating call; report it, delete only on request | `timeline.add_track` created a copy and left the Media Pool on `Archive`. |
| Preset backup path | Pass `--backup-dir` as an absolute path (now resolved in the helper) | Resolve's ExportProject fails silently on a relative path. |
| Whisper model | `large-v3` on the raw audio; distrust `large-v3-turbo` on game audio | Turbo invented ~20 s of text; check `avg_logprob` and re-run the window alone. |
| GIF hold | Validate every GIF (Resolve 25 fps, >= 1.5 s) before mutating the timeline | A 1-second GIF aborted a run after BGM/SFX were already placed. |
| Zoom framing | Corner avatar: no black band, slight off-centre; keep the hair tip inside | Centre-exact framing shows a band; the first pass clipped the ahoge. |
| Font audit | Scan subtitle cue blobs as UTF-16 as well as ASCII | A track marked Mitr Bold still carried hidden Open Sans metadata in some cues; an ASCII-only audit missed it. |
| Fusion Text+ reads | Read exported `.drp`/DRT, not live Fusion tools, on Aomi-mama-class projects | A live TextPlus read probe hung Resolve (Aomi debut project, 2026-09-30). |
| Archive deletion | Export one fresh verified `.drp`, report the exact files and bytes removed, and say there is no longer a rollback point | Deleting archives on request is fine; deleting them silently is not. |
| Enrichment re-run | After an aborted `apply_enrichment_d22` reset the Media Pool folder and pre-validate GIFs with PIL (>= 1.5 s after conform) | The script imports into its bin and leaves the current folder there before it checks GIF length. |
| Focus insert on 21.1.0.17 | `InsertGeneratorIntoTimeline` goes to V1 (ripples it) if V1 is unlocked and fails if V1 is locked; for N clips on a new track use DRT injection (`drt_focus_track` internals, clone Element per range), import, then set Fusion Transform | `apply_vtuber_zoom --apply` failed at the first insert on day 25; a manual unlocked insert split V1 on the throwaway copy. |
| Enrichment append on one audio track | Two SFX whose trimmed ranges overlap on the same track push the later one to the earlier one's end (day 25: clap 1885 -> 1936); keep SFX >= their trimmed length apart or use another track. `ExportCurrentFrameAsStill` needs an absolute path | `AppendToTimeline` does not overlap on a track; a relative still path returns False silently. |
| DRT import name | `ImportTimelineFromFile(drt, {'timelineName': X})` on 21.1.0.17 names the timeline after the file (`patched`); rename by unique ID right after import and read the name back | A stage keyed on the requested name hit KeyError on the Bunny Girl copy (2026-10-17). |
| Overlay append range | `AppendToTimeline` endFrame is exclusive for MOV video and MP3 audio on 21.1.0.17: pass `endFrame = duration` for back-to-back chapter overlays, then read GetStart/GetEnd | `endFrame = duration - 1` left a 1-frame gap after every chapter overlay. |
| BGM loop splice | Loop a short BGM by finding its repeat lag (spectral self-similarity, then sample cross-correlation) and cutting both pieces at a near-silent frame inside the repeated section; set `SetFades` for the head/tail only | Two pieces can't overlap on one audio track, so a crossfade isn't possible there; a silent-break splice in a repeating section gave no click (Bunny Girl, 2026-10-17). |
| Adjustment Clip head extension | An Adjustment Clip whose head is dragged earlier keeps a Fusion comp sized to its old length ("No frame available for MediaOut1"); a new `AddFusionComp` still fails to render the added head. Rebuild the track from fresh template clips at the hand-set ranges via DRT (`scripts/drt_rebuild_focus_track.py`), then probe-render each range | Bunny Girl V2 clip 5104-5352 rendered only its original 5206+ part (2026-10-17). Tail extension and trimming were fine. |
| Hand-copied zoom clips | Before a final render, rebuild every Fusion Adjustment Clip the user copied, trimmed or extended from fresh template clones via DRT (`assemble.py rezoom2` keeps Inspector-only clips); give every probe render a timeout and `StopRendering` | A copied-then-trimmed clip rendered its first ~40 frames, then failed the full render at 82% and hung a probe at 0% until scripting stopped answering (Bunny Girl, 2026-10-17). |
| Skill manifest refresh | `refresh_skill_manifest.py` / `verify_skill_bundle.py` skip gitignored files (`scripts/scratch/*`) and drop declarations of removed skills; move uninstalled upstream skills out before a release rather than hand-editing the manifest | Scratch files were listed in the manifest, so every scratch edit broke the bundle check (2026-10-17). |
| HyperFrames CLI pin | When `npx --no-install hyperframes` asks for a newer release than the one cached, run the cached `npm-cache/_npx/<hash>/node_modules/hyperframes/bin/hyperframes.mjs` with `node` instead of downloading | A new upstream release (0.8.169) made `npx --no-install` refuse to run the cached 0.8.168 overnight (2026-10-18). |
| 9:16 from a 16:9 VTuber shot | Duplicate the finished timeline, apply `p2_9x16_build.RASTER`, set V1 Zoom = 1920/607.5 and Pan for the face column, re-aim Fusion zooms (1.2x is enough on a narrow frame), then confirm the preset really applied (`load_subtitle_preset_auto` dry run says `already_matches=True`) before burn-in-rendering a short range to measure the subtitle position | The position is not readable from the preset bytes. A UI preset load did not stick, so the first burn-in test measured the default style (y 1500-1620); with Mitr-short-001 applied the cues sit at y ~990-1060 (Bunny Girl, 2026-10-18). |
| Resolve Thai ASR | Set `transcriptionLanguage` to `th` (`Thai` is rejected) before `MediaPoolItem.TranscribeAudio`; if a long clip degrades into a repeated token, cut that window to a WAV, import it into a scratch bin, transcribe it alone and delete the bin | Auto-detect returned English; the 95 s pass repeated "ฟรรรม" over 61-89 s while the 32 s window alone came out clean (Bunny Girl ep2, 2026-10-18). |
| DRT zoom template without Fusion | `.hermes/day23-drt/template.drt` Adjustment Clips import with no Fusion comp and no Inspector properties; run `AddFusionComp`, add one Transform between MediaIn/MediaOut, then set `window_transform` values and read back | `retune_vtuber_zoom` failed "clip has no Fusion comp"; `SetProperty('ZoomX')` read back 0 (Bunny Girl ep2, 2026-10-18). |
| Preset auto relaunch | After `load_subtitle_preset_auto --apply`, if the relaunched Resolve shows the project but scripting returns None, ask the user to quit and reopen Resolve; then confirm with the dry run (`already_matches=True`) | The script's relaunched instance never answered scripting for 15+ minutes; a user restart fixed it (2026-10-18). |
| Mix headroom | Measure the source dialogue peak first; with a -1.2 dBFS voice, BGM -19 dB + SFX reached +0.01 dBFS, so drop A1 by 1 dB rather than the SFX | Lowering the whoosh 2 dB did not move the peak; A1 -1 dB gave -0.6 dBFS / -15.2 LUFS (Bunny Girl ep2). |
| Replacing a placed media file | Never overwrite a file that is already in the Media Pool; write the new render under a new name (`ch01b.mov`), delete the old timeline clips and pool items, import the new file and place it at the same record frames | Overwriting `ch01.mov` in place made the 9:16 render fail at 0% with "Error decoding full resolution media" (Bunny Girl ep2, 2026-10-18). |
| 9:16 zoom vs subtitles | With `Mitr-short-001` (cues at y ~990-1060) and the face column filling the top, a top-anchored Fusion punch-in pushes the chin into the subtitle line; use 1.1x (not 1.2x) and keep slam words at y >= 1160 and the info band at y >= 1520 | At 1.2x the chin dropped onto the cues, and slam words at y 1100 touched them (Bunny Girl ep2 9:16). |
| Drive manifests | Enumerate `G:` asset roots with `os.scandir` into a manifest | `ls` on Drive stalled over 2 minutes. |

## Transform and offline-media traps

- Set transform floats (e.g. `0.25`), not strings. A setter immediately after append can return False while the value is already correct; wait/read back before another write.
- `ZoomGang=True` links ZoomX and ZoomY. Probing one can change the other.
- Fit overlays using their actual source raster and Media Pool FPS/Frames. Compare Resolve-rendered pixels, not only Inspector numbers.
- An offline overlay can replace the whole composite with Media Offline while V1 is online. Inspect overlay tracks first.
- If an offline item's GetMediaPoolItem() is None, there is no pool entry to relink. Re-import/re-place only after approval, preserving record frames, tracks, source ranges and transforms.

## Database boundaries

On observed Resolve 21.1.0.17, Subtitle track preset loading has no public scripting setter. Prefer the exact user-approved saved preset over guessed font/size/position values. `scripts/load_subtitle_preset.py` reads preset bytes with a Python/SQLite workaround, not a native preset API; it is currently dry-run only and its `--apply` flag stops before any database write because it cannot verify Resolve has fully exited. Do not bypass that block. Any future writer requires explicit database-write authorization, a verified `.drp`, confirmed Resolve shutdown, exact target-row mutation, and readback of cue text/frames, video/audio coverage, track states and style bytes. Do not guess Inspector size from QFont pointSize. Leave already-matching styles unchanged.

Preset names are exact: `Mitr-Font` and `Mitr Font` are not interchangeable without approval. An empty `--list` can mean the preset lives in another library's User.db; discover/read that source and use an approved `--user-db` rather than switching the project's active library. Do not use `--orientation` without `--timeline` for a single-timeline request: it implies all timelines. Full workflow: `.agents/skills/thai-subtitles-resolve/references/srt-insertion-and-presets.md`.

After any insertion-script failure, re-read the live subtitle track before retrying; append may already have succeeded. Use `Project.SetCurrentTimeline`, not `ProjectManager.SetCurrentTimeline`.

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
bytecode caches. `work/PLAN.md`, `work/WORKLOG.md`, `reference/` and `.mcp.json` are
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
`work/PLAN.md` Task 2's all-timeline font heading must not be used to bypass Task 3's
explicit sample approval. Review/reorder that plan with its owner before any
batch writes; this skill-package review does not approve the remaining clips.

## Offline review and enrichment tooling

The reusable scripts added by the enrichment work, all run from the repository root with `python -m`:

| Script | Purpose |
|---|---|
| `scripts/resolve_preflight.py` | MCP-first verdict (`USE_MCP`/`FALLBACK_SCRIPT`/`BLOCKED`) for a needed tool or API method. |
| `scripts/review_enrichment_readonly.py` | Read-only inventory of every timeline, track, item and asset library. |
| `scripts/build_offline_review.py` | Per-timeline ffprobe/ffmpeg packets: caption map, mixed-audio metrics, sampled frames, HTML contact sheet. |
| `scripts/build_offline_asset_draft.py` | Subtitle-keyed SFX/GIF/BGM shortlist plus a local human review page. |
| `scripts/apply_vdo_python.py` | Capture an approved `vdo` GIF's exposed values and apply them by exact project/timeline/clip IDs. |
| `scripts/enrich_timelines_python.py` | Native Python batch enrichment onto copies; dry-run default, BGM-only when no cue is defensible. |
| `scripts/promote_drafts_to_originals.py` | Idempotent promotion of verified drafts into originals by exact IDs. |
| `scripts/anomaly_sweep.py` | Read-only structural sweep over every timeline. |
| `scripts/cleanup_backups.py` | Export one fresh verified `.drp`, then delete the named archives. |

Media-analysis APIs stay out of this path: the offline route is ffprobe/ffmpeg plus the saved native
subtitle map, so no provider quota or key is involved. Local ASR (faster-whisper) is a hint only —
Thai speech over game audio transcribed unreliably and must not be treated as a caption or beat source.

The `.hermes/` directory holds this project's working artifacts (review packets, drafts, reports,
renders, `.drp` archives) and is gitignored; it is not part of the installable bundle.

## Imported references that are not prerequisites

Generic references to global `colorist`, `colorist-assistant`, `editor`, `assistant-editor`, `online-editor`, `post-supervisor`, `deliverables-knowledge`, `quality-control`, and `qc-domain` do not prove those skills are installed here. No copies were found in the inspected primary skill roots. Use the included craft guides and actual task requirements instead of pretending to load unavailable skills. Related workflow archives may also reference their parent plugin; they are preserved context, not a claim of a configured plugin.

Official Hermes reference: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills#project-local-skills

## External standalone skills

| Topic | This project's rule | Why |
|---|---|---|
| HyperFrames core skill install | Preserve the upstream copies and run `scripts/refresh_skill_manifest.py`; report its local-reference verdict separately from Codex skill discovery. The current `npx skills add` core set is discoverable, while this repo's verifier reports 18 unresolved local reference paths in those copied skills. | A successful skills install does not imply this repo's bundle validator can resolve every upstream reference. |
