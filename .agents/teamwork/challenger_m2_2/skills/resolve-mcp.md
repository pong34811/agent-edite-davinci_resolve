# resolve-mcp Skill Reference

Orientation and index for DaVinci Resolve MCP work — grading, editing, conforming, delivery, media analysis, and .drp/.drt/.drx file work, live in a running Resolve or offline with none open.

Core rules:
1. Source media is sacred: never modify, transcode, convert, proxy, relink, or derive source media unless explicitly asked.
2. Read the build before you promise a capability: Resolve scripting API varies by patch release.
3. Live vs offline server division: Python MCP drives live running Resolve; Node advanced server authors offline files / direct DB edits.
4. Save with ProjectManager.SaveProject() and restore original states (active project, timeline, playhead, page).
