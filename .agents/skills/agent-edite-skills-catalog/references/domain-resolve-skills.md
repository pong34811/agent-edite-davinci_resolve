# Domain skills — DaVinci Resolve MCP (9 skills)

Source: `.agents/skills/resolve-*/SKILL.md` (v0.3.0 family). The domain set is
the core of this repo: `resolve-mcp` is the map, the other eight own one domain
each and self-trigger on their own `description`.

## `resolve-mcp` — the index (220 lines)

Load this when a task spans several domains. It states the allowed-channels
mandate, the two-server model, the domain table, and the build-verification
rule. It does not auto-load the other skills; it points at them.

### Domain routing table (verbatim from the skill)

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

Less-common domains with no dedicated skill — go straight to the kernel/tool:
project lifecycle (`project_manager` → `docs/kernels/project-lifecycle-kernel.md`),
review/annotations (`timeline_markers` → `review-annotation-kernel.md`),
extension authoring (`script_plugin` → `extension-authoring-kernel.md`),
pipeline DB-as-truth (advanced `pipeline` tool → `resolve-advanced/README.md`).

### Two servers — compute offline, apply live

- **Live** — `davinci-resolve` (Python): drives a *running* Resolve via the
  scripting API.
- **Advanced / offline** — `davinci-resolve-advanced` (Node): authors
  `.drp`/`.drt`/`.drx` files and patches the project DB with **no Resolve open**.
- Rule of thumb: compute grades, QC, and conform math offline; apply the result
  live. Node never drives Resolve.

### "Read the build before you promise a capability"

The scripting API changes per PATCH release, not per major one. Before
answering what is possible: `resolve_control get_version` (note **both**
`version_string` and `mcp.version`), then `check_version_support` (every gate
this build does not clear), then `api_truth "<topic>"` (each fact carries a
`version_context`).

- `unknown` is the common answer and means **probe, not yes**.
- `mcp.version` is the version the process STARTED with — a `git pull` does not
  refresh it until restart, so an `api_truth` miss may mean "stale server".
- When a build is too old, say so and name the floor; do not offer the call and
  let it fail.

### Cross-cutting rules (always)

- **Source media is sacred**: never modify, transcode, convert, proxy, relink, or
  derive source media unless explicitly asked; outputs go to sidecars, scratch,
  or the analysis project root.
- **Frame-first color**: inspect Resolve-rendered frames before applying any
  grade/look/LUT/CDL/DRX, and preserve a recoverable grade version.
- **Guards refuse rather than fabricate** on the advanced server — read the
  "refused" message before retrying (usually wrong value space, log-encoded
  frames, missing media, or a missing optional dep).
- **Tool selection (MCP first)**: check the `davinci-resolve` catalog, then the
  official Resolve MCP (`get_whats_new`, `search_scripting_api`,
  `get_scripting_api`, `run_script`), and only then a Python script behind a
  stated `MCP-GAP:` line. `python scripts/resolve_preflight.py --need <tool[.action]>`.

### Catalog shape (davinci-resolve MCP v4.10.4)

37 compound tools: session/meta 5 (`resolve_control`, `setup`, `knowledge`,
`layout_presets`, `script_plugin`), projects/settings 5 (`project_manager`,
`project_manager_folders`, `project_manager_cloud`, `project_manager_database`,
`project_settings`), media/analysis 6 (`media_storage`, `media_pool`, `folder`,
`media_pool_item`, `media_pool_item_markers`, `media_analysis`), timeline/edit 6
(`timeline`, `timeline_frame`, `timeline_markers`, `timeline_versioning`,
`timeline_ai`, `edit_engine`), timeline items 5 (`timeline_item`,
`timeline_item_markers`, `timeline_item_fusion`, `timeline_item_color`,
`timeline_item_takes`), color 4 (`graph`, `color_group`, `gallery`,
`gallery_stills`), fusion 2 (`fusion_comp`, `fuse_plugin`), delivery/assets 5
(`render`, `render_presets`, `lut`, `dctl`).

## Per-domain notes

- **`resolve-color`** — "two servers, one grade"; has a *frame-first rule
  (non-negotiable, see AGENTS.md)*, an offline `drx` grading/QC catalog, and
  `media_analysis assess_grade` for "did the grade damage the image?". Read its
  "What this build cannot do" before offering a capability.
- **`resolve-edit`** — live edit-kernel essentials, "show the gaps before
  cutting them" (`edit_engine`), word-level editing and spoken search, offline
  `editorial` actions, and trimming a timeline tail (no MCP trim setter).
  Also carries *approved reference video styling via Python*.
- **`resolve-conform`** — "no Resolve? the work does not have to stop"; live
  conform essentials, offline `conform` engine, carrying grades across a
  re-conform, offline-reference clips, and an offline conform QC engine.
- **`resolve-delivery`** — delivery targets short path, live render essentials,
  offline `deliverable` QC (video/loudness/blanking/completeness), media
  front-end + provenance, and the **p2 batch final-export pattern**.
- **`resolve-fusion`** — author `.comp` offline, apply live via `fusion_comp`;
  shortest of the domain skills (52 lines).
- **`resolve-audio`** — "rough mix before anything else", plan/measure offline,
  live loudness contracts and the silence gate, Fairlight track/bus layouts.
- **`resolve-media-pool`** — verify offline, import live; `media` actions;
  boundaries per AGENTS.md. For reading/analyzing footage use
  `resolve-media-analysis`; for deliverable-side media QC use `resolve-delivery`.
- **`resolve-media-analysis`** — the *First Rule*: uses FFprobe, FFmpeg, and
  optionally Whisper to READ and ANALYZE source media — never modify, transcode,
  convert, or create derivatives. Gives the MCP context about what footage is.

## Where the depth actually lives

`AGENTS.md` (canonical brief + Domain Routing index), `docs/SKILL.md` (operating
reference for both servers — never load whole), `docs/kernels/` (per-action
depth), `resolve-advanced/README.md` (offline catalog),
`docs/reference/api-coverage.md` (method-by-method Resolve API reference).
