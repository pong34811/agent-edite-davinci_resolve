# Decisions (Task 0, answered by user)
- ASPECT: 16:9 1920x1080 (project already 1920x1080 @ 60fps)
- CLIPS_PER_VIDEO: 4-8
- APPROVAL: auto (no pause before building timelines)
- Resolve: reuse open project `2026-10-03` (4 clips online incl. 3 AV1, 0 timelines)
- GPU: faster-whisper large-v3 float16 works after `gpu_env.setup()` (pip nvidia-cublas-cu12 + nvidia-cudnn-cu12 in venv)
- Ruling: code lives in `work/`, artifacts in `work/hoshi/2026-10-03/` (WORK_DIR); plan's `work/<artifact>` means WORK_DIR/<artifact>.
- Ruling (Task 3/4): shortlist per_hour 14->20 and transcribe PAD_S 90->60. With 14/90 the padded spans covered ~70% of footage (413 min), defeating the funnel; 20/60 covers ~50% (320 min) with more candidate windows. Cost if wrong: more GPU time or slightly lower recall.
- Ruling (Task 5): contact-sheet/packets tests were written before code but not run RED first (they passed on first run). Cost: none observed.
- Ruling (Task 4): sequential large-v3 ran ~2.5x realtime (too slow); switched to faster-whisper BatchedInferencePipeline (batch_size=16, beam 1) on the same large-v3 fp16: ~26x realtime. Cost if wrong: none (same model/accuracy class); VAD is built into batched mode.
