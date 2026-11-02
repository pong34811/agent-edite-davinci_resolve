"""Pass A scoring: 60 s windows at 30 s hop from per-second RMS/peak dB -> merged top windows."""
import json
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
import config
from windows import merge_windows

W_LOUD, W_PEAK, W_JUMP, W_PLATEAU = 0.30, 0.15, 0.30, 0.25
SPEECH_FLOOR_DB_BELOW_P95 = 30
MIN_SPEECH_RATIO, DEMOTE = 0.2, 0.3

def _z(a: np.ndarray) -> np.ndarray:
    sd = a.std()
    return (a - a.mean()) / sd if sd > 1e-9 else np.zeros_like(a)

def _jump(rms: np.ndarray) -> np.ndarray:
    """rms[t] minus median(rms[t-10 .. t-3]); 0 for the first 10 s."""
    j = np.zeros_like(rms)
    if len(rms) > 10:
        med = np.median(sliding_window_view(rms, 8), axis=1)      # med[i] = median(rms[i:i+8])
        j[10:] = rms[10:] - med[: len(rms) - 10]
    return j

def score_windows(rms, peak, win: int = 60, hop: int = 30):
    rms = np.asarray(rms, dtype=float); peak = np.asarray(peak, dtype=float)
    starts = list(range(0, max(len(rms) - win, 0) + 1, hop))
    if not starts or len(rms) < win:
        return []
    jump = _jump(rms)
    p85 = np.percentile(rms, 85)
    speech_thr = np.percentile(rms, 95) - SPEECH_FLOOR_DB_BELOW_P95
    loud = np.array([rms[s:s + win].mean() for s in starts])
    pk = np.array([peak[s:s + win].max() for s in starts])
    jp = np.array([jump[s:s + win].max() for s in starts])
    pl = np.array([(rms[s:s + win] > p85).mean() for s in starts])
    sp = np.array([(rms[s:s + win] > speech_thr).mean() for s in starts])
    raw = W_LOUD * _z(loud) + W_PEAK * _z(pk) + W_JUMP * _z(jp) + W_PLATEAU * _z(pl)
    rng = raw.max() - raw.min()
    sc = (raw - raw.min()) / rng if rng > 1e-9 else np.zeros_like(raw)
    sc = np.where(sp < MIN_SPEECH_RATIO, sc * DEMOTE, sc)
    return [(float(s), float(s + win), float(v)) for s, v in zip(starts, sc)]

def top_n(duration_s: float, per_hour: int = 20) -> int:
    return max(1, round(duration_s / 3600 * per_hour))

def pick_top(wins, n: int, gap_s: float = 15):
    best = sorted(wins, key=lambda w: w[2], reverse=True)[:n]
    return merge_windows(best, gap_s=gap_s)

def top(source_id: str, per_hour: int = 20):
    d = np.load(config.WORK_DIR / "scores" / f"{source_id}.features.npz")
    wins = score_windows(d["rms"], d["peak"])
    res = pick_top(wins, top_n(len(d["rms"]), per_hour))
    (config.WORK_DIR / "scores" / f"{source_id}.top.json").write_text(json.dumps(res), encoding="utf-8")
    return res
