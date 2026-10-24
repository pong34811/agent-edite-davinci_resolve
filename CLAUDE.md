# CLAUDE.md

@AGENTS.md

Claude Code specifics (all other rules are in `AGENTS.md`, shared with Codex and Hermes):

- Use the `davinci-resolve` MCP first; it must be enabled in `.claude/settings.local.json` (not listed in `disabledMcpjsonServers`). The built-in `DaVinci Resolve` MCP (`get_resolve_status`, `run_script`) is the second channel.
- Before writing any script, search `scripts/INDEX.md`. New throwaway tools go only in `scripts/scratch/`, never outside this repository.
- Skills are in `.agents/skills/`; read the `SKILL.md` directly if the Skill tool does not list it.
- When the task ends, follow `.agents/skills/project-learning/SKILL.md` to record rules, scripts and corrections, update `AGENTS.md`/skills, then commit and `git push` immediately (every task, no need to ask).
