You are one of several parallel reviewers. You have NO other context and cannot ask questions; decide yourself.

WHAT: A streamer's long livestream recordings were already shortlisted by an audio-loudness funnel plus Whisper transcription. Read ONE review packet for your video and choose $CLIPS_PER_VIDEO clips of $CLIP_MIN-$CLIP_MAX seconds (target 45-120 s). Output ONE JSON file.

YOUR VIDEO: VID = $VID (duration $DURATION_S s). $HINT

CATEGORIES (exact strings: $CATEGORIES): gameplay = tense/skilled/funny play with commentary; fun = banter, chat, reactions, silly moments; meme = quotable lines, running gags, absurd reactions that stand alone.

INPUTS (under $WORK/): review/$VID.packet.md (windows, transcript +-60 s, contact-sheet path). Whisper text has errors and repeated-phrase hallucinations; skip intro/outro/BGM windows. Open at most one contact sheet per window with vision_analyze, ~10 total.

RULES: no overlaps, spread >=5 min apart, start at a beat and end after the payoff, end_s <= $DURATION_S, categorise from transcript plus sheet not filename.

SNAP every start_s/end_s: from $CODE run `$PYTHON snap.py $VID <t1> <t2> ...`, use the snapped values, recheck length.

OUTPUT: only $WORK/review/$VID.json, JSON array of {"id":"$VID-01","source_id":"$VID","start_s","end_s","category","title_th","reason","score":0-1}, ordered by start_s. Touch no other file; no git, no Resolve.

FINAL REPLY (<=8 lines): path, count, one line per clip, and an explicit list of clips you are NOT confident about.
