"""Read-only verification of the p2 caption fix (agent 5). No Resolve writes, no timeline switching."""
from __future__ import annotations
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.resolve_common import connect_resolve, preserved_state  # noqa: E402
from scripts.p2_apply_fixed_captions import parse, cues  # noqa: E402

THAI = re.compile(r"[฀-๿]")
D = json.loads((ROOT / "exports/publish-qc/data.json").read_text(encoding="utf-8"))
OUT = ROOT / "exports/work/agent5_data.json"


def trk(tl, kind):
    return [[(x.GetName(), x.GetStart(), x.GetEnd()) for x in sorted(tl.GetItemListInTrack(kind, n) or [], key=lambda i: i.GetStart())]
            for n in range(1, tl.GetTrackCount(kind) + 1)]


def rules(cs, fps):
    ex = []
    prev = None
    for t, s, e in cs:
        if len(THAI.findall(t)) > 14: ex.append(["chars>14", s, t, len(THAI.findall(t))])
        if (e - s) / fps > 1.5 + 0.05: ex.append(["sec>1.5", s, t, round((e - s) / fps, 3)])
        if prev is not None and s < prev: ex.append(["overlap", s, t])
        prev = e
    return ex


def main():
    r = connect_resolve()
    pm = r.GetProjectManager()
    p = pm.GetCurrentProject()
    assert p.GetName() == "aomimama-2026-09-p2", p.GetName()
    res = {"project": p.GetName(), "rows": []}
    with preserved_state(r):
        tls = {i: p.GetTimelineByIndex(i) for i in range(1, 89)}
        for i in range(1, 89):
            tl = tls[i]; row = D[i - 1]
            assert tl.GetName() == row["name"], (i, tl.GetName())
            fps = float(tl.GetSetting("timelineFrameRate"))
            ent = {"i": i, "name": tl.GetName(), "fps": fps, "sub_tracks": tl.GetTrackCount("subtitle"),
                   "sub_locked": bool(tl.GetIsTrackLocked("subtitle", 1))}
            live = cues(tl)
            ent["live_n"] = len(live)
            if i <= 44:
                ent["subs_equal_data"] = live == [tuple(c) for c in row["subs"]["cues"]]
            else:
                srt = parse(ROOT / f"exports/captions-fixed/{i}.srt", fps)
                ent["srt_n"] = len(srt)
                ent["subs_equal_srt"] = live == srt
                ent["old_n"] = row["subs"]["count"]
                ent["old_issues"] = len(row["subs"]["issues"])
                ent["rule_exceptions"] = rules(live, fps)
                ent["old_rule_exceptions"] = len(rules([tuple(c) for c in row["subs"]["cues"]], fps))
                # video/audio vs data.json (pre-change snapshot of the same timeline)
                v = trk(tl, "video"); a = trk(tl, "audio")
                dv = [[(x["name"], x["s"], x["e"]) for x in t["items"]] for t in row["video"]]
                ent["video_equal_data"] = [sorted(t, key=lambda z: z[1]) for t in v] == [sorted(t, key=lambda z: z[1]) for t in dv]
                ent["audio_summary_equal_data"] = all(
                    len(x) == t["n"] and sum(e - s for _, s, e in x) == t["covered"] and sorted({n for n, _, _ in x})[:3] == t["names"]
                    for x, t in zip(a, row["audio"])) and len(a) == len(row["audio"])
                hn = [k for k in range(1, 45) if tls[k].GetName() + '_9x16' == tl.GetName()]
                ent['pair'] = hn
                h = tls[hn[0]]
                hv, ha = trk(h, "video"), trk(h, "audio")
                ent["V1_equal_horizontal"] = v[0] == hv[0]
                ent["audio_equal_horizontal"] = a == ha
                ent["video_tracks"] = len(v); ent["audio_tracks"] = len(a)
            res["rows"].append(ent)
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print("written", OUT)


main()
