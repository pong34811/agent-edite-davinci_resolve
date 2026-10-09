# VTuber Focus Position Audit Plan

> **For agentic workers:** This plan is for read-only inspection and planning. Do not edit Resolve timelines while executing it. Any later edit requires a separately reviewed implementation plan and a fresh verified `.drp` backup.

**Goal:** Build a fresh, evidence-backed per-timeline position and framing plan for VTuber Zoom Focus across the 49 canonical timelines in `aomimama-2026-09-p1`.

**Architecture:** Use the live DaVinci Resolve MCP for build/capability checks and read-only timeline/subtitle inventory, then use Resolve Python only for confirmed MCP gaps through `scripts/resolve_common.py`. Refresh the canonical timeline identity map, inspect the avatar at subtitle-led candidate moments across each interval, and record safe normalized framing values plus confidence and an explicit `ready`, `no_op`, or `deferred` decision for every timeline. Keep all evidence and the resulting plan as local reports; make no Resolve mutations.

**Tech Stack:** DaVinci Resolve Studio 21.1.0.17, live `davinci-resolve` MCP, Resolve Python API via `scripts/resolve_common.py`, Python 3, FFmpeg/FFprobe only if the live viewer capture cannot provide the required frames.

**Spec:** The user's VTuber Focus request in this conversation and repository rules in `AGENTS.md`, `docs/OPERATING-NOTES.md`, `.agents/skills/resolve-video-enrichment/SKILL.md`, and `.agents/skills/house-style/SKILL.md`.

## Global Constraints

- Target project is the user's main project `aomimama-2026-09-p1`; do not switch to the recovered project or a draft copy.
- The target corpus is the 49 canonical timeline names in the existing cue manifest, matched to the live Resolve project by exact name and refreshed unique ID; do not identify timelines by index alone.
- The live project currently reports 53 timeline entries: exclude `T25 ..._MOVE_ERROR_20261007` and the three `_archived_v*` T25 versions; include the corrected T25 timeline whose exact canonical name is at live index 52 in the latest read-only inventory.
- No timeline, track, clip, subtitle, source media, project setting, or folder may be changed during this audit. Do not save the project. Read-only preview navigation may temporarily activate a timeline or move its playhead only after capturing the full working-state snapshot, and must restore and verify that state before exit.
- Preserve the project's approved 1920x1080, 16:9 raster and each timeline's own record FPS. Read raster, timeline FPS, playback FPS, media paths, track layout, cue coverage, and current Focus coverage before analyzing frames.
- Do not trust old timeline IDs. The stored cue and batch plans have stale IDs; refresh by exact canonical name and stop on missing or ambiguous matches.
- Do not treat the longest contiguous subtitle cluster as a confirmed joke/reaction. Inspect subtitle text and surrounding picture; listen to the corresponding audio where available. Mark the basis and evidence for each decision.
- Framing must protect the VTuber's full head, face, ears, and meaningful hands; target 3–5% headroom where the frame allows it, retain subtitle legibility, and avoid blank edges, distortion, or cropping.
- An absent, uncertain, off-screen, or moving avatar may yield `no_op` or `deferred`; never force a zoom to satisfy a count.
- Adjustment Clips are intended for V2 and `OFFLINE_DRAFT_GIF` for V3 in the later edit, but this audit does not create, move, or transform either type of clip.
- Do not write to Resolve's project database or modify a `.drp` directly.

## Review Focus

- Timeline identity drift and T25 recovery/archive copies: match all 49 canonical names exactly, report duplicate/missing IDs, and prove archive names are excluded.
- Invalid legacy avatar boxes: 14 rows in the existing position plan have zero width or height; re-measure from actual frames and mark unobservable positions `deferred`.
- Subtitle candidate quality: the old manifest has 48 candidates based on longest clusters and one T29 no-op; confirm each cue is an actual relevant beat and reconsider T49, which the old batch excluded on a stale assumption that a focus clip already existed.
- Avatar motion during the candidate: compare frames at cue start, midpoint, and end, plus samples at least every 0.5 seconds for longer cues and at visible motion changes; reduce zoom or defer if one safe static crop cannot keep the face/head/hands visible throughout.
- Caption overlap and subtitle visibility: inspect frames with the native subtitle overlay or a verified preview; do not infer subtitle clearance from a still without captions.
- Transform interpretation: calculate proposed Resolve Transform values from the current, measured bounding box and the build-verified model; label values provisional until visualized in a preview during a later, separately approved edit.

---

### Task 1: Reconcile the 49-timeline live inventory

**Files:**
- Create: `scripts/audit_vtuber_focus_positions.py`
- Create: `tests/test_audit_vtuber_focus_positions.py`
- Create: `.hermes/artifacts/vtuber-focus-review-2026-10-07/position-audit/live-inventory.json`
- Read: `.superpowers/sdd/2026-10-07_095727-vtuber-adjustment-focus/cue-manifest.json`

**Interfaces:**
- Consumes: `connect_resolve()` from `scripts/resolve_common.py`, live project and timeline objects, and the canonical names in `cue-manifest.json`.
- Produces: a read-only JSON inventory keyed by canonical timeline name with current unique ID, resolution, record FPS, playback FPS, timeline range, track names/locks/enabled states, video/audio/subtitle coverage, media paths, and Adjustment Clip coverage.

- [ ] **Step 1: Check the MCP catalog and live Resolve build**

Run `resolve_control.get_version`, `check_version_support` for the required read methods, and `api_truth` for timeline enumeration and frame capture. Inspect the live schemas for timeline inventory, subtitle transcript/items, and frame capture before calling them.

Expected: live build and MCP version are recorded; use MCP for every supported read. For each unsupported read needed by the plan, record one `MCP-GAP: <tool.action> -> <result>` line and run `python scripts/resolve_preflight.py --need <method> --probe-api` before scripting it.

- [ ] **Step 2: Write failing tests for canonical timeline reconciliation**

Add tests for exact-name matching with refreshed IDs, a missing canonical timeline, a duplicate canonical name, T25 recovery/archive exclusion, and reordered live timeline entries.

Run: `pytest tests/test_audit_vtuber_focus_positions.py -k canonical -v`

Expected: FAIL because the reconciliation function is not implemented.

- [ ] **Step 3: Implement read-only inventory checks**

Add `audit_project(project_name: str) -> dict` in `scripts/audit_vtuber_focus_positions.py`. It must use `connect_resolve()`, refuse a project-name mismatch, enumerate all timelines without switching active timeline, and map exactly the 49 canonical names to one live timeline each.

- [ ] **Step 4: Run canonical matching tests**

Run: `pytest tests/test_audit_vtuber_focus_positions.py -k canonical -v`

Expected: PASS for unique name matching, refreshed IDs, reordered timeline entries, and explicit failure on missing/ambiguous matches.

- [ ] **Step 5: Capture and validate current track/media/subtitle coverage**

For each matched timeline, read its own `GetSetting('timelineFrameRate')`, raster, start/end, all track names and item ranges, subtitle item IDs/text/start/end, and source paths for picture-bearing video items. Record current adjustment-generator ranges and their tracks without editing them. Inventory reads should not activate other timelines; preview navigation later may switch timeline/playhead only under the saved-state/restore guard.

- [ ] **Step 6: Run inventory and regression checks**

Run: `pytest tests/test_audit_vtuber_focus_positions.py -k inventory -v`

Expected: PASS for per-timeline FPS/raster fields, subtitle count/readback equality, source-path capture, current Focus coverage, no mutation calls, and state restoration on both success and error paths.

- [ ] **Step 7: Run and inspect the inventory**

Run `python -m scripts.audit_vtuber_focus_positions inventory --output <path>`.

Expected: 49 canonical rows, a separate list of excluded T25 recovery/archive entries, explicit missing/offline media and subtitle-track anomalies, and a state-restoration result of `true`. No Resolve write or save call occurs.

### Task 2: Refresh subtitle-led visual review points

**Files:**
- Modify: `scripts/audit_vtuber_focus_positions.py`
- Modify: `tests/test_audit_vtuber_focus_positions.py`
- Create: `.hermes/artifacts/vtuber-focus-review-2026-10-07/position-audit/cue-review.json`

**Interfaces:**
- Consumes: live inventory from Task 1 and exact subtitle items from each canonical timeline.
- Produces: per-timeline candidate intervals with cue text, selected frame samples, editorial basis, and `ready`, `no_op`, or `deferred` status.

- [ ] **Step 1: Write failing tests for subtitle candidate boundaries**

Cover cue adjacency, overlapping cues, cues near frame 0 and timeline end, sub-2-second cues, empty text, and duplicate cue IDs.

Run: `pytest tests/test_audit_vtuber_focus_positions.py -k candidate -v`

Expected: FAIL because the refreshed candidate logic is not implemented.

- [ ] **Step 2: Derive candidates from actual subtitle ranges**

Implement `build_candidates(inventory: dict) -> list[dict]`. Use exact subtitle item ranges and transcript text; join nearby cues only when their ranges form one coherent speaking/reaction beat. Candidate timing must be bounded by the relevant cue(s), not automatically expanded to a fixed 5-second window.

- [ ] **Step 3: Run candidate tests**

Run: `pytest tests/test_audit_vtuber_focus_positions.py -k candidate -v`

Expected: PASS with candidates tied to live cue IDs, frame-bounded intervals, and no duplicate candidate rows.

- [ ] **Step 4: Capture contextual picture and audio evidence**

Implement `capture_candidate_evidence(candidate: dict) -> dict` using the verified live MCP timeline-frame capture where it includes the actual composite. Capture at candidate start, midpoint, and end, with subtitle visibility. If the MCP capture omits subtitles or cannot capture a non-active timeline reliably, record the capability gap and use the verified read-only preview route; do not change project state without snapshot/restore readback. Listen to the corresponding audio segment where the available tooling supports it.

Assert: each reviewed candidate has exact frame/timecode, image evidence path, subtitle text, and an audio-evidence state of `heard`, `unavailable`, or `not_required` with a reason. Never label a candidate a reaction solely from subtitle text.

- [ ] **Step 5: Assign the beat decision for each timeline**

For each canonical timeline, select a candidate only when picture/audio/context support a joke, reaction, emotional change, or otherwise important moment. Record a concise reason. Use `no_op` when no moment merits a zoom and `deferred` when footage or evidence is unavailable.

Assert: exactly 49 timeline decisions exist, with no silent omissions; T29's previously short candidate is re-evaluated; T49 is re-evaluated rather than skipped because of an old focus assumption.

### Task 3: Measure VTuber position and safe framing for each selected interval

**Files:**
- Modify: `scripts/audit_vtuber_focus_positions.py`
- Modify: `tests/test_audit_vtuber_focus_positions.py`
- Create: `.hermes/artifacts/vtuber-focus-review-2026-10-07/position-audit/framing-review.json`
- Create: `.hermes/artifacts/vtuber-focus-review-2026-10-07/position-audit/framing-contact-sheet.jpg`

**Interfaces:**
- Consumes: `ready` intervals and contextual frame evidence from Task 2.
- Produces: a normalized avatar bounding box per sample, confidence/evidence, a conservative provisional Transform (`Size`, `Center X`, `Center Y`), headroom estimate, caption-overlap result, and a framing decision.

- [ ] **Step 1: Write failing tests for avatar-box validation and crop safety**

Cover valid normalized boxes, out-of-frame/zero-area boxes, headroom bounds, subtitle bands, and a moving avatar whose start/middle/end union makes the requested crop unsafe.

Run: `pytest tests/test_audit_vtuber_focus_positions.py -k framing -v`

Expected: FAIL because avatar measurements and safe-crop decisions are not implemented.

- [ ] **Step 2: Measure the avatar on every sample frame**

Implement `measure_avatar(frame_path: str) -> dict` or use the documented vision-review workflow to record normalized `(x_min, y_min, x_max, y_max)` for the visible VTuber, distinguishing head/face and hands where visible. Keep one record per sampled frame and identify manual versus automated measurements.

Assert: every measurement has a valid positive-area box within `[0,1]`; zero-area or off-screen results are rejected as unmeasured, never converted into a zoom value.

- [ ] **Step 3: Calculate a safe static crop across the full candidate**

Implement `propose_transform(sample_boxes: list[dict], raster: tuple[int,int], headroom_fraction: float = 0.04) -> dict`. First verify the Transform coordinate convention against `resolve_control.api_truth` and a live read-only probe or existing render evidence; do not use the legacy plan's equation without verification. Use the union of measured subject boxes across the sampled interval; ensure a static transform keeps head, face, and important hands in-frame throughout. Favor 3–5% headroom when feasible, reserve subtitle space, and reject any value that creates blank edges or cuts important content.

- [ ] **Step 4: Run framing tests**

Run: `pytest tests/test_audit_vtuber_focus_positions.py -k framing -v`

Expected: PASS for valid box handling, zero-area rejection, safe static crop calculations, and conservative `deferred` results when movement/captions prevent a safe frame.

- [ ] **Step 5: Review measurements against the evidence images**

Create an indexed contact sheet for all selected intervals. Have an independent reviewer check avatar boxes, transform direction, crop safety, headroom, subtitle overlap, and the editorial basis against source frames. Resolve disagreements by correcting the row or marking it `deferred`.

Assert: every `ready` row has a reviewer verdict and evidence path; no row is marked `ready` solely from an Inspector number or an unverified old plan.

### Task 4: Publish the reconciled 49-row inspection plan

**Files:**
- Create: `.hermes/artifacts/vtuber-focus-review-2026-10-07/position-audit/final-plan.json`
- Create: `.hermes/artifacts/vtuber-focus-review-2026-10-07/position-audit/final-plan.md`
- Modify: `tests/test_audit_vtuber_focus_positions.py`

**Interfaces:**
- Consumes: inventory, cue decisions, framing measurements, reviewer results.
- Produces: one auditable row for each canonical timeline: exact live ID/name, selected subtitle interval or no-op/deferred reason, avatar bounding box, confidence, provisional Size/Center, headroom, caption clearance, sample evidence, and review result.

- [ ] **Step 1: Write failing tests for report completeness**

Cover exactly 49 canonical rows, no duplicate timeline names, status totals summing to 49, required evidence on `ready` rows, and separate exclusion of recovery/archive timelines.

Run: `pytest tests/test_audit_vtuber_focus_positions.py -k report -v`

Expected: FAIL because the report validator is not implemented.

- [ ] **Step 2: Generate the canonical report**

Implement `write_final_plan(inventory: dict, cue_review: dict, framing_review: dict, output_dir: Path) -> tuple[Path, Path]`. The Markdown version must use readable Thai timeline names and include a compact summary plus a complete 49-row table; JSON is the machine-readable source of truth.

- [ ] **Step 3: Run report tests and validator**

Run: `pytest tests/test_audit_vtuber_focus_positions.py -k report -v` and `python -m scripts.audit_vtuber_focus_positions validate --plan <final-plan.json>`.

Expected: PASS; each canonical timeline appears exactly once, `ready`/`no_op`/`deferred` totals equal 49, every `ready` row has valid numeric values and evidence, and excluded archive copies are listed separately.

- [ ] **Step 4: Run the audit validator and self-review**

Review every non-`ready` row, every low-confidence row, and all previously degenerate-box ordinals before calling the plan complete.

Expected: validator passes all structural checks, report confirms Resolve state unchanged, no timeline mutations or saves occurred, and every unverified assumption is called out. This plan does not authorize edits or renders; a separate implementation stage uses the approved per-timeline positions, places Adjustment Clips on V2, preserves/moves approved GIFs to V3, and takes a fresh `.drp` backup before writes.
