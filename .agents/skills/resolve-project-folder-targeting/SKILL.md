---
name: resolve-project-folder-targeting
description: Use when creating or choosing a Resolve project/library folder for a highlight job, especially when the source footage folder and the Resolve folder share similar names.
---

# Resolve project folder targeting

Three locations are distinct; never substitute one for another:
- **Source footage**: read-only folder on disk.
- **Resolve destination**: library + folder in Project Manager (e.g. a screenshot breadcrumb such as `Projects / <channel> / <month>`).
- **WORK_DIR**: job artifacts in the repo.

Steps:
1. Read-only first: `resolve_control runtime_mode`, `project_manager get_current`, `project_manager list`.
2. Confirm the library and current folder match what the user showed or named. If they do not, stop and report; navigate the observed folder tree rather than guessing (list/load are scoped to the current folder).
3. If a same-name project exists, reuse it; never overwrite. If its name differs but media paths match, offer reuse instead of switching.
4. Never switch away from an unsaved project; get consent before saving or switching one that is unrelated.
5. After creating: set timeline fps, `project_manager save`, and read back name, folder and settings.
