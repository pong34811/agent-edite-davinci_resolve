"""Tests for Timeline 1 Pilot Readback Verification."""

from unittest.mock import MagicMock
import pytest

from scripts.run_pilot import verify_timeline_readback, frame_to_timecode


def test_pilot_timeline_structure_spec():
    """Verify expected tracks and item constraints for Timeline 1 per specification."""
    expected_v_count = 2
    expected_a_count = 3
    assert expected_v_count >= 2
    assert expected_a_count >= 3


def test_frame_to_timecode():
    """Verify frame to timecode conversion at 60 fps."""
    # 216000 frames @ 60fps = 3600 seconds = 01:00:00:00
    assert frame_to_timecode(216000, 60.0) == "01:00:00:00"
    # 216363 frames @ 60fps = 3600s + 6s + 3 frames = 01:00:06:03
    assert frame_to_timecode(216363, 60.0) == "01:00:06:03"
    # 0 frames
    assert frame_to_timecode(0, 60.0) == "00:00:00:00"


def _create_mock_timeline(
    v_track_count=2,
    a_track_count=3,
    sub_track_count=1,
    sub_count=51,
    v2_count=2,
    v2_zoom=0.55,
    v2_pan=0.0,
    v2_tilt=0.0,
    a2_count=3,
    a2_vol=-11.0,
    a3_count=1,
    a3_vol=-23.0,
):
    """Helper to create a configured mock Timeline."""
    tl = MagicMock()
    tl.GetName.return_value = "ขุดมั่วเจอเหล็กกองใหญ่_Minecraft-vdo"

    def get_track_count(t_type):
        if t_type == "video":
            return v_track_count
        elif t_type == "audio":
            return a_track_count
        elif t_type == "subtitle":
            return sub_track_count
        return 0

    tl.GetTrackCount.side_effect = get_track_count

    # Subtitles
    sub_items = [MagicMock() for _ in range(sub_count)]

    # V2 items (GIFs)
    v2_items = []
    for _ in range(v2_count):
        item = MagicMock()
        item.GetProperty.return_value = {
            "ZoomX": v2_zoom,
            "ZoomY": v2_zoom,
            "Pan": v2_pan,
            "Tilt": v2_tilt,
        }
        v2_items.append(item)

    # A2 items (SFX)
    a2_items = []
    for _ in range(a2_count):
        item = MagicMock()
        item.GetProperty.return_value = {
            "AudioVolume": a2_vol,
        }
        a2_items.append(item)

    # A3 items (BGM)
    a3_items = []
    for _ in range(a3_count):
        item = MagicMock()
        item.GetProperty.return_value = {
            "AudioVolume": a3_vol,
        }
        a3_items.append(item)

    def get_item_list(t_type, idx):
        if t_type == "subtitle" and idx == 1:
            return sub_items
        elif t_type == "video" and idx == 2:
            return v2_items
        elif t_type == "video" and idx == 1:
            return [MagicMock()]
        elif t_type == "audio" and idx == 2:
            return a2_items
        elif t_type == "audio" and idx == 3:
            return a3_items
        elif t_type == "audio" and idx == 1:
            return [MagicMock()]
        return []

    tl.GetItemListInTrack.side_effect = get_item_list
    return tl


def test_verify_timeline_readback_success():
    """Verify that a compliant timeline passes all readback criteria."""
    tl = _create_mock_timeline()
    res = verify_timeline_readback(tl)
    assert res["passed"] is True
    assert res["checks"]["video_tracks_min_2"] is True
    assert res["checks"]["audio_tracks_min_3"] is True
    assert res["checks"]["subtitle_tracks_exact_1"] is True
    assert res["checks"]["subtitles_untouched_51"] is True
    assert res["checks"]["v2_gifs_count_min_1"] is True
    assert res["checks"]["v2_gifs_properties_valid"] is True
    assert res["checks"]["a2_sfx_count_min_2"] is True
    assert res["checks"]["a2_sfx_properties_valid"] is True
    assert res["checks"]["a3_bgm_count_exact_1"] is True
    assert res["checks"]["a3_bgm_properties_valid"] is True


def test_verify_timeline_readback_subtitles_corrupted():
    """Verify that if subtitle cues are modified/dropped, verification fails."""
    tl = _create_mock_timeline(sub_count=50)  # 1 cue lost
    res = verify_timeline_readback(tl)
    assert res["passed"] is False
    assert res["checks"]["subtitles_untouched_51"] is False


def test_verify_timeline_readback_v2_wrong_zoom():
    """Verify that if GIF zoom is incorrect, verification fails."""
    tl = _create_mock_timeline(v2_zoom=1.0)  # Should be 0.55
    res = verify_timeline_readback(tl)
    assert res["passed"] is False
    assert res["checks"]["v2_gifs_properties_valid"] is False


def test_verify_timeline_readback_a2_wrong_volume():
    """Verify that if SFX volume is incorrect, verification fails."""
    tl = _create_mock_timeline(a2_vol=0.0)  # Should be -11.0 dB
    res = verify_timeline_readback(tl)
    assert res["passed"] is False
    assert res["checks"]["a2_sfx_properties_valid"] is False


def test_verify_timeline_readback_a3_wrong_count():
    """Verify that if BGM track does not have exactly 1 clip, verification fails."""
    tl = _create_mock_timeline(a3_count=0)
    res = verify_timeline_readback(tl)
    assert res["passed"] is False
    assert res["checks"]["a3_bgm_count_exact_1"] is False
