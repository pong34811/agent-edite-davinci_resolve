"""Plan the frame maths for a silent gap after every chapter card (Pop Kinetic explainers). Pure logic, no Resolve.

A chapter card (full-screen wipe) must finish before speech resumes. The timeline is split at CUTS (inside the pause
before each chapter's first word), every item after a cut moves right by GAP per cut, the video gap is filled with the
GAP source frames before the next piece (hidden by the card) and audio is left empty. The card itself starts at its own
record frame W, which may differ from the cut when the chapter's first subtitle cue begins before the cut.

Used by `scripts/scratch/bunny_ep1_gap/gap_edit.py` (Bunny Girl ep1, 2026-11-21); see
`.agents/skills/pop-kinetic-chapter-gap/SKILL.md`.
"""
from __future__ import annotations

from collections.abc import Sequence


def cuts_passed(start: int, cuts: Sequence[int]) -> int:
    """How many A/V cuts are at or before an item's start (the item itself moves)."""
    return sum(c <= start for c in cuts)


def item_shift(start: int, cuts: Sequence[int], gap: int) -> int:
    return gap * cuts_passed(start, cuts)


def subtitle_shift(start: int, end: int, cuts: Sequence[int], gap: int) -> int:
    """A cue that ends after a cut belongs to the later segment, even when it starts before the cut."""
    return gap * sum(end > c for c in cuts)


def wipe_record(wipe: int, cuts: Sequence[int], gap: int) -> int:
    """A wipe overlay starts at its cut, so it moves only by the cuts strictly before it."""
    return wipe + gap * sum(c < wipe for c in cuts)


def whoosh_record(wipe: int, cuts: Sequence[int], gap: int, lead: int = 2) -> int:
    return wipe_record(wipe, cuts, gap) - lead


def wipe_ranges(wipes: Sequence[int], chapter_starts: Sequence[int], cuts: Sequence[int], gap: int) -> list[tuple[int, int, int]]:
    """(wipe, record start, frames) for every wiped chapter; a chapter ends where the next chapter's overlay starts.

    `chapter_starts` is every chapter's overlay start frame in timeline order (wiped or not); `wipes` is the subset
    that has a card. An unwiped chapter keeps its own start, a wiped one starts at its card.
    """
    starts = list(chapter_starts)
    if starts != sorted(set(starts)) or not set(wipes) <= set(starts) or list(wipes) != sorted(wipes) or (wipes and starts[-1] == wipes[-1]):
        raise ValueError('chapter_starts must be unique, ordered, cover every wipe and end with a chapter after the last wipe')
    out = []
    for w in wipes:
        nxt = starts[starts.index(w) + 1]
        s, e = wipe_record(w, cuts, gap), wipe_record(nxt, cuts, gap)
        out.append((w, s, e - s))
    return out


def overlay_local(t_seconds: float, wipe: int, fps: float, gap_seconds: float, has_gap: bool = True) -> float:
    """Local time of an overlay element in the re-rendered chapter: the wipe sits at local 0, content after the gap."""
    return round(t_seconds - wipe / fps + (gap_seconds if has_gap else 0.0), 4)


def split_ranges(start: int, end: int, cuts: Sequence[int]) -> list[tuple[int, int]]:
    edges = [start] + [c for c in cuts if start < c < end] + [end]
    return list(zip(edges, edges[1:]))


def video_fillers(cuts: Sequence[int], gap: int) -> list[tuple[int, int, int]]:
    """(record start, record end, source in) for the video piece hidden under each card."""
    return [(c + j * gap, c + (j + 1) * gap, c - gap) for j, c in enumerate(cuts)]


def pick_cut(db: Sequence[float], onset_s: float, gap_frames: int, fps: float, threshold: float = -40.0,
             window_s: float = 1.0, min_silence_s: float = 0.10) -> int | None:
    """Frame for the A/V cut: inside the silent run just before the speech onset, at least min_silence_s long.

    `db` is a 10 ms RMS map in dBFS. Returns None when there is no such pause (do not cut mid-word; ask or move the card).
    """
    i = int(round(onset_s * 100))
    lo = max(0, int(round((onset_s - window_s) * 100)))
    k = i - 1
    while k >= lo and db[k] <= threshold:
        k -= 1
    run_start, run_end = k + 1, i                      # [run_start, run_end) is silent, in 10 ms units
    if (run_end - run_start) * 0.01 < min_silence_s:
        return None
    want = onset_s - gap_frames / fps                  # the card should end right at the onset
    return max(int(round(run_start * 0.01 * fps)), min(int(round(want * fps)), int(round((run_end - 1) * 0.01 * fps))))
