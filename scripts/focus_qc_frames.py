"""Render a short range of the ACTIVE timeline with burned-in subtitles and extract QC frames.

MCP-GAP: davinci-resolve timeline_frame.capture -> RENDER_START_FAILED
(StartRendering refused) on p2 Resolve 21.1.0.17, so render through the scripting API.

Usage:
  python -m scripts.focus_qc_frames --start 1995 --end 2272 --out <dir> --name pilot [--frames 3]
Restores the render preset it found. Read-only for the timeline.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.resolve_common import connect_resolve  # noqa: E402


def require(value, message):
    if not value:
        raise RuntimeError(message)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--start", type=int, required=True)
    ap.add_argument("--end", type=int, required=True, help="exclusive end frame")
    ap.add_argument("--out", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--frames", type=int, default=3)
    ap.add_argument("--width", type=int, default=1280, help="render width (1080 for a 9:16 timeline)")
    ap.add_argument("--height", type=int, default=720, help="render height (1920 for a 9:16 timeline)")
    a = ap.parse_args()

    r = connect_resolve()
    require(r is not None, "Resolve unavailable")
    project = r.GetProjectManager().GetCurrentProject()
    require(not project.IsRenderingInProgress(), "render busy")
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    preset = f"focus-qc-{int(time.time())}"
    require(project.SaveAsNewRenderPreset(preset), "preset save failed")
    try:
        require(project.LoadRenderPreset("H.264 Master"), "base preset failed")
        require(project.SetCurrentRenderFormatAndCodec("mp4", "H264_NVIDIA"), "codec failed")
        require(project.SetCurrentRenderMode(1), "render mode failed")
        require(project.SetRenderSettings({
            "TargetDir": str(out), "CustomName": a.name,
            "SelectAllFrames": False, "ExportVideo": True, "ExportAudio": False,
            "FormatWidth": a.width, "FormatHeight": a.height, "FrameRate": 60.0,
            "MarkIn": a.start, "MarkOut": a.end - 1,
            "ExportSubtitle": True, "SubtitleFormat": "BurnIn"}), "settings rejected")
        job = project.AddRenderJob()
        require(job and project.StartRendering([job], False), "render start refused")
        deadline = time.monotonic() + 300
        while project.IsRenderingInProgress():
            require(time.monotonic() < deadline, "render timeout")
            time.sleep(1)
        status = project.GetRenderJobStatus(job)
        require(status.get("JobStatus") == "Complete", str(status))
        video = out / f"{a.name}.mp4"
        require(video.is_file() and video.stat().st_size > 0, "missing video")
        span = a.end - a.start
        picks = [0, span // 2, span - 1] if a.frames == 3 else [span // 2]
        for label, i in zip(("start", "mid", "end"), picks):
            subprocess.run(["ffmpeg", "-y", "-i", str(video), "-vf", f"select=eq(n\\,{i})",
                            "-frames:v", "1", str(out / f"{a.name}-{label}.jpg"),
                            "-hide_banner", "-loglevel", "error"], check=True)
        project.DeleteRenderJob(job) if "DeleteRenderJob" in dir(project) else None
        print("OK", video, video.stat().st_size)
    finally:
        print("preset_restored", bool(project.LoadRenderPreset(preset)))


if __name__ == "__main__":
    main()
