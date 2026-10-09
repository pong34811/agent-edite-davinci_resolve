"""Independent read-only verification of the p2 9:16 pilot against the LIVE original + saved baseline.

MCP-GAP: timeline.compare_timelines compares two timelines' structure, but not subtitle text, audio GetProperty
levels, GIF source ranges, Fusion inputs and the raster settings in one result -> read-only script.

Also writes the original's subtitle cues as an SRT (exports/9x16-pilot/cues_from_timeline.srt) for caption_lint.
Usage: python -m scripts.p2_9x16_verify
"""
from __future__ import annotations

import json
import sys

from scripts.p2_9x16_build import RASTER, items, protected
from scripts.p2_9x16_common import OUT, TARGET_NAME, diff, find, project_and_timeline, signature
from scripts.p2_9x16_layout import TARGET_ID, fusion_transform


def srt_time(frame, fps=60):
    ms = round(frame * 1000 / fps)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main():
    r, pm, p, orig = project_and_timeline()
    new = find(p, TARGET_ID, TARGET_NAME)
    base = json.loads((OUT / "baseline_original.json").read_text(encoding="utf-8"))
    res = {}
    res["original_vs_baseline_diffs"] = diff(base, signature(orig))
    po, pn = protected(orig), protected(new)
    res["subtitles_equal"] = po["sub"] == pn["sub"]
    res["subtitle_count"] = [len(po["sub"]), len(pn["sub"])]
    res["audio_equal"] = po["audio"] == pn["audio"]
    res["audio_count"] = [len(po["audio"]), len(pn["audio"])]
    res["v1_equal"] = po["v1"] == pn["v1"]
    res["range_fps"] = [po["range"], pn["range"], po["fps"], pn["fps"]]
    res["settings"] = {k: new.GetSetting(k) for k, _ in RASTER}
    res["settings_ok"] = all(str(res["settings"][k]) == v for k, v in RASTER)
    rng = lambda tl, n: [(x.GetName(), x.GetStart(), x.GetEnd(), x.GetSourceStartFrame() if n != "adj" else None,
                          x.GetSourceEndFrame() if n != "adj" else None) for x in items(tl, "video", n if n != "adj" else 0)]
    res["focus_ranges"] = [[(x.GetName(), x.GetStart(), x.GetEnd()) for x in items(orig, "video", 2)],
                           [(x.GetName(), x.GetStart(), x.GetEnd()) for x in items(new, "video", 3)]]
    res["focus_equal"] = res["focus_ranges"][0] == res["focus_ranges"][1]
    g = lambda tl, n: [(x.GetName(), x.GetStart(), x.GetEnd(), x.GetSourceStartFrame(), x.GetSourceEndFrame()) for x in items(tl, "video", n)]
    res["gif_equal"] = g(orig, 3) == g(new, 4)
    res["v2_panel"] = g(new, 2)
    res["v2_equal_v1_range"] = g(new, 2) == g(orig, 1)
    res["tracks"] = {k: new.GetTrackCount(k) for k in ("video", "audio", "subtitle")}
    props = ("ZoomX", "ZoomY", "Pan", "Tilt", "CropTop", "CropBottom")
    res["v1_props"] = {k: items(new, "video", 1)[0].GetProperty(k) for k in props}
    res["v2_props"] = {k: items(new, "video", 2)[0].GetProperty(k) for k in props}
    res["gif_props"] = [{k: x.GetProperty(k) for k in ("ZoomX", "ZoomY", "Pan", "Tilt")} for x in items(new, "video", 4)]
    t = fusion_transform(items(new, "video", 3)[0])
    res["focus_fusion"] = {k: t.GetInput(k) for k in ("Size", "Pivot", "Center", "Edges")}
    off = []
    for n in range(1, new.GetTrackCount("video") + 1):
        for x in items(new, "video", n):
            m = x.GetMediaPoolItem()
            if m is not None and str(m.GetClipProperty("Online Status") or "Online").lower().startswith("off"):
                off.append(x.GetName())
    res["offline"] = off
    res["ok"] = (not res["original_vs_baseline_diffs"] and res["subtitles_equal"] and res["audio_equal"] and res["v1_equal"]
                 and po["range"] == pn["range"] and float(po["fps"]) == float(pn["fps"]) and res["settings_ok"]
                 and res["focus_equal"] and res["gif_equal"] and res["v2_equal_v1_range"] and not off
                 and res["tracks"] == {"video": 4, "audio": 3, "subtitle": 1})
    srt = []
    for i, (txt, s, e) in enumerate(po["sub"], 1):
        srt.append(f"{i}\n{srt_time(s)} --> {srt_time(e)}\n{txt}\n")
    (OUT / "cues_from_timeline.srt").write_text("\n".join(srt), encoding="utf-8")
    (OUT / "verify.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1, default=str))
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
