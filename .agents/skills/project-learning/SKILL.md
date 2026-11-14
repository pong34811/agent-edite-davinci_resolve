---
name: project-learning
description: Use at the start and end of any DaVinci Resolve editing task in this repo, and whenever you are about to write a new script. Finds the existing tool first, keeps throwaway scripts inside the repo, and records new rules, scripts and corrections so the next session (Claude Code, Codex or Hermes) starts smarter and faster.
version: 0.2.1
author: Warit (pong34811)
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [Workflow, Knowledge, Scripts, AGENTS]
user-invocable: false
---

# Project Learning

Why this exists: agents kept writing new tools outside the repo and never recorded what they learned, so every session re-derived the same things. This skill is the loop that stops that.

## Channel-specific learning

- Before work, read `docs/channels/README.md` and only the profile indexed for the named channel. Keep channel facts, presets and lessons isolated; do not borrow them from another channel without evidence. If identity or evidence conflicts, ask the user rather than guessing. Shared rules remain in `house-style`.
- At the end, propose a learning only when warranted; record it in that channel's profile with date, project/timeline ID or document reference, finding, status, applicability, confirmer and a safe evidence link, following the README template. No automatic memory is implied.
- Mark `confirmed` only for user-confirmed facts or evidence actually inspected, identifying the source; mark unverified ideas `hypothesis` and never treat them as mandatory editing rules or approved preferences. Preserve conflicting history; mark an older entry `superseded` only when justified, with the reason and link to the replacement; unresolved conflicts require user confirmation.
- Privacy: do not put credentials, footage, transcripts or private information in shared notes or exposed links. Do not send footage, audio, transcript or personal information to external providers without explicit permission and scope.

## YouTube post-edit research

For each editing assignment, consult `.agents/skills/resolve-video-enrichment/references/post-edit-review.md`: research current official guidance at the start and, after QC, prepare a separate evidence-limited public comparator review. This is a manual workflow, not automatic execution; it does not authorize timeline changes, external uploads, analytics access or publishing. Keep channel-specific hypotheses separate from confirmed learning.

## Before writing any script

1. Probe the MCP first (see `AGENTS.md` "Start of task checklist").
2. Open `scripts/INDEX.md`; search by task, then `grep -ri "<keyword>" scripts/*.py`.
3. A project-specific script (`p2`, `armigon`, `sakuyako`) may be adapted: copy it into `scripts/scratch/`, change the constants, keep the `resolve_common` plumbing.
4. Nothing fits: print `MCP-GAP: <tool/action checked> -> <reason>` and write `scripts/scratch/<name>.py`. Never write to the Desktop, `%TEMP%`, the home directory or another repo.

## Before saying the task is done

Answer each, in order, and act on every "yes":

| Question | Where it goes |
|---|---|
| Did a call fail or behave unexpectedly, and did you find the cause? | One row in the table of `docs/OPERATING-NOTES.md` (rule + why). |
| Is the script in `scripts/scratch/` reusable by another timeline or project? | Move to `scripts/`, use `resolve_common`, add a test for pure logic, add a row to `scripts/INDEX.md` with its scope label. Otherwise leave it in scratch. |
| Did the user correct taste (cut rhythm, subtitle wording, framing)? | Append to `.agents/skills/house-style/SKILL.md` using its capture protocol. |
| Is there a rule that applies to every task? | Add it to `AGENTS.md`, one or two lines. Anything narrower goes to OPERATING-NOTES or a domain skill. |
| Did you use a workflow, technique or tool sequence that worked (or failed) and is not yet in a skill? | Follow "Writing or updating a skill" below: update the existing skill that covers it; create a new folder in `.agents/skills/` only when none fits. |
| Did project state change (which timelines are done, what is blocked)? | The agent's memory or `work/WORKLOG.md`; not AGENTS.md. |

## Writing or updating a skill

1. **Location.** Every skill for this project lives in `.agents/skills/<name>/` inside this repo, so it is committed and shared by Claude Code, Codex and Hermes. Never create or edit a project skill only in `~/.claude/skills`, `~/.codex/skills`, `~/.hermes/skills`, `~/.agents/skills` or `.claude/skills`. If an agent's own skill tool wrote one there (Hermes `~/.hermes/pending/skills/`, Codex `skill-creator`), copy it into `.agents/skills/` in the same task.
2. **Search before creating.** Run `ls .agents/skills` and `grep -ril "<keyword>" .agents/skills/*/SKILL.md`, and read the `description` of each candidate.
3. **Update when a skill already covers it.** Add the step, trap or example to that skill's `SKILL.md` or a file in its `references/`, keep its `name` and folder, and bump `version` (minor for a new workflow, patch for a fix or wording). Do not create a near-duplicate skill.
4. **Create only when nothing fits.** A new skill needs frontmatter `name` (equal to the folder name) and a `description` that says when to use it. Every local file it cites must exist (the bundle test checks this).
5. **Vendored third-party skills** (HyperFrames, superpowers) are copies of upstream: put project-specific additions in the project's own skill or a `references/` note rather than rewriting upstream text, so a later upstream update stays mergeable.
6. **Register.** Run `python scripts/refresh_skill_manifest.py` (adds new skills to `docs/skills-manifest.json` as `supporting`), then `python -m pytest -q tests/test_skill_bundle.py`.

## Cleaning up files

Gitignored folders are not proof of junk: tests, scripts, channel profiles and live Resolve timelines can read them. Before deleting any path, run `git grep -n -F "<path>"` over `tests/ scripts/ docs/ .agents/` and check Resolve media for it; gitignored files cannot be recovered after `rm`. Deleting `.agents/teamwork/` on 2026-11-07 removed the audit evidence two Armigon QC tests read (they now skip when it is absent).

## Finish

- `python -m pytest -q` (tests that need Resolve are skipped without `--live`).
- After touching skills, scripts or docs: `python scripts/refresh_skill_manifest.py`.
- Inspect `git status`; stage only this task's files. Never stage footage, renders, `.drp`/`.drt`, `.env`, credentials, or unrelated pre-existing changes.
- Write release notes in Thai as verified bullet points. Preview a patch release (default) with `python scripts/release.py --title "<หัวข้อไทย>" --notes-file <path>`; add `--publish` to update `VERSION`/`CHANGELOG.md`, commit those paths, tag, push `main` + the tag, and publish the GitHub Release. Use `--bump minor|major` only when justified. The helper appends `### Skill ที่อัปเดต` and `### ไฟล์ที่เปลี่ยน` from `git diff --name-status <previous tag> HEAD`, so push the content commit first and do not hand-write those lists. Verify the published tag and release URL; never force-push or move an existing tag.
- If checks, credentials, or network block publishing, report the blocker and do not claim success.
- In the final report: name the path used (`davinci-resolve` MCP, Studio MCP, or script), list recorded learnings and paths, include version/release URL when published, and say what was not verified.
