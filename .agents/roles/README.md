# Roles

Two kinds of role live here.

**Team roles** — who does which part of an editing job when several agents work
on one project (an OpenBot channel, or several sessions at once). Each role
file says what the role owns, what it must not touch, and what a finished
handoff contains.

| Role | File | Owns |
|---|---|---|
| Producer / lead | `producer-lead.md` | brief, plan, Resolve write turn, final QC, repo learning and commit |
| Resolve editor | `resolve-editor.md` | all timeline writes: 16:9 cut, 9:16 build, zoom, subtitles, audio mix |
| Render & QC | `render-qc.md` | `.drp` backups, test renders, ffprobe/loudness/black-frame/position checks, scripts and tests |
| Thai content | `thai-content.md` | highlight picks, hook, Thai subtitle proofread, YouTube title/description/thumbnail text |
| Floating helper | `floating-helper.md` | any unowned or late part, and help for a role that asks; no Resolve writes without the turn |

**Reviewer roles** — single-purpose checkers that never edit:
`cut-reviewer.md`, `grade-match-verifier.md`.

## Current assignment (Davinci Team channel, 2026-11-23)

| Role | Agent |
|---|---|
| Producer / lead | claude |
| Resolve editor | antigravity |
| Render & QC (and backup editor) | opencode |
| Thai content | chatgpt |
| Floating helper | hermes |

The agent names change; the roles do not. Update this table when the user
reassigns someone.

## Rules every role follows

1. **One Resolve writer at a time.** Only the agent holding the write turn
   (given by the lead) changes Resolve state. Everyone else reads only. Before
   writing, say in the chat that you hold the turn; say when you release it.
   On Day 35 three agents started the same fix at once — that is the failure
   this rule prevents.
2. Rules in `AGENTS.md` apply to every role: MCP first, Python scripts second,
   no GUI automation, verified `.drp` backup before a batch change, work on a
   copy timeline, never overwrite source footage.
3. **One owner per @everyone job.** When a task is requested with `@everyone`,
   only the designated owner for that domain (e.g. producer-lead for downloads
   and pipeline dispatch, resolve-editor for Resolve writes) takes execution.
   Other members must check for active claim files (e.g. `_DOWNLOADING_by_<agent>.txt`
   or lock files) and active system processes before initiating work, preventing
   duplicate work runs (e.g. parallel downloaders creating ~110 GB of duplicate data).
4. No upload, final render, release, or timeline deletion unless the user asked
   for it in words.
5. Report only what was verified, with the evidence (file path, measured
   number, frame checked). Say what was not checked.
6. Name every file you changed in your handoff, so the lead can stage only the
   task's files.
