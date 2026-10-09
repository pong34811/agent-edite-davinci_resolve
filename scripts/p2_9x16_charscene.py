"""Full-screen character-scene 9:16 (no game panel) for p2 timelines whose V1 is a chat/character scene.

MCP-GAP: same as p2_9x16_convert (MCP duplicate/track/transform actions auto-archive; Fusion inputs not settable;
build+verify+still gate must run in one process) -> scripting API via scripts/resolve_common.

Windows are 9:16 crops of the source, sized so ear-to-eye spans ~527 canvas px (the approved pilot focus look).
  LAYOUT_A (chat scene, OBS "LIVE CHAT" layout): big avatar right of centre (ear tips y~225, eyes y~500, eye-mid
    x 1280..1430 as she leans) -> full-height window centred on x 1350; LIVE CHAT panel (x<640) out of frame.
  LAYOUT_B (room scene, small avatar bottom-left: ear tips y~540, eyes y~740, eye-mid x 250..380) -> window centred
    on 315, scale 2.6.
idx 8 (strinova 006): A rec 0..~1938, crossfade ~1939..1957 (chat-panel metric crosses 50% at 1947/1948) -> SWITCH 1948,
  then B to the end (trailing black kept). V1 (whole range, cut untouched) = A; added V2 = same source re-appended
  video-only from SWITCH = B. Tracks: Character A / Character B / VTUBER_FOCUS / ENRICH_GIF.
idx 23 (Becastled 001): chat scene A for the whole range (12 samples + full cut scan) -> V1 = A, no added track.
  Tracks: Character / VTUBER_FOCUS / ENRICH_GIF.
Focus Adjustment Clip: mild punch-in, Fusion Size 1.15 about the frame centre (Pivot = Center = (0.5, 0.5)) instead of
the pilot's 2.05, which would over-zoom an already full-screen face.

Usage: python -m scripts.p2_9x16_charscene --index 8|23 [--apply] [--replace-id <old _9x16 id>]
"""
from __future__ import annotations

import json
import sys
import time

from PIL import Image

from scripts.p2_9x16_build import DELAY, RASTER, SHORT, activate, items, protected, set_float
from scripts.p2_9x16_common import ROOT, check, diff
from scripts.p2_9x16_convert import (OUT, PILOT_ID, POS_TOL, RETAINED_ID, append_result, find_id, find_name, health,
                                     match, pixel_check, read_protected, rng, source_frame, stable_sig)
from scripts.p2_9x16_layout import CANVAS_H, CANVAS_W, FIT, PROPS, SRC_H, SRC_W, TILT_PX, export, fusion_transform
from scripts.resolve_common import connect_resolve, preserved_state

EYE_CANVAS_Y = 960.0
LAYOUT_A = {"eye_x": 1350.0, "eye_y": 500.0, "scale": 1920 / 1080}
LAYOUT_B = {"eye_x": 315.0, "eye_y": 740.0, "scale": 2.6}
FOCUS = {"Size": 1.15, "Pivot": {1: 0.5, 2: 0.5, 3: 0.0}, "Center": {1: 0.5, 2: 0.5, 3: 0.0}}
CONFIGS = {
    8: {"idpre": "ee6cafd2", "stream": "strinova - 006", "switch": 1948,
        "stills": [("A_normal", 600, "A"), ("A_gif", "gif0", "A"), ("A_preswitch", 1930, "A"), ("B_postswitch", 1965, "B"),
                   ("B_normal", 2500, "B"), ("B_focus", "focus0", "BF"), ("B_end", "end", "B")]},
    23: {"idpre": "7883e0aa", "stream": "Becastled - 001", "switch": None,
         "stills": [("A_normal", 600, "A"), ("A_gif", "gif0", "A"), ("A_mid", 2900, "A"), ("A_focus", "focus0", "AF"),
                    ("A_end", "end", "A")]},
}
# idx 30 (Becastled 002, 30 fps source on a 60 fps timeline): room scene, big avatar right of centre, no chat panel
# (eyes y ~500, face centre x 1340..1530 over 12 samples) -> full-height window centred x 1430. Cut scan: 0 cuts.
CONFIGS[30] = {"idpre": "6affc2c8", "stream": "Becastled - 002", "switch": None,
               "layout_a": {"eye_x": 1430.0, "eye_y": 500.0, "scale": 1920 / 1080},
               "stills": [("A_normal", 600, "A"), ("A_gif", "gif0", "A"), ("A_mid", 2900, "A"), ("A_focus", "focus0", "AF"),
                          ("A_end", "end", "A")]}
# idx 36 (Becastled 003, 60 fps): same room scene, eyes y ~510, face centre x 1340..1470 -> window centred x 1410.
CONFIGS[36] = {"idpre": "6cb426af", "stream": "Becastled - 003", "switch": None,
               "layout_a": {"eye_x": 1410.0, "eye_y": 510.0, "scale": 1920 / 1080},
               "stills": [("A_normal", 600, "A"), ("A_gif", "gif0", "A"), ("A_mid", 3000, "A"), ("A_focus", "focus0", "AF"),
                          ("A_end", "end", "A")]}
IDX = 8
CFG = CONFIGS[IDX]


def window(lay):
    s = lay["scale"]
    w, h = CANVAS_W / s, CANVAS_H / s
    x0 = min(max(lay["eye_x"] - w / 2, 0.0), SRC_W - w)
    y0 = min(max(lay["eye_y"] - EYE_CANVAS_Y / s, 0.0), SRC_H - h)
    return x0, y0, w, h


def props(lay):
    x0, y0, w, h = window(lay)
    s = lay["scale"]
    cx = CANVAS_W / 2 + (SRC_W / 2 - (x0 + w / 2)) * s
    cy = CANVAS_H / 2 + (SRC_H / 2 - (y0 + h / 2)) * s
    z = s / FIT
    return {"ZoomX": z, "ZoomY": z, "Pan": cx - CANVAS_W / 2, "Tilt": -(cy - CANVAS_H / 2) / TILT_PX,
            "CropTop": 0.0, "CropBottom": 0.0}


def expected(src, lay, focus=False):
    x0, y0, w, h = window(lay)
    img = src.crop((x0, y0, x0 + w, y0 + h)).resize((CANVAS_W, CANVAS_H), Image.BILINEAR)
    if focus:
        S = FOCUS["Size"]
        px, py = FOCUS["Pivot"][1] * CANVAS_W, (1 - FOCUS["Pivot"][2]) * CANVAS_H
        tx, ty = px + (FOCUS["Center"][1] - 0.5) * CANVAS_W, py - (FOCUS["Center"][2] - 0.5) * CANVAS_H
        img = img.transform((CANVAS_W, CANVAS_H), Image.AFFINE, (1 / S, 0, px - tx / S, 0, 1 / S, py - ty / S), Image.BILINEAR)
    return img


def tracks():
    """(focus track, gif track, video track count) on the new timeline."""
    return (3, 4, 4) if CFG["switch"] else (2, 3, 3)


def plan(p):
    sw = CFG["switch"]
    orig = p.GetTimelineByIndex(IDX)
    check(orig is not None and orig.GetUniqueId().startswith(CFG["idpre"]), "index/id mismatch")
    check(float(orig.GetSetting("timelineFrameRate")) == 60.0, "fps")
    names = [orig.GetTrackName("video", n) for n in range(1, orig.GetTrackCount("video") + 1)]
    check(names == ["Video 1", "VTUBER_FOCUS", "ENRICH_GIF"], f"layout {names}")
    v1 = items(orig, "video", 1)
    m = v1[0].GetMediaPoolItem() if len(v1) == 1 else None
    check(m is not None and CFG["stream"] in m.GetName(), "V1 source")
    src_fps = float(m.GetClipProperty("FPS"))
    check(60.0 % src_fps == 0 and m.GetClipProperty("Resolution") == "1920x1080", "V1 source fps/res")
    if sw:
        check(v1[0].GetStart() < sw < v1[0].GetEnd(), "switch outside V1")
    focus = [(x.GetStart(), x.GetEnd()) for x in items(orig, "video", 2)]
    gifs = [(x.GetName(), x.GetStart(), x.GetEnd()) for x in items(orig, "video", 3)]
    a = v1[0]
    pl = {"index": IDX, "name": orig.GetName(), "id": orig.GetUniqueId(), "target": orig.GetName() + "_9x16", "focus": focus,
          "gifs": gifs, "switch": sw, "v1src": [(a.GetName(), a.GetStart(), a.GetEnd(), a.GetSourceStartFrame(), a.GetSourceEndFrame(),
                                                  m.GetClipProperty("File Path"), src_fps)],
          "props_A": props(LAYOUT_A), "window_A": window(LAYOUT_A)}
    if sw:
        check(all(s >= sw for s, _ in focus), "focus clip before the switch")
        pl.update(props_B=props(LAYOUT_B), window_B=window(LAYOUT_B))
    return orig, pl


def delete_old(p, pl, old_id):
    old = find_id(p, old_id)
    if old is None:
        return "absent"
    check(old.GetName() == pl["target"], "old id has a different name; refusing")
    check([old.GetSetting("timelineResolutionWidth"), old.GetSetting("timelineResolutionHeight")] == ["1080", "1920"], "old raster")
    check(p.GetCurrentTimeline().GetUniqueId() != old_id, "old timeline is active")
    check(p.GetMediaPool().DeleteTimelines([old]), "DeleteTimelines failed")
    time.sleep(DELAY)
    check(find_id(p, old_id) is None and not find_name(p, pl["target"]), "old timeline still present")
    return "deleted"


def build(r, pm, p, orig, pl, log):
    sw = CFG["switch"]
    ft, gt, nv = tracks()
    mp = p.GetMediaPool()
    activate(p, orig)
    base_sig = stable_sig(orig)
    (OUT / str(IDX)).mkdir(parents=True, exist_ok=True)
    (OUT / str(IDX) / "baseline_original.json").write_text(json.dumps(base_sig, ensure_ascii=False, indent=1), encoding="utf-8")
    base = protected(orig)
    orig_v = [rng(orig, n, False) for n in (1, 2, 3)]
    new = orig.DuplicateTimeline(pl["target"])
    check(new is not None and new.GetName() == pl["target"], "DuplicateTimeline failed")
    time.sleep(DELAY)
    log["new_id"] = new.GetUniqueId()
    activate(p, new)
    check(protected(new) == base and [rng(new, n, False) for n in (1, 2, 3)] == orig_v, "duplicate differs")
    for k, v in RASTER:
        new.SetSetting(k, v)
        time.sleep(0.3)
    time.sleep(DELAY)
    check(all(str(new.GetSetting(k)) == v for k, v in RASTER) and float(new.GetSetting("timelineFrameRate")) == 60.0, "raster")
    want_v2 = None
    if sw:
        check(new.AddTrack("video", {"index": 2}), "AddTrack")
        time.sleep(DELAY)
        check([rng(new, n, False) for n in (1, 2, 3, 4)] == [orig_v[0], [], orig_v[1], orig_v[2]], "track shift")
        a = items(orig, "video", 1)[0]
        ss = a.GetSourceStartFrame() + (sw - a.GetStart())
        info = {"mediaPoolItem": a.GetMediaPoolItem(), "startFrame": ss, "endFrame": a.GetSourceEndFrame(), "mediaType": 1,
                "trackIndex": 2, "recordFrame": sw}
        check(mp.AppendToTimeline([info]), "append V2 segment failed")
        time.sleep(DELAY)
        want_v2 = [(a.GetName(), sw, a.GetEnd(), ss, a.GetSourceEndFrame())]
        check(rng(new, 2) == want_v2, f"V2 segment {rng(new, 2)} != {want_v2}")
    check([rng(new, n, False) for n in (ft, gt)] == orig_v[1:] and protected(new) == base, "drift after track setup")
    for x in items(new, "video", gt):
        for k in ("ZoomX", "ZoomY", "Tilt"):
            set_float(x, k, SHORT[k], 0.5 if k == "Tilt" else 0.005)
    layers = [(1, pl["props_A"])] + ([(2, pl["props_B"])] if sw else [])
    for n, pr in layers:
        for x in items(new, "video", n):
            for k, v in pr.items():
                set_float(x, k, v, 0.5 if k in POS_TOL else 0.005)
    log["readback"] = {n: {k: items(new, "video", n)[0].GetProperty(k) for k in PROPS} for n, _ in layers}
    log["focus_before"], log["focus_readback"] = [], []
    for x in items(new, "video", ft):
        t = fusion_transform(x)
        log["focus_before"].append({k: t.GetInput(k) for k in ("Size", "Center", "Pivot")})
        for k in ("Size", "Pivot", "Center"):
            t.SetInput(k, FOCUS[k])
            time.sleep(0.5)
        time.sleep(DELAY)
        rb = {k: t.GetInput(k) for k in ("Size", "Center", "Pivot")}
        log["focus_readback"].append(rb)
        check(abs(float(rb["Size"]) - FOCUS["Size"]) < 1e-6 and all(abs(float(rb[k][i]) - FOCUS[k][i]) < 1e-6
                                                                     for k in ("Pivot", "Center") for i in (1, 2)), "focus readback")
    names = ("Character A", "Character B", "VTUBER_FOCUS", "ENRICH_GIF") if sw else ("Character", "VTUBER_FOCUS", "ENRICH_GIF")
    for n, nm in enumerate(names, 1):
        new.SetTrackName("video", n, nm)
        time.sleep(0.3)
    check(protected(new) == base, "protected drift at end")
    check(pm.SaveProject(), "SaveProject failed")
    time.sleep(DELAY)
    return new, base_sig, want_v2


def verify(p, orig, new, base_sig, want_v2):
    ft, gt, nv = tracks()
    activate(p, orig)
    res = {"original_vs_baseline_diffs": diff(base_sig, stable_sig(orig))}
    po = protected(orig)
    activate(p, new)
    pn = protected(new)
    res.update(subtitles_equal=po["sub"] == pn["sub"], subtitle_count=[len(po["sub"]), len(pn["sub"])],
               audio_equal=po["audio"] == pn["audio"], audio_count=[len(po["audio"]), len(pn["audio"])],
               v1_equal=po["v1"] == pn["v1"], range_fps=[po["range"], pn["range"], po["fps"], pn["fps"]],
               settings_ok=all(str(new.GetSetting(k)) == v for k, v in RASTER),
               focus_equal=rng(orig, 2, False) == rng(new, ft, False), gif_equal=rng(orig, 3) == rng(new, gt),
               v2_segment=rng(new, 2) if want_v2 else None, v2_ok=(rng(new, 2) == want_v2) if want_v2 else True,
               tracks={k: new.GetTrackCount(k) for k in ("video", "audio", "subtitle")})
    res["ok"] = (not res["original_vs_baseline_diffs"] and res["subtitles_equal"] and res["audio_equal"] and res["v1_equal"]
                 and po["range"] == pn["range"] and float(pn["fps"]) == 60.0 and res["settings_ok"] and res["focus_equal"]
                 and res["gif_equal"] and res["v2_ok"]
                 and res["tracks"] == {"video": nv, "audio": orig.GetTrackCount("audio"), "subtitle": orig.GetTrackCount("subtitle")})
    return res


def stills(p, new, pl):
    d = OUT / str(IDX)
    end = new.GetEndFrame()
    special = {"end": end - 4}
    if pl["focus"]:
        special["focus0"] = (pl["focus"][0][0] + pl["focus"][0][1]) // 2
    if pl["gifs"]:
        special["gif0"] = (pl["gifs"][0][1] + pl["gifs"][0][2]) // 2
    res, ok = {}, True
    for label, f, lay in CFG["stills"]:
        f = special.get(f, f)
        if not isinstance(f, int):
            continue
        path = export(p, new, f, d / f"{label}_{f}.png")
        pc = pixel_check(path)
        best = None
        for off in (0, -1, 1):
            src, sf = source_frame(pl["v1src"], f + off, d / f"src_{label}_{f}_{off:+d}.png")
            exp = expected(src, LAYOUT_A if lay.startswith("A") else LAYOUT_B, lay.endswith("F"))
            m = (match(path, exp, (0, 0, CANVAS_W, 960)), match(path, exp, (0, 960, CANVAS_W, CANVAS_H)), off)
            if best is None or m[0]["corr"] + m[1]["corr"] > best[0]["corr"] + best[1]["corr"]:
                best = m
        good = (pc["size"] == [1080, 1920] and best[1]["corr"] >= 0.97 and best[1]["mad"] <= 8.0
                and (label.endswith("gif") or (best[0]["corr"] >= 0.97 and best[0]["mad"] <= 8.0)))
        res[label] = {"path": str(path.relative_to(ROOT)), "frame": f, "layout": lay, **pc, "match_top": best[0],
                      "match_low": best[1], "offset": best[2], "ok": bool(good)}
        ok = ok and good
        print(label, f, best, pc["dark_rows"], good, flush=True)
    res["ok"] = ok
    return res


def main():
    global IDX, CFG
    if "--index" in sys.argv:
        IDX = int(sys.argv[sys.argv.index("--index") + 1])
        CFG = CONFIGS[IDX]
    if "layout_a" in CFG:
        global LAYOUT_A
        LAYOUT_A = CFG["layout_a"]
    apply = "--apply" in sys.argv
    old_id = sys.argv[sys.argv.index("--replace-id") + 1] if "--replace-id" in sys.argv else None
    r = connect_resolve()
    pm, p = health(r)
    orig, pl = plan(p)
    print("PLAN", json.dumps({k: v for k, v in pl.items() if k != "v1src"}, ensure_ascii=False, default=str), flush=True)
    if not apply:
        return 0
    rc = 0
    with preserved_state(r):
        prot_before = read_protected(p, [PILOT_ID, RETAINED_ID])
        r.OpenPage("edit")
        time.sleep(2)
        check(r.GetCurrentPage() == "edit", "not on Edit page")
        entry = {"index": IDX, "time": time.strftime("%Y-%m-%d %H:%M:%S"), "name": pl["name"], "id": pl["id"],
                 "target": pl["target"], "mode": "character full-screen", "switch": CFG["switch"], "focus_choice": FOCUS,
                 **{k: pl[k] for k in ("props_A", "window_A", "props_B", "window_B") if k in pl}}
        log = {}
        try:
            activate(p, orig)  # make sure an old _9x16 is not active before deleting it
            if old_id:
                entry["old_delete"] = {"id": old_id, "result": delete_old(p, pl, old_id)}
                print("OLD", entry["old_delete"], flush=True)
            check(not find_name(p, pl["target"]), "target exists")
            new, base_sig, want_v2 = build(r, pm, p, orig, pl, log)
            entry["new_id"] = log["new_id"]
            v = verify(p, orig, new, base_sig, want_v2)
            s = stills(p, new, pl)
            entry.update(build=log, verify=v, stills=s, status="built" if v["ok"] and s["ok"] else "FAILED_CHECK")
        except Exception as e:  # noqa: BLE001
            entry.update(build=log, status="ERROR", error=repr(e))
        append_result(entry)
        print("RESULT", entry["status"], entry.get("new_id"), "verify_ok", entry.get("verify", {}).get("ok"),
              entry.get("verify", {}).get("subtitle_count"), entry.get("verify", {}).get("audio_count"),
              entry.get("error", ""), flush=True)
        rc = 0 if entry["status"] == "built" else 1
        prot_after = read_protected(p, [PILOT_ID, RETAINED_ID])
        pd = {t[:8]: len(diff(prot_before[t], prot_after[t])) for t in prot_before}
        print("PROTECTED_TIMELINES_DIFFS", pd, flush=True)
        rc = rc or int(any(pd.values()))
    print("RESTORED", p.GetCurrentTimeline().GetName(), r.GetCurrentPage(), flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
