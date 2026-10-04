---
name: house-style
description: The editorial and finishing preferences this project's work is judged against — cut rhythm, shot selection, delivery conventions, and the corrections that have already been given. Load before assembling, restructuring, or refining any cut so the same note does not have to be given twice.
version: 0.3.0
author: Warit (pong34811), Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [Editing, House-Style, Corrections, Workflow]
user-invocable: false
---















# House Style















The craft guides in `docs/guides/` describe editing in general. This file







describes **how this editor wants it done** — the accumulated, specific







corrections that would otherwise have to be repeated every session.















Read it before any edit task. Append to it whenever a correction is given.















## The capture protocol















This file is only worth what gets written into it. When the user corrects an







editorial decision — rejects a cut, changes a shot choice, adjusts a duration,







says "not like that" — do not just fix it. Fix it, then add the rule here.















A useful entry has three parts:















- **The rule**, stated as an instruction, not an observation.







- **Why**, in the user's terms — what it was in service of.







- **The trap**, if there is one: what makes it easy to get wrong.















Write rules that are falsifiable. "Cut on motion" is a rule; "make it feel







dynamic" is not. If a correction is one-off and situational, it does not belong







here — this file is for what generalizes.















When an entry turns out to be wrong or too broad, edit it. A stale rule







confidently followed is worse than no rule.















---















## Pacing and rhythm















<!-- Hold lengths, when to cut early, what "too long" means for this material. -->















For short-form subtitle passes, keep each Thai caption to at most three short







words and about 14 Thai characters, with no more than 1.5 seconds on screen.







Write Thai captions without spaces between Thai words; keep spaces only around







Latin terms such as names. Use shorter holds when the spoken words arrive







faster. The trap is using spaces to show word grouping, which makes Thai text







look unnaturally spread out.















## Subtitle track only















Create and continue dialogue captions only on native Resolve Subtitle tracks.







Do not use Text+ / TextPlus, Fusion titles, or text on video tracks as a







substitute, even if they offer easier styling. The user wants subtitles kept







in the existing Subtitle-track workflow. Historical Text+ captions are not







permission to create more; migrating existing captions must preserve their







text and timing and must not remove unrelated titles or overlays.















Treat a native-track preference as a creation rule, not permission to modify every historical Text+ timeline.







Confirm the migration targets; preserve protected horizontal versions. After







verifying exact text and frames, disable a captions-only legacy track rather







than deleting its clips. Never disable a mixed track of titles and overlays.







When the user handles fonts/styles, do not revive an older font/style plan;







report legibility problems without styling or retiming outside current scope.







For preserve-text-and-timing migrations, flag legacy house-style exceptions







instead of dropping words, shortening holds, or splitting cues automatically.















## Saved subtitle font presets

When the user requests subtitle font styling by preset, load the exact approved
saved Subtitle-track preset instead of manually guessing font, size, stroke or
position. Discover the saved name and source library; ask before substituting
`Mitr Font` for `Mitr-Font` or borrowing a preset from another library. This
keeps the user's established style intact. Python-based SQL workarounds still
require explicit database-write approval and a verified backup; a font request
alone does not authorize SQL. Preserve every cue's text/timing and all original
video/audio ranges.

## Shot selection















<!-- What earns a place in the cut; what gets dropped even when it's a good shot. -->















_Not yet captured._















## Cut points















<!-- Cut on motion vs on rest, handles, how much air before and after a beat. -->















_Not yet captured._















## Structure and openings















<!-- How a piece starts, what the first frames have to do, how it lands. -->















_Not yet captured._















## Rejected by default















Things not to add unless explicitly asked. Seeded from the rough-cut deliverable







contract in the `resolve-rough-cut` skill, which exists because this work gets







thrown away:















- Titles, captions, and text cards







- Transitions (an assembly is hard cuts)







- Effects and speed ramps







- Music beds







- Grading on a cut that was asked for as an assembly















## Delivery conventions















<!-- Aspect ratios, timeline naming, versioning, where renders go. -->















_Not yet captured._















---















## Where personal grading taste lives















Colour and look preferences are **not** kept here — this file travels with the







repository. Grading taste lives in the user-level `colorist-assistant` skill and







in persistent memory. Load those for look selection, grade transfer, and the







Resolve API traps around them.















If any entry below would be specific to one person rather than to this project's







work, it belongs in the user-level skill instead, and this file should be







gitignored rather than committed.







