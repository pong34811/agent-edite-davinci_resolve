---
name: video-footage-review
description: Review video footage and produce a first-pass edit cutlist.
---

# Video Footage Review & First-Pass Edit

## Workflow

### 1. Inventory the footage

List all files in the target folder. If the path is a single file, note that — do not assume a folder of clips.

Use `search_files(pattern="*", target="files", path="<folder-path>")`; do not assume the inventory contains multiple clips.

### 2. Get video metadata

```bash
ffprobe -v quiet -print_format json -show_format -show_streams "<video-file>"
```

Capture: resolution, fps, duration, codecs, audio channels, creation tool (look for `encoder` tag — e.g. `Blackmagic Design DaVinci Resolve Studio`).

### 3. Extract frames for visual review

Extract one frame every N seconds (10s is a good default for a first pass; use 5s for fast-paced content):

```bash
mkdir -p "<scratch-dir>/frames"
ffmpeg -y -i "<video-file>" -vf "fps=1/10" -q:v 2 "<scratch-dir>/frames/frame_%03d.jpg"
```

### 4. Extract audio for transcription

Whisper works best with mono 16kHz PCM WAV:

```bash
ffmpeg -y -i "<video-file>" -vn -acodec pcm_s16le -ar 16000 -ac 1 "<scratch-dir>/audio.wav"
```

### 5. Transcribe with Whisper

**Pitfall — Whisper is not in the default Python.** On this machine openai-whisper lives in Python 3.12 at `C:/Users/warit/AppData/Local/Programs/Python/Python312/python.exe`. Do not use the default `python` or venv `python` — they will raise `ModuleNotFoundError`.

```bash
C:/Users/warit/AppData/Local/Programs/Python/Python312/python.exe -c "
import whisper
model = whisper.load_model('medium')  # 'small' ok for quick check; 'medium' for accuracy
result = model.transcribe('<scratch-dir>/audio.wav', fp16=False, language=None)
for seg in result['segments']:
    print(f'[{seg[\"start\"]:.1f}-{seg[\"end\"]:.1f}] {seg[\"text\"].strip()}')
"
```

- Use `language=None` (auto-detect) when the language is uncertain or mixed.
- Use `language='th'` when you know the content is Thai.
- Start with `small`; escalate to `medium` if the transcript is too noisy to read.
- `base` model frequently produces garbled output on mixed-language or noisy audio — skip it for review work.

### 6. Visually inspect key frames

Use `vision_analyze` on frames at: start (frame_001), ~25% through, ~50%, ~75%, and the last frame. Look for:
- Visual quality issues (artifacts, corruption, glitches)
- Scene changes or shot boundaries
- On-screen text
- Whether the visual is consistent with the audio content

### 7. Compile the first-pass cutlist

Cross-reference the transcript timestamps with the visual inspection. Categorize each segment:

- **Cut** — wrong words, factual errors, recording glitches, dead space (no speech/progress for >3s), long silences, unintelligible mixed-language noise
- **Keep** — clear content that advances the story

Produce a structured report with a cutlist table (timestamp ranges, duration, reason) and a keep list.

### 8. Select short-form highlights and hand off to Resolve

Use this when the source is a long recording or the user asks for one Resolve timeline per selected moment.

1. **Shortlist systematically.** Inventory every source first. Use transcript, audio-event/energy cues, and coarse visual sampling to shortlist candidate windows across the full runtime; do not let a score or transcript alone decide a clip.
2. **Review context and boundaries.** Inspect candidate contact sheets alongside transcript/audio context. Choose one continuous source range per highlight with enough lead-in and payoff. Extract or inspect the exact source frame at each proposed IN and OUT; move boundaries off menus, loading screens, dead air, or cut-off reactions. Recheck any range after changing its timecodes.
3. **Write and validate a manifest.** Record source ID, category, source-relative IN/OUT, concise summary/title, evidence, and confidence. Validate duration and source bounds, then run the Resolve builder in dry-run mode and confirm every source maps to the intended Media Pool item before any write.
4. **Preflight the live project.** Read back the active project name, resolution, `timelineFrameRate`, and `timelinePlaybackFrameRate` separately. A 60 fps timeline setting does not prove the playback rate is 60. Compare every approved project property, including resolution, with the live values. If any differ, stop before creating timelines or markers and ask whether to restore the approved target or explicitly accept the current value; record the user's choice. Never silently inherit a changed resolution.
5. **Build and verify.** Only after the manifest, dry-run, and project settings pass, create the requested separate timelines and source markers. Save through Resolve, then read back each timeline's source range, duration, frame rate, resolution, and tracks/items. Verify each source marker by reading `MediaPoolItem.GetMarkers()` and matching its customData, start frame, duration, name, and category color; an `AddMarker()` success alone is not readback. Keep all edits in the Resolve project; leave source media unchanged.
6. **Reconcile after user QC instead of rebuilding.** Re-read the live project and target bin; map timelines by `GetUniqueId()` rather than name, since users may rename clips. Treat each surviving timeline's actual `GetSourceStartFrame()`/`GetSourceEndFrame()` as authoritative, update manifests and selection reports to those frame-exact ranges, and preserve all QC edits. For retained timelines, align source markers to the live start frame, duration, name, and category; remove only markers whose customData belongs to timelines the user removed. Resolve has no in-place marker-range edit, so replace a changed marker with `DeleteMarkerByCustomData()` then `AddMarker()`, and read it back from `GetMarkers()` by frame/customData, duration, color, and name before saving. Never lengthen a QC-approved short clip just to satisfy the original target; report it as an exception. Save the project, then verify timeline/bin counts and marker counts match.
7. **Report the handoff.** In the user's language, provide the complete source inventory and a clip table with category, source TC IN–OUT, duration, and content summary. State clearly whether timelines were actually created, what was verified, and any blocker; do not present a shortlist as a completed Resolve edit.

## Output format

Deliver the report in the language the user used for the request. Structure:

1. **Footage inventory** — table of files, sizes, formats, durations
2. **Content summary** — what the video is about (from transcript + visual)
3. **First-pass cutlist** — table: # | start | end | duration | reason
4. **Keep list** — timestamp ranges of content to retain
5. **Notes** — any observations about audio quality, language mixing, or structural issues

## Pitfalls

- **Whisper model choice matters.** `base` produces unusable output on mixed-language Thai content; use `small` minimum, `medium` for publication-grade transcripts.
- **Do not trust a single or context-starved Whisper pass.** For uncertain Thai speech, re-transcribe a 4–10 s window with neighboring words and 1–3 s margins, using both raw and per-window voice-band denoised audio with `medium` and `large-v3-turbo` (`language="th"`, `condition_on_previous_text=False`, and temperature fallback). Compare text and confidence indicators; a short crop loses Thai word boundaries, while global denoising can degrade clean sections. When the user asks for transcription, try context-rich, alternate-model passes before asking them to listen or sending crops; retain uncertainty if results still conflict.
- **The folder may contain a single file, not multiple clips.** Check before assuming a multi-clip workflow.
- **Frame count ≠ video duration / interval.** ffmpeg's `fps=1/10` filter produces frames at 10s boundaries starting from 0; a 196s video yields 20 frames (0, 10, 20, ... 190), not 21. The last ~6 seconds have no frame.
- **Vision analysis needs absolute paths.** On Windows, use `C:/Users/...` or `file:///C:/...` form — relative or backslash paths fail.

## References

- [whisper-transcription.md](references/whisper-transcription.md) — Whisper setup, model selection, and troubleshooting for this environment.
