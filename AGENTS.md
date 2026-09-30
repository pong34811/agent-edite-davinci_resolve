# agent-edite-davinci_resolve — Editing Agent Rules

This repository packages the user's existing DaVinci Resolve editing skills. It is not the MCP server implementation and does not contain footage or a Resolve project database.

## Before editing

- Read `.agents/skills/house-style/SKILL.md` and `docs/OPERATING-NOTES.md`, then load the skill matching the actual request. Use `read_file` if a project skill is not yet registered in `skill_view`.
- Skills are in `.agents/skills/`; their Resolve manuals retain the original `docs/` and `resolve-advanced/README.md` layout. `docs/related-skills/` and `docs/skill-variants/` are archives, not default editing instructions.
- Current explicit user instructions govern scope. Historical skill usage does not authorize a new edit, render, import, relink, cleanup, or database patch.
- Discover the live project, timeline IDs, exact Resolve build, resolution, both frame-rate settings, media paths, and existing video/audio/subtitle coverage before writing.
- Preserve the project's approved aspect ratio. Do not automatically turn a 16:9 project into 9:16 or assume settings from another project.

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
