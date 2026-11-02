You are one of several parallel reviewers. You have NO other context and cannot ask questions; decide yourself.

WHAT: A streamer's long livestream recordings were already shortlisted by an audio-loudness funnel plus Whisper transcription. Read ONE review packet for your video and choose $CLIPS_PER_VIDEO clips of $CLIP_MIN-$CLIP_MAX seconds (target 45-120 s) that would make good short-form clips. Output ONE JSON file.

YOUR VIDEO: VID = $VID (duration $DURATION_S s). $HINT

CATEGORIES (use exactly these strings: $CATEGORIES): gameplay = tense/skilled/funny moments of playing a game with the streamer commenting; fun = banter, chatting, special-occasion moments, reactions to drawing or audience interaction, silly moments; meme = quotable lines, running gags, absurd or over-the-top reactions that work as a standalone short.

INPUTS (under $WORK/):
- review/$VID.packet.md : shortlist windows. Each section is `## <VID>-wNN  H:MM:SS-H:MM:SS score=..`, then `sheet: <path to a jpg contact sheet: 6 frames in a 3x2 grid with a timestamp on each tile>`, then transcript lines `[H:MM:SS] text` covering the window +-60 s. Read it FIRST and fully.
- The transcript is automatic Whisper: it has errors and hallucinations (endless repeated greetings or thank-yous over silence). Lines that repeat the same phrase are probably not real speech. Windows may be intro/outro/BGM-only: skip those.
- Open at most ONE contact sheet per window with `vision_analyze` (image_url = the sheet path) and no more than ~10 sheets in total, to tell gameplay vs chatting vs drawing vs idle screens.

RULES: clip length $CLIP_MIN-$CLIP_MAX s; clips must not overlap and should be spread across the stream (prefer >=5 min apart unless clearly different beats); start at the beginning of a beat or sentence and end right after the payoff, never mid-word; a clip may extend beyond the shortlist window but must stay inside the video (end_s <= $DURATION_S). Categorise from transcript plus sheet, not from the filename. Only raw content is judged; no titles or captions are made later.

SNAPPING (required for every start_s and end_s): run from $CODE : `$PYTHON snap.py $VID <t1> <t2> ...` (seconds; prints `t -> snapped`). Use the snapped values, then re-check the length is still within $CLIP_MIN-$CLIP_MAX s. Shell is git-bash on Windows; use forward slashes.

OUTPUT: write ONLY $WORK/review/$VID.json (UTF-8 JSON array, written with python json.dump(ensure_ascii=False)). Each item exactly:
{"id":"$VID-01","source_id":"$VID","start_s":float,"end_s":float,"category":"<one of the categories>","title_th":"short Thai title","reason":"1-2 sentences why it is interesting","score":0.0-1.0}
ids sequential `$VID-01..`, ordered by start_s, $CLIPS_PER_VIDEO items. Do NOT modify or create any other file, do not run git, do not touch Resolve.

VERIFY with a quick python snippet: item count, durations, end_s <= duration, no overlaps. FINAL REPLY (<=8 lines): path written, clip count, one line per clip (id, H:MM:SS-H:MM:SS, category, title), and an explicit list of clips where you are NOT confident (garbled transcript, guessed punchline, cut points only approximate).
