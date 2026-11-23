---
name: resolve-project-folder-targeting
description: Use when creating or choosing a Resolve project/library folder for a highlight job, especially when the source footage folder and the Resolve folder share similar names.
version: 0.2.0
---

# Resolve project folder targeting

Three locations are distinct; never substitute one for another:
- **Source footage**: read-only folder on disk (e.g. `G:/My Drive/Projects/<channel>/<YYYY-MM>`).
- **Resolve destination**: library + folder in Project Manager (e.g. `<channel>/<YYYY-MM>`).
- **WORK_DIR**: job artifacts in the repo (`work/highlight/<channel>/<job>/`).

Steps:
1. Read-only first: `resolve_control runtime_mode`, `project_manager get_current`, `project_manager list`.
2. Confirm the library and current folder match what the user showed or named. If they do not, stop and report; navigate the observed folder tree rather than guessing (list/load are scoped to the current folder). For highlight jobs, organize into subfolder `<channel>/<YYYY-MM>`.
3. If a same-name project exists, reuse it; never overwrite. If its name differs but media paths match, offer reuse instead of switching.
4. **Never call `SaveProject()` on an `Untitled Project`** (such as when Resolve has just opened); doing so opens a modal GUI prompt that halts headless scripts and MCP tools.
5. Create new projects with `media_location_path` pointing to the source footage directory (e.g. `project_manager create` or `pm.CreateProject(name, media_location_path)`).
6. After creating: set timeline fps (`timelineFrameRate`), `project_manager save`, and read back name, folder and settings. Note that `timelinePlaybackFrameRate` cannot be set via scripting API on 21.1.0.17 (reads 24 fps) and must be confirmed/set by the user in Project Settings → Master Settings.
