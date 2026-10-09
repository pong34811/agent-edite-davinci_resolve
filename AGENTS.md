# agent-edite-davinci_resolve — Editing Agent Rules

This repository packages the user's existing DaVinci Resolve editing skills. It is not the MCP server implementation and does not contain footage or a Resolve project database.

## Before editing

- Read `.agents/skills/house-style/SKILL.md` and `docs/OPERATING-NOTES.md`, then load the skill matching the actual request. Use `read_file` if a project skill is not yet registered in `skill_view`.
- Skills are in `.agents/skills/`; their Resolve manuals retain the original `docs/` and `resolve-advanced/README.md` layout. `docs/related-skills/` and `docs/skill-variants/` are archives, not default editing instructions.
- Current explicit user instructions govern scope. Historical skill usage does not authorize a new edit, render, import, relink, cleanup, or database patch.
- Discover the live project, timeline IDs, exact Resolve build, resolution, both frame-rate settings, media paths, and existing video/audio/subtitle coverage before writing.
- Preserve the project's approved aspect ratio. Do not automatically turn a 16:9 project into 9:16 or assume settings from another project.

## Allowed tools: Resolve MCP and Resolve Python only

All Resolve work goes through exactly two channels: the DaVinci Resolve MCP servers and Python that uses the Resolve scripting API. Do not drive Resolve through screenshots/GUI automation, computer-use, a browser, keystroke macros, or third-party editing tools. Exceptions that are not Resolve control: `ffprobe`/`ffmpeg` for read-only media analysis and render verification (see Verification), and the explicit last-resort SQLite task below.

### Tool inventory

**A. `davinci-resolve` MCP** (community server `davinci-resolve-mcp` v4.9.2, at `Desktop\davinci-resolve-mcp`, configured in `.mcp.json`). Tools are grouped by domain; each takes an `action`, so read the schema of the one you need.

| Domain | Tools |
|---|---|
| Session / meta | `resolve_control` (`get_version`, `check_version_support`, `api_truth`, `report_issue`), `setup`, `knowledge`, `layout_presets`, `script_plugin` |
| Projects | `project_manager`, `project_manager_folders`, `project_manager_database`, `project_manager_cloud`, `project_settings` |
| Media | `media_storage`, `media_pool`, `media_pool_item`, `media_pool_item_markers`, `folder`, `media_analysis` |
| Timeline / edit | `timeline`, `timeline_frame`, `timeline_markers`, `timeline_versioning`, `timeline_ai`, `edit_engine` |
| Timeline items | `timeline_item`, `timeline_item_markers`, `timeline_item_takes`, `timeline_item_color`, `timeline_item_fusion` |
| Color | `graph`, `color_group`, `gallery`, `gallery_stills`, `lut`, `dctl` |
| Fusion | `fusion_comp`, `fuse_plugin` |
| Delivery | `render`, `render_presets` |

Matching skills live in `.agents/skills/` (`resolve-edit`, `resolve-color`, `resolve-audio`, `resolve-fusion`, `resolve-media-pool`, `resolve-media-analysis`, `resolve-conform`, `resolve-delivery`, `resolve-rough-cut`, `resolve-tighten-recording`, `resolve-mcp` as the index). Load the one that matches the request.

**B. `DaVinci Resolve Studio` MCP** (Blackmagic's built-in server, Resolve 21.1+). Use it for build-truth and scripting, not as a second editor:
- Discovery (read-only, use first): `get_resolve_status`, `get_whats_new`, `search_scripting_api`, `get_scripting_api`, `get_scripting_docs`.
- Execution: `run_script` (sandboxed Python); `run_script_unsafe` only when `run_script` is shown insufficient and the user's request covers the effect.
- Assets: `list_luts`, `generate_lut`, `delete_lut`, `list_dctls`, `update_dctl`, `delete_dctl` (deletes need explicit authorization).
- `launch_resolve` only when the user asks to start Resolve.

**C. Python scripting API** via `scripts/` (see `scripts/README.md`): `resolve_common.py` (`connect_resolve`, `require_resolve`, `preserved_state`, `api_has_method`), `resolve_preflight.py` (`--need`, `--list-tools`, `--probe-api`), `backup_drp.py` (verified `.drp` export), `caption_lint.py` (offline Thai caption rule check — run before any SRT import), plus the task scripts for subtitles/style, enrichment, review, focus/framing, project operations, and bundle upkeep (`verify_skill_bundle.py`, `refresh_skill_manifest.py`).

Which server supplies a tool, and the exact tool catalog, must be confirmed live; this inventory is a map, not proof a tool is available on the running build.

## Tool selection: MCP first, scripting API second (mandatory)

For any task that touches Resolve, follow this order. Do not skip to a script.

1. **Check the `davinci-resolve` MCP first** (inventory A; use B's discovery tools to confirm build-specific API facts). Read the attached tool catalog and the schema of the tool matching the task. Run `resolve_control get_version`, `check_version_support`, and `api_truth "<topic>"` for build-specific capability.
2. **Use the MCP when a tool/action covers the task.** Try a read-only/probe call first. `python scripts/resolve_preflight.py --need <tool[.action]>` gives a `USE_MCP` / `FALLBACK_SCRIPT` / `BLOCKED` verdict from the saved schemas and server config; it cannot see the live catalog, so it does not replace step 1.
3. **Write a Resolve Python scripting-API script only after the MCP is shown not to cover it:** no matching tool/action in the catalog, or the MCP call failed with a recorded error. Confirm the method exists with `name in dir(obj)` (never bare `hasattr`), e.g. `resolve_preflight.py --need <Method> --probe-api`.
4. **Before writing the script, state one line:** `MCP-GAP: <tool/action checked> -> <result>`.
5. Put the script in `scripts/`, connect through `scripts/resolve_common.py` (`connect_resolve`), and do not copy another `get_resolve()`. All safety rules below still apply to the script.
6. If neither the MCP nor the scripting API has the capability, report `BLOCKED` with the evidence. Do not guess method names.
7. End the task by reporting which path was used (`davinci-resolve` MCP, Studio MCP, or Python script) and why.

## Safety and house style

- Never overwrite or alter source footage. Requested analysis may decode sources into new scratch frames/WAVs; editing references originals. Relinking/replacing/transcoding sources needs explicit authorization for that operation.
- Thai short-form captions: at most three short words / about 14 Thai characters, at most 1.5s per cue; no spaces between Thai words, spaces around Latin names only. Split or flag text rather than silently dropping speech to meet a limit.
- For subtitle import, use an empty subtitle track and a bare `{"mediaPoolItem": item}` payload. Re-importing a corrected SRT at the same path requires removal of the stale cached pool item. Verify count, text, absolute frames, and approved style.
- Adjustment Clip / VTuber focus: prefer Resolve scripting; change only approved adjustment clips, preserve all underlying video/audio/subtitle ranges, and render-check framing including head, face, hands, headroom, and caption overlap.
- Work in recoverable variants unless the user explicitly approves edits to originals behind a fresh verified `.drp`. Keep backups/archived timelines; deleting them is a separate authorized action.
- Start structural mutations with at least ~1.2s spacing, then save and read back. Numeric transform values must be numeric, not strings; re-read after a false setter return before retrying.
- Direct SQLite writes are a last-resort, explicit task: verify/export backup, close the project, target exact rows, use a transaction, reopen and read back. Never patch an open database.

## Verification and handoff

Save with `ProjectManager.SaveProject()`. Read back every modified target and restore the original active project/timeline, playhead, page, folder, and track states. Verify each batch item, not just one example. For renders, require Complete status, a nonempty output, ffprobe video/audio verification, and visual QC; native still export can omit subtitles.

Only report what was actually verified. Skills/documents are not proof that a tool is installed or an API works on the currently running build. This packaging task does not itself authorize connecting to or changing Resolve.
