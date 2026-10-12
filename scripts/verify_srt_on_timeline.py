"""Read-only: compare a subtitle track's cues to an SRT (text + absolute frames)."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from resolve_common import require_resolve
from caption_lint import parse_srt


def main(srt, track=1):
    resolve = require_resolve()
    tl = resolve.GetProjectManager().GetCurrentProject().GetCurrentTimeline()
    fps = float(tl.GetSetting("timelineFrameRate"))
    origin = tl.GetStartFrame()
    items = tl.GetItemListInTrack("subtitle", track)
    cues = list(parse_srt(Path(srt).read_text(encoding="utf-8-sig")))
    bad = 0
    if len(items) != len(cues):
        print("COUNT MISMATCH", len(items), len(cues)); bad += 1
    prev_end = -1
    for n, (it, (_, s, e, t)) in enumerate(zip(items, cues), 1):
        es, ee = int(s * fps + 0.5) + origin, int(e * fps + 0.5) + origin
        gs, ge = it.GetStart(), it.GetEnd()
        name = it.GetName()
        if abs(gs - es) > 1 or abs(ge - ee) > 1 or name.strip() != t.strip() or gs < prev_end:
            bad += 1; print("cue", n, (gs, ge), (es, ee), repr(name), repr(t))
        prev_end = ge
    print("items=%d cues=%d fps=%s origin=%d mismatches=%d last_end=%d" % (len(items), len(cues), fps, origin, bad, prev_end))
    for kind in ("video", "audio"):
        for it in tl.GetItemListInTrack(kind, 1):
            print(kind, it.GetName(), it.GetStart(), it.GetEnd())
    return bad

if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1]) else 0)
