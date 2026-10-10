"""Replace the subtitle track of p2 vertical (_9x16) timelines with the rule-fixed SRT from p2_fix_captions.py.

MCP-GAP: no MCP action replaces a subtitle track from SRT with a bare mediaPoolItem append and cue-level readback.
Per timeline: verify the live cues still equal the planned input, snapshot V/A ranges, delete the old subtitle
track, add an empty one, import the SRT, bare append, read back every cue (text + absolute frames), re-check V/A.
Stops at the first failed timeline. Old cues are kept in exports/captions-fixed/old/<index>.json.
The subtitle PRESET is reloaded afterwards with scripts/load_subtitle_preset.py (not done here).

Run from repo root: python -m scripts.p2_apply_fixed_captions 88 [87 86 ...] [--apply] [--horizontal]
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.resolve_common import connect_resolve, preserved_state  # noqa: E402

DATA = ROOT / "exports" / "publish-qc" / "data.json"
HORIZONTAL = "--horizontal" in sys.argv  # 1920x1080 timelines: SRTs from captions-fixed-h, names without _9x16
FIX = ROOT / "exports" / ("captions-fixed-h" if HORIZONTAL else "captions-fixed")
PROJECT = "aomimama-2026-09-p2"
GAP = 1.3
TIME = re.compile(r"(\d+):(\d\d):(\d\d)[,.](\d{3})\s*-->\s*(\d+):(\d\d):(\d\d)[,.](\d{3})")


class Stop(Exception):
    pass


def check(c, msg):
    if not c:
        raise Stop(msg)


def parse(path, fps):
    txt = Path(path).read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    out = []
    for block in re.split(r"\n\s*\n", txt.strip()):
        lines = block.split("\n")
        m = TIME.search(lines[1])
        g = [int(x) for x in m.groups()]
        a = (g[0] * 3600 + g[1] * 60 + g[2]) * 1000 + g[3]
        b = (g[4] * 3600 + g[5] * 60 + g[6]) * 1000 + g[7]
        out.append(("\n".join(lines[2:]).strip(), int(a * fps / 1000 + 0.5), int(b * fps / 1000 + 0.5)))
    return out


def cues(tl):
    return [(x.GetName(), x.GetStart(), x.GetEnd()) for n in range(1, tl.GetTrackCount("subtitle") + 1)
            for x in sorted(tl.GetItemListInTrack("subtitle", n) or [], key=lambda i: i.GetStart())]


def va(tl):
    return [[(x.GetName(), x.GetStart(), x.GetEnd()) for x in tl.GetItemListInTrack(k, n) or []]
            for k in ("video", "audio") for n in range(1, tl.GetTrackCount(k) + 1)]


def find_pool_srt(folder, name):
    for c in folder.GetClipList() or []:
        if c.GetName() == name:
            return c
    return None


def one(r, p, idx, planned, apply):
    tl = p.GetTimelineByIndex(idx)
    check(tl is not None and tl.GetName().endswith("_9x16") != HORIZONTAL,
          f"index {idx} is not a {'horizontal' if HORIZONTAL else '_9x16'} timeline")
    fps = float(tl.GetSetting("timelineFrameRate"))
    row = next(x for x in planned if x["index"] == idx)
    check(row["name"] == tl.GetName(), f"name mismatch at {idx}")
    srt = FIX / f"{idx}.srt"
    new = parse(srt, fps)
    p.SetCurrentTimeline(tl)
    time.sleep(GAP)
    check(p.GetCurrentTimeline().GetUniqueId() == tl.GetUniqueId(), "activate failed")
    old = cues(tl)
    saved = FIX / "old" / f"{idx}.json"
    if not saved.exists():  # a retry after a failed readback keeps the first snapshot of the ORIGINAL cues
        check(old == [tuple(c) for c in row["subs"]["cues"]], "live cues differ from the QC snapshot (project changed?)")
    check(tl.GetTrackCount("subtitle") == 1, "expected exactly one subtitle track")
    before = va(tl)
    print(idx, tl.GetName()[:30], "old", len(old), "new", len(new), flush=True)
    if not apply:
        return
    (FIX / "old").mkdir(exist_ok=True)
    if not saved.exists():
        saved.write_text(json.dumps(old, ensure_ascii=False), encoding="utf-8")
    was_locked = bool(tl.GetIsTrackLocked("subtitle", 1))
    if was_locked:  # a locked track refuses DeleteTrack; the replacement is locked again below
        check(tl.SetTrackLock("subtitle", 1, False), "unlock failed")
        time.sleep(GAP)
    check(tl.DeleteTrack("subtitle", 1), "DeleteTrack failed")
    time.sleep(GAP)
    check(tl.AddTrack("subtitle"), "AddTrack failed")
    time.sleep(GAP)
    check(tl.GetTrackCount("subtitle") == 1 and not (tl.GetItemListInTrack("subtitle", 1) or []), "new track not empty")
    mp = p.GetMediaPool()
    stale = [c for c in (mp.GetCurrentFolder().GetClipList() or []) if c.GetName() == srt.name]
    if stale:  # a re-import of the same path returns the cached (old) text: drop the stale pool items first
        check(mp.DeleteClips(stale), "could not remove stale SRT pool item")
        time.sleep(GAP)
    uniq = FIX / "import" / f"{idx}_{int(time.time())}.srt"  # fresh path every run: Resolve caches SRT text per path
    uniq.parent.mkdir(exist_ok=True)
    uniq.write_bytes(srt.read_bytes())
    imported = mp.ImportMedia([str(uniq)])
    time.sleep(GAP)
    check(imported, "ImportMedia returned nothing")
    item = imported[0]
    check(mp.AppendToTimeline([{"mediaPoolItem": item}]), "AppendToTimeline failed")
    time.sleep(GAP)
    got = cues(tl)
    check(got == new, f"readback differs: {len(got)} vs {len(new)} cues; first diff "
          f"{next(((a, b) for a, b in zip(got, new) if a != b), None)}")
    check(va(tl) == before, "video/audio ranges changed")
    if was_locked:
        check(tl.SetTrackLock("subtitle", 1, True) and tl.GetIsTrackLocked("subtitle", 1), "relock failed")
    print(idx, "OK", len(got), "cues", flush=True)


def main():
    apply = "--apply" in sys.argv
    ids = [int(a) for a in sys.argv[1:] if a.isdigit()]
    planned = json.loads(DATA.read_text(encoding="utf-8"))
    r = connect_resolve()
    pm = r.GetProjectManager()
    p = pm.GetCurrentProject()
    check(p is not None and p.GetName() == PROJECT, "wrong project")
    with preserved_state(r):
        for idx in ids:
            try:
                one(r, p, idx, planned, apply)
            except Stop as e:
                print("STOP", idx, e, flush=True)
                return 1
        if apply:
            pm.SaveProject()
    return 0


if __name__ == "__main__":
    sys.exit(main())
