# agent-edite-davinci_resolve — Editing Agent Rules

This repository packages the user's existing DaVinci Resolve editing skills. It is not the MCP server implementation and does not contain footage or a Resolve project database.

## Start of task checklist (Claude Code, Codex, Hermes)

Entry points: Claude Code reads `CLAUDE.md` (a thin pointer to this file); Codex and Hermes read this file; skills live in `.agents/skills/`. Keep the rules here only.

0. Run `python scripts/check_mcp_update.py` (compares the installed community MCP with the newest tag of https://github.com/samuelgursky/davinci-resolve-mcp). If it says `UPDATE`, read the upstream `CHANGELOG.md` for the new versions, run it with `--apply`, tell the user to restart the agent session so the MCP reloads, and continue with the Studio MCP / scripts until then. `BLOCKED` (local changes in the install) or `UNKNOWN` (offline): report it, do not force.
1. Read `.agents/skills/house-style/SKILL.md` and `docs/OPERATING-NOTES.md`; load the domain skill that matches the request (`resolve-mcp` is the index). If the user names a channel or project (Katy404, Aomi-mama, Armigon, Tygarina, Sakuyako-Cheris, Laffy, Kael), read its profile in `docs/channels/` first.
2. Check the attached MCP tool catalog and run a read-only probe (`resolve_control get_version`; Studio MCP `get_resolve_status`). If the `davinci-resolve` MCP is disabled or unreachable, say so before falling back.
3. Search `scripts/INDEX.md` and `grep -r` in `scripts/` for an existing tool. **Never create a tool outside this repository** (no new folders on the Desktop, no temp scripts under `%TEMP%` or the home directory).
4. Only if nothing exists, print the `MCP-GAP:` line and write the script in `scripts/scratch/` (gitignored, no approval needed). Promote it to `scripts/` only when it is reusable: use `resolve_common`, add a test, add a row to `scripts/INDEX.md`.

## Before editing

- Read `.agents/skills/house-style/SKILL.md` and `docs/OPERATING-NOTES.md`, then load the skill matching the actual request. Use `read_file` if a project skill is not yet registered in `skill_view`.
- Skills are in `.agents/skills/`; their Resolve manuals retain the original `docs/` and `resolve-advanced/README.md` layout. `docs/related-skills/` and `docs/skill-variants/` are archives, not default editing instructions.
- Current explicit user instructions govern scope. Historical skill usage does not authorize a new edit, render, import, relink, cleanup, or database patch.
- Discover the live project, timeline IDs, exact Resolve build, resolution, both frame-rate settings, media paths, and existing video/audio/subtitle coverage before writing.
- Preserve the project's approved aspect ratio. Do not automatically turn a 16:9 project into 9:16 or assume settings from another project.

## Allowed tools: Resolve MCP and Resolve Python ONLY (Strict Mandate)

All DaVinci Resolve editing, cutting, conforming, grading, audio mixing, track modification, and rendering work MUST go through exactly two authorized channels:
1. **DaVinci Resolve MCP servers** (`davinci-resolve` community MCP and `DaVinci Resolve Studio` built-in MCP)
2. **Python scripting API** utilizing `scripts/resolve_common.py` (`connect_resolve`, `require_resolve`, `preserved_state`) or standalone verified scripts in `scripts/`.

### STRICTLY PROHIBITED:
- **NO screenshots/GUI automation** (e.g. `pyautogui`, `pynput`, `win32gui` mouse/keyboard clicking, computer-use).
- **NO keystroke macros or hotkey emulation**.
- **NO browser automation** to manipulate Resolve.
- **NO external non-Resolve video editing software** (e.g. Premiere, CapCut, ffmpeg-only assembly when timeline editing is requested).
- **Exceptions that are not Resolve control**:
  - `ffprobe`/`ffmpeg` for **read-only** media analysis, probe, and render QC verification (see Verification section).
  - Last-resort offline SQLite database inspection/patching when Resolve is completely closed and a verified `.drp` backup exists.

### Tool Inventory & Capabilities

**A. `davinci-resolve` MCP** (community server `davinci-resolve-mcp`, at `C:\Users\warit\Desktop\davinci-resolve-mcp`, configured in `.mcp.json`; the installed version is whatever `scripts/check_mcp_update.py` prints). Tools are grouped by domain; each takes an `action`:

| Domain | Tools & Primary Actions |
|---|---|
| Session / meta | `resolve_control` (`get_version`, `check_version_support`, `api_truth`, `report_issue`), `setup`, `knowledge`, `layout_presets`, `script_plugin` |
| Projects | `project_manager` (`get_current_project`, `load_project`, `create_project`, `save_project`, `export_project`, `import_project`, `close_project`), `project_manager_folders`, `project_manager_database`, `project_manager_cloud`, `project_settings` (`get_project_settings`, `set_project_setting`) |
| Media | `media_storage`, `media_pool` (`get_root_folder`, `get_current_folder`, `set_current_folder`, `import_media`, `import_timeline_from_file`, `create_empty_timeline`), `media_pool_item` (`get_clip_property`, `set_clip_property`), `media_pool_item_markers`, `folder`, `media_analysis` |
| Timeline / edit | `timeline` (`get_timeline_by_name`, `set_current_timeline`, `get_track_count`, `get_item_list_in_track`, `export`, `duplicate_timeline`, `create_sub_timeline`, `delete_timeline`), `timeline_frame`, `timeline_markers`, `timeline_versioning`, `timeline_ai`, `edit_engine` (`duplicate_clips`, `copy_clips`, `move_clips`, `insert_generator`) |
| Timeline items | `timeline_item` (`get_name`, `get_start`, `get_end`, `get_duration`, `get_property`, `set_property`, `get_fusion_comp_count`, `add_fusion_comp`), `timeline_item_markers`, `timeline_item_takes`, `timeline_item_color`, `timeline_item_fusion` |
| Color | `graph`, `color_group`, `gallery`, `gallery_stills`, `lut`, `dctl` |
| Fusion | `fusion_comp` (`get_tool_list`, `add_tool`, `connect_tool`, `set_tool_input`), `fuse_plugin` |
| Delivery | `render` (`add_render_job`, `start_rendering`, `get_render_job_status`, `delete_all_render_jobs`), `render_presets` |

Matching domain skills in `.agents/skills/`: `resolve-edit`, `resolve-color`, `resolve-audio`, `resolve-fusion`, `resolve-media-pool`, `resolve-media-analysis`, `resolve-conform`, `resolve-delivery`, `resolve-rough-cut`, `resolve-tighten-recording`, `resolve-video-enrichment`, with `resolve-mcp` as the index.

**B. `DaVinci Resolve Studio` MCP** (Blackmagic's built-in server, Resolve 21.1+):
- Discovery (read-only): `get_resolve_status`, `get_whats_new`, `search_scripting_api`, `get_scripting_api`, `get_scripting_docs`.
- Execution: `run_script` (sandboxed Python for execution on the running host); `run_script_unsafe` only when `run_script` is demonstrated insufficient and explicitly authorized.
- Assets: `list_luts`, `generate_lut`, `delete_lut`, `list_dctls`, `update_dctl`, `delete_dctl`.
- `launch_resolve`: only when the user explicitly requests starting Resolve.

**C. Python Scripting API via `scripts/`** — the catalogue is `scripts/INDEX.md` (task → script → scope). Do not duplicate script lists here.
- Shared plumbing: `scripts/resolve_common.py` (`connect_resolve`, `require_resolve`, `preserved_state`, `api_has_method`), `resolve_preflight.py` (`--need`, `--list-tools`, `--probe-api`), `backup_drp.py` (`export_verified`).
- Scope labels in the index: `ใช้ซ้ำ` (any project), `p2` / `armigon` / `sakuyako` (project-specific constants), `ครั้งเดียว` (one-off; use as an example only).

## Tool Selection Hierarchy: MCP First, Scripting API Second (Mandatory)

For any task touching DaVinci Resolve, follow this exact sequence:
1. **Check the `davinci-resolve` MCP first** (Inventory A). Read the tool schema. Use `resolve_control get_version` and `check_version_support`.
2. **Execute via MCP** when a tool/action covers the task. Always test with a read-only probe call first.
3. **Fallback to Resolve Python Scripting API** only when:
   - No matching MCP tool or action exists in the current version.
   - An MCP call fails due to a recorded build limitation or bug.
4. **Mandatory Documentation Line before script writing:**
   `MCP-GAP: <tool/action checked> -> <result/reason for script fallback>`
5. Script location and standards:
   - Place all scripts in `scripts/`.
   - Always connect using `scripts/resolve_common.py:connect_resolve`.
   - Wrap state mutations in `preserved_state(resolve)`.
   - Read back and verify every modification.
6. If neither MCP nor Python Scripting API supports the feature, mark task as `BLOCKED` with evidence. Never invent method names.
7. Always end each task by reporting the path used (`davinci-resolve` MCP, Studio MCP, or Python script) and the rationale.

## Editing Architecture and House Rules

### 1. Track Architecture Standards
- **16:9 Landscape Video:**
  - `Video 1`: Base Footage (Gameplay + VTuber webcam)
  - `Video 2`: `VTuber Zoom` (Adjustment Clip track with Fusion Transform)
  - `Video 3`: `REACTIONS` (Overlays, GIFs, popups, illustrations)
  - `Subtitle 1`: Native Thai Subtitles (always on top, unaffected by Adjustment Clips)
- **9:16 Vertical Shorts / TikTok:**
  - `Video 1`: `Game Top` (Cropped & panned gameplay in top frame)
  - `Video 2`: `REACTIONS` (GIFs / popups)
  - `Video 3`: `VTuber Bottom` (Framed avatar in bottom frame)
  - `Video 4`: `VTuber Zoom` (Adjustment Clip track zooming the avatar)
  - `Subtitle 1`: Native Thai Subtitles (always on top)

### 2. VTuber Zoom Focus Guidelines
- **Target Adjustment Clips only**: Never modify underlying Video 1/3 clips or audio/subtitle tracks.
- **Focal Point**: Avatar centered (`Center X / Y`), scale adjusted so avatar is the dominant subject.
- **Framing**: Frame from head to chest/hands.
- **Headroom**: Maintain ~5–8% headroom above the head.
- **Crop Prohibition**: NEVER cut off the head, face, ears/hair ornaments, or hands. If tight framing risks cropping, reduce zoom level.
- **Subtitle & HUD Safety**: Ensure no critical HUD or subtitle overlap.

**QC gate สำหรับ Zoom Focus:** ยืนยันว่าตัวละครในทุกช่วงเป็น Armigon ก่อนซูม; ตรวจภาพเต็มเฟรม ไม่มีขอบดำหรือ blur ที่เพิ่มจาก `Adjustment Clip`; อ่าน `Center`/`Size` และ keyframe ของ transform พร้อม `MotionBlur` เพื่อประเมินความเสี่ยงการสั่น แล้วตรวจภาพเคลื่อนไหวเมื่อจำเป็น เทียบภาพเฟรมเดียวกันเมื่อเปิด/ปิด `Adjustment Clip` เพื่อแยกการตัดเขา/มือหรือ overlay ที่มีอยู่ใน source ออกจากผลของ zoom ภาพ still และการไม่พบ keyframe ใน input ที่ตรวจไม่ใช่หลักฐานว่า motion ทุกเฟรมไม่มีอาการสั่น บันทึกผลและขอบเขตหลักฐานตาม `.agents/skills/resolve-video-enrichment/references/adjustment-focus.md`.

### 3. DRT Transfer Pattern for Safe Track Injections
Direct API insertion (`InsertGeneratorIntoTimeline`) can misplace clips across track indices on complex timelines. The verified bulletproof pattern:
1. Export timeline to DRT: `timeline.Export(drt_path, resolve.EXPORT_DRT, resolve.EXPORT_NONE)`
2. Parse and inject target track/clips via `scripts/drt_focus_track.py`
3. Import back into project: `media_pool.ImportTimelineFromFile(drt_path)`
4. Read back and verify all original tracks against baseline.

### 4. Safety and Recoverability
- Never overwrite source footage.
- Always export a verified `.drp` backup before running batch operations (`backup_drp.py`).
- Work in recoverable variants (`_focus_variant`, `_bak`). Only update original master timelines upon explicit user instruction.
- Always save via `project_manager.SaveProject()` and read back all modified items.

## Finish of task: record what you learned

**Mandatory after every task, every time (user's standing instruction, 2026-10-24):** record everything learned (update this file when a rule applies to every task; write or update the matching skill in `.agents/skills/` for workflows, traps and techniques), then run tests + manifest refresh, then commit and `git push origin main` immediately, without asking again. Check `git status` before staging; never commit footage, renders, `.drp`/`.drt`, `.env` or credentials. If the push fails, report the error; do not force-push.

Follow `.agents/skills/project-learning/SKILL.md`. In short, before reporting done:

- Channel facts (project names, presets the user confirmed, traps, open work) -> the channel's profile in `docs/channels/`.
- New rule or trap learned from a failure → one row in `docs/OPERATING-NOTES.md` (rule, why).
- New or promoted script → row in `scripts/INDEX.md`; delete or leave in `scripts/scratch/` anything that was a one-off.
- A correction the user gave about taste (cut rhythm, subtitles, framing) → `.agents/skills/house-style/SKILL.md`.
- Changes to this file stay short: add a rule only if it applies to every task; otherwise put it in OPERATING-NOTES or a skill.
- Run `python -m pytest -q` and `python scripts/refresh_skill_manifest.py` after touching skills, scripts or docs.

## Verification and handoff

Save with `ProjectManager.SaveProject()`. Read back every modified target and restore the original active project/timeline, playhead, page, folder, and track states. Verify each batch item, not just one example. For renders, require Complete status, a nonempty output, ffprobe video/audio verification, and visual QC; native still export can omit subtitles.

Only report what was actually verified. Skills/documents are not proof that a tool is installed or an API works on the currently running build. This packaging task does not itself authorize connecting to or changing Resolve.
