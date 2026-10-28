"""Delete `<main>_archived_vNN` timelines (the auto-archives the community MCP makes).

Dry run by default: lists each archive, its main timeline, and whether their
video/audio clip ranges match. `--confirm` exports a verified .drp first, deletes
only archives whose main timeline exists, saves, and reads the timeline list back.
Archives without a main timeline are always kept and reported.

Usage: python scripts/delete_archived_timelines.py --project "<name>" [--confirm] [--backup-dir backups]
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from backup_drp import export_verified  # noqa: E402
from resolve_common import connect_resolve  # noqa: E402

ARCHIVE = re.compile(r"^(?P<main>.+)_archived_v\d+$")


def main_name(name: str) -> str | None:
    """'X_archived_v01' -> 'X'; anything else -> None."""
    m = ARCHIVE.match(name)
    return m.group("main") if m else None


def plan(names: list[str]) -> tuple[list[tuple[str, str]], list[str]]:
    """Pair archives with an existing main name; return (pairs, orphans)."""
    present = set(names)
    pairs, orphans = [], []
    for n in names:
        base = main_name(n)
        if base is None:
            continue
        (pairs.append((n, base)) if base in present else orphans.append(n))
    return pairs, orphans


def ranges(tl) -> dict:
    out = {}
    for kind in ("video", "audio"):
        out[kind] = [[(i.GetStart(), i.GetEnd()) for i in (tl.GetItemListInTrack(kind, t) or [])]
                     for t in range(1, tl.GetTrackCount(kind) + 1)]
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--project", required=True)
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--backup-dir", type=Path, default=Path(__file__).resolve().parents[1] / "backups")
    a = ap.parse_args()
    r = connect_resolve()
    if r is None:
        raise SystemExit("Resolve scripting unavailable (run scripts/resolve_recover.py)")
    pm = r.GetProjectManager()
    p = pm.GetCurrentProject()
    if p is None or p.GetName() != a.project:
        raise SystemExit(f"open project is {p and p.GetName()!r}, expected {a.project!r}")
    tls = {}
    for i in range(1, p.GetTimelineCount() + 1):
        t = p.GetTimelineByIndex(i)
        tls[t.GetName()] = t
    pairs, orphans = plan(list(tls))
    differs = []
    for arc, base in pairs:
        same = ranges(tls[arc]) == ranges(tls[base])
        if not same:
            differs.append(arc)
        print(f"{'same' if same else 'DIFF'}  {arc}  ->  {base}")
    for o in orphans:
        print(f"KEEP (no main timeline)  {o}")
    print(f"archives={len(pairs)} differ_from_main={len(differs)} orphans={len(orphans)} total={len(tls)}")
    if not a.confirm:
        print("dry run: add --confirm to delete")
        return 0
    cur = p.GetCurrentTimeline()
    if cur is not None and main_name(cur.GetName()) is not None:
        p.SetCurrentTimeline(tls[main_name(cur.GetName())])
        time.sleep(0.5)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    print("drp bytes", export_verified(pm, p, a.backup_dir / f"{a.project}-before-delete-archives-{stamp}.drp"))
    mp = p.GetMediaPool()
    mp.DeleteTimelines([tls[arc] for arc, _ in pairs])
    time.sleep(1.5)
    after = {p.GetTimelineByIndex(i).GetName() for i in range(1, p.GetTimelineCount() + 1)}
    left = [arc for arc, _ in pairs if arc in after]
    mains_ok = all(base in after for _, base in pairs)
    saved = pm.SaveProject()
    print(f"deleted={len(pairs) - len(left)} still_present={left} mains_intact={mains_ok} "
          f"timelines_now={len(after)} save={saved}")
    return 0 if not left and mains_ok else 1


if __name__ == "__main__":
    sys.exit(main())
