"""Delete one stray half-built `_9x16` copy by exact name + id, only while it is still 16:9.

MCP-GAP: timeline delete in the davinci-resolve MCP auto-archives the timeline (adds `_archived_vNN`), so the
scripting API is used through scripts/resolve_common. The timeline is never activated (reading it hung Resolve).

Usage: python scripts/p2_delete_stray_copy.py <timeline_id> <exact_name> [--apply]   (default: dry run)
"""
from __future__ import annotations

import sys
import time

from resolve_common import connect_resolve

PROJECT = "aomimama-2026-09-p2"


def main() -> int:
    tid, name = sys.argv[1], sys.argv[2]
    apply = "--apply" in sys.argv
    r = connect_resolve()
    pm = r.GetProjectManager()
    p = pm.GetCurrentProject()
    if not p or p.GetName() != PROJECT:
        print("wrong project loaded")
        return 1
    matches = [t for t in (p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1))
               if t.GetUniqueId() == tid and t.GetName() == name]
    if len(matches) != 1:
        print("no unique match for id+name; nothing deleted")
        return 1
    tl = matches[0]
    w, h = tl.GetSetting("timelineResolutionWidth"), tl.GetSetting("timelineResolutionHeight")
    print("FOUND", name, tid, "raster", w, h, "tracks", tl.GetTrackCount("video"))
    if (w, h) != ("1920", "1080") and "--allow-any-raster" not in sys.argv:
        print("raster is not 1920x1080; refusing to delete (pass --allow-any-raster only on explicit user request)")
        return 1
    cur = p.GetCurrentTimeline()
    if cur is not None and cur.GetUniqueId() == tid:
        print("it is the active timeline; refusing")
        return 1
    if not apply:
        print("dry run only")
        return 0
    before = p.GetTimelineCount()
    ok = p.GetMediaPool().DeleteTimelines([tl])
    time.sleep(1.25)
    pm.SaveProject()
    time.sleep(1.25)
    gone = all(p.GetTimelineByIndex(i).GetUniqueId() != tid for i in range(1, p.GetTimelineCount() + 1))
    print("DELETED", ok, "count", before, "->", p.GetTimelineCount(), "gone", gone)
    return 0 if (ok and gone) else 1


if __name__ == "__main__":
    sys.exit(main())
