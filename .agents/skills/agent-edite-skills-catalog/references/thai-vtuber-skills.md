# Thai / VTuber production skills (10 skills)

This is the user's actual production domain: Thai VTuber clips for YouTube,
native Thai subtitles, thumbnails, and the enrichment layer.

## `resolve-video-enrichment` — the hub for Thai VTuber editing (110 lines, 17 files)

Triggers (Thai, verbatim): "เรียนรู้การตัดคลิป VTuber ไทยใน DaVinci Resolve
ให้คนดูชอบบน YouTube", "ช่วยเลือกไฮไลต์ วาง hook จังหวะมุก และ reaction จากไลฟ์",
"ปรับคลิปให้เข้าใจง่าย ซับอ่านทัน เสียงชัด โดยคงบุคลิก VTuber", "ตรวจสอบทุก
Timeline แล้วทำ Zoom Focus VTuber ด้วย Adjustment Clip เท่านั้น", "ใช้ Adjustment
Clip ที่เลือกอยู่บน Timeline สร้างใน video track ใหม่ ซูมให้ VTuber อยู่กลางเฟรม
ศีรษะถึงอก/มือ เว้นที่เหนือหัว", "จัดการรูปภาพประกอบใหม่", "ใช้ Hermes subagent
delegation แบ่งงานดูคลิปแนวตั้งและแนวนอนทั้งหมดของ katy404 / KT404".

**Authorization rule**: research, a cutlist, an assembly, enrichment, caption
migration, and publication are NOT the same authorization. "ตอนนี้เป็น DaVinci
Resolve ทุก Timeline ไว้แล้ว" = inventory only.

### Chapter index (load on demand with `skill_view(name="resolve-video-enrichment", file_path=...)`)

| File | Load when |
|---|---|
| `references/resolve-editing-workflow.md` | source review, trim choices, rough cut, finishing order |
| `references/vtuber-story-and-pacing.md` | highlight selection, hooks, comic timing, personality, Thai beat design |
| `references/thai-captions-audio-framing.md` | native Thai captions, dialogue-first sound, readable avatar/game framing |
| `references/youtube-packaging-and-feedback.md` | titles/thumbnails, metric definitions, retention diagnosis, experiments |
| `references/katy404-channel-study.md` | KT404/Katy404 existing-timeline-first or public-upload review |
| `references/youtube-delivery-and-rights.md` | upload specs, Shorts rules, licenses, monetization boundaries |
| `references/automation-safety.md` | **before** live enrichment, transforms, rendering, restoration, recovery |
| `references/asset-coverage.md` | per-timeline coverage, approved promotion to originals, archive cleanup |
| `references/asset-library-and-cues.md` | library discovery, cue planning, copies-then-originals batch recipe |
| `references/illustration-assets.md` | still-image overlays, provenance/rights, placement/QC |
| `references/horizontal-gif-placement.md` | 16:9 GIF placement on V2, Pan/Tilt-to-pixel model, `vdo` preset by script |
| `references/adjustment-focus.md` | subtitle-led VTuber focus using Adjustment Clips only |
| `references/vertical-9x16-conversion.md` | **only** for an explicitly authorized 16:9 → 9:16 conversion |
| `references/offline-media-repair.md` | explicitly approved repair of items missing Media Pool entries |
| `references/render-qc.md` | Windows bridge/render examples and per-output QC |
| `templates/vtuber-edit-brief.md` | the editable brief, cutlist, experiment and acceptance-record template |
| `assets/katy404-vertical-reaction-layout.png` | the user-designated vertical cat-reaction layout |

### 13-step procedure (condensed)

1. **Bound the task** — deliverable, audience, promise, format, targets, rights,
   exclusions. A rough-cut request does not imply music, captions, effects,
   grading, rendering, or publishing.
2. **Establish evidence** — label what was watched/heard/transcribed vs sampled.
   One live controller for Resolve, `delegate_task` for disjoint immutable
   evidence batches. A transcript, waveform peak, or title alone cannot
   establish a funny or truthful clip.
3. **Select the story** — hook → minimum context → turn → payoff → reaction, as
   functions, not time quotas. No universal rapid-cut or meme-density rule.
4. **Write the plan** — source ranges, absolute record frames, track map,
   captions, cue jobs, assets/licenses, protected material. Read each target's
   own `Timeline.GetSetting("timelineFrameRate")`; never substitute the project
   setting. BGM covers the whole timeline; GIF holds 1.5–2.5 s.
5. **Preflight and preserve** — capture active project/timeline IDs, timecode,
   page, folder, track enable/lock states, per-timeline record FPS, raster.
   Relinking, proxies/transcoding, deletion, and SQL need separate authorization.
6. **Assemble before decorating** — build the sound/story spine first.
7. **Finish only within scope** — protect avatar head/face/hands/headroom, game
   evidence, caption space; never auto-convert an approved horizontal timeline.
8. **Thai caption contract** — native Subtitle tracks only, ≤3 short words /
   ~14 Thai characters, ≤1.5 s, no spaces between Thai words (spaces only around
   Latin terms). Split or flag rather than drop speech.
9. **Keep speech intelligible** — dialogue first, then game/effects/music.
   Source speech loudness can differ ~20 LU between timelines in one batch, so
   derive BGM/SFX gains per timeline from measured speech loudness.
10. **Pilot, then batch** — load `automation-safety.md`; activate each target by
    unique ID, serialize bridge calls, begin structural mutations ~1.2 s apart.
11. **Verify and restore** — `ProjectManager.SaveProject()`, compare all changed
    and protected ranges, restore the original active project/timeline/timecode/
    page/folder/track states.
12. **Package and learn** — truthful Thai titles/thumbnails matching the opening/
    payoff; publish only when explicitly authorized.
13. **Report in the user's language** — what changed, what was verified, exact
    deliverable paths, deferred checks.

### Highest-value pitfalls

- Learning from text/screenshots is not consent to inspect private footage or
  connect to Resolve; an authorized live review is still not approval to edit.
- Burned-in caption pixels do not expose native subtitle items; a native still
  export may omit subtitles.
- An inactive `Timeline.GetCurrentTimecode()` can report the active timeline's
  playhead — activate before reading.
- A project's `timelineFrameRate` may differ from an individual timeline's
  record rate; `timelinePlaybackFrameRate` was not script-settable on the
  observed build.
- When the user pastes an Inspector screenshot showing a Video Preset (e.g.
  `vdo`), they are choosing that preset for GIF placement: read the loaded
  clip's properties and apply them — say plainly that the preset itself was not
  loaded because no scripting API exists.
- Copies-then-originals is the promotion approval; still export a fresh `.drp`
  first and compare against both the pre-edit dump and the copy.
- Pixel-measure overlay position on a real frame; Inspector numbers alone were
  wrong for non-full-width sources.
- Strip invisible/bidirectional Unicode controls before distilling any source.

## `thai-subtitles-resolve` — native Thai subtitles (558 lines)

Triggers: insert native Thai subtitles into Resolve timelines, load saved font
presets. Ships `references/native-caption-migration.md` and
`references/srt-insertion-and-presets.md`.

### The finding that matters: SRT import IS scriptable

```python
items = mp.ImportMedia([srt_path])      # -> MediaPoolItem, Type == "Subtitle"
tl.AddTrack("subtitle")                 # MUST exist first
mp.AppendToTimeline([{"mediaPoolItem": items[0]}])
```

(most guides, and this repo's own `api_truth`, said it is not scriptable).

### Verified end-to-end route (Resolve Studio 21.1.0.17, 60 fps, 16:9)

ffmpeg decode → `scripts/asr_words_th.py` (faster-whisper `large-v3` on the RAW
audio, char-level times + pythainlp) → hand-curated cue starts →
`scripts/build_dynamic_srt.py` → `scripts/caption_lint.py` → import → read back
with `scripts/verify_srt_on_timeline.py <srt>` (it reads the CURRENT timeline, so
activate the target first).

- `large-v3` beat `large-v3-turbo` on this material (turbo invented ~20 s of
  gameplay audio). Re-transcribe a doubtful 20–30 s window alone with
  `beam_size=8`; the voice-band-filtered pass can merge a whole window into one
  unusable segment.
- The MCP route works: `media_pool.import_media` → `timeline.add_track`
  (`track_type: subtitle`) → `media_pool.append_to_timeline` with `clip_ids`. It
  auto-archives a copy `Timeline N_archived_vNN` per mutating call and may leave
  the Media Pool folder on `Archive` — report both, clean up only on request.
- Preset names are exact: `Mitr Font` exists, `Mitr-Font` does not. Ask, never
  substitute.
- `scripts/load_subtitle_preset.py --backup-dir` must be an absolute path; a
  relative path made Resolve's `ExportProject` fail.

### Caption timing for short-form

`MAX_DISPLAY_S = 1.5`; clamp order = display cap → `next_start - min_gap` →
timeline end; `MIN_GAP_S ≈ 0.034` (2 frames @60); break early on a pause
`>= 0.7 s`; never drop words to fit — flag low confidence instead. Whisper
stretches a trailing token over silence, parking a 3-word caption ~5 s.

### Timebase

Whisper time is relative to the extracted WAV; WAV t=0 is the clip's
`tl_start_frame`, so `timeline_time = wav_time + tl_start_frame/fps`. Get ranges
from `GetLeftOffset()`/`GetDuration()` per item and check `GetProperty("Speed")`
— a retimed clip breaks the linear mapping.

### Safety and the two Python traps

Source media is read-only; only project-database state changes. Skip timelines
that already have a subtitle track unless `--replace` is passed.

- Do not name a loop-local `text` when the enclosing loop scans a string called
  `text` — shadowing silently drops the rest of the segment.
- `all()` on an empty iterable is True, and Thai vowel/tone marks are not
  `isalnum()` — use `unicodedata.category(c).startswith("P")` for punctuation.

Style copies: direct DB writes need explicit authorization for that operation;
permission to insert subtitles or change a font is not permission to write SQL.
Qt's `pointSize` descriptor is **not** the Inspector Size (8.14286 displayed as
Size 58); Resolve's Stroke checkbox is labelled **Outside Only**.

## `thai-proofread` — Thai spelling/tone QA (118 lines)

Triggers: "ตรวจสอบ ความถูกต้อง ภาษาไทย เเก้ไขคำผิด", before importing SRT
captions into Resolve, after Whisper output needs cleanup, house-style caption QA.

Procedure: segment into words (newlines/pipes/periods as delimiters) → check
against a Thai dictionary, flagging unknown and mixed-Latin tokens → verify tone
markers (่ ้ ๊ ๋) and vowel completeness → flag duplicates, invalid characters,
stray spaces inside Thai runs.

Pitfalls: don't auto-fix names without confirmation (Latin names get spaces
around them only); don't merge captions past 1.5 s or 3 short words; stray `แ็` /
`เ` / `า` ligature errors are common. Verification: run on a sample caption file,
diff shows only real corrections with no dropped cues.

## `vtuber-content-curriculum` — 24-topic knowledge base (57 lines, 8 files)

Triggers: "เรียนรู้การทำคอนเทนต์ VTuber ไทย", "ศึกษาหัวข้อทั้งหมด"; agent needs
domain knowledge before planning, editing, or reviewing; questions about any of
the 24 curriculum topics.

| Reference | Topics |
|---|---|
| `references/content-strategy.md` | 1-3, 23-24: VTuber Thai style, YouTube strategy, scriptwriting, performance analysis, continuous learning |
| `references/video-production.md` | 4-6, 12-13: AI editing, pacing, hooks, zoom/cut/transition, character reactions |
| `references/audio-and-subtitles.md` | 7-9, 19: Thai subtitles, SFX, BGM, audio mixing |
| `references/visual-elements.md` | 10-11, 18: Meme/GIF, motion graphics, thumbnails |
| `references/platform-editing.md` | 15-16: Shorts 9:16, long-form 16:9 |
| `references/intelligence-automation.md` | 17, 22: AI highlight detection, agent workflow |
| `references/quality-safety.md` | 20-21: QC, copyright |
| `references/thai-culture.md` | 14: Thai humor and internet culture |

For editing tasks, also load `resolve-video-enrichment` and `house-style`.
Pitfalls: curriculum principles are starting points, not universal rules; Thai
internet culture evolves fast; **do not treat learning as authorization to edit,
publish, or change Resolve projects**.

## `vtuber-thumbnail-layout` — layout rules (66 lines, 6 files)

Triggers: "จัดวางโมเดล", "ปกแนวนอน/แนวตั้ง", "วาง avatar ปก", "safe zone thumbnail".

- Landscape 1920×1080: text left-centre `y ≈ 380–520`, model right 35–50%, avoid
  the bottom-right timestamp.
- Shorts 1080×1920: text top-centre `y ≈ 280–650`, model bottom-centre, avoid
  bottom 25% + right 20%.
- Hook: 1–4 words, red `#EC1C24`, ~8% black stroke, Mitr Bold. Secondary text
  white `#FFFFFF` with black stroke.
- Game: 0 px blur + left gradient mask; talk: 46–60 px blur.
- Model separation: white stroke 8–18 px + drop shadow + rim light.

Pitfalls: never crop a landscape cover for Shorts — recompose; never place text
in the timestamp badge (1580–1900, 980–1060) or the bottom scrubber; no more
than one red accent; never claim CTR from prettiness without evidence. Verify
with `vtuber-thumbnail-qc`.

## `vtuber-thumbnail-qc` — scored thumbnail QC (84 lines)

Triggers: "QC ปก", "ตรวจปกคลิป", "ตรวจ thumbnail", "ปกนี้ใช้ได้ไหม", "รีวิวปก
VTuber"; final gate before export/upload.

- Script: `scripts/qc_previews.py` → mobile 10%/20%, grayscale, squint,
  duration-badge overlay, feed sheet, `tech_report.json`.
- Checklist (23 steps): `references/qc-checklist.md`; report skeleton:
  `templates/qc-report.md`.
- Score: Character 15 · Expression 10 · Composition 10 · Text Readability 10 ·
  Thai Typography 10 · Contrast 10 · Color 5 · Content Relevance 10 · Curiosity 10 ·
  Mobile 5 · Brand 5 = 100. Bands: 90–100 ready · 80–89 minor fixes · 70–79
  usable, fix · 60–69 fix before publish · <60 rework. Severity 🔴 CRITICAL /
  🟠 IMPORTANT / 🟡 OPTIONAL. Clickbait class: GOOD CURIOSITY / BORDERLINE /
  MISLEADING.
- Auto-QC after a build is expected — don't wait for the user to ask.

Pitfalls: never flatter, never critique from taste — every point ties to
clarity, CTR, accuracy, or brand; banned vague fixes ("ทำให้เด่นขึ้น"); write
numbers ("ขยายใบหน้า VTuber ~20–30% และเลื่อนซ้ายให้ดวงตาอยู่ 1/3 บน"); if you
cannot verify, write "ไม่สามารถยืนยันจากข้อมูลที่มี"; Thai readability is tested on
`*_mobile.png`, not full-res. **The fix list is the deliverable, not the score.**

## `youtube-content` — transcripts → summaries/threads/blogs (96 lines)

Ships `references/output-formats.md` and `scripts/fetch_transcript.py`.

## `youtube-downloader` — yt-dlp download workflow (81 lines)

Ships `references/queue-format.md`. Project conventions: entry points
`python downloader.py` (compat shim) and installed `download`; code in
`youtube_downloader/`; runtime dep `yt-dlp`, Python 3.10+; MP4 merge up to 1080p;
**up to 22 unique HTTP(S) URLs per run**, playlists expand before limit/dedup;
queue state `.download_queue.json`, `--resume` resumes pending/failed items;
`--output-dir <path>`.

Cookies: never read a browser cookie store or use account credentials unless the
user explicitly authorizes cookie-based access; prefer public unauthenticated
access; a `cookies.txt` may hold session secrets — never print, copy, stage, or
expose it.

User preferences: reply in Thai for user-facing summaries, keep code/paths in
English; report status as `path:line`; prefer continuous execution over repeated
confirmation; assume resume when a queue exists.

## `gif-search` — Tenor GIF search/download (91 lines)

curl + jq against the Tenor API; search, get URLs, preview sizes, download, top
result, full metadata. Pairs with the GIF placement rules in
`resolve-video-enrichment`'s `references/horizontal-gif-placement.md`.
