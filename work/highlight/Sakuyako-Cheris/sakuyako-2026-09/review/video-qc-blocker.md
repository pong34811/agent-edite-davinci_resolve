# Video/audio QC blocker

Candidate selection is provisional: 19 review JSON files, 72 candidates. No Resolve timelines were created in this continuation.

## Actual checks

- Current-session video_analyze on source_previews/v03-02.mp4 failed: Codex Responses does not support video_url input.
- Auxiliary vision was temporarily configured with provider openrouter, model google/gemini-2.5-flash after the user chose real video QC before timeline creation.
- Current-session video tool still returned the same Codex error after config change.
- A fresh Hermes one-shot wrote video_provider_smoke.json claiming successful analysis of a five-second man-in-kitchen food-tasting video. This result is REJECTED: it does not match the actual source.
- ffprobe on the exact target found 87.526693 seconds, 1280x720, video plus audio, 17842701 bytes.
- An actual frame extracted at local t=20 seconds (v03-02.smoke-frame.jpg) shows a MOBA stream with VTuber overlay, not a kitchen. Vision inspection identified hero names Yin and Johnson, suggesting Mobile Legends rather than the prior reviewer label LoL. Game labels and audio-derived titles must be rechecked; a reviewer summary is not source truth.
- A direct fresh runtime attempt could not resolve OpenRouter vision and attempted fallback; the process failed with missing httpx in its rerouted interpreter. No successful source-matching video/audio QC established.
- Restoring auxiliary.vision.provider=auto and auxiliary.vision.model='' to the settings read before this experiment. No primary model configuration was changed.

## Required unblock

An authenticated video-capable route that passes source-matching visual and audio smoke tests. Only then run all 72 candidate intervals through real video/audio QC. Preserve all source footage and provisional review files. Do not treat video_provider_smoke.json as evidence of clip content; keep it only as a failed diagnostic record.
