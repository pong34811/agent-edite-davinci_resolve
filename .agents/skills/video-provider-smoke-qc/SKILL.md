---
name: video-provider-smoke-qc
description: Use when validating a video analysis provider before QC.
---

# Validate video analysis before batch QC

Before sending any source video or audio to an external provider (including
Gemini), obtain explicit user authorization for that upload and provider. Do
not infer permission from a request to analyze, QC, or summarize a video. Prefer
local/read-only checks when authorization is absent; if provider access is
needed, pause and explain what media would be sent.

- Smoke-test one known source clip before sending a candidate batch. Compare the returned duration and scene against live ffprobe facts and an independently extracted source frame; a success flag does not prove the provider processed the intended video.
- Reject an analysis whose scene or duration conflicts with the exact source, even if it claims to hear clear audio. Keep the returned result as a failed diagnostic, not clip evidence.
- Treat `success=true` with a refusal to access the video as a failed media test. Inspect the installed transport adapter: a Gemini-native adapter may convert `image_url` data URLs into MIME-preserving `inlineData` while silently skipping `video_url`. If the user has authorized the upload and the adapter is verified in source, a task-owned client call can carry `data:video/mp4` through that supported converter; validate actual duration, independently extracted frames and explicit audio receipt before batching. Do not edit global Hermes code or claim the ordinary `video_analyze` tool was fixed by changing models alone.
- Require cue timestamps as numeric total seconds (82.0 for 01:22, never 1.22). Flag inconsistencies against subtitles and visible scene transitions for parent review; an in-bounds timestamp is not proof of the correct beat.
- For native Gemini structured reports, request JSON mode and reserve answer-token headroom explicitly: thinking can consume `maxOutputTokens` and truncate a valid report mid-field. Preserve raw content and finish reason before validation. Quarantine out-of-bounds or malformed cues with the original proposal and reason, rather than accepting them or silently dropping them; one invalid cue must not be mistaken for a verified timestamp.
- Require the video analysis to explicitly state whether audio was actually available. Contact sheets, silencedetect and ASR do not verify dialogue, humor or complete sentence boundaries.
- Auxiliary vision configuration can remain cached in a live session. After changing routing through hermes config set, verify the route in a fresh process and retest source matching before batch processing.
- For a no-media-API fallback, use only cached local ASR models with `local_files_only=True`, `HF_HUB_OFFLINE=1`, and `TRANSFORMERS_OFFLINE=1`, plus FFmpeg audio measurements and timestamped frames from authorized previews. Smoke-test Thai speech before batching: game audio/humming can yield confidently wrong words even with large-v3-turbo. Retain ASR as provisional alignment evidence, keep existing captions unchanged, and do not call frame samples plus ASR a complete audiovisual or humor review.
- Saved credential metadata does not establish that the auxiliary resolver can authenticate to that provider. Check actual resolution and real video output; never print secrets or inspect credential file contents.
- Record the prior auxiliary settings before experimenting. Restore them if the route fails rather than leaving all image/video auxiliary requests on an unverified provider.
- If source-matching video/audio QC is blocked, preserve provisional candidates separately from final selects and report the blocker. Do not manufacture evidence or label provisional timelines as verified.
