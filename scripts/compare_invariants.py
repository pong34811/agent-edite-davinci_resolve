"""Read-only invariant comparison: a _9x16 timeline vs its live 16:9 original.

Compares subtitle cues (text + absolute start/end), audio items (name/range/volume),
V1 item ranges, duration, FPS, and flags offline media. No writes.
usage: python scripts/compare_invariants.py <original_name> [<new_name>]
"""
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import m2_convert_pilot as m2  # noqa: E402


def items(tl, kind, n):
    return tl.GetItemListInTrack(kind, n) or []


def sub_sig(tl):
    out = []
    for n in range(1, tl.GetTrackCount("subtitle") + 1):
        for it in items(tl, "subtitle", n):
            out.append((n, it.GetStart(), it.GetEnd(), it.GetName()))
    return out


def audio_sig(tl):
    out = []
    for n in range(1, tl.GetTrackCount("audio") + 1):
        for it in items(tl, "audio", n):
            out.append((n, it.GetStart(), it.GetEnd(), it.GetName(), m2.get_item_property(it, "AudioVolume") or m2.get_item_property(it, "Volume")))
    return out


def v1_sig(tl):
    return [(it.GetStart(), it.GetEnd(), it.GetSourceStartFrame(), it.GetSourceEndFrame(), it.GetName()) for it in items(tl, "video", 1)]


def offline(tl):
    bad = []
    for n in range(1, tl.GetTrackCount("video") + 1):
        for it in items(tl, "video", n):
            if it.GetName() == "Adjustment Clip":
                continue
            mpi = it.GetMediaPoolItem()
            if mpi is None:
                bad.append((n, it.GetName(), "no pool item"))
            elif (mpi.GetClipProperty("Offline") or mpi.GetClipProperty("Clip Color")) in (True, "Offline"):
                bad.append((n, it.GetName(), "offline"))
    return bad


def main():
    on = sys.argv[1]
    nn = sys.argv[2] if len(sys.argv) > 2 else on + "_9x16"
    resolve = m2.get_resolve()
    proj = resolve.GetProjectManager().GetCurrentProject()
    o, n = m2.find_timeline_by_name(proj, on), m2.find_timeline_by_name(proj, nn)
    assert o and n, "timeline missing"
    res = {
        "fps": (o.GetSetting("timelineFrameRate"), n.GetSetting("timelineFrameRate")),
        "raster_new": (n.GetSetting("timelineResolutionWidth"), n.GetSetting("timelineResolutionHeight")),
        "range": ((o.GetStartFrame(), o.GetEndFrame()), (n.GetStartFrame(), n.GetEndFrame())),
        "subs_equal": sub_sig(o) == sub_sig(n),
        "subs_count": (len(sub_sig(o)), len(sub_sig(n))),
        "audio_equal": audio_sig(o) == audio_sig(n),
        "audio_count": (len(audio_sig(o)), len(audio_sig(n))),
        "v1_ranges_equal": v1_sig(o) == v1_sig(n),
        "offline_new": offline(n),
        "v3_equal_ranges": [(i.GetStart(), i.GetEnd()) for i in items(o, "video", 3)] == [(i.GetStart(), i.GetEnd()) for i in items(n, "video", 3) if True],
    }
    if not res["audio_equal"]:
        a, b = audio_sig(o), audio_sig(n)
        res["audio_diff_first"] = [(x, y) for x, y in zip(a, b) if x != y][:3]
    if not res["subs_equal"]:
        a, b = sub_sig(o), sub_sig(n)
        res["subs_diff_first"] = [(x, y) for x, y in zip(a, b) if x != y][:3]
    print(json.dumps(res, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
