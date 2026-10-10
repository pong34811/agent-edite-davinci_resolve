"""Render every p2 horizontal (1920x1080, non-_9x16) timeline with burned-in subtitles; one job per timeline, started by id.

MCP-GAP: render.add_job/start work one timeline per call (44 x set_current + set_settings + add_job); a batch needs
a loop. Starts ONLY the jobs it creates (the project queue still holds ~50 old QC jobs that must not run).
Output: exports/render-final-h/raw/<NN>_<name>.mp4 ; exports/render-final-h/done.jsonl gets one line per completed job
(read by scripts/p2_loudnorm_worker_h.py). Run from repo root: python -m scripts.p2_render_horizontal [--limit N]
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

OUT = ROOT / "exports" / "render-final-h"
RAW = OUT / "raw"
PROJECT = "aomimama-2026-09-p2"


def safe(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', "", name).strip()


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    RAW.mkdir(parents=True, exist_ok=True)
    r = connect_resolve()
    pm = r.GetProjectManager()
    p = pm.GetCurrentProject()
    assert p is not None and p.GetName() == PROJECT, "wrong project"
    jobs = []
    with preserved_state(r):
        assert p.SetCurrentRenderFormatAndCodec("mp4", "H264"), "format/codec"
        n = 0
        for i in range(1, p.GetTimelineCount() + 1):
            tl = p.GetTimelineByIndex(i)
            name = tl.GetName()
            if name.endswith("_9x16") or "archived" in name:
                continue
            n += 1
            if limit and n > limit:
                break
            p.SetCurrentTimeline(tl)
            time.sleep(1.3)
            assert p.GetCurrentTimeline().GetUniqueId() == tl.GetUniqueId(), "activate failed"
            custom = f"{n:02d}_{safe(name)}"
            ok = p.SetRenderSettings({
                "SelectAllFrames": True, "TargetDir": str(RAW), "CustomName": custom, "ExportVideo": True,
                "ExportAudio": True, "FormatWidth": 1920, "FormatHeight": 1080, "FrameRate": 60,
                "AudioCodec": "aac", "AudioBitDepth": 16, "AudioSampleRate": 48000,
                "ExportSubtitle": True, "SubtitleFormat": "BurnIn"})
            assert ok, f"SetRenderSettings failed for {name}"
            jid = p.AddRenderJob()
            assert jid, f"AddRenderJob failed for {name}"
            jobs.append({"n": n, "index": i, "name": name, "id": tl.GetUniqueId(), "job": jid,
                         "file": str(RAW / f"{custom}.mp4"), "dur_frames": tl.GetEndFrame() - tl.GetStartFrame()})
            print("JOB", n, i, jid, flush=True)
            time.sleep(0.5)
    assert limit or len(jobs) == 44, f"expected 44 horizontal timelines, got {len(jobs)} (jobs queued, not started)"
    (OUT / "jobs.json").write_text(json.dumps(jobs, ensure_ascii=False, indent=1), encoding="utf-8")
    ids = [j["job"] for j in jobs]
    assert p.StartRendering(ids), "StartRendering failed"
    pending = {j["job"]: j for j in jobs}
    done_path = OUT / "done.jsonl"
    done_path.write_text("", encoding="utf-8")
    while pending:
        time.sleep(6)
        for jid in list(pending):
            st = p.GetRenderJobStatus(jid) or {}
            s = st.get("JobStatus")
            if s in ("Complete", "Failed", "Cancelled"):
                j = pending.pop(jid)
                j["status"] = s
                j["ms"] = st.get("TimeTakenToRenderInMs")
                with done_path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(j, ensure_ascii=False) + "\n")
                print("DONE", j["n"], s, j["ms"], flush=True)
    print("ALL DONE", len(jobs), flush=True)


if __name__ == "__main__":
    main()
