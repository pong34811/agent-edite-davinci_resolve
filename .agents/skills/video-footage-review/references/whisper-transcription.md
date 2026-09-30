# Whisper transcription on Windows

This reference repairs a missing link in the imported footage-review skill. Follow the Thai-specific timestamp/tokenization and hallucination rules in `.agents/skills/thai-subtitles-resolve/SKILL.md` for publication captions.

## Probe the interpreter before a batch

The recorded working openai-whisper interpreter was `C:/Users/warit/AppData/Local/Programs/Python/Python312/python.exe`. This is a historical environment path, not proof it still exists. Through `terminal`, probe that interpreter (or the approved ASR venv) with `-c "import whisper; print(whisper.__file__)"`; do not install into the default Python just because it lacks the module. The default command in this Windows Git Bash environment is `python`, and `pip` may belong to a different interpreter. Use `<verified-interpreter> -m pip` only when installation is actually authorized.

For faster-whisper CUDA, register PyTorch's `torch/lib` or the installed NVIDIA wheel DLL directories before importing ctranslate2/faster-whisper. Probe WhisperModel loading, not only torch.cuda.is_available(). Preserve CPU fallback as an explicit, measured choice; do not promise CUDA works without a real model-load result.

## Extraction and timing

Decode sources read-only with ffmpeg into a NEW scratch mono 16kHz PCM WAV. Never replace the camera/gameplay original. Map ASR-relative timestamps through actual timeline item source offsets and source/timeline frame rates; retimed clips need a separate mapping. Avoid overlapping-window duplicates.

## Model and uncertainty

For Thai gameplay use small at minimum; medium or large-v3-turbo for noisy/uncertain words. Set language='th' when known and condition_on_previous_text=False. Compare context-rich 4–10s windows with margins, raw vs per-window voice-band denoised audio, and independent model passes. Do not treat confidence alone as speech correctness or invent full coverage for unresolved intervals. Preserve genuinely spoken English game lines; remove stray foreign-script glyphs with their character-time entries.

## Verification

Reparse UTF-8 SRT outputs: consecutive indices, one-line cues, no overlaps, brief gaps, at most 1.5s per cue, short readable Thai text, no stray scripts, and final cue within the approved clip end. Record unresolved spans and uncertain names. If requested only to deliver SRT sidecars, do not import them into Resolve. If import is approved, use the exact empty-track/bare-payload workflow and read back every cue/text/frame/style.
