"""Set the focus-clip transform for a list of ordinals on the ORIGINAL project.

No render, no track change: updates the Transform on the existing focus clip
and verifies readback + protected tracks. Use scripts/focus_tune.py when a
rendered QC frame is also wanted.

Geometry (measured, see SDD ledger Ruling 7):
    final = 0.5 + (source - Center) / Size
  so the visible source window is [Center - 0.5*Size, Center + 0.5*Size].
  Keep Center +- 0.5*Size inside [0,1] to avoid blank/wrapped edges.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from scripts.resolve_common import connect_resolve

PROJECT = "aomimama-2026-09-p1"
ART = Path(".hermes/artifacts/vtuber-focus-review-2026-10-07").resolve()


def require(v, m):
    if not v:
        raise RuntimeError(m)


def activate(project, tl):
    project.SetCurrentTimeline(tl)
    time.sleep(1.25)
    require(project.GetCurrentTimeline().GetUniqueId() == tl.GetUniqueId(),
            "wrong active timeline")


def protected(tl, baseline):
    for tr in baseline["tracks"]:
        items = tl.GetItemListInTrack(tr["kind"], tr["index"]) or []
        actual = [(x.GetName(), x.GetStart(), x.GetEnd()) for x in items]
        expected = [(x["name"], x["start"], x["end"]) for x in tr["items"]]
        require(actual == expected, f"protected drift {tr['kind']} {tr['index']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spec", required=True,
                    help="JSON file: [{ordinal,size,cx,cy}, ...]")
    a = ap.parse_args()
    spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))

    r = connect_resolve()
    require(r is not None, "Resolve unavailable")
    pm = r.GetProjectManager()
    entry = pm.GetCurrentProject()
    en = entry.GetName()
    etl = entry.GetCurrentTimeline().GetName()
    etc = entry.GetCurrentTimeline().GetCurrentTimecode()
    page = r.GetCurrentPage()
    project = entry if en == PROJECT else pm.LoadProject(PROJECT)
    require(project is not None and not project.IsRenderingInProgress(), "busy")

    rows = []
    for item in spec:
        n = item["ordinal"]
        tl = [project.GetTimelineByIndex(i)
              for i in range(1, project.GetTimelineCount() + 1)
              if project.GetTimelineByIndex(i).GetName().startswith(item["name_prefix"])]
        require(len(tl) == 1, f"T{n:02d} timeline not unique")
        tl = tl[0]
        activate(project, tl)
        baseline = json.loads((ART / f"timeline-{n:02d}.json").read_text(encoding="utf-8"))
        protected(tl, baseline)
        tracks = [i for i in range(1, tl.GetTrackCount("video") + 1)
                  if tl.GetTrackName("video", i).startswith("VTUBER_FOCUS")]
        require(len(tracks) == 1, f"T{n:02d} focus track not unique: {tracks}")
        items = tl.GetItemListInTrack("video", tracks[0]) or []
        require(len(items) == 1, f"T{n:02d} focus track holds {len(items)}")
        clip = items[0]
        comp = clip.GetFusionCompByIndex(clip.GetFusionCompCount())
        node = [v for v in comp.GetToolList().values()
                if v.GetAttrs().get("TOOLS_RegID") == "Transform"][0]
        want = {"Size": float(item["size"]), "Edges": float(item.get("edges", 0.0)),
                "Center": {1: float(item["cx"]), 2: float(item["cy"]), 3: 0.0},
                "Pivot": {1: 0.5, 2: 0.5, 3: 0.0}}
        old = {"Size": node.GetInput("Size"), "Center": node.GetInput("Center"),
               "Pivot": node.GetInput("Pivot")}
        for k, v in want.items():
            node.SetInput(k, v)
        time.sleep(1.25)
        got = {"Size": node.GetInput("Size"), "Center": node.GetInput("Center"),
               "Pivot": node.GetInput("Pivot")}
        require(got["Size"] == want["Size"] and got["Center"] == want["Center"],
                f"T{n:02d} readback mismatch: {got}")
        require(pm.SaveProject(), f"T{n:02d} save failed")
        protected(tl, baseline)
        rows.append({"ordinal": n, "name": tl.GetName(), "track": tracks[0],
                     "track_name": tl.GetTrackName("video", tracks[0]),
                     "clip_id": clip.GetUniqueId(),
                     "range": [int(clip.GetStart()), int(clip.GetEnd())],
                     "old": old, "new": got, "protected_ok": True})
        print(f"SET T{n:02d} {tl.GetTrackName('video', tracks[0])} "
              f"Size={got['Size']} Center={got['Center']}", flush=True)

    out = ART / "focus-fix" / f"{time.strftime('%Y%m%d-%H%M%S')}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    o = pm.LoadProject(en)
    for i in range(1, o.GetTimelineCount() + 1):
        t = o.GetTimelineByIndex(i)
        if t.GetName() == etl:
            activate(o, t)
            t.SetCurrentTimecode(etc)
            break
    time.sleep(0.3)
    r.OpenPage(page)
    print("REPORT", str(out))


if __name__ == "__main__":
    main()
