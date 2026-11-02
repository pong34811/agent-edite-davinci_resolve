# Sakuyako-Cheris Candidate Review Guide

This is a source-review task, not a code change. Review only the immutable packet assigned to your source ID and its linked contact sheets; do not edit source video, shared pipeline files, Resolve, or other reviewers' files.

## Candidate rules

- Select 4–8 distinct, self-contained moments for this source when evidence supports that many. If the recording does not support at least four genuinely good moments, return only the good candidates and state the shortfall; never pad with weak/redundant clips.
- Each proposed interval must be 30–180 seconds, within the source duration, and contain a coherent setup/context, turn or event, and payoff/reaction. Prefer about 45–120 seconds when the beat allows it.
- Candidates from the same source must not overlap. Spread candidates across the full recording where possible; avoid multiple cuts of the same event.
- Choose categories only from `gameplay`, `fun`, `meme`, based on the actual moment, not filename.
- Whisper Thai transcript is noisy evidence only. Verify picture/audio around each selected moment using its contact sheet; inspect no more than 10 sheets for this source. Do not assert exact quotes, actions, or punchlines that the packet/sheet cannot support. Mark uncertainty plainly in `reason`.
- Use candidate start/end as continuous source-relative seconds, never concatenated clock digits or frame counts. Convert `H:MM:SS` by `hours*3600 + minutes*60 + seconds` (e.g. `0:18:30` = `1110` seconds); reject any endpoint beyond the inventory duration. Snap all start/end times using `HIGHLIGHT_JOB=C:/Users/warit/Desktop/agent-seacrh-virus-cut/work/Sakuyako-Cheris/sakuyako-2026-09/job.json` and `C:/Users/warit/AppData/Local/Programs/Python/Python312/python.exe C:/Users/warit/Desktop/agent-seacrh-virus-cut/work/snap.py <source_id> <t1> <t2> ...`; use returned snapped values and re-check duration/source bounds/no-overlap.

## Required output

Write ONLY the assigned `work/Sakuyako-Cheris/sakuyako-2026-09/review/<source_id>.json` as a UTF-8 JSON array. Each item must have exactly these fields:

- `id`: sequential `<source_id>-01`, `<source_id>-02`, ... ordered by start time
- `source_id`: assigned source ID
- `start_s`: snapped numeric source-relative start in seconds
- `end_s`: snapped numeric source-relative end in seconds
- `category`: `gameplay`, `fun`, or `meme`
- `title_th`: concise Thai clip title grounded in verified content
- `reason`: 1–2 sentences describing the evidence and why the beat is interesting; flag any uncertainty
- `score`: number from 0.0 through 1.0, comparative only, not a view prediction

Do not create timelines or perform any Resolve operations. After writing, validate your output locally for item count, keys, bounds, duration, categories, sequential IDs, sort order, and no overlaps. Final response must state the path, candidate count, and any source/caption uncertainty.
