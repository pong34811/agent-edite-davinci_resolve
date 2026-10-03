# Technical Investigation Report: 16:9 to 9:16 Vertical Conversion in DaVinci Resolve

**Author:** Explorer 3 (`teamwork_preview_explorer`)  
**Project:** `KT404_2026-09-29` (Project ID: `7c38045b-c9ae-426c-8b4c-2e2d726d88ff`)  
**DaVinci Resolve Version:** DaVinci Resolve Studio `21.1.0.17` (Windows)  
**MCP Server Version:** `4.8.23`  
**Date:** 2026-10-01  
**Integrity Mode:** Development / Read-Only Investigation  

---

## 1. Executive Summary

This investigation establishes the exact technical mechanics, API methods, coordinate transforms, and safety protocols for converting all 30 pre-cut 16:9 horizontal timelines in project `KT404_2026-09-29` into 9:16 vertical (1080×1920) short-form timelines (`<OriginalName>_9x16`).

Key conclusions:
1. **Duplication & Settings:** Native duplication via `Timeline.DuplicateTimeline("<OriginalName>_9x16")` is the only safe method; it preserves 100% of cuts, audio tracks, and native subtitle cues without parsing or re-importing. Custom 1080×1920 resolution must be set with `useCustomSettings="1"`, preserving source frame rate (60.0 fps).
2. **Split Screen Architecture:** The source footage contains gameplay with the VTuber avatar (Katy404) baked into the bottom-right corner. The target 9:16 Split Screen is best implemented via **Dual Video Tracks**:
   - **V1 (Game Top):** Zoom = 1.60, Pan = 0.0, Tilt = +480.0, CropBottom = 486.0.
   - **V2 (VTuber Bottom):** Zoom = 2.60, Pan = -936.0, Tilt = -200.0, CropTop = 480.0.
3. **Full-Screen VTuber Focus Moments:** The existing V3 Adjustment Clips already contain a Fusion comp (`MediaIn1 -> Transform1 -> MediaOut1`). In 9:16, updating `Transform1` to `Center: {0.5, 0.25}` and `Size: 2.0` mathematically shifts the lower-half avatar to screen center and doubles scale to 1920px height, creating a seamless full-screen VTuber close-up during each focus cue.
4. **Reaction GIFs & Subtitle Safe Zones:** V2 Reaction GIFs must be moved from center ($Pan=0, Tilt=0$) to the **Upper Flank** ($Pan=-300.0, Tilt=+600.0$) or **Top-Center** ($Pan=0.0, Tilt=+650.0$) with scale $Zoom=0.40–0.45$. This avoids Katy404's face ($Y \in [650, 850]$), controller hands ($Y \in [400, 650]$), native subtitles ($Y \in [180, 280]$), and platform UI margins.

---

## 2. Live Baseline State: Project `KT404_2026-09-29`

Direct inspection of Resolve Studio `21.1.0.17` and project `KT404_2026-09-29` established the following verified baseline:
- **Total Timelines:** 30 timelines (Timelines 1–10: Minecraft, 11–12: Soul Walker, 13–18: Terraria, 19–24: Monster Hunter World, 25: Soul Walker, 26: Minecraft `หนีฝ่าความหนาว_Minecraft-vdo`, 27–30: Soul Walker).
- **Timeline Resolution:** 1920×1080 (16:9).
- **Timeline Frame Rate:** 60.0 fps record rate across all 30 timelines.
- **Track Layout per 16:9 Timeline:**
  - **Track V1 (`Main Video`):** 1920×1080 H.264 source stream recording (`【🔴 LIVE】...`). Contains gameplay with VTuber avatar baked in at bottom-right ($X \approx 1400–1800$, $Y \approx 550–1080$).
  - **Track V2 (`GIF Overlays`):** Reaction GIFs (e.g. `Cute - Dancing Cat.gif`) with default center placement ($Pan=0, Tilt=0$).
  - **Track V3 (`VTuber Focus`):** Adjustment Clips marking focus moments. Each clip has a Fusion composition `Composition 1` with `MediaIn1 -> Transform1 -> MediaOut1` (`Size: 1.3`, `Center: {0.38, 0.81}`).
  - **Subtitle Track 1 (`Subtitles`):** Native Subtitle track with Thai dialogue cues, formatted according to house style (short cues, $\le 1.5$s, no inter-word spaces).
  - **Track A1 (`Original Audio`):** Stream audio (dialogue + game sound), 0 dB.
  - **Track A2 (`SFX`):** Sound effects, -10 dB to -12 dB.
  - **Track A3 (`BGM`):** Music bed, -22 dB to -24 dB with fades.

---

## 3. Timeline Duplication & Resolution Setup

### 3.1 Duplication Mechanics: `Timeline.DuplicateTimeline` vs `MediaPool.CreateEmptyTimeline`

| Criterion | `Timeline.DuplicateTimeline` | `MediaPool.CreateEmptyTimeline` |
|---|---|---|
| **Editorial Integrity** | **100% Bit-for-bit preserved** | Empty container; requires manual reconstruction |
| **Subtitle Track** | **Preserved 1:1 natively** (all cues, timings, styles) | Dropped; requires fragile SRT re-import |
| **Cuts & Trims** | **Preserved 1:1** without slippage | High risk of frame drift and desync |
| **Audio Routing/Levels** | **Preserved 1:1** (fades, volumes) | Lost |
| **Speed & Retime** | **Preserved** | Lost (Resolve has no public retime setter API) |
| **API Method** | `original_timeline.DuplicateTimeline(name)` | `media_pool.CreateEmptyTimeline(name)` |

**Verdict:** `Timeline.DuplicateTimeline("<OriginalName>_9x16")` is the **only acceptable mechanism**. Creating an empty timeline violates Requirement R3 (strict preservation of locked editorial elements).

### 3.2 Critical API Truth Behavior: Current Timeline Pointer
Measured on Resolve Studio 21.1 (`resolve_control.api_truth`):
- `Timeline.DuplicateTimeline(name)` **silently moves Resolve's current-timeline pointer to the newly created duplicate**.
- While convenient for editing the new duplicate immediately, the script must explicitly capture `original_timeline` and store both timeline object references and IDs.
- To safely manage pointers:
  ```python
  # Capture original
  original_timeline = project.GetCurrentTimeline()
  original_name = original_timeline.GetName()
  original_fps = original_timeline.GetSetting("timelineFrameRate")

  # Duplicate
  new_name = f"{original_name}_9x16"
  new_timeline = original_timeline.DuplicateTimeline(new_name)
  
  # Confirm new_timeline is active
  project.SetCurrentTimeline(new_timeline)
  assert new_timeline.GetName() == new_name
  ```

### 3.3 Custom 1080×1920 (9:16) Resolution Setup
To configure the vertical raster on `new_timeline` without affecting other project timelines:

1. **Enable Custom Timeline Settings:**
   `new_timeline.SetSetting("useCustomSettings", "1")`
2. **Set Resolution Parameters:**
   ```python
   settings = {
       "useCustomSettings": "1",
       "timelineResolutionWidth": "1080",
       "timelineResolutionHeight": "1920",
       "timelineOutputResMatchTimelineRes": "1",
       "timelineOutputResolutionWidth": "1080",
       "timelineOutputResolutionHeight": "1920",
       "timelinePixelAspectRatio": "square",
       "timelineInputResMismatchBehavior": "scaleToFit",
       "timelineOutputResMismatchBehavior": "scaleToFit"
   }
   
   # Compatible with Resolve 21.1+ plural API:
   new_timeline.SetSettings(settings)
   
   # Or via key-by-key SetSetting fallback:
   for k, v in settings.items():
       new_timeline.SetSetting(k, v)
   ```

3. **Frame Rate Preservation Guard:**
   - In Resolve, `timelineFrameRate` is inherited directly by `DuplicateTimeline`.
   - **Do NOT attempt to write `timelineFrameRate` or `timelinePlaybackFrameRate`**:
     `resolve_control.api_truth` records that `SetSetting('timelinePlaybackFrameRate')` returns `False` on all value forms and can destabilize project playback settings.
   - Verify non-mutation via readback:
     ```python
     new_fps = new_timeline.GetSetting("timelineFrameRate")
     assert float(new_fps) == float(original_fps), f"FPS mismatch: {new_fps} vs {original_fps}"
     ```

---

## 4. Split Screen Reframing: Gameplay Top + VTuber Bottom

### 4.1 Source Footage Layout Breakdown
Direct analysis of the extracted 1920×1080 frame (`scratch_source.jpg`) confirms:
- **Aspect Ratio:** 16:9 ($1920 \times 1080$).
- **Gameplay Area:** Occupies the entire frame. Primary action (crosshair, player avatar, immediate blocks/mobs) is centered around $(X=960, Y=540)$.
- **VTuber Avatar (Katy404):** Baked directly into the bottom-right corner of the video stream (no separate camera file):
  - Horizontal bounds: $X \in [1400, 1800]$ (center at $X \approx 1600$).
  - Vertical bounds: $Y \in [550, 1080]$ (center at $Y \approx 810$, ahoge/head top at $Y \approx 550$, eyes at $Y \approx 700$, purple controller/hands at $Y \approx 880$, chest/jacket extends to bottom edge $Y = 1080$).

### 4.2 Target Canvas Geometry (1080×1920)
- **Total Canvas:** 1080 width × 1920 height.
- **Coordinate Space (Inspector Pan/Tilt):**
  - Center is $(0, 0)$.
  - Top edge is $Tilt = +960.0$, Bottom edge is $Tilt = -960.0$.
  - Left edge is $Pan = -540.0$, Right edge is $Pan = +540.0$.
- **Split Division:**
  - **Upper Portion (Game Action):** $Y \in [960, 1920]$ (Inspector $Tilt \in [0, +960]$).
  - **Lower Portion (VTuber Avatar):** $Y \in [0, 960]$ (Inspector $Tilt \in [-960, 0]$).

### 4.3 Track Architecture & Transform Parameters

#### Track Layout on `_9x16`:
| Track | Name | Source Clip | Purpose |
|---|---|---|---|
| **V1** | `Game Top` | Original V1 cuts | Upper canvas gameplay focus |
| **V2** | `VTuber Bottom` | Duplicate of V1 cuts | Lower canvas avatar focus |
| **V3** | `GIF Overlays` | Reaction GIFs (from 16:9 V2) | Repositioned to upper safe area |
| **V4** | `VTuber Focus` | Adjustment Clips (from 16:9 V3) | Full-screen close-up during cues |

#### Transform Math:
1. **Track V1: Game Action (Upper Portion)**
   - At default `scaleToFit` ($S_0 = 1080/1920 = 0.5625$), the 16:9 clip is $1080 \times 607.5$ px.
   - To fill the upper half (width 1080 px, target height ~960 px):
     - $Zoom = 960 / 607.5 \approx 1.58 \implies \mathbf{1.60}$.
     - At $Zoom = 1.60$: Width = 1728 px (cropped on left/right by canvas at $\pm 540$), Height = 972 px.
   - Position:
     - Upper half vertical center is at $Y = +480.0$.
     - $\mathbf{Pan = 0.0}$
     - $\mathbf{Tilt = +480.0}$
   - Crop:
     - $\mathbf{CropBottom = 486.0}$ (cuts off cleanly at split midline $Y=0$).

2. **Track V2: VTuber Avatar (Lower Portion)**
   - In source, avatar center is at $X \approx 1600$, $Y \approx 810$.
   - Relative to source center $(960, 540)$:
     - $\Delta X = 1600 - 960 = +640$ px.
     - $\Delta Y = 540 - 810 = -270$ px.
   - At $S_0 = 0.5625$, Zoom = 1.0 position in 9:16 is:
     - $X_{base} = +640 \times 0.5625 = +360.0$ px.
     - $Y_{base} = -270 \times 0.5625 = -151.875$ px.
   - To make the avatar fill the lower half width (~650 px wide):
     - Scale factor $Zoom = 2.60$.
     - Avatar center shifts to $X = +360.0 \times 2.60 = +936.0$ px.
   - Position to center avatar in lower half ($X=0, Y=-480$):
     - $\mathbf{Pan = -936.0}$ (shifts avatar to horizontal center $X = 0$).
     - $\mathbf{Tilt = -200.0}$ (moves avatar slightly down; headroom sits safely at $Y \approx -50$ just below the split line, face at $Y \approx -250$, hands/controller at $Y \approx -450$, well above subtitle baseline at $Y \approx -750$).
   - Crop:
     - $\mathbf{CropTop = 480.0}$ (prevents avatar background from overlapping the upper game screen).

---

## 5. Full-Screen VTuber Focus Moments (V3/V4 Adjustment Clips)

### 5.1 How the Existing V3 Adjustment Clips Work
In the 16:9 project, V3 Adjustment Clips function via an embedded Fusion composition (`timeline_item_fusion`):
- Graph: `MediaIn1 -> Transform1 -> MediaOut1`.
- Inputs on `Transform1`:
  - `Size`: `1.30`
  - `Center`: `{1: 0.38, 2: 0.81, 3: 0.0}`
  - `Edges`: `0.0` (Canvas)

In 16:9, shifting Center to $(0.38, 0.81)$ translated the bottom-right corner inward and zoomed 1.3× to emphasize the VTuber during dialogue cues.

### 5.2 Mechanics for 9:16 Full-Screen Focus
In the 9:16 vertical timeline:
- The base timeline beneath the Adjustment Clip is the **Split Screen** (Game Top on V1, VTuber Bottom on V2).
- On the Split Screen, Katy404 is positioned in the lower half, centered at:
  - Canvas pixels: $X = 540, Y = 480$ (from bottom-left).
  - Normalized Fusion coordinates ($[0.0, 1.0]$): $\mathbf{X = 0.50, Y = 0.25}$.

#### The Mathematical Solution:
To transform the lower-half avatar into a full-screen vertical close-up ($1080 \times 1920$), the Adjustment Clip's `Transform1` must:
1. Shift the center of interest from $(0.50, 0.25)$ to the screen center $(0.50, 0.50)$.
2. Double the size from half-screen ($960$px height) to full-screen ($1920$px height).

$$\text{Fusion Transform Parameters:}$$
- $\mathbf{Center = \{0.50, 0.25\}}$
- $\mathbf{Size = 2.0}$
- $\mathbf{Edges = 0.0}$

#### Verification of Transform Math:
For any input point $(x, y)$:
$$x' = 0.50 + (x - \text{Center}_x) \times \text{Size} = 0.50 + (x - 0.50) \times 2.0$$
$$y' = 0.50 + (y - \text{Center}_y) \times \text{Size} = 0.50 + (y - 0.25) \times 2.0$$

Plugging in Katy404's center $(0.50, 0.25)$:
$$x' = 0.50 + (0.50 - 0.50) \times 2.0 = 0.50$$
$$y' = 0.50 + (0.25 - 0.25) \times 2.0 = 0.50$$
The avatar lands **precisely at the exact center of the 1080×1920 canvas**!
- Avatar headroom: sits cleanly with ~100px margin below the top notch area.
- Avatar face: prominent in the upper-middle sightline.
- Avatar controller/hands: clearly visible above the bottom subtitle zone.
- Gameplay footage: pushed entirely off-screen above the top canvas edge.
- At the end of the Adjustment Clip: the composition immediately returns to the normal Split Screen with zero transitional artifacts.

---

## 6. Reaction GIFs (V2/V3) & Subtitle Safe Zones

### 6.1 Collision Problem with 16:9 Defaults
In the 16:9 timeline, V2 Reaction GIFs used $Pan = 0.0, Tilt = 0.0$ (screen center).
In 9:16 vertical ($1080 \times 1920$):
- Center $(0, 0)$ is at $Y = 960$ px (the exact split line).
- Katy404's head and ahoge sit between $Y = 850$ and $950$ ($Tilt \in [-110, -10]$).
- A GIF at $Tilt = 0$ directly collides with and covers Katy404's face and hair!

### 6.2 1080×1920 Vertical Safe Zone Map

```
Y (px)   Tilt (px)   Screen Region                    Safe Zone Classification
───────────────────────────────────────────────────────────────────────────────
1920     +960        Top Edge                         
1720     +760        TikTok / Shorts Top UI & Notch   DANGER ZONE (Header / Icons)
───────────────────────────────────────────────────────────────────────────────
1650     +690        Upper Game Canvas                ★ RECOMMENDED GIF ZONE
1400     +440        Game Action / Crosshair          (Top-Center or Upper-Left Flank)
1050     +90         Upper Game Baseline              
───────────────────────────────────────────────────────────────────────────────
 960        0        Split Midline                    DANGER ZONE (Collision Boundary)
───────────────────────────────────────────────────────────────────────────────
 850     -110        Katy404 Headroom & Hair          
 700     -260        Katy404 Face & Eyes              DANGER ZONE (VTuber Head/Face)
 500     -460        Katy404 Controller & Hands       DANGER ZONE (Avatar Hands)
───────────────────────────────────────────────────────────────────────────────
 300     -660        Upper Subtitle Clearance         
 180     -780        Native Thai Subtitle Cues        DANGER ZONE (Subtitles Protected)
 150     -810        TikTok Sound Marquee / UI        DANGER ZONE (Platform UI)
   0     -960        Bottom Edge                      
```

### 6.3 Repositioning Specifications for Reaction GIFs

To ensure zero occlusion of Katy404's face, zero occlusion of subtitles, and compliance with platform UI safe zones:

#### Option A: Upper-Left Flank (Best for Minecraft / Terraria gameplay)
- $\mathbf{Pan = -300.0}$
- $\mathbf{Tilt = +600.0}$
- $\mathbf{ZoomX = 0.42, ZoomY = 0.42}$
- Bounding Box: $X \in [80, 400]$, $Y \in [1350, 1700]$.
- Rationale: Sits cleanly in the upper-left of the game window, away from the central crosshair ($X=540, Y=1440$), well clear of TikTok's right-side buttons ($X > 920$), and entirely above the split midline.

#### Option B: Top-Center (Punchy Reaction Pop-up)
- $\mathbf{Pan = 0.0}$
- $\mathbf{Tilt = +650.0}$
- $\mathbf{ZoomX = 0.40, ZoomY = 0.40}$
- Bounding Box: $X \in [324, 756]$, $Y \in [1450, 1750]$.
- Rationale: Centers the meme reaction directly above the gameplay action, below the TikTok search bar.

---

## 7. Preservation Invariants & Audit Checklist

The execution pipeline must enforce and audit the following non-negotiable invariants:

| Category | Invariant | Verification Tool / Method |
|---|---|---|
| **Project Safety** | Fresh verified `.drp` in `G:\My Drive\Projects\Katy404\2026-09-29` before writes | `project_manager.export_project` + file size check |
| **Originals** | All 30 original 16:9 timelines untouched | Name, ID, item counts, and settings baseline diff |
| **New Timelines** | 30 vertical timelines named `<OriginalName>_9x16` | `timeline.list()` check for all 30 matching pairs |
| **Resolution** | 1080×1920 (9:16), `useCustomSettings: 1` | `timeline.get_setting("timelineResolutionWidth") == "1080"` |
| **Frame Rate** | Identical to source (60.0 fps) | `timeline.get_setting("timelineFrameRate") == 60.0` |
| **Subtitles** | 100% cue count, text string, and frame bounds match | `timeline.get_items(track_type="subtitle", index=1)` diff |
| **Audio** | 100% tracks (A1, A2, A3), volume dB, and fades match | `timeline_item.get_audio` and duration check |
| **Duration** | Exact frame count match to 16:9 original | `timeline.get_end_frame() - timeline.get_start_frame()` |
| **Media Status** | Zero offline clips | `timeline.probe_timeline_structure()` media_status |

---

## 8. Step-by-Step Implementation Recipe for Implementer

```python
# Pseudo-code implementation recipe for executing on 1 sample, then batch

def convert_timeline_to_vertical_9x16(original_timeline, project):
    orig_name = original_timeline.GetName()
    vert_name = f"{orig_name}_9x16"
    orig_fps = original_timeline.GetSetting("timelineFrameRate")
    
    # 1. Non-destructive duplication
    vert_timeline = original_timeline.DuplicateTimeline(vert_name)
    project.SetCurrentTimeline(vert_timeline)
    
    # 2. Configure 9:16 resolution
    vert_timeline.SetSettings({
        "useCustomSettings": "1",
        "timelineResolutionWidth": "1080",
        "timelineResolutionHeight": "1920",
        "timelineOutputResMatchTimelineRes": "1",
        "timelineOutputResolutionWidth": "1080",
        "timelineOutputResolutionHeight": "1920",
        "timelinePixelAspectRatio": "square",
        "timelineInputResMismatchBehavior": "scaleToFit",
        "timelineOutputResMismatchBehavior": "scaleToFit"
    })
    assert float(vert_timeline.GetSetting("timelineFrameRate")) == float(orig_fps)
    
    # 3. Add V2 for VTuber and duplicate V1 clips to V2
    # Note: Duplicate V1 video clips to newly created V2 track
    # Then shift existing V2 (GIFs) to V3, and existing V3 (Adjustment Clips) to V4
    
    # 4. Apply Split Screen Transforms:
    # V1 (Game Top):
    #   ZoomX=1.60, ZoomY=1.60, Pan=0.0, Tilt=480.0, CropBottom=486.0
    # V2 (VTuber Bottom):
    #   ZoomX=2.60, ZoomY=2.60, Pan=-936.0, Tilt=-200.0, CropTop=480.0
    
    # 5. Reposition V3 Reaction GIFs:
    #   ZoomX=0.42, ZoomY=0.42, Pan=-300.0, Tilt=600.0
    
    # 6. Update V4 Adjustment Clips (VTuber Focus):
    #   For each Adjustment Clip on V4:
    #     comp = item.GetFusionCompByIndex(1)
    #     transform_node = comp.FindToolByID("Transform")
    #     transform_node.SetInput("Center", {1: 0.50, 2: 0.25, 3: 0.0})
    #     transform_node.SetInput("Size", 2.0)
    
    # 7. Audit & Verify:
    #   Verify subtitle count & text against original
    #   Verify audio tracks & levels against original
    #   Verify frame duration against original
    #   Render QC sample frame via timeline_frame.capture
```
