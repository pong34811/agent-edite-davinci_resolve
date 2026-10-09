"""Set the Transform on ONE existing focus clip and render one QC frame.

MCP-GAP: live MCP tools absent this session; native scripting API via
resolve_common.

Usage:
  python -m scripts.focus_tune --ordinal 2 --size 1.8 --cx 1.10 --cy 0.17 \
      --label s18_cy017 [--frames 1|3] [--tag run1]

Writes a distinct output dir per (ordinal, label) so candidates never
overwrite each other. Restores render preset, active timeline, timecode and
page. Protected tracks are verified against the saved baseline before and
after the transform change.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

from scripts.resolve_common import connect_resolve

PROJECT = "aomimama-2026-09-p1"
ART = Path(".hermes/artifacts/vtuber-focus-review-2026-10-07").resolve()
SDD = Path(".superpowers/sdd/2026-10-07_095727-vtuber-adjustment-focus").resolve()


def require(value, message):
    if not value:
        raise RuntimeError(message)


def activate(project, timeline):
    project.SetCurrentTimeline(timeline)
    time.sleep(1.25)
    require(project.GetCurrentTimeline().GetUniqueId() == timeline.GetUniqueId(),
            "wrong active timeline")


def protected(timeline, baseline):
    for track in baseline["tracks"]:
        items = timeline.GetItemListInTrack(track["kind"], track["index"]) or []
        actual = [(x.GetName(), x.GetStart(), x.GetEnd()) for x in items]
        expected = [(x["name"], x["start"], x["end"]) for x in track["items"]]
        require(actual == expected,
                f"protected drift: {track['kind']} {track['index']}")


def timecode(frame, fps):
    require(fps == 60, "timecode helper verified only for 60fps")
    seconds, f = divmod(frame, 60)
    h, seconds = divmod(seconds, 3600)
    m, s = divmod(seconds, 60)
    return f"{h:02d}:{m:02d}:{s:02d}:{f:02d}"


def transform_of(item):
    """Highest-index comp: on an inserted Adjustment Clip the render comes
    from the LAST comp, not index 1 (see focus_apply_batch.active_comp)."""
    comp = item.GetFusionCompByIndex(item.GetFusionCompCount())
    ts = [t for t in comp.GetToolList().values()
          if t.GetAttrs().get("TOOLS_RegID") == "Transform"]
    require(len(ts) == 1, "ambiguous Transform")
    return ts[0]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ordinal", type=int, required=True)
    ap.add_argument("--size", type=float, required=True)
    ap.add_argument("--cx", type=float, required=True)
    ap.add_argument("--cy", type=float, required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--px", type=float, default=None, help="Pivot x (zoom anchor)")
    ap.add_argument("--py", type=float, default=None, help="Pivot y (zoom anchor)")
    ap.add_argument("--edges", type=float, default=0.0,
                    help="Fusion Edges: 0=Canvas 1=Wrap 2=Duplicate 3=Mirror")
    ap.add_argument("--frames", type=int, default=1)
    ap.add_argument("--tag", default="tune")
    a = ap.parse_args()

    n = a.ordinal
    plan = json.loads((SDD / "plan-batch.json").read_text(encoding="utf-8"))
    row = next(t for t in plan["targets"] if t["ordinal"] == n)
    s, e = row["cue"]
    want = {"Size": a.size, "Edges": a.edges,
            "Center": {1: a.cx, 2: a.cy, 3: 0.0}}
    pivot = None
    if a.px is not None and a.py is not None:
        pivot = {1: a.px, 2: a.py, 3: 0.0}

    r = connect_resolve()
    require(r is not None, "Resolve unavailable")
    pm = r.GetProjectManager()
    entry = pm.GetCurrentProject()
    entry_name = entry.GetName()
    entry_tl_name = entry.GetCurrentTimeline().GetName()
    entry_tc = entry.GetCurrentTimeline().GetCurrentTimecode()
    entry_page = r.GetCurrentPage()
    project = entry if entry_name == PROJECT else pm.LoadProject(PROJECT)
    require(project is not None and not project.IsRenderingInProgress(),
            "target unavailable/busy")

    out = ART / "focus-tune" / a.tag / f"T{n:02d}-{a.label}"
    out.mkdir(parents=True, exist_ok=False)
    preset = f"Hermes-focus-tune-{a.tag}-{n:02d}-{a.label}-{int(time.time())}"
    preserved = False
    record = {"ordinal": n, "label": a.label, "size": a.size,
              "center": {"1": a.cx, "2": a.cy, "3": 0.0},
              "cue": [s, e], "out": str(out)}
    try:
        require("SetRenderSettings" in dir(project), "render API missing")
        require(project.SaveAsNewRenderPreset(preset), "preset save failed")
        preserved = True
        tl = [project.GetTimelineByIndex(i)
              for i in range(1, project.GetTimelineCount() + 1)
              if project.GetTimelineByIndex(i).GetUniqueId() == row["timeline_id"]]
        require(len(tl) == 1, "timeline identity changed")
        timeline = tl[0]
        activate(project, timeline)
        baseline = json.loads((ART / f"timeline-{n:02d}.json").read_text(encoding="utf-8"))
        protected(timeline, baseline)
        items = timeline.GetItemListInTrack("video", row.get("track", 3)) or []
        require(len(items) == 1, f"focus track holds {len(items)} items")
        clip = items[0]
        require(int(clip.GetStart()) == s and int(clip.GetEnd()) == e,
                "focus range drift")
        node = transform_of(clip)
        for k, v in want.items():
            node.SetInput(k, v)
        if pivot is not None:
            node.SetInput("Pivot", pivot)
        time.sleep(1.25)
        record["readback"] = {k: node.GetInput(k) for k in ("Size", "Center", "Edges")}
        record["readback"]["Pivot"] = node.GetInput("Pivot")
        require(record["readback"]["Size"] == a.size, "Size readback mismatch")
        require(float(record["readback"]["Center"][1]) == a.cx
                and float(record["readback"]["Center"][2]) == a.cy,
                "Center readback mismatch")
        require(pm.SaveProject(), "save failed")

        # Resolve caches the Fusion output: step the playhead off and back so the
        # render picks up the new graph. Without this the render returns the
        # pre-change pixels and an identical byte count hides it.
        mid = s + (e - s) // 2
        timeline.SetCurrentTimecode(timecode(mid, 60))
        time.sleep(0.4)
        timeline.SetCurrentTimecode(timecode(max(s, mid - 2), 60))
        time.sleep(0.4)
        timeline.SetCurrentTimecode(timecode(mid, 60))
        time.sleep(0.6)

        require(project.LoadRenderPreset("H.264 Master"), "base preset failed")
        require(project.SetCurrentRenderFormatAndCodec("mp4", "H264_NVIDIA"), "codec failed")
        require(project.SetCurrentRenderMode(1), "render mode failed")
        require(project.SetRenderSettings({
            "TargetDir": str(out), "CustomName": f"T{n:02d}-{a.label}",
            "SelectAllFrames": False, "ExportVideo": True, "ExportAudio": False,
            "FormatWidth": 1280, "FormatHeight": 720, "FrameRate": 60.0,
            "MarkIn": s, "MarkOut": e - 1,
            "ExportSubtitle": True, "SubtitleFormat": "BurnIn"}), "settings rejected")
        job = project.AddRenderJob()
        require(job and project.StartRendering([job], False), "render start failed")
        deadline = time.monotonic() + 300
        while project.IsRenderingInProgress():
            require(time.monotonic() < deadline, "render timeout")
            time.sleep(1)
        status = project.GetRenderJobStatus(job)
        require(status.get("JobStatus") == "Complete", str(status))
        video = out / f"T{n:02d}-{a.label}.mp4"
        require(video.is_file() and video.stat().st_size > 0, "missing video")
        span = e - s
        idxs = {"mid": [span // 2]} if a.frames == 1 else {
            "start": [0], "mid": [span // 2], "end": [span - 1]}
        record["frames"] = []
        for label, group in idxs.items():
            for i in group:
                image = out / f"{label}.jpg"
                subprocess.run(["ffmpeg", "-y", "-i", str(video), "-vf",
                                f"select=eq(n\\,{i})", "-frames:v", "1", str(image),
                                "-hide_banner", "-loglevel", "error"], check=True)
                record["frames"].append({"label": label, "frame": s + i,
                                         "path": str(image)})
        protected(timeline, baseline)
        record["protected_ok"] = True
    finally:
        if preserved:
            record["preset_restored"] = bool(project.LoadRenderPreset(preset))
        original = (pm.GetCurrentProject() if entry_name == PROJECT
                    else pm.LoadProject(entry_name))
        if original is not None:
            cands = [original.GetTimelineByIndex(i)
                     for i in range(1, original.GetTimelineCount() + 1)
                     if original.GetTimelineByIndex(i).GetName() == entry_tl_name]
            if cands:
                activate(original, cands[0])
                cands[0].SetCurrentTimecode(entry_tc)
                time.sleep(0.4)
            r.OpenPage(entry_page)
        (out / "tune.json").write_text(
            json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ordinal": n, "label": a.label, "readback": record.get("readback"),
                      "frames": record.get("frames")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
