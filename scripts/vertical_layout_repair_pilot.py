"""Conservative geometry for the approved reference-only vertical repair pilot.

MCP-GAP: timeline duplicate/item transform actions are not attached to this
session; the configured community server interpreter is missing. Resolve's
21.1.0.17 Python API was read-only probed before executing a pilot. This module
is pure geometry and never connects to or modifies Resolve on import.
"""
from __future__ import annotations

import math

from scripts.armigon_9x16_batch_one import portrait_transform

SOURCE_ID = "1da4c177-d84e-4136-80c6-35fd7fef52f9"
GAME_CROP = (280.0, 0.0, 1000.0, 640.0)
SUBJECT_CROP = (830.0, 70.0, 1280.0, 470.0)
FULLSCREEN_CROP = (1010.0, 60.0, 1280.0, 540.0)


def layout_properties(crop: tuple[float, float, float, float],
                      panel_top: float, panel_height: float) -> dict[str, float]:
    """Map a reviewed source rectangle to one exact 1080-wide panel."""
    x0, y0, x1, y1 = crop
    if not (0 <= x0 < x1 <= 1280 and 0 <= y0 < y1 <= 702):
        raise ValueError("Crop exceeds the verified 1280x702 source")
    if not (0 <= panel_top < panel_top + panel_height <= 1920):
        raise ValueError("Panel exceeds the verified 1080x1920 canvas")
    if not math.isclose((x1 - x0) / (y1 - y0), 1080 / panel_height):
        raise ValueError("Crop aspect cannot fill this panel without blank/stretch")
    props = portrait_transform(crop, panel_top, 1280, 702,
                               crop_top_src=y0, panel_height=panel_height)
    fit = 1080 / 1280
    props.update(CropLeft=x0 * fit, CropRight=(1280 - x1) * fit,
                 CropBottom=(702 - y1) * fit)
    return props


def centered_subject_inputs() -> dict[str, dict[str, object]]:
    """Static source-space compositor; only for this reviewed camera layout.

    A source-left game patch fills the panel behind the translated subject
    rectangle. This uses no blur, wrap, mirror, generated asset or keyframe.
    Visible subject bounds are annotated on the original reference still;
    motion/occlusion still require pixel QC rather than relying on this math.
    """
    shift = (830.0 + 1280.0) / 2 - (1025.0 + 1274.0) / 2
    return {
        "background_shift": {
            "Center": {1: 0.5 + 830.0 / 1280.0, 2: 0.5, 3: 0.0},
            "Size": 1.0, "MotionBlur": 0.0, "Edges": 0.0,
        },
        "subject_shift": {
            "Center": {1: 0.5 + shift / 1280.0, 2: 0.5, 3: 0.0},
            "Size": 1.0, "MotionBlur": 0.0, "Edges": 0.0,
        },
        "rectangle": {
            "Center": {1: ((1005.0 + 1280.0) / 2 + shift) / 1280.0,
                       2: 1.0 - ((70.0 + 470.0) / 2) / 702.0, 3: 0.0},
            "Width": 275.0 / 1280.0, "Height": 400.0 / 702.0,
            "MaskWidth": 1280.0, "MaskHeight": 702.0,
            "UseFrameFormatSettings": 0.0, "SoftEdge": 0.0,
            "MotionBlur": 0.0,
        },
    }
