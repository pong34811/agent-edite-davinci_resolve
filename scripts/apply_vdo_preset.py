"""Apply an Inspector *Video preset* ("vdo") to the GIF items on the REACTIONS track.

Resolve 21.1 has no scripting call for Inspector > Video Presets > Load Preset
(``Project.SetPreset`` / ``GetPresetList`` are project-settings presets), and the
preset body is not readable from ``User.db`` (``VideoPresetsBA`` holds no
"vdo" entry).  So a preset here is a captured set of TimelineItem properties,
stored in ``scripts/video_presets.json``.  Loading a preset in the GUI copies
exactly those Inspector values onto the clip, so applying the same values by
``TimelineItem.SetProperty`` gives the same result.  The shipped ``vdo`` entry was
captured from a clip the user loaded "vdo" onto (Zoom 0.420 gang, Position 0 /
32.284, everything else default).

Only transform/composite properties in the preset are written; picture, audio,
subtitles, fades and the item's range/track are never touched.  Default is a
read-only dry run.

Usage::

    python scripts/apply_vdo_preset.py                       # dry run, all timelines, track "REACTIONS"
    python scripts/apply_vdo_preset.py --apply
    python scripts/apply_vdo_preset.py --apply --only-originals
    python scripts/apply_vdo_preset.py --apply --timeline "name or id" --timeline ...
    python scripts/apply_vdo_preset.py --capture vdo         # (re)capture from the clip under the playhead
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SCRIPT_API = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
SCRIPT_LIB = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
PRESET_FILE = Path(__file__).with_name("video_presets.json")
TOL = 1e-4
GAP = 0.45  # s between property writes (transform setters can return False if hit too fast)


def connect():
    os.environ.setdefault("RESOLVE_SCRIPT_API", SCRIPT_API)
    os.environ.setdefault("RESOLVE_SCRIPT_LIB", SCRIPT_LIB)
    sys.path.append(os.path.join(SCRIPT_API, "Modules"))
    import DaVinciResolveScript as dvr  # noqa: E402
    resolve = dvr.scriptapp("Resolve")
    if not resolve:
        sys.exit("Resolve is not running / scripting is not enabled")
    return resolve


def load_presets() -> dict:
    return json.loads(PRESET_FILE.read_text(encoding="utf-8"))


def same(a, b) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return bool(a) == bool(b)
    try:
        return abs(float(a) - float(b)) <= TOL
    except (TypeError, ValueError):
        return a == b


def timelines(project):
    return [project.GetTimelineByIndex(i) for i in range(1, project.GetTimelineCount() + 1)]


def activate(project, tl) -> None:
    if not project.SetCurrentTimeline(tl):
        raise RuntimeError(f"cannot activate {tl.GetName()}")
    time.sleep(1.0)
    if project.GetCurrentTimeline().GetUniqueId() != tl.GetUniqueId():
        raise RuntimeError(f"active timeline mismatch for {tl.GetName()}")


def find_track(tl, name: str | None, index: int | None) -> int | None:
    if index:
        return index if index <= tl.GetTrackCount("video") else None
    for k in range(1, tl.GetTrackCount("video") + 1):
        if tl.GetTrackName("video", k) == name:
            return k
    return None


def diff_item(item, values: dict) -> dict:
    return {k: (item.GetProperty(k), v) for k, v in values.items() if not same(item.GetProperty(k), v)}


def write_item(item, values: dict) -> list[str]:
    """Set every differing property, wait, read back, retry once. Returns failures."""
    for k, v in diff_item(item, values).items():
        val = v[1]
        item.SetProperty(k, val if isinstance(val, bool) else float(val))
        time.sleep(GAP)
    bad = diff_item(item, values)
    if bad:  # a False setter can already have applied; re-read, then retry once
        time.sleep(1.0)
        for k, v in diff_item(item, values).items():
            item.SetProperty(k, v[1] if isinstance(v[1], bool) else float(v[1]))
            time.sleep(GAP)
        bad = diff_item(item, values)
    return [f"{k}: got {g}, want {w}" for k, (g, w) in bad.items()]


def capture(resolve, project, name: str) -> None:
    tl = project.GetCurrentTimeline()
    item = tl.GetCurrentVideoItem()
    if not item:
        sys.exit("no video item under the playhead on the active timeline")
    keep = ("ZoomX", "ZoomY", "Pan", "Tilt", "RotationAngle", "AnchorPointX", "AnchorPointY", "Pitch", "Yaw",
            "FlipX", "FlipY", "CropLeft", "CropRight", "CropTop", "CropBottom", "CropSoftness", "Opacity",
            "CompositeMode")
    props = item.GetProperty()
    values = {k: props[k] for k in keep if k in props}
    presets = load_presets() if PRESET_FILE.exists() else {}
    presets[name] = {"source": f"{tl.GetName()} :: {item.GetName()}", "values": values}
    PRESET_FILE.write_text(json.dumps(presets, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"captured '{name}' from {presets[name]['source']}: {values}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--preset", default="vdo")
    ap.add_argument("--track-name", default="REACTIONS")
    ap.add_argument("--track-index", type=int, default=0)
    ap.add_argument("--timeline", action="append", default=[], help="name or unique id; repeatable")
    ap.add_argument("--only-originals", action="store_true", help="skip timelines whose name ends with [ENHANCED]")
    ap.add_argument("--all-media", action="store_true", help="include non-GIF items on the track")
    ap.add_argument("--apply", action="store_true", help="write (default: dry run)")
    ap.add_argument("--capture", metavar="NAME", help="store the clip under the playhead as preset NAME and exit")
    args = ap.parse_args()

    resolve = connect()
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    if args.capture:
        capture(resolve, project, args.capture)
        return 0

    preset = load_presets()[args.preset]
    values = preset["values"]
    print(f"preset '{args.preset}' (from {preset['source']}): {values}")

    tls = timelines(project)
    if args.timeline:
        tls = [t for t in tls if t.GetName() in args.timeline or t.GetUniqueId() in args.timeline]
    if args.only_originals:
        tls = [t for t in tls if not t.GetName().endswith("[ENHANCED]")]

    cur = project.GetCurrentTimeline()
    saved = {"id": cur.GetUniqueId(), "tc": cur.GetCurrentTimecode(), "page": resolve.GetCurrentPage()}
    failures, changed, total = [], 0, 0
    try:
        for tl in tls:
            k = find_track(tl, args.track_name, args.track_index)
            if not k:
                print(f"- {tl.GetName()[:40]}: no '{args.track_name}' track, skipped")
                continue
            if args.apply:
                activate(project, tl)
            for it in tl.GetItemListInTrack("video", k) or []:
                mpi = it.GetMediaPoolItem()
                path = (mpi.GetClipProperty("File Path") if mpi else "") or ""
                if not args.all_media and not path.lower().endswith(".gif"):
                    continue
                total += 1
                d = diff_item(it, values)
                tag = "ok" if not d else ("would change " + ", ".join(f"{a}:{g}->{w}" for a, (g, w) in d.items()))
                if args.apply and d:
                    bad = write_item(it, values)
                    tag = "FAILED " + "; ".join(bad) if bad else "applied"
                    (failures.append((tl.GetName(), it.GetName(), bad)) if bad else None)
                    changed += 0 if bad else 1
                print(f"  {tl.GetName()[:28]:28} @{it.GetStart():>5} {it.GetName()[:30]:30} {tag}")
        if args.apply:
            print("SaveProject:", pm.SaveProject())
    finally:
        if args.apply:  # restore working state and read it back
            back = next((t for t in timelines(project) if t.GetUniqueId() == saved["id"]), None)
            if back:
                project.SetCurrentTimeline(back)
                time.sleep(1.0)
                back.SetCurrentTimecode(saved["tc"])
                time.sleep(1.0)
                print("restored:", project.GetCurrentTimeline().GetUniqueId() == saved["id"],
                      back.GetCurrentTimecode() == saved["tc"], resolve.GetCurrentPage() == saved["page"])

    print(f"GIF items checked: {total}; applied: {changed}; failures: {len(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
