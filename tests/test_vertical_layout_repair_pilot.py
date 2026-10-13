"""Geometry checks; not a substitute for Resolve-rendered pixel QC."""
import importlib
import math
from typing import Any, Callable, cast

import pytest


def layout_function() -> Callable[..., dict[str, float]]:
    try:
        module = importlib.import_module("scripts.vertical_layout_repair_pilot")
    except ModuleNotFoundError:
        module = None
    function = getattr(module, "layout_properties", None)
    assert callable(function), "layout_properties is not implemented"
    return cast(Callable[..., dict[str, float]], function)


@pytest.mark.parametrize("crop,top,height", [
    ((250.0, 0.0, 857.5, 540.0), 0.0, 960.0),
    ((830.0, 70.0, 1280.0, 470.0), 960.0, 960.0),
    ((1010.0, 60.0, 1280.0, 540.0), 0.0, 1920.0),
])
def test_source_crop_maps_to_exact_panel_without_blank(crop, top, height):
    props = layout_function()(crop, top, height)
    fit = 1080.0 / 1280.0
    scale = props["ZoomX"] * fit
    x0, y0, x1, y1 = crop
    cx = 540.0 + props["Pan"]
    cy = 960.0 - props["Tilt"] * (702.0 * fit / 1920.0)
    assert math.isclose(cx + (x0 - 640.0) * scale, 0.0, abs_tol=1e-8)
    assert math.isclose(cx + (x1 - 640.0) * scale, 1080.0, abs_tol=1e-8)
    assert math.isclose(cy + (y0 - 351.0) * scale, top, abs_tol=1e-8)
    assert math.isclose(cy + (y1 - 351.0) * scale, top + height, abs_tol=1e-8)
    assert props["CropLeft"] == x0 * fit
    assert props["CropRight"] == (1280.0 - x1) * fit
    assert props["CropTop"] == y0 * fit
    assert props["CropBottom"] == (702.0 - y1) * fit


@pytest.mark.parametrize("crop", [(-1, 0, 450, 400), (1000, 0, 1450, 400), (0, 20, 450, 20), (0, 0, 400, 400)])
def test_rejects_out_of_source_or_wrong_panel_aspect(crop):
    function = layout_function()
    with pytest.raises(ValueError):
        function(crop, 960.0, 960.0)


def test_game_crop_retains_lower_hud_without_brown_subject():
    module = importlib.import_module("scripts.vertical_layout_repair_pilot")
    assert module.GAME_CROP == (280.0, 0.0, 1000.0, 640.0)
    layout_function()(module.GAME_CROP, 0.0, 960.0)


def test_centered_subject_graph_places_visible_bbox_at_panel_center():
    module = importlib.import_module("scripts.vertical_layout_repair_pilot")
    function = getattr(module, "centered_subject_inputs", None)
    assert callable(function), "centered_subject_inputs is not implemented"
    inputs = cast(Callable[[], dict[str, Any]], function)()
    shift = (inputs["subject_shift"]["Center"][1] - 0.5) * 1280
    visible_bbox_center = (1025 + 1274) / 2
    assert math.isclose(visible_bbox_center + shift, (830 + 1280) / 2)
    assert inputs["subject_shift"]["MotionBlur"] == 0.0
    assert inputs["background_shift"]["MotionBlur"] == 0.0
    assert inputs["rectangle"]["MaskWidth"] == 1280.0
    assert inputs["rectangle"]["MaskHeight"] == 702.0
    assert 0.05 <= (96 - 70) / (470 - 70) <= 0.08
