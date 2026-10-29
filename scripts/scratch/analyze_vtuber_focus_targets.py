"""Read-only inventory of all project timelines and subtitle-led focus candidates."""
from __future__ import annotations
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from resolve_common import connect_resolve

def main():
    r = connect_resolve()
    if not r:
        print("Resolve unavailable", file=sys.stderr)
        return 1
    p = r.GetProjectManager().GetCurrentProject()
    out = {"project": p.GetName(), "timelines": []}
    for i in range(1, p.GetTimelineCount() + 1):
        tl = p.GetTimelineByIndex(i)
        fps = float(tl.GetSetting("timelineFrameRate") or 30)
        cues = []
        for st in range(1, (tl.GetTrackCount("subtitle") or 0) + 1):
            for item in tl.GetItemListInTrack("subtitle", st) or []:
                cues.append({"start": item.GetStart(), "end": item.GetEnd(), "text": item.GetName()})
        out["timelines"].append({
            "index": i, "name": tl.GetName(), "id": tl.GetUniqueId(),
            "fps": fps, "duration_frames": tl.GetEndFrame() - tl.GetStartFrame(),
            "subtitles": len(cues), "cues": cues[:5]  # sample
        })
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
