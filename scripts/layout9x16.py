"""9:16 split-screen layout math for 1920x1080 stream sources on a 1080x1920 canvas.

Empirically calibrated on Resolve 21.1.0.17 (scripts/calibrate_crop.py, calibrate_zoom.py):
  * fit scale of a 1920x1080 source on 1080x1920 = 0.5625 canvas px / source px at Zoom 1
  * Zoom multiplies that scale
  * Pan: 1 canvas px per unit (+ = image moves right)
  * Tilt: (fitted_h / canvas_h) = 0.3164 canvas px per unit (+ = image moves UP)
  * Crop*: units are PRE-zoom fitted px -> canvas px = crop * Zoom
"""
from __future__ import annotations

import time
from typing import Any, Dict

CANVAS_W, CANVAS_H = 1080, 1920
SRC_W, SRC_H = 1920, 1080
FIT = min(CANVAS_W / SRC_W, CANVAS_H / SRC_H)  # 0.5625
TILT_PX = (SRC_H * FIT) / CANVAS_H  # canvas px per Tilt unit
SPLIT_Y = 960  # top panel 0..960 (game), bottom panel 960..1920 (VTuber)

# Source regions shown in each panel (source px). Chosen so the game panel never
# includes the facecam (avatar starts at x~1390) and the avatar panel keeps headroom.
GAME_X0 = 255            # game panel shows source x 255..1380 (1125 wide) at 0.96 px/px
GAME_SCALE = SPLIT_Y / 1000.0  # source content rows 40..1040 (1000 tall) fill the 960px panel
AVATAR_X0, AVATAR_Y0 = 1245, 480  # avatar panel shows source x 1245..1920, y 480..1080
AVATAR_SCALE = 1.6


def _pan(img_center_x: float) -> float:
    return img_center_x - CANVAS_W / 2


def _tilt(img_center_y: float) -> float:
    return -(img_center_y - CANVAS_H / 2) / TILT_PX


def game_params() -> Dict[str, float]:
    zoom = GAME_SCALE / FIT
    img_w = SRC_W * GAME_SCALE
    center_x = -GAME_X0 * GAME_SCALE + img_w / 2
    # source row 40 -> canvas y 0 ; image center (source row 540) -> 500*scale
    center_y = (SRC_H / 2 - 40) * GAME_SCALE
    # hide the source's bottom black bar (source rows >1040) below canvas y=960
    crop_bottom = (SRC_H - 1040) * FIT
    return dict(ZoomX=zoom, ZoomY=zoom, Pan=_pan(center_x), Tilt=_tilt(center_y), CropBottom=crop_bottom)


def avatar_params(scale: float = AVATAR_SCALE, cx: float = 1605.0) -> Dict[str, float]:
    """Lower-panel crop of the facecam. `scale` = canvas px per source px, `cx` = avatar centre x (source px).

    The panel always ends at the source frame bottom (y=1080), so the visible source rows are
    [1080 - 960/scale, 1080]. x0 is clamped so the panel never leaves the source frame.
    """
    zoom = scale / FIT
    panel_w_src = CANVAS_W / scale
    panel_h_src = SPLIT_Y / scale
    y0 = SRC_H - panel_h_src
    x0 = min(max(cx - panel_w_src / 2, 0.0), SRC_W - panel_w_src)
    cx_src = x0 + panel_w_src / 2
    cy_src = y0 + panel_h_src / 2
    center_x = CANVAS_W / 2 + (SRC_W / 2 - cx_src) * scale
    center_y = (SPLIT_Y + SPLIT_Y / 2) + (SRC_H / 2 - cy_src) * scale
    crop_top = y0 * FIT  # hide source rows above the panel top
    return dict(ZoomX=zoom, ZoomY=zoom, Pan=_pan(center_x), Tilt=_tilt(center_y), CropTop=crop_top)


# Per-stream facecam anchor: (eye_mid_x, eye_y) in SOURCE pixels, read from labelled source stills
# (scripts/export_source_stills.py). The pilot (Minecraft 003) is the approved look: its eyes land at
# canvas y=1456, so every stream is scaled to put the eyes at EYE_TARGET_Y. That keeps the Fusion focus
# zoom (fixed pivot) framing identical to the pilot on every timeline.
EYE_TARGET_Y = 1456.0
AVATAR_BY_SOURCE = {
    "Minecraft - 002": (1588.0, 868.0),
    "Minecraft - 003": (1605.0, 790.0),   # pilot (approved): scale 1.60
    "Soul Walker - 003": (1605.0, 797.0),
    "Terraria": (1602.0, 825.0),
    "Monster Hunter": (1585.0, 845.0),
    "Soul Walker - 004": (1615.0, 835.0),
    "Soul Walker - 005": (1570.0, 800.0),
}


def avatar_spec_for(source_name: str):
    """Return (scale, centre_x) for the lower panel, or None for an unknown stream."""
    for key, (ex, ey) in AVATAR_BY_SOURCE.items():
        if key in source_name:
            return (CANVAS_H - EYE_TARGET_Y) / (SRC_H - ey), ex
    return None


# V3 (Adjustment Clip, Fusion Transform): zoom the composited lower panel to fill the canvas.
FOCUS: Dict[str, Any] = dict(Size=2.05, Pivot=(0.5, 0.25), Center=(0.5, 0.5))

# V4 reaction GIF: pilot look = ~454px wide, centre at canvas (240, 511) (upper-left of the game panel).
GIF_ZOOM = 0.42
GIF_CENTER = (240.0, 511.0)


def gif_params(w: int, h: int) -> Dict[str, float]:
    fit = min(CANVAS_W / w, CANVAS_H / h)
    fw, fh = w * fit, h * fit
    return dict(
        ZoomX=GIF_ZOOM,
        ZoomY=GIF_ZOOM,
        Pan=(GIF_CENTER[0] - CANVAS_W / 2) / (fw / CANVAS_W),
        Tilt=-(GIF_CENTER[1] - CANVAS_H / 2) / (fh / CANVAS_H),
    )


def _set(item: Any, props: Dict[str, float], pause: float = 0.2) -> None:
    for k, v in props.items():
        item.SetProperty(k, float(v))
        time.sleep(pause)


def readback(item: Any, names) -> Dict[str, Any]:
    out = {}
    for n in names:
        v = item.GetProperty(n)
        out[n] = v
    return out


if __name__ == "__main__":
    import json

    print(json.dumps({"game": game_params(), "avatar": avatar_params(), "focus": FOCUS, "gif_281x374": gif_params(281, 374)}, indent=1))
