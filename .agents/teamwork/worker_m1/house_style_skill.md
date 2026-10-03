# House Style Skill Dump
Source: C:\Users\warit\Desktop\agent-edite-davinci_resolve\.agents\skills\house-style\SKILL.md

## Pacing and rhythm
For short-form subtitle passes, keep each Thai caption to at most three short words and about 14 Thai characters, with no more than 1.5 seconds on screen.
Write Thai captions without spaces between Thai words; keep spaces only around Latin terms such as names. Use shorter holds when the spoken words arrive faster.

## Subtitle track only
Create and continue dialogue captions only on native Resolve Subtitle tracks. Do not use Text+ / TextPlus, Fusion titles, or text on video tracks as a substitute.
For preserve-text-and-timing migrations, flag legacy house-style exceptions instead of dropping words, shortening holds, or splitting cues automatically.

## Safety & Invariants
- Save with ProjectManager.SaveProject()
- Never alter source footage
- Restore UI state
