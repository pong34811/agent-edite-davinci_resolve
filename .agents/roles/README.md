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
| Floating helper | `floating-helper.md` | any unowned or late part, /learn ownership (docs/OPERATING-NOTES.md, skills manifest refresh, commit for learning entries), and help for a role that asks; no Resolve writes without the turn |

**Reviewer roles** — single-purpose checkers that never edit:
`cut-reviewer.md`, `grade-match-verifier.md`.

## Current assignment (Davinci Team channel, 2026-11-28)

| Role | Agent |
|---|---|
| Producer / lead (+ /learn owner: docs/OPERATING-NOTES.md, skills manifest, commit/push) | Hermes-claude |
| Resolve editor (16:9 + 9:16, default holder of the Resolve write turn) | antigravity |
| Render & QC (and backup editor) | opencode (new agent, joined 2026-11-28) |
| Thai content + floating helper (non-Resolve gaps: ASR, subtitle drafts, titles, docs) | Hermes chatgpt |
| Cut reviewer (read-only, `cut-reviewer.md`) | Learning Coach |

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

## Speed and quality rules (added 2026-11-24 after the KT404 2026-11 job)

The 56-clip job took ~20 h; most of it was waiting on hung Resolve, duplicate
work and rework, not editing. These rules remove those losses.

7. **Lead splits every @everyone job in the first reply**: one owner per part,
   by name, with the output path each part must produce. Others do not start
   that part. Parallel work only on parts that do not touch Resolve (ASR,
   subtitles, loudness, title review, frame QC).
8. **"Done" = path + count + one check.** e.g. "`edit/qc_render/` 56/56 mp4,
   all > 0 bytes, ffprobe OK". A claim without files on disk is not done.
9. **Long Resolve batches run under the watchdog**, never in a chat turn:
   `python scripts/scratch/hl2611/supervise.py --out <dir> --project "<P>" -- <py> <resume-safe script>`
   started detached. It restarts Resolve and resumes after a hang (no new file
   for 8 min and Resolve CPU idle). Read `<dir>/supervise.log` for status.
   Batch scripts must be resume-safe (skip finished items) and do one
   timeline per Resolve call; never queue all timelines in one render.
10. **Quality gates before Resolve work, not after.** Check on a 1–2 clip pilot
    first and only then batch: subtitles from the clip's own audio + lint +
    a listen of the pilot; loudness measured (≤ −1 dBTP) on the pilot mix;
    project created with `CreateProject(name, media_location)` and verified.
11. **Never wait on your own command.** Wait loops must match a PID or an
    output file, not a process command line.
12. Status every 30 min while a long job runs: done/total, ETA, blockers.
