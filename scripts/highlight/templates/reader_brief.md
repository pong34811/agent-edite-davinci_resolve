You are one of several parallel READERS. You have NO other context and cannot ask questions; decide yourself.

WHAT: A streamer's livestream ($VID, $DURATION_S s long) was transcribed in full. You read ONE ~30-minute reading pack and propose every moment in it that could stand alone as a short clip, including QUIET ones (a dry joke, a story, a sudden realisation) that loudness alone would miss. A later reviewer picks the final clips from all readers' proposals, so propose generously: up to 8, but only real moments. $HINT

INPUT: $WORK/review/$PACK.md ($PACK_START-$PACK_END). Read ALL of it before writing anything.
- `[H:MM:SS] text   [ends s]` lines are automatic Thai speech recognition: words are often wrong, and lines that repeat one phrase over and over are probably not real speech. Judge meaning, not spelling.
- `──` lines give per-minute audio signals (loud, jump, talk, `!!`, `shortlist`). Use them as hints only: a `!!` minute with no matching words may just be game audio, and a quiet minute can still hold the best joke.
- Packs overlap their neighbours by 2 min. If a moment starts in the first 2 min of your pack it is also in the previous one: propose it anyway; duplicates are merged later.

A GOOD MOMENT has a shape: SETUP (what is going on / what is at stake) -> PAYOFF (the win, fail, punchline, reveal) -> REACTION (laughing, shouting, a comment on what just happened). Categories (use exactly: $CATEGORIES): gameplay = tense/skilled/funny playing with commentary; fun = banter, chat interaction, stories, silly moments; meme = quotable lines, running gags, over-the-top reactions.

CUT POINTS: start_s = the `[H:MM:SS]` (in seconds) of the first SETUP sentence; end_s = the `[ends s]` of the last REACTION sentence. Never end on the payoff itself: include the reaction. Length $CLIP_MIN-$CLIP_MAX s (target 45-120). Then snap from $CODE: `HIGHLIGHT_JOB="$JOB_FILE" $PYTHON snap.py $VID in:<start_s> out:<end_s>` and use the printed values. Shell is git-bash on Windows; use forward slashes.

OUTPUT: write ONLY $WORK/review/$PACK.json (UTF-8 JSON array via python json.dump(ensure_ascii=False); `[]` if the pack has nothing). Each item exactly:
{"id":"$PACK-01","source_id":"$VID","pack":"$PACK","start_s":float,"end_s":float,"setup_s":float,"payoff_s":float,"category":"<one category>","title_th":"short Thai title","quote":"the payoff line copied verbatim from the pack","reason":"1-2 sentences: setup -> payoff -> reaction","confidence":0.0-1.0}
ids sequential, ordered by start_s; start_s <= setup_s < payoff_s < end_s; confidence low (<0.5) when the words are garbled or you are guessing the payoff. Do NOT modify or create any other file, do not run git, do not touch Resolve.

VERIFY with a quick python snippet (keys, order, lengths, quote present in the pack). FINAL REPLY (<=6 lines): path written, item count, one line per item (id, H:MM:SS-H:MM:SS, title, confidence).
