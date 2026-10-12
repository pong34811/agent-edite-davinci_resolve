---
name: resolve-mcp
description: Orientation and index for DaVinci Resolve MCP work — grading, editing, conforming, delivery, media analysis, and .drp/.drt/.drx file work, live in a running Resolve or offline with none open. Load this for a map of the domain skills, the live-vs-offline servers, and the cross-cutting safety rules. The per-domain skills (resolve-color / resolve-edit / resolve-conform / resolve-delivery / resolve-media-analysis) carry the depth and self-trigger on their own descriptions; use this as the map, or when a task spans several domains.
version: 0.3.0
author: Warit (pong34811), Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [Resolve, MCP, Index]
---

# DaVinci Resolve MCP — Index

Orientation for any Resolve MCP task. This is the **map, not the depth** — each

domain skill below carries its own routing and triggers on its own `description`.

Open the one that matches, or use this when a task spans several domains. This

skill does not auto-load the others; it points at them.

## Allowed Channels: Resolve MCP and Resolve Python API ONLY

All DaVinci Resolve editing, cutting, timeline modification, grading, and rendering must go through exactly two authorized channels:
1. **DaVinci Resolve MCP Servers** (`davinci-resolve` live server / `DaVinci Resolve Studio` built-in MCP)
2. **Resolve Python Scripting API** (`scripts/resolve_common.py:connect_resolve`)

**Strictly forbidden**: GUI click automation, computer-use, keystroke emulation/macros, browser automation, or non-Resolve video editors.

## Two servers — compute offline, apply live

- **Live** — `davinci-resolve` (Python): drives a *running* Resolve via the scripting API.
- **Advanced / offline** — `davinci-resolve-advanced` (Node): authors `.drp`/`.drt`/`.drx` files and patches the project DB with **no Resolve open**.

Rule of thumb: compute grades, QC, and conform math offline; apply the result live. Node never drives Resolve.

## Domains

| Task | Skill | Kernel | Any-MCP-client prompt |
|---|---|---|---|
| Grading, looks, shot match, LUT/CDL/DRX | `resolve-color` | `color-grade-kernel.md` | `/color_grade_workflow` |
| Cutting, trimming, ranges, variants, changelist | `resolve-edit` | `timeline-edit-kernel.md` | `/timeline_edit_workflow` |
| Conform, relink, finishing QC, grade tracing | `resolve-conform` | `timeline-conform-interchange-kernel.md` | `/conform_workflow` |
| Render, deliverable QC, media/provenance | `resolve-delivery` | `render-deliver-kernel.md` | `/delivery_workflow` |
| Fusion comps (titles, MG, VFX) | `resolve-fusion` | `fusion-composition-kernel.md` | `/fusion_workflow` |
| Audio / Fairlight (tracks, buses, loudness) | `resolve-audio` | `audio-fairlight-kernel.md` | `/audio_workflow` |
| Media pool ingest / organize / multicam | `resolve-media-pool` | `media-pool-ingest-kernel.md` | `/media_pool_workflow` |
| Reading/analyzing source media | `resolve-media-analysis` | `media-analysis-guide.md` | `/analyze_media` |

## Less-common domains (no dedicated skill — go straight to the kernel/tool)

These have real coverage but low enough traffic that they route through this

index rather than their own skill:

- **Project lifecycle** — create/export/import/archive/restore projects,

  databases, settings, presets: `project_manager` compound tool →

  `docs/kernels/project-lifecycle-kernel.md`. Offline DB read/patch: advanced

  `project_read` / `project_db` (project CLOSED + quit/relaunch).

- **Review / annotations** — timeline markers, review reports, annotation

  copy/move/scope: `timeline_markers` → `docs/kernels/review-annotation-kernel.md`.

  Offline audit/lineage: advanced `provenance`.

- **Extension authoring** — install/remove Fuse/DCTL/Lua-Python plugins:

  `script_plugin` → `docs/kernels/extension-authoring-kernel.md`,

  `docs/authoring/`.

- **Pipeline (DB-as-truth)** — YAML-authored canonical project DB, staged runs

  with gates + provenance + drift: advanced `pipeline` tool →

  `resolve-advanced/README.md`.

## Read the build before you promise a capability

**The scripting API changes per PATCH release, not per major one.** "Resolve 21"

is not a fine enough label to reason from: `GetFairlightPresets` exists on 20.2.2

and not on 19.1.3, and three surfaces reported in 21.0.4 are absent from 21.0.2.

Guidance given without knowing the build is how an agent ends up insisting a

method is there when it is not (issue #132).

So, before describing what is possible:

1. `resolve_control get_version` → note **both** `version_string` (the Resolve

   build) and `mcp.version` (this server).

2. `resolve_control check_version_support` → every recorded gate this build does

   **not** clear. With a `symbol`, it answers for one method.

3. `resolve_control api_truth "<topic>"` → each fact now carries a

   `version_context` saying whether it was measured on an older, newer, or

   identical build. **An older measurement is a prior, not a finding.**

Two failure modes worth naming, because neither announces itself:

- **`unknown` is the common answer, and it means probe — not yes.** Only

  surfaces with recorded evidence are gated; most of the API has never been

  version-bisected. Absence from the unavailable list is not a promise that a

  method exists.

- **`mcp.version` is the version this process STARTED with.** A running server

  keeps executing it, so `git pull` does not refresh the ledger until restart —

  an `api_truth` miss may mean "stale server", not "no known issues".

When a build is too old for what was asked, say so and name the floor. Do not

offer the call and let it fail.

## Cross-cutting rules (always)

- **Source media is sacred** (AGENTS.md): never modify, transcode, convert, proxy,

  relink, or derive source media unless explicitly asked. Outputs go to sidecars,

  scratch, or the analysis project root.

- **Frame-first color**: inspect Resolve-rendered frames before applying any

  grade/look/LUT/CDL/DRX, and preserve a recoverable grade version.

- **Guards refuse rather than fabricate** on the advanced server — read a

  "refused" message before retrying (usually wrong value space, log-encoded

  frames, missing media, or a missing optional dep; call the advanced

  `capabilities` tool).

## Deeper references

- `AGENTS.md` — canonical brief + the `## Domain Routing` index (all platforms).
- `docs/SKILL.md` — operating reference for both servers.
- `docs/kernels/` — per-action depth. `resolve-advanced/README.md` — offline catalog.

## Tool selection (MCP first)

Before any script, check the davinci-resolve MCP catalog; write a Resolve Python scripting-API script only after a stated `MCP-GAP:` line shows the MCP lacks the tool/action. Follow `AGENTS.md` "Tool selection" and run `python scripts/resolve_preflight.py --need <tool[.action]>`.

### Complete 37 Compound Tools Catalog (davinci-resolve MCP v4.10.4)

All 37 compound tools grouped by domain:

| Domain | MCP Tools | Key Actions & Responsibilities |
|---|---|---|
| **Session & Meta (5)** | `resolve_control` | `get_version`, `check_version_support`, `api_truth`, `report_issue`, `open_page`, `quit` |
| | `setup` | Client environment checks and automated setup |
| | `knowledge` | Built-in post-production craft guidance and manuals (`topics`, `get`, `search`) |
| | `layout_presets` | Save, load, list, export, import, delete UI layout presets |
| | `script_plugin` | Lua and Python script plugin installation and management |
| **Projects & Settings (5)** | `project_manager` | CRUD on projects (`create`, `load`, `save`, `close`, `delete`, `export_project`, `import_project`, `snapshot`) |
| | `project_manager_folders` | Create, open, delete project manager folders |
| | `project_manager_cloud` | Cloud project libraries and collaboration |
| | `project_manager_database` | Disk/PostgreSQL database management and switching |
| | `project_settings` | Get/set project-level settings and preset defaults |
| **Media & Analysis (6)** | `media_storage` | Mounted volume inspection, folder walk, and import |
| | `media_pool` | Root/current folder navigation, import media, create timelines |
| | `folder` | Media pool subfolder CRUD and clip organization |
| | `media_pool_item` | Metadata, clip properties, proxy linking, audio mapping |
| | `media_pool_item_markers` | Clip-level markers and cues |
| | `media_analysis` | Audio loudness measurement, dialogue mix plans, and offline video/still QC |
| **Timeline & Edit (6)** | `timeline` | Active timeline properties, track count, export DRT/EDL/OTIO, duplicate |
| | `timeline_frame` | Playhead positioning, timecode reads, and frame grabs |
| | `timeline_markers` | Timeline-level markers, scene cut detection, review reports |
| | `timeline_versioning` | Timeline version management and snapshotting |
| | `timeline_ai` | AI-assisted scene detection and audio transcription |
| | `edit_engine` | Compound editing plans, silence ripple, selects, dialogue-driven cuts |
| **Timeline Items (5)** | `timeline_item` | Transform, crop, pan, tilt, composite modes, speed, Fusion comp count |
| | `timeline_item_markers` | Item-level markers and annotations |
| | `timeline_item_fusion` | Direct Fusion comp access on timeline clips |
| | `timeline_item_color` | Grade versions, CDL, PowerGrade apply, node graph |
| | `timeline_item_takes` | Multitake and take selection management |
| **Color & Look (4)** | `graph` | Node graph inspection, LUT assignment, CDL application |
| | `color_group` | Color group assignments and group-level grades |
| | `gallery` | Still album management and DRX grade import/export |
| | `gallery_stills` | Grabbing, exporting, and deleting gallery stills |
| **Fusion (2)** | `fusion_comp` | Add tools, connect inputs, set parameters, keyframes, modifiers |
| | `fuse_plugin` | Custom Fuse plugin management and loading |
| **Delivery & Assets (5)** | `render` | Add render jobs, start/stop rendering, query job status |
| | `render_presets` | Load and manage delivery presets and burn-in data |
| | `lut` | LUT file inspection, export, and verification |
| | `dctl` | DCTL template creation, verification, and encryption |

### Key Capabilities in v4.10.4

1. **Advanced Subtitle Engine & Formatting**:
   - The upstream server's subtitle database module (subtitle-db.mjs) and subtitle track editing guide provide dedicated subtitle parsing, styling, and track safety.
   - Presets and caption styles are governed by subtitle format modules (subtitle-captions.js, subtitle-preset.js, subtitle-style.js).
   - Subtitle property guards prevent inadvertent mutations to audio and video tracks during subtitle editing.
2. **Conform QC Suite & Synthetic Oracles**:
   - Automated verification against synthetic edit fixtures in conform-qc, enabling offline conform verification before rendering or live delivery.
3. **Execution Lifecycle & Thread-Safe Dispatch**:
   - Multi-threaded tool dispatching with schema null-default safeguards.
   - Robust Windows child-process text encoding and stdin discipline.

### Official Resolve scripting MCP (second line, before a hand-written script)

If the `davinci-resolve` tool has no matching action, check the official Resolve MCP before writing a file in `scripts/`: `get_whats_new` (features newer than your training), `search_scripting_api` / `get_scripting_api` (confirm the method exists on this build), then `run_script` for a one-off. Use `run_script_unsafe` only with explicit user approval. Record the result in the `MCP-GAP:` line.

