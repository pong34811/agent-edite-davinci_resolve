"""Render single frames of a named timeline as PNG with burned-in subtitles (no ffmpeg needed).

Native still export can omit subtitles; this renders one-frame jobs instead.

Usage: python -m scripts.render_subtitle_stills --suffix _focus_variant --frames 1650,3650 --out <dir>
Restores the entry timeline/playhead and the render preset it found; deletes the jobs it added. Timeline is not modified.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.focus_apply_batch import activate, check  # noqa: E402
from scripts.resolve_common import connect_resolve  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--suffix", required=True, help="timeline name suffix to render")
    ap.add_argument("--frames", required=True, help="comma-separated record frames")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    frames = [int(x) for x in a.frames.split(",")]
    r = connect_resolve()
    project = r.GetProjectManager().GetCurrentProject()
    check(not project.IsRenderingInProgress(), "render busy")
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    entry = project.GetCurrentTimeline()
    entry_id, entry_tc = entry.GetUniqueId(), entry.GetCurrentTimecode()
    tl = next(project.GetTimelineByIndex(i) for i in range(1, project.GetTimelineCount() + 1)
              if project.GetTimelineByIndex(i).GetName().endswith(a.suffix))
    preset = f"subtitle-stills-{int(time.time())}"
    check(project.SaveAsNewRenderPreset(preset), "preset save failed")
    jobs = []
    try:
        activate(project, tl)
        check(project.SetCurrentRenderFormatAndCodec("png", "RGB8"), "png format rejected")
        check(project.SetCurrentRenderMode(1), "render mode failed")
        for f in frames:
            check(project.SetRenderSettings({
                "TargetDir": str(out), "CustomName": f"sub{f}", "SelectAllFrames": False,
                "ExportVideo": True, "ExportAudio": False, "MarkIn": f, "MarkOut": f,
                "ExportSubtitle": True, "SubtitleFormat": "BurnIn"}), f"settings rejected {f}")
            job = project.AddRenderJob()
            check(job, f"add job failed {f}")
            jobs.append(job)
        check(project.StartRendering(jobs, False), "render start refused")
        deadline = time.monotonic() + 300
        while project.IsRenderingInProgress():
            check(time.monotonic() < deadline, "render timeout")
            time.sleep(1)
        for job in jobs:
            status = project.GetRenderJobStatus(job)
            check(status.get("JobStatus") == "Complete", str(status))
        print("OK", sorted(p.name for p in out.rglob("*.png")))
    finally:
        for job in jobs:
            project.DeleteRenderJob(job)
        print("preset_restored", bool(project.LoadRenderPreset(preset)))
        back = next(project.GetTimelineByIndex(i) for i in range(1, project.GetTimelineCount() + 1)
                    if project.GetTimelineByIndex(i).GetUniqueId() == entry_id)
        activate(project, back)
        back.SetCurrentTimecode(entry_tc)
        print("jobs_left", len(project.GetRenderJobList() or []))


if __name__ == "__main__":
    main()
