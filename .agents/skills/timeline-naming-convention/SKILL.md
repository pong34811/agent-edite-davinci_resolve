---
name: timeline-naming-convention
description: Use when naming highlight timelines or changing the naming format of timeline builders.
version: 0.2.0
---

# Timeline naming & YouTube Feed Alignment

- **Base Format**: Current user-requested format: `{ชื่อคลิป}-vdo` or `{ชื่อคลิป}-{ชื่อเกม}-vdo`. Follow the live brief in `job.json`/`prompt.md`.
- `{ชื่อคลิป}` is a concise Thai title from source-verified event content, not from ASR alone or the filename. No source/candidate IDs or category prefixes in the name; keep them in metadata.
- If two names collide, stop and ask; do not silently append a suffix.
- `scripts/highlight/build_timelines.py` builds `{title}-{game}-vdo`. Changing prompt text or `job.json` does not change its output. To support a new format, change the generator with tests first (RED then GREEN) and only then claim support.
- Renaming existing timelines: follow the serialized `set_current` then `set_name` procedure in `long-video-highlight-clipping`.

## YouTube Feed Optimization (Scaling to 300+ clips/month)

At high volume (300 clips/month), titles cannot rely on per-clip paid API calls (e.g. vidIQ credit limits). Use formulaic CTR hooks and feed-specific structures generated directly from transcript context:

### 1. Divergence: 16:9 Landscape vs 9:16 Shorts
- **16:9 Landscape (Browse & Suggested Video)**:
  - Structure: `[Hook/คำอุทานกระตุกความอยากรู้] - [เหตุการณ์ไฮไลต์] | [ชื่อเกม/สตรีมเมอร์]`
  - Length: Under 60–70 characters. The critical hook must sit in the first 40 characters so mobile cards do not truncate it.
  - Context: Must include recognizable game keywords so the algorithm pairs the clip in Suggested feeds alongside related gameplay.
- **9:16 Vertical Shorts (Shorts Swipe Feed)**:
  - Structure: `[คำถาม/สปอยล์ผลลัพธ์/คำกระแทกอารมณ์] #[ชื่อเกม] #Shorts`
  - Length: Very short (< 35–45 characters). Viewers decide whether to stay within 1–2 seconds; long descriptive titles are ignored or truncated by UI elements.

### 2. Algorithmic Sanitization Gate (Crucial for Feed Distribution)
- **Zero Profanity in Titles**: YouTube's Advertiser-Friendly Guidelines and recommendation engines downrank or shadow-suppress videos with profanity in metadata (titles/tags).
- Auto-sanitize: Replace `กู`/`มึง` with conversational third-person or situational reactions; replace `ชิบหาย` with `งานหยาบ`/`เละเทะ`; replace `กระจอก` with `พลาดจัด`/`เล่นไม่ระวัง`.

### 3. Scalable Strategy (No Credit Bottleneck)
- **Macro Keyword Seeding**: Query external tools (vidIQ) only 1–2 times per month/game to capture high-volume trending keywords and competitor tags.
- **Micro Automated Title Engine**: Combine the seed keywords with verified Whisper transcript lines using local LLM rules to generate both 16:9 and 9:16 titles at zero marginal cost.
