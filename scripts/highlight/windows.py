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

def snap_to_sentence(t: float, sentences, edge: str, max_shift: float = 15.0, tail: float = 0.3) -> float | None:
    """Move a cut out of the middle of a sentence: an `in` point goes back to the sentence start, an `out` point
    forward to its end (+tail). Returns None when t is already between sentences or the shift would exceed max_shift."""
    for s in sentences:
        if s["start"] < t < s["end"]:
            new = s["start"] if edge == "in" else s["end"] + tail
            return round(new, 2) if abs(new - t) <= max_shift else None
    return None

def snap_to_silence(t: float, silences, radius: float = 3.0) -> float:
    best, bd = t, radius + 1e-9
    for a, b in silences:
        m = (a + b) / 2
        if abs(m - t) <= radius and abs(m - t) < bd:
            best, bd = m, abs(m - t)
    return best
