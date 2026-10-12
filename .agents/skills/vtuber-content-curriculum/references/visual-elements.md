# Visual Elements (Topics 10-11, 18)

## 10. Meme & GIF Integration

**Core principle:** Memes and GIFs add humor and personality when used with restraint.

**GIF integration principles:**
- Match GIF content to the moment's emotion or joke
- Use GIFs for reaction enhancement, not as primary content
- Keep GIF holds in 1.5-2.5s range (Resolve may conform 2 frames shorter)
- Place GIFs on dedicated reaction tracks (V2/V3 in 9:16, V3 in 16:9)
- Ensure GIFs don't cover the VTuber's face or key game information

**Meme usage:**
- Thai internet memes resonate with Thai audiences
- Use memes that the VTuber's community recognizes
- Don't over-meme — save for peak comedic moments
- Credit meme sources when required

**Implementation (Resolve):**
- Import GIFs to Media Pool with correct FPS metadata
- Apply approved Inspector presets (e.g., "vdo") for consistent placement
- Verify GIF duration and content before placement
- Test one GIF end-to-end before batch application

## 11. Motion Graphics & Animation

**Core principle:** Motion graphics enhance presentation without distracting from content.

**Use cases:**
- **Intro/outro:** Channel branding, subscribe reminder
- **Lower thirds:** Name displays, social media handles
- **Emphasis text:** Highlighting key words or reactions
- **Transitions:** Animated cuts between segments
- **Subscribe/CTA:** End screen animations

**Principles:**
- Match animation style to VTuber's brand and personality
- Keep animations short — 2-3 seconds maximum
- Use motion to guide attention, not decorate
- Ensure readability — text must be legible at playback speed

**Implementation:**
- Fusion comps for titles and motion graphics
- Use Fusion titles as timeline clips, not overlay on existing clips
- Wire Fusion graph properly: MediaOut must descend from MediaIn
- Test rendering before batch application

## 18. YouTube Thumbnail Design

**Core principle:** Thumbnails must stop the scroll and earn the click.

**Thumbnail principles:**
- **Face forward:** VTuber's face clearly visible, expressing emotion
- **High contrast:** Readable at small sizes (mobile)
- **Minimal text:** Max 3-4 words, large and bold
- **Color pop:** VTuber stands out from background
- **Emotion:** Reaction shot that promises entertainment

**VTuber-specific thumbnails:**
- Use the VTuber's best reaction frame
- Include game context when relevant
- Consistent branding (colors, fonts) for channel recognition
- A/B test different styles to find what works

**Technical:**
- Thumbnail size: 1280x720 (16:9) for long-form
- Thumbnail size: 1080x1920 (9:16) for Shorts
- Export from Resolve viewer, not ExportCurrentFrameAsStill (may omit subtitles)
- Use `vtuber-thumbnail-layout` and `vtuber-thumbnail-qc` skills for detailed guidance