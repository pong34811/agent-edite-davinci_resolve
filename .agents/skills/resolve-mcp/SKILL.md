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

### Live tool map (davinci-resolve MCP)

Use the tool that matches the object you are touching; read its schema, then probe read-only before writing.

| Object / task | MCP tool |
|---|---|
| Build, version, capability gates, `api_truth` | `resolve_control`, `knowledge` |
| Projects, databases, folders | `project_manager`, `project_manager_database`, `project_manager_folders`, `project_settings` |
| Timelines, tracks, subtitles, generators | `timeline`, `timeline_frame`, `timeline_markers`, `timeline_versioning`, `timeline_ai` |
| Clips: transform, crop, speed, properties | `timeline_item`, `timeline_item_markers`, `timeline_item_takes` |
| Clip color / Fusion | `timeline_item_color`, `graph`, `color_group`, `timeline_item_fusion`, `fusion_comp` |
| Media pool and sources | `media_pool`, `media_pool_item`, `media_pool_item_markers`, `media_storage`, `media_analysis` |
| Stills and look assets | `gallery`, `gallery_stills`, `lut`, `dctl` |
| Render | `render`, `render_presets` |
| Compound edit helpers | `edit_engine` |

### Official Resolve scripting MCP (second line, before a hand-written script)

If the `davinci-resolve` tool has no matching action, check the official Resolve MCP before writing a file in `scripts/`: `get_whats_new` (features newer than your training), `search_scripting_api` / `get_scripting_api` (confirm the method exists on this build), then `run_script` for a one-off. Use `run_script_unsafe` only with explicit user approval. Record the result in the `MCP-GAP:` line.
