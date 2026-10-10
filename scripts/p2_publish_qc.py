"""Read-only publish QC data pass over every timeline of the p2 project (horizontal and vertical).

MCP-GAP: davinci-resolve MCP timeline.list returns names/ids only; per-item/per-cue reads across ~88
timelines need one script. Reads only: no edits, no saves, no renders, no timeline activation.

Run from repo root: python -m scripts.p2_publish_qc
Writes exports/publish-qc/data.json
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.resolve_common import connect_resolve  # noqa: E402

OUT = ROOT / "exports" / "publish-qc"
PROJECT = "aomimama-2026-09-p2"
THAI = re.compile(r"[฀-๿]")
THAI_GAP = re.compile(r"(?<=[฀-๿])[ \t ]+(?=[฀-๿])")
MAX_CHARS, MAX_SEC = 14, 1.5


def items(tl, kind, n):
    return tl.GetItemListInTrack(kind, n) or []


def media_path(it):
    try:
        mp = it.GetMediaPoolItem()
        return mp.GetClipProperty("File Path") if mp else None
    except Exception:
        return None


def read(tl, fps):
    d = {"name": tl.GetName(), "id": tl.GetUniqueId(), "start": tl.GetStartFrame(), "end": tl.GetEndFrame(),
         "w": int(tl.GetSetting("timelineResolutionWidth")), "h": int(tl.GetSetting("timelineResolutionHeight")),
         "fps": float(tl.GetSetting("timelineFrameRate")), "playback_fps": tl.GetSetting("timelinePlaybackFrameRate")}
    d["vertical"] = d["h"] > d["w"]
    d["dur_s"] = round((d["end"] - d["start"]) / d["fps"], 2)
    # video
    vt = []
    for n in range(1, tl.GetTrackCount("video") + 1):
        its = items(tl, "video", n)
        vt.append({"track": n, "enabled": tl.GetIsTrackEnabled("video", n), "items": [
            {"name": x.GetName(), "s": x.GetStart(), "e": x.GetEnd(), "enabled": x.GetClipEnabled(),
             "path": media_path(x)} for x in its]})
    d["video"] = vt
    v1 = sorted(vt[0]["items"], key=lambda x: x["s"]) if vt else []
    gaps, cur = [], d["start"]
    for x in v1:
        if x["s"] > cur:
            gaps.append([cur, x["s"]])
        cur = max(cur, x["e"])
    if cur < d["end"]:
        gaps.append([cur, d["end"]])
    d["v1_gaps"] = gaps
    offline = set()
    for t in vt:
        for x in t["items"]:
            if x["path"] and not x["name"].lower().endswith(".gif") and not os.path.exists(x["path"]):
                offline.add(x["path"])
    d["offline_paths"] = sorted(offline)
    # audio
    at = []
    for n in range(1, tl.GetTrackCount("audio") + 1):
        its = items(tl, "audio", n)
        at.append({"track": n, "enabled": tl.GetIsTrackEnabled("audio", n), "n": len(its),
                   "covered": sum(x.GetEnd() - x.GetStart() for x in its),
                   "vol": [x.GetProperty("AudioVolume") if hasattr(x, "GetProperty") else None for x in its][:3],
                   "names": sorted({x.GetName() for x in its})[:3]})
    d["audio"] = at
    # subtitles
    cues = []
    for n in range(1, tl.GetTrackCount("subtitle") + 1):
        for x in sorted(items(tl, "subtitle", n), key=lambda x: x.GetStart()):
            cues.append((x.GetName(), x.GetStart(), x.GetEnd()))
    issues, prev_end = [], None
    for text, s, e in cues:
        secs = (e - s) / d["fps"]
        thai = len(THAI.findall(text))
        flat = text.replace("\n", "").strip()
        if not flat:
            issues.append(["empty", s, text])
        if thai > MAX_CHARS:
            issues.append(["chars>%d" % MAX_CHARS, s, text])
        if secs > MAX_SEC + 0.05:
            issues.append(["sec>%.1f" % MAX_SEC, s, "%.2fs %s" % (secs, text)])
        if THAI_GAP.search(text):
            issues.append(["thai_space", s, text])
        if text.count("\n") >= 2:
            issues.append(["lines>2", s, text])
        if prev_end is not None and s < prev_end:
            issues.append(["overlap", s, text])
        prev_end = e
    d["subs"] = {"count": len(cues), "tracks": tl.GetTrackCount("subtitle"), "issues": issues,
                 "first": cues[0][1] if cues else None, "last": cues[-1][2] if cues else None,
                 "covered_frames": sum(e - s for _, s, e in cues), "cues": cues}
    return d


def main():
    r = connect_resolve()
    p = r.GetProjectManager().GetCurrentProject()
    if p is None or p.GetName() != PROJECT:
        raise SystemExit("project %s not open" % PROJECT)
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for i in range(1, p.GetTimelineCount() + 1):
        tl = p.GetTimelineByIndex(i)
        row = read(tl, None)
        row["index"] = i
        rows.append(row)
        print(i, row["name"], row["w"], row["h"], row["dur_s"], "cues", row["subs"]["count"],
              "issues", len(row["subs"]["issues"]), flush=True)
    (OUT / "data.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print("WROTE", len(rows))


if __name__ == "__main__":
    main()
