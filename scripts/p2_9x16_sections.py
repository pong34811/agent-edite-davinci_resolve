"""Per-section 9:16 for a p2 timeline whose single V1 clip changes OBS scene (game -> room -> outro art).

MCP-GAP: same as p2_9x16_convert (MCP duplicate/track/transform actions auto-archive; Fusion inputs not settable;
build+verify+still gate must run in one process) -> scripting API via scripts/resolve_common.

Layout: V1 (whole original range, cut untouched) = game panel (stream anchors, p2_9x16_layout.STREAMS). Added V2 holds
the same source re-appended video-only as consecutive segments, one per section, each with its own transform:
  "panel"  -> lower VTuber panel (avatar_params of the stream; game shows above from V1)
  window   -> full-screen 9:16 crop (p2_9x16_charscene.window) that covers V1 completely.
V3 focus Adjustment Clips keep the pilot Fusion focus when inside a panel section, else the mild charscene FOCUS.

idx 29 (Becastled 001, `คุยสรุปเกมก่อนจบสตรีม`), measured on full-rate low-res decode + full-res frames
(exports/9x16-batch/29/sec/): hard cut game -> room at rec 8315; room -> outro art crossfade ~8426..8440 -> switch 8432.
  room: same OBS room scene as idx 8 layout B (small avatar bottom-left) -> charscene LAYOUT_B.
  outro: illustrated character, face x ~1000..1150 drifting, eyes y ~265, ears ~50 -> full-height window centred x 1080.

Usage: python -m scripts.p2_9x16_sections --index 29 [--apply]
"""
from __future__ import annotations

import json
import sys
import time

from scripts.p2_9x16_build import DELAY, RASTER, activate, items, protected, set_float
from scripts.p2_9x16_charscene import FOCUS as MILD_FOCUS, LAYOUT_B, expected as window_expected, props as window_props
from scripts.p2_9x16_common import ROOT, check, diff
from scripts.p2_9x16_convert import (OUT, PILOT_ID, POS_TOL, RETAINED_ID, append_result, expected_canvas, find_id,
                                     find_name, health, match, pixel_check, read_protected, rng, source_frame, stable_sig)
from scripts.p2_9x16_layout import CANVAS_H, CANVAS_W, PROPS, STREAMS, export, fusion_transform, stream_params
from scripts.resolve_common import connect_resolve, preserved_state

OUTRO = {"eye_x": 1080.0, "eye_y": 265.0, "scale": 1920 / 1080}
CONFIGS = {
    29: {"idpre": "44a12a19", "stream": "Becastled - 001",
         "sections": [(0, 8315, "panel"), (8315, 8432, "room"), (8432, None, "outro")],
         "stills": [("game_normal", 600, "panel"), ("game_focus", "focus0", "panelF"), ("game_precut", 8300, "panel"),
                    ("room_a", 8340, "room"), ("room_b", 8415, "room"), ("outro_a", 8470, "outro"),
                    ("outro_b", 8700, "outro"), ("end", "end", "outro")]},
}
WINDOWS = {"room": LAYOUT_B, "outro": OUTRO}


def plan(p, idx):
    cfg = CONFIGS[idx]
    orig = p.GetTimelineByIndex(idx)
    check(orig is not None and orig.GetUniqueId().startswith(cfg["idpre"]), "index/id mismatch")
    check(float(orig.GetSetting("timelineFrameRate")) == 60.0, "fps")
    names = [orig.GetTrackName("video", n) for n in range(1, orig.GetTrackCount("video") + 1)]
    check(names in (["Video 1", "VTUBER_FOCUS"], ["Video 1", "VTUBER_FOCUS", "ENRICH_GIF"]), f"layout {names}")
    v1 = items(orig, "video", 1)
    check(len(v1) == 1, "single V1 clip expected")
    a = v1[0]
    m = a.GetMediaPoolItem()
    check(cfg["stream"] in m.GetName() and float(m.GetClipProperty("FPS")) == 60.0 and m.GetClipProperty("Resolution") == "1920x1080",
          "V1 source")
    secs = [(s, e if e is not None else a.GetEnd(), k) for s, e, k in cfg["sections"]]
    check(secs[0][0] == a.GetStart() and secs[-1][1] == a.GetEnd() and all(secs[i][1] == secs[i + 1][0] for i in range(len(secs) - 1)),
          "sections do not tile V1")
    focus = [(x.GetStart(), x.GetEnd()) for x in items(orig, "video", 2)]
    gifs = [(x.GetName(), x.GetStart(), x.GetEnd()) for x in items(orig, "video", 3)] if len(names) == 3 else []
    kind_at = lambda f: next(k for s, e, k in secs if s <= f < e)
    for s, e in focus:
        check(kind_at(s) == kind_at(e - 1), "focus clip spans sections")
    game, avatar, meta, pfocus = stream_params(STREAMS[cfg["stream"]])
    seg_props = {"panel": avatar, **{k: window_props(w) for k, w in WINDOWS.items()}}
    pl = {"index": idx, "name": orig.GetName(), "id": orig.GetUniqueId(), "target": orig.GetName() + "_9x16", "nv": len(names),
          "sections": secs, "focus": focus, "focus_kind": [kind_at(s) for s, _ in focus], "gifs": gifs, "game": game,
          "seg_props": seg_props, "panel_focus": pfocus,
          "v1src": [(a.GetName(), a.GetStart(), a.GetEnd(), a.GetSourceStartFrame(), a.GetSourceEndFrame(),
                     m.GetClipProperty("File Path"))]}
    return orig, pl


def build(r, pm, p, orig, pl, log):
    nv = pl["nv"]
    mp = p.GetMediaPool()
    activate(p, orig)
    base_sig = stable_sig(orig)
    (OUT / str(pl["index"])).mkdir(parents=True, exist_ok=True)
    (OUT / str(pl["index"]) / "baseline_original.json").write_text(json.dumps(base_sig, ensure_ascii=False, indent=1), encoding="utf-8")
    base = protected(orig)
    orig_v = [rng(orig, n, False) for n in range(1, nv + 1)]
    new = orig.DuplicateTimeline(pl["target"])
    check(new is not None and new.GetName() == pl["target"], "DuplicateTimeline failed")
    time.sleep(DELAY)
    log["new_id"] = new.GetUniqueId()
    print("DUPLICATED", log["new_id"], flush=True)
    activate(p, new)
    check(protected(new) == base and [rng(new, n, False) for n in range(1, nv + 1)] == orig_v, "duplicate differs")
    for k, v in RASTER:
        new.SetSetting(k, v)
        time.sleep(0.3)
    time.sleep(DELAY)
    check(all(str(new.GetSetting(k)) == v for k, v in RASTER) and float(new.GetSetting("timelineFrameRate")) == 60.0, "raster")
    check(new.AddTrack("video", {"index": 2}), "AddTrack")
    time.sleep(DELAY)
    check([rng(new, n, False) for n in range(1, nv + 2)] == [orig_v[0], []] + orig_v[1:], "track shift")
    a = items(orig, "video", 1)[0]
    want_v2 = []
    for s, e, k in pl["sections"]:
        ss = a.GetSourceStartFrame() + (s - a.GetStart())
        se = a.GetSourceStartFrame() + (e - a.GetStart())
        info = {"mediaPoolItem": a.GetMediaPoolItem(), "startFrame": ss, "endFrame": se, "mediaType": 1, "trackIndex": 2,
                "recordFrame": s}
        check(mp.AppendToTimeline([info]), f"append V2 segment {k} failed")
        time.sleep(DELAY)
        want_v2.append((a.GetName(), s, e, ss, se))
    check(rng(new, 2) == want_v2, f"V2 segments {rng(new, 2)} != {want_v2}")
    check([rng(new, n, False) for n in range(3, nv + 2)] == orig_v[1:] and protected(new) == base, "drift after V2 segments")
    for k, v in pl["game"].items():
        set_float(items(new, "video", 1)[0], k, v, 0.5 if k in POS_TOL else 0.005)
    for x, (_, _, kind) in zip(items(new, "video", 2), pl["sections"]):
        for k, v in pl["seg_props"][kind].items():
            set_float(x, k, v, 0.5 if k in POS_TOL else 0.005)
    log["readback_v1"] = {k: items(new, "video", 1)[0].GetProperty(k) for k in PROPS}
    log["readback_v2"] = [{k: x.GetProperty(k) for k in PROPS} for x in items(new, "video", 2)]
    log["focus_readback"] = []
    for x, kind in zip(items(new, "video", 3), pl["focus_kind"]):
        want = pl["panel_focus"] if kind == "panel" else MILD_FOCUS
        t = fusion_transform(x)
        for k in ("Size", "Pivot", "Center"):
            t.SetInput(k, want[k])
            time.sleep(0.5)
        time.sleep(DELAY)
        rb = {k: t.GetInput(k) for k in ("Size", "Center", "Pivot")}
        log["focus_readback"].append(rb)
        check(abs(float(rb["Size"]) - want["Size"]) < 1e-6 and all(abs(float(rb[k][i]) - want[k][i]) < 1e-6
                                                                    for k in ("Pivot", "Center") for i in (1, 2)), "focus readback")
    for n, nm in enumerate(("Game Top", "VTuber / Character", "VTUBER_FOCUS", "ENRICH_GIF")[:nv + 1], 1):
        new.SetTrackName("video", n, nm)
        time.sleep(0.3)
    check(protected(new) == base, "protected drift at end")
    check(pm.SaveProject(), "SaveProject failed")
    time.sleep(DELAY)
    return new, base_sig, want_v2


def verify(p, orig, new, base_sig, want_v2, pl):
    nv = pl["nv"]
    activate(p, orig)
    res = {"original_vs_baseline_diffs": diff(base_sig, stable_sig(orig))}
    po = protected(orig)
    activate(p, new)
    pn = protected(new)
    res.update(subtitles_equal=po["sub"] == pn["sub"], subtitle_count=[len(po["sub"]), len(pn["sub"])],
               audio_equal=po["audio"] == pn["audio"], audio_count=[len(po["audio"]), len(pn["audio"])],
               v1_equal=po["v1"] == pn["v1"], range_fps=[po["range"], pn["range"], po["fps"], pn["fps"]],
               settings_ok=all(str(new.GetSetting(k)) == v for k, v in RASTER),
               focus_equal=rng(orig, 2, False) == rng(new, 3, False),
               gif_equal=(rng(orig, 3) == rng(new, 4)) if nv == 3 else True,
               v2_segments=rng(new, 2), v2_ok=rng(new, 2) == want_v2,
               tracks={k: new.GetTrackCount(k) for k in ("video", "audio", "subtitle")})
    res["ok"] = (not res["original_vs_baseline_diffs"] and res["subtitles_equal"] and res["audio_equal"] and res["v1_equal"]
                 and po["range"] == pn["range"] and float(pn["fps"]) == 60.0 and res["settings_ok"] and res["focus_equal"]
                 and res["gif_equal"] and res["v2_ok"]
                 and res["tracks"] == {"video": nv + 1, "audio": orig.GetTrackCount("audio"), "subtitle": orig.GetTrackCount("subtitle")})
    return res


def stills(p, new, pl):
    d = OUT / str(pl["index"])
    anchor = STREAMS[CONFIGS[pl["index"]]["stream"]]
    special = {"end": new.GetEndFrame() - 4}
    if pl["focus"]:
        special["focus0"] = (pl["focus"][0][0] + pl["focus"][0][1]) // 2
    res, ok = {}, True
    for label, f, kind in CONFIGS[pl["index"]]["stills"]:
        f = special.get(f, f)
        if not isinstance(f, int):
            continue
        path = export(p, new, f, d / f"{label}_{f}.png")
        pc = pixel_check(path)
        best = None
        for off in (0, -1, 1):
            src, sf = source_frame(pl["v1src"], f + off, d / f"src_{label}_{f}_{off:+d}.png")
            if kind.startswith("panel"):
                exp = expected_canvas(src, anchor, kind.endswith("F"))
            else:
                exp = window_expected(src, WINDOWS[kind])
            m = (match(path, exp, (0, 0, CANVAS_W, 960)), match(path, exp, (0, 960, CANVAS_W, CANVAS_H)), off)
            if best is None or m[0]["corr"] + m[1]["corr"] > best[0]["corr"] + best[1]["corr"]:
                best = m
        good = (pc["size"] == [1080, 1920] and all(x["corr"] >= 0.97 and x["mad"] <= 8.0 for x in best[:2]))
        res[label] = {"path": str(path.relative_to(ROOT)), "frame": f, "kind": kind, **pc, "match_top": best[0],
                      "match_low": best[1], "offset": best[2], "ok": bool(good)}
        ok = ok and good
        print(label, f, kind, best, good, flush=True)
    res["ok"] = ok
    return res


def main():
    idx = int(sys.argv[sys.argv.index("--index") + 1])
    apply = "--apply" in sys.argv
    r = connect_resolve()
    pm, p = health(r)
    orig, pl = plan(p, idx)
    print("PLAN", json.dumps({k: v for k, v in pl.items() if k not in ("v1src",)}, ensure_ascii=False, default=str), flush=True)
    if not apply:
        return 0
    check(not find_name(p, pl["target"]), "target exists")
    rc = 0
    with preserved_state(r):
        prot_before = read_protected(p, [PILOT_ID, RETAINED_ID])
        r.OpenPage("edit")
        time.sleep(2)
        check(r.GetCurrentPage() == "edit", "not on Edit page")
        entry = {"index": idx, "time": time.strftime("%Y-%m-%d %H:%M:%S"), "name": pl["name"], "id": pl["id"],
                 "target": pl["target"], "mode": "sections", "sections": pl["sections"], "seg_props": pl["seg_props"]}
        log = {}
        try:
            new, base_sig, want_v2 = build(r, pm, p, orig, pl, log)
            entry["new_id"] = log["new_id"]
            v = verify(p, orig, new, base_sig, want_v2, pl)
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
