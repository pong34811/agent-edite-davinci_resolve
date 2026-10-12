# Platform Editing (Topics 15-16)

## 15. YouTube Shorts Editing (9:16)

**Core principle:** Shorts demand instant engagement — every frame must earn its place.

**Shorts specifications:**
- Aspect ratio: 9:16 vertical
- Duration: 15-60 seconds (optimal 20-40s)
- Frame rate: Match source (typically 30fps or 60fps)
- Safe zones: Avoid top 250px and bottom 400px (UI overlay areas)

**Shorts editing principles:**
- **Immediate hook:** First frame must grab attention — no intro, no branding
- **Fast pace:** Cut every 1-3 seconds — no dead air
- **Captions essential:** Many viewers watch without sound
- **Loop-friendly:** End where it begins for replay value
- **Trend-aware:** Use trending audio/formats when relevant

**9:16 layout (from house style):**
```
V1: Game Top (cropped/panned gameplay)
V2: Reactions (GIFs/popups)
V3: VTuber Bottom (framed avatar)
V4: VTuber Zoom (Adjustment Clip zoom)
Subtitle 1: Native Thai Subtitles (top)
```

**Implementation:**
- Use `p2_9x16_*.py` scripts for build/convert/verify
- Calibrate Crop/Zoom/Pan/Tilt for game panel framing
- Keep V2 GIFs inside game panel, above avatar seam
- Verify pilot before batch conversion

## 16. YouTube Long-form Editing (16:9)

**Core principle:** Long-form content needs structure and pacing to maintain watch time.

**Long-form specifications:**
- Aspect ratio: 16:9 landscape
- Duration: 5-30 minutes (varies by content type)
- Frame rate: Match source
- Chapters/timestamps for navigation

**Long-form editing principles:**
- **Structure:** Intro → Content segments → Outro
- **Pacing:** Vary between fast (highlights) and slow (story/emotion)
- **Chapters:** Timestamp key sections for viewer navigation
- **Retention hooks:** Re-engage viewers every 3-5 minutes
- **End screen:** Promote related content and subscribe

**16:9 layout (from house style):**
```
V1: Base Footage (Gameplay + VTuber webcam)
V2: VTuber Zoom (Adjustment Clip track)
V3: Reactions (Overlays, GIFs, popups)
Subtitle 1: Native Thai Subtitles (top)
```

**Implementation:**
- Build structure first, then add enrichment
- Use DRT transfer for safe track injection
- Verify all original tracks after any modification
- Render with H.264 Master preset
- Loudness: I=-14 LUFS, two-pass loudnorm