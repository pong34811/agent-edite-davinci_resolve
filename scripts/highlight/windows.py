"""Pure helpers for highlight windows."""

def merge_windows(ws, gap_s: float = 15):
    out = []
    for s, e, sc in sorted(ws):
        if out and s <= out[-1][1] + gap_s:
            ps, pe, psc = out[-1]; out[-1] = (ps, max(pe, e), max(psc, sc))
        else:
            out.append((s, e, sc))
    return out

def clamp_duration(start: float, end: float, min_s: float = 30, max_s: float = 180):
    length = min(max(end - start, min_s), max_s)
    centre = (start + end) / 2
    s = centre - length / 2
    if s < 0: s = 0
    return (s, s + length)

def snap_to_silence(t: float, silences, radius: float = 3.0) -> float:
    best, bd = t, radius + 1e-9
    for a, b in silences:
        m = (a + b) / 2
        if abs(m - t) <= radius and abs(m - t) < bd:
            best, bd = m, abs(m - t)
    return best
