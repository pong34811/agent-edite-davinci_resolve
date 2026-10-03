"""M4: final read-only audit of all 30 originals vs their _9x16 (live Resolve).
Checks: originals match M1 baseline; each _9x16 exists exactly once, 1080x1920, same fps/range, 4 video tracks,
subs/audio/V1/V3/GIF ranges identical, no offline, V1/V2 transforms equal the layout for its source, V3 Fusion focus values,
no extra/orphan timelines. Writes scratch/m4_audit.json. No Resolve writes."""
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import compare_invariants as ci  # noqa: E402
import layout9x16 as L  # noqa: E402
import m2_convert_pilot as m2  # noqa: E402
import m3_convert as m3  # noqa: E402


def main():
    resolve = m2.get_resolve()
    proj = resolve.GetProjectManager().GetCurrentProject()
    entry = proj.GetCurrentTimeline()
    entry_id, entry_tc, entry_page = entry.GetUniqueId(), entry.GetCurrentTimecode(), resolve.GetCurrentPage()
    base = json.load(open(m2.BASELINE_JSON_PATH, encoding="utf-8"))
    base_by_id = {t["timeline_id"]: t for t in base["timelines"]}
    summ = {s["id"]: s for s in base["timelines_summary"]}
    all_tl = [proj.GetTimelineByIndex(i) for i in range(1, proj.GetTimelineCount() + 1)]
    names = [t.GetName() for t in all_tl]
    out = {"timeline_count": len(all_tl), "rows": [], "problems": []}
    originals = [t for t in all_tl if not t.GetName().endswith("_9x16")]
    if len(originals) != 30:
        out["problems"].append(f"expected 30 originals, found {len(originals)}")
    for o in originals:
        b = base_by_id.get(o.GetUniqueId())
        row = {"name": o.GetName(), "id": o.GetUniqueId()}
        if not b:
            out["problems"].append(f"original not in baseline: {o.GetName()}")
            continue
        row["orig_matches_baseline"] = (
            int(o.GetSetting("timelineResolutionWidth")) == b["resolution_width"]
            and int(o.GetSetting("timelineResolutionHeight")) == b["resolution_height"]
            and (o.GetStartFrame(), o.GetEndFrame()) == (b["start_frame"], b["end_frame"])
            and len(ci.sub_sig(o)) == summ[o.GetUniqueId()]["subtitle_cues"]
            and o.GetTrackCount("video") == 3 and o.GetTrackCount("audio") == summ[o.GetUniqueId()]["audio_tracks"])
        matches = [t for t in all_tl if t.GetName() == o.GetName() + "_9x16"]
        row["n_9x16"] = len(matches)
        if len(matches) != 1:
            out["problems"].append(f"{o.GetName()}: {len(matches)} _9x16 timelines")
            out["rows"].append(row)
            continue
        n = matches[0]
        res = m3.verify(o, n, m3.snapshot_original(o), m3.gif_infos(o))
        row["verify_ok"] = res["ok"]
        row["fps_equal"] = float(o.GetSetting("timelineFrameRate")) == float(n.GetSetting("timelineFrameRate"))
        row["subs"] = res["subs"][1]
        # transform audit on V1/V2/V4 and focus. Item-property readback is scaled by the PROJECT raster
        # unless the timeline is active (Pan x16/9, Tilt x9/16 on an inactive 1080x1920 timeline), so activate first.
        m3.activate(proj, n)
        v1 = ci.items(n, "video", 1)[0]
        spec = L.avatar_spec_for(ci.items(o, "video", 1)[0].GetName())
        g, a = L.game_params(), L.avatar_params(*spec)
        v2 = ci.items(n, "video", 2)[0]

        def close(item, want):
            return all(abs(float(m2.get_item_property(item, k)) - float(w)) < 0.5 if k in ("Pan", "Tilt", "CropTop", "CropBottom")
                       else abs(float(m2.get_item_property(item, k)) - float(w)) < 0.01 for k, w in want.items())
        row["v1_transform"] = close(v1, g)
        row["v2_transform"] = close(v2, a)
        gifs_ok = True
        for it in ci.items(n, "video", 4):
            mpi = it.GetMediaPoolItem()
            w, h = (int(x) for x in mpi.GetClipProperty("Resolution").split("x"))
            gifs_ok &= close(it, L.gif_params(w, h))
        row["v4_transform"] = gifs_ok
        foc = True
        for adj in ci.items(n, "video", 3):
            t = m3.fusion_transform(adj)
            foc &= bool(t) and abs(float(t.GetInput("Size")) - L.FOCUS["Size"]) < 0.01 and abs(t.GetInput("Center")[2] - 0.5) < 0.01 and abs(t.GetInput("Pivot")[2] - 0.25) < 0.01
        row["v3_focus"] = foc
        row["n_v3"] = len(ci.items(n, "video", 3))
        row["n_gif"] = len(ci.items(n, "video", 4))
        row["pass"] = all([row["orig_matches_baseline"], res["ok"], row["fps_equal"], row["v1_transform"], row["v2_transform"], row["v4_transform"], row["v3_focus"]])
        if not row["pass"]:
            out["problems"].append(f"{o.GetName()}: audit failed {row}")
        out["rows"].append(row)
    extra = [nm for nm in names if nm.endswith("_9x16") and nm[:-5] not in {o.GetName() for o in originals}]
    if extra:
        out["problems"].append(f"orphan _9x16 timelines: {extra}")
    out["passed"] = sum(1 for r in out["rows"] if r.get("pass"))
    for t in all_tl:
        if t.GetUniqueId() == entry_id:
            m3.activate(proj, t)
            t.SetCurrentTimecode(entry_tc)
            import time as _t
            _t.sleep(0.5)
            out["restored"] = [t.GetName(), t.GetCurrentTimecode(), resolve.GetCurrentPage(), entry_page]
    json.dump(out, open("scratch/m4_audit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print("restored:", out.get("restored"))
    print("timelines:", out["timeline_count"], "| passed:", out["passed"], "/", len(originals), "| problems:", len(out["problems"]))
    for p in out["problems"]:
        print("  PROBLEM:", p[:300])


if __name__ == "__main__":
    main()
