"""Turn Resolve's Dialogue Leveler on/off on every item of one audio track (Resolve 21.1 clip properties).

    py -3.13 -X utf8 -m scripts.set_dialogue_leveler --timeline-id <id> [--track 1] [--off] [--gain DB] [--apply]

Dry run by default (prints current values). With --apply it activates the timeline (the leveler keys are
"[Active Timeline Only]"), sets the properties, reads them back, saves, and restores the previously active timeline.

Enabling the leveler in 21.1.0.17 also switches on BackgroundReduction and +2 dB OutputGain, so both are set explicitly
(game audio kept, no hidden gain). Measured on Katy404 day 28 (2026-11-15): a quiet raw mic recording (-29 LUFS,
true peak -5.5 dBFS, quiet intro -35 LUFS) rendered at -13.7 LUFS, LRA 3.4 LU, peak -1.0 dBFS with the leveler alone.
On hot sources already peaking near 0 dBTP it only cut PLR ~2 dB (KT404 HL, 2026-11-05): measure a render, never assume.

MCP-GAP: timeline_item set_property covers AudioVolume, but the leveler keys need the timeline activated and read back
in one guarded step -> scripting API via resolve_common.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

KEYS = ("AudioVolume", "AudioDialogueLevelerEnabled", "AudioDialogueLevelerMode", "AudioDialogueLevelerReduceLoudDialogue",
        "AudioDialogueLevelerLiftSoftDialogue", "AudioDialogueLevelerBackgroundReduction", "AudioDialogueLevelerOutputGain")


def leveler_props(on: bool, gain_db: float | None = None) -> dict:
    """Properties to write. On: reduce loud + lift soft, background reduction off, output gain 0."""
    props = {"AudioDialogueLevelerEnabled": bool(on)}
    if on:
        props.update({"AudioDialogueLevelerReduceLoudDialogue": True, "AudioDialogueLevelerLiftSoftDialogue": True,
                      "AudioDialogueLevelerBackgroundReduction": False, "AudioDialogueLevelerOutputGain": 0.0})
    if gain_db is not None:
        props["AudioVolume"] = float(gain_db)
    return props


def mismatches(item, props: dict) -> list[str]:
    """Keys whose read-back value differs from what was written."""
    bad = []
    for k, v in props.items():
        got = item.GetProperty(k)
        if isinstance(v, bool):
            ok = bool(got) == v
        else:
            try:
                ok = abs(float(got) - float(v)) < 0.01
            except (TypeError, ValueError):
                ok = False
        if not ok:
            bad.append(f"{k}: wrote {v!r}, read {got!r}")
    return bad


def apply_to_items(items, props: dict, settle: float = 0.3) -> list[str]:
    errors = []
    for it in items:
        for k, v in props.items():
            if not it.SetProperty(k, v):
                errors.append(f"{it.GetName()}: SetProperty({k}) returned False")
            time.sleep(settle)
        errors += [f"{it.GetName()}: {m}" for m in mismatches(it, props)]
    return errors


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--timeline-id", required=True)
    ap.add_argument("--track", type=int, default=1, help="audio track index (1-based)")
    ap.add_argument("--off", action="store_true", help="disable the leveler instead of enabling it")
    ap.add_argument("--gain", type=float, default=None, help="also set AudioVolume (dB) on every item")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    from scripts.resolve_common import connect_resolve
    pm = connect_resolve().GetProjectManager(); p = pm.GetCurrentProject()
    tl = next((p.GetTimelineByIndex(k) for k in range(1, p.GetTimelineCount() + 1)
               if p.GetTimelineByIndex(k).GetUniqueId() == a.timeline_id), None)
    if tl is None:
        print("STOP: timeline id not found"); return 2
    if p.IsRenderingInProgress():
        print("STOP: render in progress"); return 2
    prev = p.GetCurrentTimeline()
    p.SetCurrentTimeline(tl); time.sleep(1.2)
    try:
        items = tl.GetItemListInTrack("audio", a.track) or []
        if not items:
            print("STOP: no items on audio track", a.track); return 2
        props = leveler_props(not a.off, a.gain)
        print("timeline", tl.GetName(), "A%d" % a.track, len(items), "item(s); write", props)
        if a.apply:
            errors = apply_to_items(items, props)
            for e in errors:
                print("ERROR", e)
            if errors:
                return 1
            if not pm.SaveProject():
                print("STOP: SaveProject failed"); return 1
        for it in items:
            print(it.GetName(), {k: it.GetProperty(k) for k in KEYS})
        print("applied" if a.apply else "dry run (add --apply)")
        return 0
    finally:
        if prev is not None:
            p.SetCurrentTimeline(prev)


if __name__ == "__main__":
    sys.exit(main())
