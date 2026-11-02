import numpy as np
import features, shortlist

def _base(n=1200, level=-35.0, seed=0):
    rng = np.random.default_rng(seed)
    rms = level + rng.normal(0, 2, n)
    return rms, rms + 6

def _contains(wins, t):
    return any(s <= t <= e for s, e, _ in wins)

def test_per_second_db_of_half_scale_sine():
    sr = 16000
    t = np.arange(sr * 3) / sr
    x = (0.5 * np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
    rms, peak = features.per_second_db(x, sr)
    assert len(rms) == 3
    assert abs(rms[0] - (-9.03)) < 0.3 and abs(peak[0] - (-6.02)) < 0.3

def test_burst_in_speech_is_top_window():
    rms, peak = _base()
    rms[300:310] = -12; peak[300:310] = -6
    wins = shortlist.score_windows(rms, peak)
    best = max(wins, key=lambda w: w[2])
    assert best[0] <= 300 and best[1] >= 310

def test_two_close_bursts_merge_into_one_region():
    rms, peak = _base()
    for a in (300, 320):
        rms[a:a + 10] = -12; peak[a:a + 10] = -6
    wins = shortlist.score_windows(rms, peak)
    top = shortlist.pick_top(wins, n=2)
    assert len(top) == 1 and top[0][0] <= 300 and top[0][1] >= 330

def test_constant_loud_bgm_ranks_below_real_burst():
    rms, peak = _base(1800)
    rms[1500:1800] = -20; peak[1500:1800] = -14      # flat BGM
    rms[300:310] = -10; peak[300:310] = -4           # burst in speech
    wins = shortlist.score_windows(rms, peak)
    top = shortlist.pick_top(wins, n=1)
    assert _contains(top, 305) and not _contains(top, 1600)

def test_burst_inside_silence_is_demoted_vs_burst_inside_speech():
    rms = np.concatenate([np.full(600, -35.0), np.full(600, -75.0)]) + np.random.default_rng(1).normal(0, 1, 1200)
    peak = rms + 6
    rms[300:310] = -12; peak[300:310] = -6     # in speech stretch
    rms[900:910] = -12; peak[900:910] = -6     # in silent stretch
    wins = shortlist.score_windows(rms, peak)
    top = shortlist.pick_top(wins, n=1)
    assert _contains(top, 305) and not _contains(top, 905)

def test_pick_top_count_scales_with_duration():
    assert shortlist.top_n(duration_s=7200, per_hour=14) == 28
    assert shortlist.top_n(duration_s=600, per_hour=14) == 2
