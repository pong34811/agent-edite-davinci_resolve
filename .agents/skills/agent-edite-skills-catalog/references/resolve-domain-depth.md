# Resolve domain depth — build gates, offline catalogs, gotchas

Source: `.agents/skills/resolve-*/SKILL.md` (v0.3.0 family). Companion to
`references/domain-resolve-skills.md`, which carries the routing table and the
shared rules. Load this one when a domain task needs the specific gate list, the
offline action catalog, or the gotcha that bites.

## The gate-reading ritual every domain skill repeats

Read `resolve_control get_version` → `build.unavailable_on_this_build` before
offering a gated surface; `check_version_support` asks about one named symbol.

- An empty `unavailable_on_this_build` means **nothing recorded is missing**, not
  that everything exists — most of the API has never been version-bisected.
- A symbol with no gate returns `unknown`, which means **probe it**.
- Probe with `name in dir(obj)`, **never bare `hasattr`**: on a Resolve object
  `hasattr` returns `True` for every name, real or invented.
- The offline `drx` / `project_db` / `conform` / `drt` / `media` routes are **not**
  version-gated — they read and write files, so they work regardless of the build
  attached, and are the fallback when a live surface turns out to be missing.

## `resolve-color` — gates, catalog, gotchas

Gated: `TimelineItem.ResetAllNodeColors` (20.2) — if absent, clear node colors one
at a time via the `graph` node-color setter, or leave them.

**The frame-first rule (non-negotiable, AGENTS.md):** before applying any grade,
look, shot match, LUT, CDL, DRX, or copied grade to a real timeline, inspect
representative Resolve-rendered frames (thumbnails, contact sheets, Gallery
stills, marker frames, scratch-only visual report). Compare bypass/current/after
at matched timecodes when the API allows, restore the prior version/node state
after any temporary bypass, preserve a recoverable grade version, and report which
frames informed the change. Never grade from metadata, graph availability, or a
style label alone unless the user explicitly asks for a blind/global pass.

**Offline `drx` catalog** (frame-stats → arithmetic → `.drx`; all local,
deterministic, and they **refuse** to fabricate a match rather than emit a silent
no-op; extraction and apply are the caller's job):

| Intent | Action |
|---|---|
| Match toward a reference still | `match_to_reference` (affine mean/std, skin-line gated, luma-preserving) |
| Within-camera drift | `level_clips` (exposure/WB to a group hero) |
| Cross-camera skin cohesion | `skin_match` (skin-gated; throws on log/wrong-space frames) |
| B-roll cohesion | `shot_match` (gray-world neutralize or hero match) |
| Known-neutral patch / gray card | `white_balance_match` |
| Black/white points to a hero | `contrast_normalize` |
| Saturation cohesion | `saturation_match` |
| Shadow cast | `black_balance` |
| Import ASC CDL (`.cc`/`.ccc`/`.cdl`) | `cdl_io` |
| Copy a Body look | `grade_transfer` |
| Attach a `.cube` LUT to a node | `lut_apply` |
| Season/host look | `author_look` / `carry_look` |
| Read frames | `scope_read` (parade/vectorscope/black-balance/clip%), `intent_tags` (low_key / motivated_warm, to exclude from neutralize), `gamut_legal` (broadcast-legal, measurement only) |
| Verify | `verify_grade` (intended vs applied → landed/drifted/missing) |

**Did the grade damage the image?** `verify_grade` asks *did Resolve apply what I
asked*; `media_analysis(action='assess_grade', params={source_path, graded_path |
 lut_path, time_seconds, working_space})` asks *is the result any good* — a grade
can land perfectly and still be flat, milky, crunchy or banded. Deterministic
numpy on a decoded frame of the **real** result (a rendered file, or the source
pushed through the LUT by ffmpeg) — never a simulated transform, because LUT
interpolation and encode rounding are where banding is introduced. Returns
`acceptable`, `flags` (each with a remedy), raw measurements, and a
`grade_shift_delta_e2000` magnitude. Flags: `flat`, `milky`, `washed_out`,
`noisy`, `clipped`, `posterized`, `banding`. **Display-referred only** — ACEScct /
S-Log3 / LogC are *refused*, not converted; convert first, then re-run.

Cross-server gotchas:

- **Grade value space** — `drx` `generate`/`merge` default to `space:'ui'`
  (Resolve PANEL units; saturation 0–100, neutral 50). Pass `space:'drx'` only for
  raw internal floats. Decoded values are ground truth only for the calibrated
  set — check the `valueFidelity` marker.
- **Hue-axis curves** — naive `[0,1]` point lists are auto-canonicalized into the
  verified bezier cage. If a result carries a `warnings` array, the curve went
  through raw and will render **FLAT** — surface it, do not ship silently.
- **Apply targeting** — `safe_apply_drx` defaults to video track 1 / item 0;
  **always pass `track_type`/`track_index`/`item_index` explicitly**, and grab a
  still/`.drx` backup first (it does not snapshot). `ApplyGradeFromDRX`
  *replaces* the graph — no append mode.
- **Relayout ("Cleanup Node Graph", no UI API)** — single clip live: grab still →
  `drx(action="relayout")` → `graph.reset_all_grades` → `safe_apply_drx` with
  explicit indices (a same-structure apply keeps the OLD layout, so the reset is
  required). Whole project offline: `project_db(action="relayout_node_graphs")`.

## `resolve-conform` — gates, engine, gotchas

| Surface | Needs | If absent |
|---|---|---|
| `MediaPoolItem.LinkProxyMedia` | 17.0 | No script-side proxy attach |
| `MediaPoolItem.LinkFullResolutionMedia` | 20.0 | Cannot swap proxies back to full-res from a script |
| `MediaPoolItem.ReplaceClipPreserveSubClip` | 20.0 | Replacing a clip loses sub-clip boundaries; relink by path instead |
| `MediaPoolItem.MonitorGrowingFile` | 20.0 | No growing-file support during ingest |
| `MediaPoolItem.GetTimeline` | 21.0.4 | Cannot ask a clip which timelines use it; walk timelines and collect their items |

Live essentials: inspect before touching (`probe_timeline_structure`,
`detect_gaps_overlaps`, `source_range_report`, `conform_boundary_report`);
interchange via `export_timeline_checked` / `import_timeline_checked`
(temp-guarded) — **`drt` is the only lossless project-native round-trip**.
**XML import through the scripting API goes _offline_** (missing media/generators
abort the import); use `import_timeline_checked` with media **sanitize**
(FCP7/FCPXML) so the API imports with links intact, then exact-path relink — and a
running MCP server must be **restarted** to pick up the sanitize fix. Missing
media: `detect_missing_media` → `build_relink_plan` (read-only, bounded; skips
broad scans when the source volume is unmounted) → execute only via
`media_pool.safe_relink` with approved paths.

**Offline `conform` engine** QCs a conform with **frame-oracle math, not filename
matching** — it catches a clip that relinked to the wrong-but-similarly-named
source. It also does: reverse/retimed subclip repair (reversed `source_start` =
`masterFrames − 1 − endoffset`, live-validated, DB-level repair); sequence lineage
store + diff (hashed snapshots, rollback); per-cut frame QC (oracle-frame vs
reference-render, scale-corrected, red/yellow/cyan verdicts — each cut judged at
the first frame CLEAR of its transition windows, because inside one the reference
is a blend or black for a fade); and reference-render compare (`REF_OFFLINE`
verdict when a burn-in-free reference exists).

**Carrying grades across a re-conform** — native ColorTrace keys on
timecode/name/order inside one project and gives up on renames, reorders, retimes
and stringouts. The MCP path is two calls:

1. Advanced server, no Resolve needed: `color_trace plan` with
   `sourceProjectName`/`sourceTimeline` (graded) and
   `targetProjectName`/`targetTimeline` (the new cut), plus `emitDir` under the
   system temp dir. Projects in a **Postgres / network / cloud library** have no
   `Project.db`: export each with `project_manager safe_project_export`
   (`allow_non_mcp_name: true`, works without loading the project) and pass
   `sourceDrp` / `targetDrp` instead. It matches on media identity (pool id / file
   path / reel / file name + source-range overlap) and only falls back to names.
   Read `summary.byMethod`, `ambiguous`, and each match's `confidence`; it writes a
   lossless `.drx` per graded match and returns `planPath`.
2. Live server: open the target project and timeline, then
   `timeline_item_color apply_trace_plan` with `plan_path` and `dry_run: true` for
   the resolution table (every entry `apply` or `skip` + reason); re-call without
   `dry_run` for a confirm_token, then with it to apply.

Gotchas: for Resolve 19.1.3 set `DbPrjVer` 17 → 16 when authoring a `.drt` or the
import can fail. `project_db` patches require the project **CLOSED** in Resolve
plus `iConfirmProjectClosed:true`; every write auto-backs-up and read-back
verifies, and Resolve caches open projects in memory — after patching, **fully
QUIT and relaunch** Resolve or the change is invisible. AAF is an honest refuse in
`editorial.parse_interchange`, not a silent empty result. Optional native deps gate
some actions (`better-sqlite3` for lineage/reverse/DB, `sharp`/ffmpeg for frame
compare) — call the advanced `capabilities` tool.

## `resolve-delivery` — targets, render, QC

**Delivery targets (the short path):** `list_delivery_targets` →
`prepare_delivery_job(target, target_dir)`. Ask for `prores422hq_master`,
`dnxhr_hqx_master`, `h264_1080p_web`, or an alias (`youtube`, `tiktok`, `avid`,
`stems`). **One definition emits BOTH the Resolve render settings and the
`deliverable_qc` spec** — QC the finished file against the returned `qc_spec`, do
not hand-write a second spec.

- Format/codec resolve against the **live** matrix; an unsupported target fails
  with the available lists and never silently substitutes. Use
  `check_availability: true` to see what this install supports.
- Image-sequence targets return `qc_spec: null` — `deliverable_qc` probes one file
  and a sequence is many. Expected, not a gap.
- Bitrate is deliberately unset (Resolve has no bitrate key); pin quality yourself
  via `settings` if a spec demands it.
- **Programme loudness is a separate projection** — a target names a standard via
  `overrides: {loudness_standard: "ebu_r128"}` and the resolve step returns a
  `loudness_target` alongside `qc_spec`; hand `loudness_target.target` to advanced
  `loudness_qc`. `render(action='list_loudness_standards')` lists them.

Live render essentials: discover → validate → apply → queue:
`probe_render_matrix` (formats/codecs/res) → `validate_render_settings` →
`safe_set_render_settings` (dry-run capable) → `prepare_render_job` (adds a job,
does **not** start it). Format AND codec accept display names or ids; a rejected
pair is a hard error with the available codecs — it never queues a job in the
previously set codec. Render lifecycle helpers require **temp output dirs by
default**; real delivery paths need explicit lower-level actions.
`GetRenderSettings` readback is version/page dependent. `safe_quick_export` forces
`EnableUpload=False` and needs `allow_render=True` before it actually renders.

**Pin the base render state with `prepare_render_job(from_preset=...)`:**
`SetRenderSettings` applies your keys *on top of* whatever the Deliver page holds
rather than replacing it, and a loaded preset carries more state than the keys you
pass — an Audio Only preset plus an explicit `ExportVideo: true` is the classic
way to ship a batch with the wrong output.

QC tools **refuse rather than fabricate** — a "refused" result means missing file,
wrong spec, or a metric it cannot honestly compute; read it, don't retry blind.
`deliverable`/`media` QC needs **ffmpeg + ffprobe on PATH** (GPL, not bundled) —
call the advanced `capabilities` tool for live status. Deliverable gates never
auto-clear; surface the per-field verdict to a human.

## `resolve-audio` — rough mix first, then buses

If the ask is "make this sound balanced" rather than "route these buses", start
with `media_analysis mix_plan` (Python server, no Resolve needed): give it the
dialogue stems and it derives the dialogue-normalisation gain, the music-bed level
under it, and ducking windows from the dialogue's own silence — then renders a
premix and **measures it**, so you report the loudness achieved rather than the
gain arithmetic. `dry_run` defaults to true: show the gains and window count
first. On a full-programme standard (`ebu_r128`, `web`) a measured programme trim
lands the whole mix on target; on `ott_dialogue_gated` it deliberately does not
trim, because dialogue is the figure being graded. Flags (`loudness_off_target`,
`true_peak_over`, `clipped`) come back with remedies and are **never
auto-corrected** — report them.

- **Named loudness standards live with the delivery targets** (`web`, `podcast`,
  `ebu_r128`, `atsc_a85`, `ott_dialogue_gated`) via
  `render(action='list_loudness_standards')`.
- **`plan_silence_ripple` calibrates its own gate.** Omit `threshold_db` and the
  threshold is measured from that clip's own dynamics (`astats` trough vs peak),
  per item, reported in `calibrations[]`. A fixed −30 dB under-detects on quiet
  location sound and over-cuts a noisy room. When trough and peak are not
  separated, no threshold distinguishes speech from room: the item is **kept
  whole** and the reason surfaced (a −30 dB default on a −33 dB programme reads as
  silent end to end and would remove the entire clip). Pass `threshold_db`
  explicitly to override; it is honoured untouched.
- Timeline audio `SetProperty` (e.g. `Volume`) can return false for some generated
  item types; `AutoSyncAudio` depends on media + Resolve's sync engine.
- **The public API does not expose Fairlight mix automation curves or plugin
  graphs.** The whole-mix preset workaround is the only write path there is:
  `GetFairlightPresets` + `ApplyFairlightPresetToCurrentTimeline`, applying a saved
  mix wholesale — both require **Resolve 20.2.2+** and are absent on 19.1.3
  (confirmed live). On an older build the per-parameter gap is the entire story;
  say the build is too old rather than suggesting a call that will not be there.
- The **AI Audio Assistant** (one-click auto-mix) is not scriptable on any build —
  no method exists on `Resolve`, `Project`, `Timeline` or `TimelineItem`.

## `resolve-fusion` — author offline, apply live

| Job | Server | Tools |
|---|---|---|
| Build/edit a comp on a **running** timeline item | `davinci-resolve` (live) | `fusion_comp` (`probe_fusion_comp`, `safe_add_tool`, `safe_set_inputs`, `safe_connect_tools`, `fusion_boundary_report`) |
| Author a `.comp` from a spec/template with **no Resolve open** | `davinci-resolve-advanced` | `fusion` (`generate`, `generate_from_template`, `list_templates`, `to_api_calls`) |

Flow: author/verify offline (`fusion generate` / `generate_from_template` → a
`.comp`, or `to_api_calls` → the ordered tool/input/connection calls) → apply live
(`safe_add_tool` → `safe_set_inputs` → `safe_connect_tools`; the `to_api_calls`
output maps directly onto those). **Probe first** (`probe_fusion_comp` /
`probe_fusion_tool`) — tool availability and input readability vary by
Resolve/Fusion build, and some inputs coerce or are write-only. Bulk mutation needs
timeline scope, not the active Fusion page. Depth stays in
`docs/kernels/fusion-composition-kernel.md`.

## `resolve-media-pool` — verify offline, import live

Live tools: `media_pool` (`safe_import_media|sequence|folder`, `organize_clips`,
`normalize_metadata`, `safe_relink|unlink`, `link_proxy_checked`, `set_clip_marks`,
`setup_multicam_timeline`). Offline `media` (needs ffmpeg + ffprobe on PATH):
`ingest_verify` (hash seal / verify / dupes-by-hash — chain of custody),
`media_inventory` (fps / codec / colorspace / TC + card-gap report), `sync`
(picture↔sound TC alignment + drift / MOS), `relink_manifest`, `rename_plan`
(**refuses camera originals**), `reel_normalize`, `turnover_package`,
`project_hygiene`. Rule of thumb: **verify + inventory the card offline before
importing, then import and organize live.**

- Non-media files are not imported; the kernel never creates proxies, transcodes,
  or derivatives of source media.
- **Native multicam clip creation/flattening is not in the public API** — the
  setup helper preps a stacked timeline you convert in Resolve's UI
  (`docs/guides/multicam-setup-guide.md`).
- **`ImportMedia` has no destination parameter** — clips always land in the
  *current* folder and an unrecognized destination argument is silently ignored.
  Create the bin, `set_current_folder` to it, **then** import.
- **`MediaPoolItem.GetTimeline` is 21.0.4+** and is not reachable through this
  server yet — a media-pool entry that *is* a timeline cannot be turned back into
  a timeline object on older builds. Check `resolve_control
  check_version_support` rather than assuming.
- **Never rename or derive camera originals** without explicit approval;
  `rename_plan` refuses them by design.

## `resolve-media-analysis` — read-only, and the gates are Resolve's own AI

**The First Rule: never touch the source.** Your relationship to source media is
READ-ONLY (full rationale in `docs/guides/media-analysis-guide.md`).

Gated surfaces in this domain are all Resolve's **own** analysis, not this repo's:
`MediaPoolItem`/`Folder.AnalyzeForIntellisearch` (21.0), `Project.ResetIntellisearchAnalysis`
(21.0), `AnalyzeForSlate` (21.0), `PerformAudioClassification` /
`ClearAudioClassification` (21.0), `RemoveMotionBlur` (21.0), `Project.GenerateSpeech`
(21.0).

**This repo's own analysis stack does not depend on any of them** — `analyze_media`
reads frames and audio off disk and runs its own vision/transcription/embedding
tiers, so an older Resolve loses Resolve's AI features, not this pipeline. **Say
which one the user is actually missing.**

Getting file paths: `media_pool_item get_clip_property(clip_id)` returns
`"File Path"`; for a timeline item, `timeline_item get_media_pool_item(item_id)`
then read clip properties; `media_storage get_files(path)` lists a directory.
Workflow: identify the media → check for existing sidecar analysis → analyze if
needed (FFprobe + optional tools) → act with context. At no point do we create
intermediate files that enter the media pipeline.

Deliverables from a transcript: `generate_captions(clip_ref, format='srt'|'vtt',
with_chapters=?)` — caption blocks under broadcast rules (line-length and
lines-per-block caps, max **and min** block duration, breaks at sentence ends then
pauses then clauses, timings snapped to spoken words, a minimum inter-block gap,
no single-word orphan); **it never drops a word to make text fit — it refuses
instead.**

Setup: on first use ask the three setup questions in the guide — (1) where to save
analysis files (alongside / directory / project), (2) tool detection (FFprobe
required, FFmpeg/Whisper optional), (3) analysis depth (quick / standard / deep).
`image_qc_capabilities` reports numpy/ffmpeg availability and cost tiers.
