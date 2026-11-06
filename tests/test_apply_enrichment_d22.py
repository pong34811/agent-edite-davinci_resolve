from scripts.apply_enrichment_d22 import sfx_frames


def test_sfx_frames_caps_at_three_seconds_and_max_s():
    assert sfx_frames(2.97, {}, 30) == 89
    assert sfx_frames(10.0, {}, 30) == 90
    assert sfx_frames(10.0, {"max_s": 1.5}, 60) == 90


def test_sfx_past_end_is_detectable():
    # Aomi-mama clothes 2026-11-06: Sad Trombone (2.97 s) at 1648 on a 1672-frame timeline
    assert 1648 + sfx_frames(2.97, {}, 30) > 1672
    assert 1583 + sfx_frames(2.97, {}, 30) <= 1672
