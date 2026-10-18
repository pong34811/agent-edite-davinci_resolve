# Utility tool skills (3 skills)

The three small non-Resolve skills in the bundle. Each is thin on prose but has
one rule that matters more than its size suggests.

## `video-provider-smoke-qc` — validate a provider before batch QC (24 lines)

Trigger: validating a video analysis provider before trusting its batch output.

**The authorization rule comes first:** before sending any source video or audio
to an external provider (including Gemini), obtain explicit user authorization
for that upload AND provider. **Do not infer permission from a request to
analyze, QC, or summarize a video.** Prefer local/read-only checks when
authorization is absent; if provider access is needed, pause and explain what
media would be sent.

Then the gate:

- **Smoke-test one known source clip before sending a candidate batch.** Compare
the returned duration and scene against live ffprobe facts and an independently
extracted source frame — **a success flag does not prove the provider processed
the intended video.** Reject an analysis whose scene or duration conflicts with
the exact source, even if it claims to hear clear audio; keep it as a failed
diagnostic, not clip evidence.
- **`success=true` with a refusal to access the video is a failed media test.**
  Inspect the installed transport adapter: a Gemini-native adapter may convert
  `image_url` data URLs into MIME-preserving `inlineData` while **silently
  skipping `video_url`**. If the upload is authorized and the adapter is verified
  in source, a task-owned client call can carry `data:video/mp4` through that
  converter — validate actual duration, independently extracted frames and
  explicit audio receipt before batching. **Do not edit global Hermes code or
  claim the ordinary `video_analyze` tool was fixed by changing models alone.**
- **Cue timestamps must be numeric total seconds** (82.0 for 01:22, never 1.22).
  Flag inconsistencies against subtitles and visible scene transitions for parent
  review — an in-bounds timestamp is not proof of the correct beat.
- **Native Gemini structured reports:** request JSON mode and reserve answer-token
  headroom explicitly, because thinking can consume `maxOutputTokens` and truncate
  a valid report mid-field. Preserve raw content and finish reason before
  validation. **Quarantine** out-of-bounds or malformed cues with the original
  proposal and reason rather than accepting them or silently dropping them.
- **Require the analysis to state whether audio was actually available.** Contact
  sheets, silencedetect and ASR do not verify dialogue, humor or complete sentence
  boundaries.
- Auxiliary vision config can stay cached in a live session — after changing
  routing with `hermes config set`, verify the route in a **fresh process** and
  retest source matching before batch processing. Record the prior auxiliary
  settings before experimenting and restore them if the route fails.
- **No-media-API fallback:** only cached local ASR models with
  `local_files_only=True`, `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, plus
  FFmpeg audio measurements and timestamped frames from authorized previews.
  Smoke-test Thai speech before batching — game audio/humming can yield
  confidently wrong words even with `large-v3-turbo`. Keep ASR as provisional
  alignment evidence, leave existing captions unchanged, and do not call frame
  samples plus ASR a complete audiovisual or humor review.
- **Saved credential metadata does not establish that the auxiliary resolver can
  authenticate** to that provider. Check actual resolution and real video output;
  never print secrets or inspect credential file contents.
- If source-matching QC is blocked, keep provisional candidates separate from
  final selects and report the blocker. **Never manufacture evidence or label
  provisional timelines as verified.**

## `youtube-content` — transcripts into summaries, threads, blogs (96 lines)

Triggers: the user shares a YouTube URL, asks to summarize a video, requests a
transcript, or wants content extracted and reformatted. Ships
`references/output-formats.md` and `scripts/fetch_transcript.py`.

Setup is unusual and worth reading before running anything: use the Python from a
package-manager-prepared Hermes source checkout, because the `youtube` extra
declares the helper's dependency — **do not install packages into Hermes with raw
pip or project-discovering `uv run`.**

```bash
source ./activate
python -c "import pm; pm.sync_venv(['youtube'], explicit=True)"
source ./activate
python -c "import youtube_transcript_api; print(youtube_transcript_api.__file__)"
```

On Windows use `. .\activate.ps1` instead of `source ./activate`. Run every
command with the interpreter whose import check succeeded.

Helper accepts any standard YouTube URL, `youtu.be` short links, shorts, embeds,
live links, or a raw 11-character video ID:

```bash
python SKILL_DIR/scripts/fetch_transcript.py "URL"              # JSON + metadata
python SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only  # plain text
python SKILL_DIR/scripts/fetch_transcript.py "URL" --timestamps
python SKILL_DIR/scripts/fetch_transcript.py "URL" --language tr,en
```

Output formats: chapters, summary (5-10 sentences), chapter summaries, X/Twitter
thread (numbered posts under 280 chars), blog post, quotes with timestamps.
Default to a summary if the user did not specify.

Workflow: fetch (`--text-only --timestamps`) → validate non-empty and in the
expected language → chunk if over ~50K characters (split ~40K with 2K overlap and
summarize each chunk before merging) → transform → re-read the output for
coherence, timestamps and completeness. If the transcript is empty, retry without
`--language` to get any available transcript, then tell the user the video likely
has transcripts disabled. On a missing dependency, repeat the PM preparation and
reactivation — **do not repair the selected generation with pip.**

## `gif-search` — Tenor GIF search and download (91 lines)

Triggers: reaction GIFs, visual content, sending GIFs in chat. Pairs with the GIF
placement rules in `resolve-video-enrichment`.

Setup: `TENOR_API_KEY` in `${HERMES_HOME:-~/.hermes}/.env`; free key from
https://developers.google.com/tenor/guides/quickstart. Needs `curl` and `jq`.

```bash
curl -s "https://tenor.googleapis.com/v2/search?q=thumbs+up&limit=5&key=${TENOR_API_KEY}" | jq -r '.results[].media_formats.gif.url'
curl -s "https://tenor.googleapis.com/v2/search?q=nice+work&limit=3&key=${TENOR_API_KEY}" | jq -r '.results[].media_formats.tinygif.url'
URL=$(curl -s "https://tenor.googleapis.com/v2/search?q=celebration&limit=1&key=${TENOR_API_KEY}" | jq -r '.results[0].media_formats.gif.url')
curl -sL "$URL" -o celebration.gif
```

| Parameter | Description |
|---|---|
| `q` | Search query (URL-encode spaces as `+`) |
| `limit` | Max results (1-50, default 20) |
| `key` | API key from `$TENOR_API_KEY` |
| `media_filter` | `gif`, `tinygif`, `mp4`, `tinymp4`, `webm` |
| `contentfilter` | `off`, `low`, `medium`, `high` |
| `locale` | `en_US`, `es`, `fr`, ... |

Formats under `.media_formats`: `gif` (full quality), `tinygif` (small preview),
`mp4` (smaller file size), `tinymp4`, `webm`, `nanogif` (tiny thumbnail). For
chat, `tinygif` URLs are lighter weight; GIF URLs work directly in markdown.
URL-encode the query (spaces as `+`, special chars as `%XX`).
