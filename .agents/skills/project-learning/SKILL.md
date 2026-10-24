---
name: project-learning
description: Use at the start and end of any DaVinci Resolve editing task in this repo, and whenever you are about to write a new script. Finds the existing tool first, keeps throwaway scripts inside the repo, and records new rules, scripts and corrections so the next session (Claude Code, Codex or Hermes) starts smarter and faster.
version: 0.1.0
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
| Did you use a workflow, technique or tool sequence that worked (or failed) and is not yet in a skill? | Write it into the matching `.agents/skills/<domain>/SKILL.md` (or its `references/`); create a new skill folder only when no domain skill fits. |
| Did project state change (which timelines are done, what is blocked)? | The agent's memory or `work/WORKLOG.md`; not AGENTS.md. |

## Finish

- `python -m pytest -q` (tests that need Resolve are skipped without `--live`).
- After touching skills, scripts or docs: `python scripts/refresh_skill_manifest.py`.
- Always, after every task (user's standing instruction): `git status`, stage the learning/doc/script changes (never footage, renders, `.drp`/`.drt`, `.env`, credentials), commit, and `git push origin main` right away without asking. Push failed → report it; never force-push.
- In the final report: name the path used (`davinci-resolve` MCP, Studio MCP, or script), list what you recorded and where, and say what you did not verify.
