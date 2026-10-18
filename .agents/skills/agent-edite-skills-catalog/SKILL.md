---
name: agent-edite-skills-catalog
description: Inventory, read, and route this repo's project skills.
version: 0.1.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [Skills, Resolve, Inventory, Routing]
---

# Project Skills Catalog (agent-edite-davinci_resolve)

Inventories and routes the 46 portable skills shipped in this repo's
`.agents/skills/`, grouping them by job and recording each group's real
triggers, verified commands, and traps so a task goes straight to the skill
that owns it. It does NOT replace those skills — load the owning skill with
`skill_view` before acting — and reading them is never authorization to edit,
render, import, relink, or publish. Read-only; stdlib only.

## When to Use

- "อ่านสกิลทั้งหมด ในโปรเจคนี้" / "read all skills in this project"
- "which skill handles X here?", "what skills does this repo ship?"
- Starting any task in this repo and unsure which project skill owns it
- Auditing the corpus after adding or renaming a skill (directory name vs
  frontmatter `name` drift), or checking a description against the 60-char bar
- Deciding whether a project skill already covers a workflow before authoring a
  new one (`superpowers-writing-skills` governs new skill authoring)

## Prerequisites

- The repo root — the checkout that contains `.agents/skills/`; skills live at
  `.agents/skills/<dir>/SKILL.md`
- Python 3 on PATH as `python`; no packages required
- `docs/README.md` → "Portable Agent Skills" is the maintainer's canonical list
  of the domain skills and the parity contract

## How to Run

1. Inventory through the `terminal` tool:
   `python <skill_dir>/scripts/inventory_skills.py --root <repo>`
   (`--json` for machine output, `--problems` for frontmatter defects only).
2. Or locate the files with `search_files` (pattern `SKILL.md`, target
   `files`, path `.agents/skills`).
3. Load the owner with `skill_view(name="<frontmatter name>")` — use the
   frontmatter `name`, not the directory name.
4. Pull one section of a large skill with `read_file` (offset/limit) instead of
   loading 500+ lines into context.

## Quick Reference

| Group | Skills | Load |
|---|---|---|
| Domain map + Resolve MCP routing (9) | `resolve-mcp`, `resolve-color`, `resolve-edit`, `resolve-conform`, `resolve-delivery`, `resolve-fusion`, `resolve-audio`, `resolve-media-pool`, `resolve-media-analysis` | `references/domain-resolve-skills.md` |
| Domain depth — build gates, offline action catalogs, the gotcha that bites (same 9) | the `resolve-*` domain skills | `references/resolve-domain-depth.md` |
| End-to-end task recipes (10) | `resolve-session`, `resolve-rough-cut`, `resolve-tighten-recording`, `resolve-trim-to-length`, `resolve-batch-export`, `resolve-folder-cover-batch`, `resolve-offline-media-repair`, `resolve-mitr-subtitle-presets`, `video-footage-review`, `video-provider-smoke-qc` | `references/task-recipe-skills.md` |
| Thai / VTuber production (10) | `resolve-video-enrichment`, `thai-subtitles-resolve`, `thai-proofread`, `vtuber-content-curriculum`, `vtuber-thumbnail-layout`, `vtuber-thumbnail-qc`, `vtuber-cover-batch-pipeline`, `youtube-content`, `youtube-downloader`, `gif-search` | `references/thai-vtuber-skills.md` |
| Superpowers methodology (15) | `superpowers-*` (dir prefix) → frontmatter names without the prefix | `references/superpowers-skills.md` |
| House rules and release (2) | `house-style`, `agent-skill-repo-release` | `references/governance-and-conventions.md` |
| Utility tools (3) | `youtube-content`, `gif-search`, `video-provider-smoke-qc` | `references/utility-tool-skills.md` |
| Authoring or editing a skill | `superpowers-writing-skills` distilled — the Iron Law, form-matching, micro-tests | `references/skill-authoring-rules.md` |
| Cutting clips in Resolve | the profile's `resolve-clip-editing` knowledge base | `skill_view(name="resolve-clip-editing")` |

Load a reference on demand with
`skill_view(name="agent-edite-skills-catalog", file_path="references/<file>")`.

## Procedure

1. Confirm the repo root and read `AGENTS.md` first — it carries the tool
   mandate, track architecture, and the "current explicit user instructions
   govern scope" rule that overrides any skill text.
2. Run the inventory script (step 1 of How to Run). Expect 46 `SKILL.md` files;
   a different count means a skill was added or removed — read `CHANGELOG.md`
   and `git status` before trusting the table above.
3. Match the task to a group in Quick Reference, then load that reference file.
4. Load the owning skill itself with `skill_view` (frontmatter name) and follow
   it — the reference files here are routing notes, not the procedure.
5. For a task spanning domains, load `resolve-mcp` (the map) plus each domain
   skill that applies.
6. If no project skill covers the task, load `resolve-clip-editing` (this
   profile's distilled cutting knowledge base), then check `docs/` (`guides/`,
   `kernels/`, `reference/`) before authoring anything new.
7. Report which skills you loaded and which rule governed the decision.

## Pitfalls

- **Directory name ≠ frontmatter name for the superpowers set.**
  `.agents/skills/superpowers-writing-skills/SKILL.md` declares
  `name: writing-skills`. `skill_view` needs the frontmatter name.
- **Descriptions here are long-form on purpose.** They run from ~40 to 566
  characters; Claude/Codex route on the full text. Do not copy them verbatim
  into a profile skill — the Hermes index truncates at 60 characters.
- **Platforms are a routing signal.** The Resolve family declares
  `[windows]`; `gif-search`, `thai-proofread`, `youtube-content`,
  `youtube-downloader`, and `vtuber-thumbnail-layout` declare cross-platform,
  so they are the ones safe to reuse outside this host.
- **Project skills are not loaded until the repo is trusted.**
  `hermes skills trust` stores the root in `skills.trusted_project_dirs` in
  `~/.hermes/config.yaml`; `skills.project_discovery: false` disables scanning
  and the notice entirely.
- **`docs/related-skills/` and `docs/skill-variants/` are archives**, not
  default editing instructions.
- **`docs/SKILL.md` (~150 KB) is the Resolve MCP operating reference, not a
  skill.** Never load it whole; use `read_file` with offset/limit.
- **Two skills depend on an external `agent-thumbnail` repo that is not in this
  bundle** — `resolve-folder-cover-batch`, `vtuber-cover-batch-pipeline`. Read
  that repo's `AGENTS.md` or stop before mutating anything.
- **Skills whose `platforms:` is `[windows]`** (`house-style`, `resolve-mcp`,
  and the Resolve family) encode native paths; pass `C:/...` forward-slash paths
  to native tools, never MSYS `/tmp`.
- **Reading is not authorization.** A learning-only request produces notes and
  stops before connecting to Resolve.

## Verification

`python <skill_dir>/scripts/inventory_skills.py --root <repo> --problems` prints
one line per frontmatter defect. Verified baseline on this repo: **46 skills,
31 flagged**, all falling into exactly three known classes — long descriptions
(>60 chars) on the Resolve family and `house-style`, the `superpowers-*`
directory/name alias pairs, and three one-off findings (`thai-proofread`
description not sentence-final; `video-provider-smoke-qc` and
`vtuber-cover-batch-pipeline` declare no `version`). Anything outside those
classes is a real regression — a skill whose frontmatter `name` no longer
matches its directory will not route.
