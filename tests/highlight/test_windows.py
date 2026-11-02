from windows import merge_windows, clamp_duration, snap_to_silence

def test_merge_windows_merges_overlap_keeps_max_score():
    assert merge_windows([(0, 40, .5), (35, 80, .9), (200, 240, .3)]) == [(0, 80, .9), (200, 240, .3)]

def test_merge_windows_merges_within_gap():
    assert merge_windows([(0, 40, .5), (50, 80, .2)], gap_s=15) == [(0, 80, .5)]

def test_clamp_grows_short_window_symmetrically():
    assert clamp_duration(100, 110) == (90, 120)

def test_clamp_shrinks_long_window_to_max():
    s, e = clamp_duration(0, 500)
    assert e - s == 180

def test_clamp_never_negative_start():
    s, e = clamp_duration(5, 10)
    assert s == 0 and e - s == 30

def test_snap_to_nearest_silence_midpoint():
    assert snap_to_silence(100, [(101, 101.6)]) == 101.3

def test_snap_ignores_far_silence():
    assert snap_to_silence(100, [(110, 111)]) == 100
