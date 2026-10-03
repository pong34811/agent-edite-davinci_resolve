"""Milestone 3 converter: 16:9 timeline -> `<name>_9x16` (1080x1920 split screen), one timeline per call.

Per timeline: DuplicateTimeline -> raster 1080x1920 -> V4 gets the reaction GIFs (exact original record
range + source range) -> V2 gets the game clip again (VTuber panel) -> transforms from layout9x16 ->
V3 adjustment-clip Fusion Transform focus. Subtitles/audio/V1/V3 ranges are never touched.

Usage:
  python scripts/m3_convert.py 2 3 4          # original timeline indexes (1-based, list order)
  python scripts/m3_convert.py --fix-pilot-gif  # repair pilot V4 GIF range only
Stops at the first failing timeline. Writes scratch/m3/<idx>/*.png QC stills + scratch/m3/results.json.
"""
import json
import os
import sys
import time

import numpy as np
from PIL import Image

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import layout9x16 as L  # noqa: E402
import m2_convert_pilot as m2  # noqa: E402

DELAY = 1.2
PROP_CHECK = ["ZoomX", "ZoomY", "Pan", "Tilt", "CropTop", "CropBottom"]
OUT_DIR = os.path.abspath("scratch/m3")


def items(tl, kind, n):
    return tl.GetItemListInTrack(kind, n) or []


def find_by_id(proj, tid):
    for i in range(1, proj.GetTimelineCount() + 1):
        t = proj.GetTimelineByIndex(i)
        if t.GetUniqueId() == tid:
            return t
    return None


def activate(proj, tl):
    proj.SetCurrentTimeline(tl)
    time.sleep(DELAY)
    assert proj.GetCurrentTimeline().GetUniqueId() == tl.GetUniqueId(), "activate failed"


def set_props(item, props, tries=3):
    for k, v in props.items():
        for _ in range(tries):
            item.SetProperty(k, float(v))
            time.sleep(0.2)
            rb = m2.get_item_property(item, k)
            if rb is not None and abs(float(rb) - float(v)) < 0.5 if k in ("Pan", "Tilt", "CropTop", "CropBottom") else (rb is not None and abs(float(rb) - float(v)) < 0.01):
                break
            time.sleep(0.8)
        else:
            raise RuntimeError(f"property {k} did not stick: want {v}, got {rb}")


def fusion_transform(adj):
    comp = adj.GetFusionCompByIndex(1)
    if not comp:
        return None
    for t in (comp.GetToolList() or {}).values():
        if "Transform" in t.GetAttrs().get("TOOLS_Name", ""):
            return t
    return None


def snapshot_original(tl):
    snap = {"v1": [], "v2": [], "v3": []}
    for key, n in (("v1", 1), ("v2", 2), ("v3", 3)):
        for it in items(tl, "video", n):
            d = {"id": it.GetUniqueId(), "s": it.GetStart(), "e": it.GetEnd(),
                 **{p: m2.get_item_property(it, p) for p in PROP_CHECK}}
            if key == "v3":
                t = fusion_transform(it)
                d["fusion"] = [t.GetInput("Size"), t.GetInput("Pivot"), t.GetInput("Center")] if t else None
            snap[key].append(d)
    return json.loads(json.dumps(snap, default=str))


def place_gifs(media_pool, new_tl, gifs):
    """gifs: list of dict(mpi, rec, src_s, src_e, name, res). Appends to V4 with exact ranges."""
    placed = []
    for g in gifs:
        # A GIF that plays through to its last source frame loses that frame when the inclusive
        # last index is passed (observed: 43-frame GIF came back 0..41); ask for one past the end.
        total = int(float(g["mpi"].GetClipProperty("Frames")))
        end = g["src_e"] + 1 if g["src_e"] >= total - 1 else g["src_e"]
        info = {"mediaPoolItem": g["mpi"], "startFrame": g["src_s"], "endFrame": end,
                "mediaType": 1, "trackIndex": 4, "recordFrame": g["rec"]}
        if not media_pool.AppendToTimeline([info]):
            raise RuntimeError(f"append GIF failed at {g['rec']}")
        time.sleep(DELAY)
    for it, g in zip(sorted(items(new_tl, "video", 4), key=lambda i: i.GetStart()), gifs):
        w, h = (int(x) for x in g["res"].split("x"))
        set_props(it, L.gif_params(w, h))
        placed.append((it.GetStart(), it.GetEnd()))
    return placed


def gif_infos(tl):
    out = []
    for it in sorted(items(tl, "video", 2), key=lambda i: i.GetStart()):
        mpi = it.GetMediaPoolItem()
        out.append(dict(mpi=mpi, rec=it.GetStart(), end=it.GetEnd(), src_s=it.GetSourceStartFrame(),
                        src_e=it.GetSourceEndFrame(), name=it.GetName(), res=mpi.GetClipProperty("Resolution")))
    return out


def export_stills(proj, tl, idx, fps):
    os.makedirs(os.path.join(OUT_DIR, str(idx)), exist_ok=True)
    start, end = tl.GetStartFrame(), tl.GetEndFrame()
    v3 = sorted(items(tl, "video", 3), key=lambda i: i.GetStart())
    v4 = sorted(items(tl, "video", 4), key=lambda i: i.GetStart())
    busy = [(i.GetStart() - 30, i.GetEnd() + 30) for i in v3 + v4]
    normal = next(f for f in range(start + 300, end, 60) if not any(a <= f <= b for a, b in busy))
    frames = [("normal", normal)]
    if v4:
        frames.append(("gif", (v4[0].GetStart() + v4[0].GetEnd()) // 2))
    if v3:
        frames.append(("focus", (v3[0].GetStart() + v3[0].GetEnd()) // 2))
    paths = {}
    for label, f in frames:
        tl.SetCurrentTimecode(m2.frame_to_timecode(f, fps))
        time.sleep(0.6)
        p = os.path.join(OUT_DIR, str(idx), f"{label}_{f}.png")
        ok = proj.ExportCurrentFrameAsStill(p)
        time.sleep(0.3)
        if not ok or not os.path.exists(p):
            raise RuntimeError(f"still export failed for {label}@{f}")
        paths[label] = p
    return paths


def pixel_check(path):
    a = np.array(Image.open(path).convert("RGB"))
    g = a.max(axis=2)
    # A real void is pure black across the whole row. Dark game scenes (night, boss arenas) are legitimate
    # content in the TOP panel, so they are reported (`top_dark_rows`) for eyeballing, not failed. The
    # avatar always covers rows 1300+ (eyes sit at y~1456), so a pure-black row there is a real geometry fault.
    dark = g.max(axis=1) < 16
    return {"size": list(Image.open(path).size), "dark_rows": int(dark.sum()),
            "top_dark_rows": int(dark[:960].sum()), "bottom_dark_rows": int(dark[1300:].sum())}  # rows 960-1300 = headroom above the avatar, may be dark game bg


def stills_pass(st):
    return all(v["size"] == [1080, 1920] and v["bottom_dark_rows"] < 40 for v in st.values())


def convert(proj, media_pool, idx, rows):
    r = next(x for x in rows if x["index"] == idx)
    orig = proj.GetTimelineByIndex(idx)
    assert orig.GetUniqueId() == r["id"] and orig.GetName() == r["name"], "index drift"
    name = orig.GetName() + "_9x16"
    if m2.find_timeline_by_name(proj, name):
        raise RuntimeError(f"target already exists: {name}")
    fps = float(orig.GetSetting("timelineFrameRate"))
    v1 = items(orig, "video", 1)
    assert len(v1) == 1, "expected exactly one V1 clip"
    src_name = v1[0].GetName()
    spec = L.avatar_spec_for(src_name)
    if spec is None:
        raise RuntimeError(f"no avatar spec for source {src_name}")
    pre = snapshot_original(orig)
    gifs = gif_infos(orig)
    v1_mpi, v1_s, v1_e = v1[0].GetMediaPoolItem(), v1[0].GetStart(), v1[0].GetEnd()
    v1_ss, v1_se = v1[0].GetSourceStartFrame(), v1[0].GetSourceEndFrame()

    activate(proj, orig)
    new = orig.DuplicateTimeline(name)
    if not new:
        raise RuntimeError("DuplicateTimeline failed")
    time.sleep(DELAY)
    activate(proj, new)
    for k, v in (("useCustomSettings", "1"), ("timelineResolutionWidth", "1080"), ("timelineResolutionHeight", "1920"),
                 ("timelineOutputResMatchTimelineRes", "1"), ("timelineOutputResolutionWidth", "1080"),
                 ("timelineOutputResolutionHeight", "1920"), ("timelinePixelAspectRatio", "square"),
                 ("timelineInputResMismatchBehavior", "scaleToFit"), ("timelineOutputResMismatchBehavior", "scaleToFit")):
        new.SetSetting(k, v)
    time.sleep(DELAY)
    assert new.GetSetting("timelineResolutionWidth") == "1080" and new.GetSetting("timelineResolutionHeight") == "1920"
    assert float(new.GetSetting("timelineFrameRate")) == fps

    if new.GetTrackCount("video") < 4:
        new.AddTrack("video")
        time.sleep(DELAY)
    # GIFs: V2 (dup) -> V4, then clear V2 copies
    old_v2 = items(new, "video", 2)
    place_gifs(media_pool, new, gifs)
    if old_v2:
        new.DeleteClips(old_v2, False)
        time.sleep(DELAY)
    assert not items(new, "video", 2), "V2 not cleared"
    # VTuber panel: game clip again on V2 with the identical source range
    info = {"mediaPoolItem": v1_mpi, "startFrame": v1_ss, "endFrame": v1_se, "mediaType": 1, "trackIndex": 2, "recordFrame": v1_s}
    if not media_pool.AppendToTimeline([info]):
        raise RuntimeError("append VTuber panel failed")
    time.sleep(DELAY)
    for n, nm in ((1, "Game Top"), (2, "VTuber Bottom"), (3, "VTuber Focus"), (4, "Reaction GIFs")):
        try:
            new.SetTrackName("video", n, nm)
        except Exception:
            pass
    nv1, nv2 = items(new, "video", 1)[0], items(new, "video", 2)[0]
    set_props(nv1, L.game_params())
    set_props(nv2, L.avatar_params(*spec))
    for adj in items(new, "video", 3):
        t = fusion_transform(adj)
        if t is None:
            raise RuntimeError("V3 adjustment clip without Transform tool")
        t.SetInput("Size", L.FOCUS["Size"])
        t.SetInput("Pivot", {1: L.FOCUS["Pivot"][0], 2: L.FOCUS["Pivot"][1], 3: 0.0})
        t.SetInput("Center", {1: L.FOCUS["Center"][0], 2: L.FOCUS["Center"][1], 3: 0.0})
        time.sleep(0.4)
    return orig, new, pre, gifs, fps


def verify(orig, new, pre, gifs):
    import compare_invariants as ci

    res = {}
    res["subs"] = (ci.sub_sig(orig) == ci.sub_sig(new), len(ci.sub_sig(new)))
    res["audio"] = (ci.audio_sig(orig) == ci.audio_sig(new), len(ci.audio_sig(new)))
    res["v1_range"] = ci.v1_sig(orig) == ci.v1_sig(new)
    res["range"] = (orig.GetStartFrame(), orig.GetEndFrame()) == (new.GetStartFrame(), new.GetEndFrame())
    res["raster"] = (new.GetSetting("timelineResolutionWidth"), new.GetSetting("timelineResolutionHeight"))
    res["offline"] = ci.offline(new)
    res["v3_ranges"] = [(i.GetStart(), i.GetEnd()) for i in items(orig, "video", 3)] == [(i.GetStart(), i.GetEnd()) for i in items(new, "video", 3)]
    res["gif_ranges"] = [(g["rec"], g["end"], g["src_s"], g["src_e"], g["name"]) for g in gifs] == [
        (i.GetStart(), i.GetEnd(), i.GetSourceStartFrame(), i.GetSourceEndFrame(), i.GetName())
        for i in sorted(items(new, "video", 4), key=lambda i: i.GetStart())]
    nv2 = items(new, "video", 2)
    res["v2_range"] = len(nv2) == 1 and (nv2[0].GetStart(), nv2[0].GetEnd()) == (items(orig, "video", 1)[0].GetStart(), items(orig, "video", 1)[0].GetEnd())
    res["tracks"] = (new.GetTrackCount("video"), new.GetTrackCount("audio"), new.GetTrackCount("subtitle"))
    post = snapshot_original(orig)
    res["original_untouched"] = post == pre
    res["ok"] = all([res["subs"][0], res["audio"][0], res["v1_range"], res["range"], res["raster"] == ("1080", "1920"),
                     not res["offline"], res["v3_ranges"], res["gif_ranges"], res["v2_range"], res["original_untouched"],
                     res["tracks"][0] == 4, res["tracks"][1] == orig.GetTrackCount("audio"), res["tracks"][2] == 1])
    return res


def fix_gifs(proj, media_pool, idx):
    """Rebuild V4 GIFs of an existing <name>_9x16 from its original (ranges + transforms)."""
    orig = proj.GetTimelineByIndex(idx)
    new = m2.find_timeline_by_name(proj, orig.GetName() + "_9x16")
    assert new
    gifs = gif_infos(orig)
    activate(proj, new)
    cur = items(new, "video", 4)
    if cur:
        new.DeleteClips(cur, False)
        time.sleep(DELAY)
    place_gifs(media_pool, new, gifs)
    got = [(i.GetStart(), i.GetEnd(), i.GetSourceStartFrame(), i.GetSourceEndFrame()) for i in sorted(items(new, "video", 4), key=lambda i: i.GetStart())]
    want = [(g["rec"], g["end"], g["src_s"], g["src_e"]) for g in gifs]
    print(idx, "gif ranges equal:", got == want, got, want)
    return got == want


def fix_pilot_gif(proj, media_pool):
    orig = m2.find_timeline_by_name(proj, m2.PILOT_NAME)
    new = m2.find_timeline_by_name(proj, m2.TARGET_NAME)
    assert new.GetUniqueId() == "2b0779e3-6b5d-4fd2-91b3-2d55ffaed2a3"
    gifs = gif_infos(orig)
    activate(proj, new)
    cur = items(new, "video", 4)
    print("before", [(i.GetStart(), i.GetEnd(), i.GetSourceStartFrame(), i.GetSourceEndFrame()) for i in cur], "want", [(g["rec"], g["end"], g["src_s"], g["src_e"]) for g in gifs])
    if cur:
        new.DeleteClips(cur, False)
        time.sleep(DELAY)
    place_gifs(media_pool, new, gifs)
    after = sorted(items(new, "video", 4), key=lambda i: i.GetStart())
    print("after", [(i.GetStart(), i.GetEnd(), i.GetSourceStartFrame(), i.GetSourceEndFrame(), m2.get_item_property(i, "Tilt")) for i in after])


def reapply_avatar(proj, rows, idx):
    """Re-set only the V2 (VTuber panel) transform on an existing <name>_9x16, then re-export stills."""
    r = next(x for x in rows if x["index"] == idx)
    orig = proj.GetTimelineByIndex(idx)
    assert orig.GetUniqueId() == r["id"]
    new = m2.find_timeline_by_name(proj, orig.GetName() + "_9x16")
    assert new, "target missing"
    fps = float(new.GetSetting("timelineFrameRate"))
    spec = L.avatar_spec_for(items(orig, "video", 1)[0].GetName())
    assert spec, "no avatar spec"
    activate(proj, new)
    v2 = items(new, "video", 2)
    assert len(v2) == 1
    set_props(v2[0], L.avatar_params(*spec))
    print("V2", {k: m2.get_item_property(v2[0], k) for k in PROP_CHECK})
    return new, fps


def main():
    args = sys.argv[1:]
    resolve = m2.get_resolve()
    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    assert proj.GetUniqueId() == m2.PROJECT_ID
    media_pool = proj.GetMediaPool()
    entry_tl = proj.GetCurrentTimeline()
    entry_id, entry_tc, entry_page = entry_tl.GetUniqueId(), entry_tl.GetCurrentTimecode(), resolve.GetCurrentPage()
    rows = json.load(open("scratch/survey_sources.json", encoding="utf-8"))
    results_path = os.path.join(OUT_DIR, "results.json")
    os.makedirs(OUT_DIR, exist_ok=True)
    results = json.load(open(results_path, encoding="utf-8")) if os.path.exists(results_path) else {}
    try:
        if "--fix-gifs" in args:
            for idx in [int(a) for a in args if a.isdigit()]:
                ok = fix_gifs(proj, media_pool, idx)
                print("save", pm.SaveProject())
                if not ok:
                    return 1
            return 0
        if "--fix-pilot-gif" in args:
            fix_pilot_gif(proj, media_pool)
            print("save", pm.SaveProject())
            return 0
        if "--reapply-avatar" in args:
            for idx in [int(a) for a in args if a.isdigit()]:
                new, fps = reapply_avatar(proj, rows, idx)
                stills = export_stills(proj, new, idx, fps)
                st = {k: pixel_check(p) for k, p in stills.items()}
                print(idx, "stills", st, "save", pm.SaveProject())
            return 0
        for idx in [int(a) for a in args]:
            print(f"=== timeline {idx}")
            orig, new, pre, gifs, fps = convert(proj, media_pool, idx, rows)
            res = verify(orig, new, pre, gifs)
            stills = export_stills(proj, new, idx, fps)
            res["stills"] = {k: pixel_check(p) for k, p in stills.items()}
            res["stills_ok"] = stills_pass(res["stills"])
            res["needs_eyeball"] = [k for k, v in res["stills"].items() if v["top_dark_rows"] >= 200]
            res["name"] = new.GetName()
            res["saved"] = bool(pm.SaveProject())
            results[str(idx)] = res
            json.dump(results, open(results_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
            print(json.dumps({k: v for k, v in res.items() if k != "stills"}, ensure_ascii=False, default=str))
            if not (res["ok"] and res["stills_ok"] and res["saved"]):
                print("STOP: invariant/pixel check failed")
                return 1
            time.sleep(DELAY)
    finally:
        t = find_by_id(proj, entry_id)
        if t:
            activate(proj, t)
            t.SetCurrentTimecode(entry_tc)
            time.sleep(0.5)
            print("restored", t.GetName(), t.GetCurrentTimecode(), "page", resolve.GetCurrentPage(), "(was", entry_page + ")")
    return 0


if __name__ == "__main__":
    sys.exit(main())
