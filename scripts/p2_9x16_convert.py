"""Generalized p2 16:9 -> 9:16 converter: one original (by project-list index + exact id) -> `<name>_9x16`.

MCP-GAP: timeline.duplicate / set_setting / add_track / timeline_item.set_property exist in the davinci-resolve MCP,
but each is a registered destructive action that auto-archives (`<name>_archived_vNN` copies, Media Pool folder moves);
Fusion Transform inputs are not settable via timeline_item_fusion; and build -> verify -> still export -> numpy check
must run in one process with per-step invariant checks -> scripting API via scripts/resolve_common.

Steps (pilot order, scripts/p2_9x16_build + p2_9x16_layout): duplicate -> raster 1080x1920 -> AddTrack video idx 2
(focus V2->V3, GIFs V3->V4 untouched) -> V2 panel = each V1 clip re-appended video-only with the same ranges ->
GIF preset "short" (floats) -> V1 game / V2 avatar transforms from the stream's anchors (p2_9x16_layout.STREAMS) ->
Fusion Transform on EVERY V3 Adjustment Clip -> track names -> save -> verify vs live original + in-process baseline
-> stills (normal / first GIF / first focus) + numpy checks. Stops (exit 1) on the first failed check.
Non-60fps timelines and unknown streams/layouts are flagged and skipped, never guessed. Subtitles/audio/cuts untouched;
no subtitle preset, no render.

Usage: python -m scripts.p2_9x16_convert <index>:<id-prefix> [...] [--apply]   (default dry run: plan only)
Results append to exports/9x16-batch/results.json; stills under exports/9x16-batch/<index>/.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time

import numpy as np
from PIL import Image

from scripts.p2_9x16_build import AUDIO_KEYS, DELAY, FOCUS_GEN, RASTER, SHORT, activate, items, protected, set_float
from scripts.p2_9x16_common import PROJECT, ROOT, check, diff, signature
from scripts.p2_9x16_layout import (CANVAS_H, CANVAS_W, GAME_SCALE, PROPS, SPLIT_Y, SRC_H, STREAMS, export,
                                   fusion_transform, pixel_check, stream_for, stream_params)
from scripts.resolve_common import connect_resolve, preserved_state

OUT = ROOT / "exports" / "9x16-batch"
RESULTS = OUT / "results.json"
PILOT_ID = "1d5238ed-414a-45b7-8458-7310de771be3"
RETAINED_ID = "9a5a81e1-5811-427b-95ba-94b7242913db"
POS_TOL = ("Pan", "Tilt", "CropTop", "CropBottom")
# Layout gate, calibrated on the approved pilot stills + idx 2/3 (MAD 1.3-2.3, corr 0.999-1.000); a wrong-eye_x
# control scored corr <= 0.14 and Fusion Size +/-0.05 scored corr ~0.93.
MATCH_CORR, MATCH_MAD = 0.97, 8.0


def stable_sig(tl):
    """signature() minus reads that depend on whether the timeline is ACTIVE (track enable/lock flags read False
    on inactive timelines on 21.1.0.17; audio GetProperty adds default keys when active) -> fixed audio key set."""
    return normalize(signature(tl, fusion=True))


def normalize(s):
    for kind, tracks in s["tracks"].items():
        for t in tracks:
            t.pop("enabled", None)
            t.pop("locked", None)
            if kind == "audio":
                for it in t["items"]:
                    it["props"] = {k: it["props"].get(k) for k in AUDIO_KEYS}
    return s


def read_protected(p, ids):
    """Read protected timelines while each is ACTIVE (see stable_sig), so before/after reads are comparable."""
    out = {}
    for t in ids:
        tl = find_id(p, t)
        check(tl is not None, f"protected timeline {t} missing")
        activate(p, tl)
        out[t] = stable_sig(tl)
    return out


SLOW_RASTER = "--slow-raster" in sys.argv


class Flag(Exception):
    """Timeline needs separate handling (not a failure of a built timeline)."""


def health(r):
    check(r is not None, "Resolve unavailable")
    pm = r.GetProjectManager()
    p = pm.GetCurrentProject()
    check(p is not None and p.GetName() == PROJECT, "wrong/no project")
    check(r.GetCurrentPage() is not None, "GetCurrentPage did not respond")
    check(not p.IsRenderingInProgress(), "render in progress")
    return pm, p


def find_id(p, tid):
    for i in range(1, p.GetTimelineCount() + 1):
        t = p.GetTimelineByIndex(i)
        if t.GetUniqueId() == tid:
            return t
    return None


def find_name(p, name):
    return [p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1)
            if p.GetTimelineByIndex(i).GetName() == name]


def tl_fps(tl):
    return float(tl.GetSetting("timelineFrameRate"))


def plan(p, idx, idprefix, existing_ok=False):
    orig = p.GetTimelineByIndex(idx)
    check(orig is not None and orig.GetUniqueId().startswith(idprefix), f"index {idx} is not id {idprefix}")
    name = orig.GetName()
    pl = {"index": idx, "name": name, "id": orig.GetUniqueId(), "target": name + "_9x16"}
    if tl_fps(orig) != 60.0:
        raise Flag(f"timeline fps {orig.GetSetting('timelineFrameRate')} != 60")
    if [orig.GetSetting("timelineResolutionWidth"), orig.GetSetting("timelineResolutionHeight")] != ["1920", "1080"]:
        raise Flag("original raster is not 1920x1080")
    nv = orig.GetTrackCount("video")
    names = [orig.GetTrackName("video", n) for n in range(1, nv + 1)]
    if names not in (["Video 1", "VTUBER_FOCUS"], ["Video 1", "VTUBER_FOCUS", "ENRICH_GIF"]):
        raise Flag(f"unexpected video track layout {names}")
    v1 = items(orig, "video", 1)
    if not v1 or any(x.GetMediaPoolItem() is None for x in v1):
        raise Flag("V1 empty or has a non-media item")
    keys = {stream_for(x.GetMediaPoolItem().GetName())[0] for x in v1}
    if None in keys or len(keys) != 1:
        raise Flag(f"V1 source not a single calibrated stream: {[x.GetName() for x in v1]}")
    for x in v1:
        m = x.GetMediaPoolItem()
        # 60 fps sources, or an integer divisor (Becastled 002 is 30 fps on a 60 fps timeline: each source frame spans
        # 2 record frames; source ranges stay in source-frame units and are compared exactly after the V2 append)
        if m.GetClipProperty("Resolution") != "1920x1080" or 60.0 % float(m.GetClipProperty("FPS")) != 0:
            raise Flag(f"V1 source {m.GetClipProperty('Resolution')} @ {m.GetClipProperty('FPS')}")
    focus = items(orig, "video", 2)
    if any(x.GetName() != FOCUS_GEN for x in focus):
        raise Flag("V2 holds something other than Adjustment Clips")
    gifs = items(orig, "video", 3) if nv == 3 else []
    if any(x.GetMediaPoolItem() is None for x in gifs):
        raise Flag("GIF track holds a non-media item")
    key = keys.pop()
    pl["v1src"] = [(x.GetName(), x.GetStart(), x.GetEnd(), x.GetSourceStartFrame(), x.GetSourceEndFrame(),
                    x.GetMediaPoolItem().GetClipProperty("File Path"), float(x.GetMediaPoolItem().GetClipProperty("FPS")))
                   for x in v1]
    pl["src_fps"] = sorted({t[6] for t in pl["v1src"]})
    pl.update(stream=key, nv=nv, v1=[(x.GetName(), x.GetStart(), x.GetEnd(), x.GetSourceStartFrame(), x.GetSourceEndFrame()) for x in v1],
              focus=[(x.GetStart(), x.GetEnd()) for x in focus],
              gifs=[(x.GetName(), x.GetStart(), x.GetEnd(), x.GetSourceStartFrame(), x.GetSourceEndFrame()) for x in gifs])
    if find_name(p, pl["target"]) and not existing_ok:
        raise Flag(f"target already exists: {pl['target']}")
    return orig, pl


def rng(tl, n, src=True):
    return [(x.GetName(), x.GetStart(), x.GetEnd()) + ((x.GetSourceStartFrame(), x.GetSourceEndFrame()) if src else ())
            for x in items(tl, "video", n)] if n <= tl.GetTrackCount("video") else []


def step(msg):
    """Progress line before each Resolve call, so an external watchdog can name the call that stalls."""
    print("STEP", time.strftime("%H:%M:%S"), msg, flush=True)


def build(r, pm, p, orig, pl, log, existing=None, late_activate=False):
    anchor = STREAMS[pl["stream"]]
    game, avatar, meta, focus = stream_params(anchor)
    log.update(game=game, avatar=avatar, avatar_meta=meta, focus=focus)
    mp = p.GetMediaPool()
    activate(p, orig)  # position props of an INACTIVE timeline read scaled by the active timeline's raster
    base_sig = stable_sig(orig)
    d = OUT / str(pl["index"])
    d.mkdir(parents=True, exist_ok=True)
    (d / "baseline_original.json").write_text(json.dumps(base_sig, ensure_ascii=False, indent=1), encoding="utf-8")
    base = protected(orig)
    nv = pl["nv"]
    orig_v = [rng(orig, n, False) for n in range(1, nv + 1)]

    if existing:
        # --existing: an untouched duplicate already made (DuplicateTimeline hung Resolve on some timelines). Refuse
        # unless it is exactly the target name, still 16:9 and track-for-track identical (checked below).
        new = find_id(p, existing)
        check(new is not None and new.GetName() == pl["target"], "existing copy not found by id+name")
        check([new.GetSetting("timelineResolutionWidth"), new.GetSetting("timelineResolutionHeight")] == ["1920", "1080"]
              and new.GetTrackCount("video") == nv, "existing copy is not an untouched duplicate")
        log["existing"] = True
    else:
        new = orig.DuplicateTimeline(pl["target"])
        check(new is not None and new.GetName() == pl["target"], "DuplicateTimeline failed")
        time.sleep(DELAY)
    log["new_id"] = new.GetUniqueId()
    print("DUPLICATED", log["new_id"], flush=True)
    if late_activate:
        # idx 27: the hang came right after DuplicateTimeline (activate copy + read-back). Verify the copy's ranges
        # and set its raster while it is still INACTIVE (both are activation-independent reads/writes), then activate.
        step("inactive: video ranges of copy")
        check([rng(new, n, False) for n in range(1, nv + 1)] == orig_v, "duplicate video tracks differ")
        step("inactive: subtitle/audio ranges of copy")
        po, pn = protected(orig), protected(new)
        check(po["sub"] == pn["sub"] and [a[:6] for a in po["audio"]] == [a[:6] for a in pn["audio"]], "duplicate content differs")
        for k, v in RASTER:
            step(f"inactive: SetSetting {k}")
            new.SetSetting(k, v)
            time.sleep(0.3)
        time.sleep(DELAY)
        step("activate copy")
        activate(p, new)
        step("active: protected read-back")
        check(protected(new) == base, "duplicate protected content differs")
    elif SLOW_RASTER:
        # idx 27/33 variation: activate first, then one raster key at a time, HEIGHT before width, 3 s pause + read-back.
        step("activate copy")
        activate(p, new)
        step("active: protected read-back")
        check(protected(new) == base, "duplicate protected content differs")
        check([rng(new, n, False) for n in range(1, nv + 1)] == orig_v, "duplicate video tracks differ")
        order = ["useCustomSettings", "timelineResolutionHeight", "timelineResolutionWidth",
                 "timelineOutputResMatchTimelineRes", "timelineOutputResolutionHeight", "timelineOutputResolutionWidth",
                 "timelinePixelAspectRatio", "timelineInputResMismatchBehavior", "timelineOutputResMismatchBehavior"]
        want = dict(RASTER)
        for k in order:
            step(f"active: SetSetting {k}={want[k]}")
            new.SetSetting(k, want[k])
            time.sleep(3)
            step(f"read-back {k}={new.GetSetting(k)}")
    else:
        activate(p, new)
        check(protected(new) == base, "duplicate protected content differs")
        check([rng(new, n, False) for n in range(1, nv + 1)] == orig_v, "duplicate video tracks differ")
        for k, v in RASTER:
            new.SetSetting(k, v)
            time.sleep(0.3)
        time.sleep(DELAY)
    log["settings"] = {k: new.GetSetting(k) for k, _ in RASTER}
    for k, v in RASTER:
        check(str(log["settings"][k]) == v, f"setting {k} = {log['settings'][k]} (want {v})")
    check(tl_fps(new) == 60.0, "fps changed")

    step("AddTrack")
    check(new.AddTrack("video", {"index": 2}), "AddTrack index 2 failed")
    time.sleep(DELAY)
    want = [orig_v[0], []] + orig_v[1:]
    check(new.GetTrackCount("video") == nv + 1 and [rng(new, n, False) for n in range(1, nv + 2)] == want,
          "track shift did not give V1 game / V2 empty / V3 focus / V4 GIFs")
    check(protected(new) == base, "protected drift after AddTrack")

    step("V2 append")
    for a in items(orig, "video", 1):
        info = {"mediaPoolItem": a.GetMediaPoolItem(), "startFrame": a.GetSourceStartFrame(),
                "endFrame": a.GetSourceEndFrame(), "mediaType": 1, "trackIndex": 2, "recordFrame": a.GetStart()}
        check(mp.AppendToTimeline([info]), "append V2 panel failed")
        time.sleep(DELAY)
    check(rng(new, 2) == rng(orig, 1), f"V2 panel range mismatch {rng(new, 2)} vs {rng(orig, 1)}")
    check([rng(new, n, False) for n in range(3, nv + 2)] == orig_v[1:], "V3/V4 drift after V2 append")
    check(protected(new) == base, "protected drift after V2 append")
    if nv == 3:
        check(rng(new, 4) == rng(orig, 3), "GIF ranges mismatch")
        step("GIF preset")
        for x in items(new, "video", 4):
            for k in ("ZoomX", "ZoomY", "Tilt"):
                set_float(x, k, SHORT[k], 0.5 if k == "Tilt" else 0.005)
        log["gifs"] = [{k: x.GetProperty(k) for k in ("ZoomX", "ZoomY", "Pan", "Tilt", "ZoomGang")} for x in items(new, "video", 4)]

    step("V1/V2 transforms")
    for n, props in ((1, game), (2, avatar)):
        for x in items(new, "video", n):
            for k, v in props.items():
                set_float(x, k, v, 0.5 if k in POS_TOL else 0.005)
    log["v1_readback"] = [{k: x.GetProperty(k) for k in PROPS} for x in items(new, "video", 1)]
    log["v2_readback"] = [{k: x.GetProperty(k) for k in PROPS} for x in items(new, "video", 2)]

    step("focus Fusion")
    log["focus_before"], log["focus_readback"] = [], []
    for x in items(new, "video", 3):
        t = fusion_transform(x)
        log["focus_before"].append({k: t.GetInput(k) for k in ("Size", "Center", "Pivot", "Edges")})
        for k in ("Size", "Pivot", "Center"):
            t.SetInput(k, focus[k])
            time.sleep(0.5)
        time.sleep(DELAY)
        rb = {k: t.GetInput(k) for k in ("Size", "Center", "Pivot", "Edges")}
        log["focus_readback"].append(rb)
        check(abs(float(rb["Size"]) - focus["Size"]) < 1e-6 and
              all(abs(float(rb[k][i]) - focus[k][i]) < 1e-6 for k in ("Pivot", "Center") for i in (1, 2)), f"focus readback {rb}")

    for n, nm in ((1, "Game Top"), (2, "VTuber Bottom"), (3, "VTUBER_FOCUS"), (4, "ENRICH_GIF"))[:nv + 1]:
        new.SetTrackName("video", n, nm)
        time.sleep(0.3)
    check(protected(new) == base, "protected drift at end of build")
    step("save")
    check(pm.SaveProject(), "SaveProject failed")
    time.sleep(DELAY)
    log["saved"] = True
    return new, base_sig


def verify(p, orig, new, base_sig, pl):
    activate(p, orig)
    res = {"original_vs_baseline_diffs": diff(base_sig, stable_sig(orig))}
    po = protected(orig)
    activate(p, new)
    pn = protected(new)
    res["subtitles_equal"], res["subtitle_count"] = po["sub"] == pn["sub"], [len(po["sub"]), len(pn["sub"])]
    res["audio_equal"], res["audio_count"] = po["audio"] == pn["audio"], [len(po["audio"]), len(pn["audio"])]
    res["v1_equal"] = po["v1"] == pn["v1"]
    res["range_fps"] = [po["range"], pn["range"], po["fps"], pn["fps"]]
    res["settings_ok"] = all(str(new.GetSetting(k)) == v for k, v in RASTER)
    res["focus_equal"] = rng(orig, 2, False) == rng(new, 3, False)
    res["gif_equal"] = rng(orig, 3) == rng(new, 4)
    res["v2_equal_v1_range"] = rng(new, 2) == rng(orig, 1)
    res["tracks"] = {k: new.GetTrackCount(k) for k in ("video", "audio", "subtitle")}
    want_tracks = {"video": pl["nv"] + 1, "audio": orig.GetTrackCount("audio"), "subtitle": orig.GetTrackCount("subtitle")}
    res["focus_fusion"] = [{k: fusion_transform(x).GetInput(k) for k in ("Size", "Pivot", "Center")} for x in items(new, "video", 3)]
    off = []
    for n in range(1, new.GetTrackCount("video") + 1):
        for x in items(new, "video", n):
            m = x.GetMediaPoolItem()
            if m is not None and str(m.GetClipProperty("Online Status") or "Online").lower().startswith("off"):
                off.append(x.GetName())
    res["offline"] = off
    res["ok"] = (not res["original_vs_baseline_diffs"] and res["subtitles_equal"] and res["audio_equal"] and res["v1_equal"]
                 and po["range"] == pn["range"] and float(po["fps"]) == float(pn["fps"]) == 60.0 and res["settings_ok"]
                 and res["focus_equal"] and res["gif_equal"] and res["v2_equal_v1_range"] and not off
                 and res["tracks"] == want_tracks and len(res["focus_fusion"]) == len(pl["focus"]))
    return res


def source_frame(item_list, f, dst):
    """Clean ffmpeg decode (read-only) of the V1 source frame shown at record frame f."""
    it = next(x for x in item_list if x[1] <= f < x[2])
    fps = it[6] if len(it) > 6 else 60.0  # source fps (record frames are 60 fps)
    sf = it[3] + int((f - it[1]) * fps / 60.0)
    if not dst.exists():
        # A single-frame `-ss` seek returned a neighbouring frame deep into Becastled 002 (idx 32: corr 0.80 at every
        # +/-4 offset); seeking PRE frames earlier and decoding forward lands exactly (corr 0.9998).
        pre = min(30, sf)
        raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{(sf - pre) / fps:.4f}", "-i", it[5],
                              "-frames:v", str(pre + 1), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                             capture_output=True, check=True, timeout=300).stdout
        frames = np.frombuffer(raw, np.uint8).reshape(-1, SRC_H, 1920, 3)
        Image.fromarray(frames[pre]).save(dst)
    return Image.open(dst).convert("RGB"), sf


def expected_canvas(src, anchor, focus=False):
    """The 9:16 frame the layout should produce from a clean source frame (no GIF/subtitle)."""
    _, _, meta, fo = stream_params(anchor)
    x0g = anchor["game_x0"]
    top = src.crop((x0g, 0, x0g + CANVAS_W / GAME_SCALE, SRC_H)).resize((CANVAS_W, SPLIT_Y), Image.BILINEAR)
    s = meta["scale"]
    low = src.crop((meta["x0"], meta["y0"], meta["x0"] + CANVAS_W / s, SRC_H)).resize((CANVAS_W, CANVAS_H - SPLIT_Y),
                                                                                     Image.BILINEAR)
    comp = Image.new("RGB", (CANVAS_W, CANVAS_H))
    comp.paste(top, (0, 0))
    comp.paste(low, (0, SPLIT_Y))
    if focus:  # Fusion Transform: scale about Pivot (kept fixed), then offset by Center - 0.5 (y up)
        S = fo["Size"]
        px, py = fo["Pivot"][1] * CANVAS_W, (1 - fo["Pivot"][2]) * CANVAS_H
        tx, ty = px + (fo["Center"][1] - 0.5) * CANVAS_W, py - (fo["Center"][2] - 0.5) * CANVAS_H
        comp = comp.transform((CANVAS_W, CANVAS_H), Image.AFFINE, (1 / S, 0, px - tx / S, 0, 1 / S, py - ty / S),
                              Image.BILINEAR)
    return comp


def match(still, exp, box):
    a = np.asarray(Image.open(still).convert("L").crop(box).resize((135, 120)), float)
    b = np.asarray(exp.convert("L").crop(box).resize((135, 120)), float)
    return {"mad": round(float(np.abs(a - b).mean()), 2), "corr": round(float(np.corrcoef(a.ravel(), b.ravel())[0, 1]), 4)}


def facecam_source(src, game_x0):
    """Deep-blue avatar hair in the source facecam box (gated >= 3000 px) vs the strip right of game_x0 (info)."""
    a = np.asarray(src).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = (b > 110) & (r < 70) & (g < 70) & (b > r + 60)
    return {"hair_px_facecam_box": int(m[500:1000, :int(game_x0)].sum()),
            "hair_px_right_of_game_x0": int(m[500:1000, int(game_x0):int(game_x0) + 150].sum())}


def avatar_metrics(path, y0):
    a = np.array(Image.open(path).convert("RGB")).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = (b > 110) & (r < 70) & (g < 70) & (b > r + 60)
    m[:y0] = False
    rows = np.where(m.sum(axis=1) > 8)[0]
    return {"deep_blue_px": int(m.sum()), "head_top_y": int(rows.min()) if len(rows) else None}


def stills(p, new, pl, reuse=False):
    d = OUT / str(pl["index"])
    busy = [(s - 30, e + 30) for s, e in pl["focus"]] + [(g[1] - 30, g[2] + 30) for g in pl["gifs"]]
    end = new.GetEndFrame()
    normal = next((f for f in list(range(600, end - 30, 60)) + list(range(60, 600, 60))
                   if not any(a <= f <= b for a, b in busy)), None)
    frames = [("normal", normal)]
    if pl["gifs"]:
        frames.append(("gif", (pl["gifs"][0][1] + pl["gifs"][0][2]) // 2))
    if pl["focus"]:
        s, e = pl["focus"][0]
        frames.append(("focus", (s + e) // 2))
    if len(pl["v1src"]) > 1:  # several V1 items: one still inside each item and one on each side of every cut
        for k, it in enumerate(pl["v1src"]):
            frames.append((f"v1item{k + 1}", (it[1] + it[2]) // 2))
            if k:
                frames += [(f"cut{k}_before", it[1] - 3), (f"cut{k}_after", it[1] + 3)]
    res, ok = {}, normal is not None
    anchor = STREAMS[pl["stream"]]
    for label, f in frames:
        if f is None:
            continue
        path = d / f"{label}_{f}.png"
        if not reuse or not path.exists():
            path = export(p, new, f, path)
        pc = pixel_check(path)
        av = avatar_metrics(path, 0 if label == "focus" else 960)  # informational (blue scenery can fool it)
        in_focus = label == "focus" or any(s <= f < e for s, e in pl["focus"])  # a GIF can sit inside a focus clip
        # ffmpeg -ss can land one frame off Resolve's frame (fast pans: corr 0.957 vs 0.985 one frame earlier), so
        # take the best of record frames f-1, f, f+1 per region; a wrong layout scores ~0 at every offset.
        best = None
        for off in (0, -1, 1):
            g = min(max(f + off, 0), new.GetEndFrame() - 1)
            s_img, s_f = source_frame(pl["v1src"], g, d / (f"src_{label}_{f}.png" if off == 0 else f"src_{label}_{f}_{off:+d}.png"))
            exp = expected_canvas(s_img, anchor, in_focus)
            m = (match(path, exp, (0, 0, CANVAS_W, SPLIT_Y)), match(path, exp, (0, SPLIT_Y, CANVAS_W, CANVAS_H)), off)
            if off == 0:
                src, sf = s_img, s_f
            if best is None or m[0]["corr"] + m[1]["corr"] > best[0]["corr"] + best[1]["corr"]:
                best = m
            if best[0]["corr"] >= 0.99 and best[1]["corr"] >= 0.99:
                break
        top, low = best[0], best[1]
        res[label] = {"path": str(path.relative_to(ROOT)), "frame": f, "source_frame": sf, **pc, **av,
                      "match_top": top, "match_low": low, "match_frame_offset": best[2],
                      **facecam_source(src, anchor["game_x0"])}
        # Gate: raster, no black rows where the avatar sits, rendered frame == layout rebuilt from the clean source,
        # avatar present in the source facecam box. The GIF still's top panel carries the GIF, so only its lower
        # panel is gated.
        good = (pc["size"] == [1080, 1920] and pc["bottom_dark_rows"] == 0 and low["corr"] >= MATCH_CORR
                and low["mad"] <= MATCH_MAD and (label == "gif" or (top["corr"] >= MATCH_CORR and top["mad"] <= MATCH_MAD))
                and res[label]["hair_px_facecam_box"] >= 3000)
        res[label]["ok"] = bool(good)
        ok = ok and good
    res["ok"] = ok
    return res


def append_result(entry):
    data = json.loads(RESULTS.read_text(encoding="utf-8")) if RESULTS.exists() else []
    data.append(entry)
    RESULTS.write_text(json.dumps(data, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


def reverify(targets):
    """Read-only re-check of already-built `_9x16` timelines (verify + stills gate on the exported stills)."""
    r = connect_resolve()
    pm, p = health(r)
    rc = 0
    with preserved_state(r):
        for idx, pre in targets:
            idx = int(idx)
            orig, pl = plan(p, idx, pre, existing_ok=True)
            news = find_name(p, pl["target"])
            check(len(news) == 1, f"expected one {pl['target']}")
            new = news[0]
            check([new.GetSetting("timelineResolutionWidth"), new.GetSetting("timelineResolutionHeight")] == ["1080", "1920"], "raster")
            base = normalize(json.loads((OUT / str(idx) / "baseline_original.json").read_text(encoding="utf-8")))
            v = verify(p, orig, new, base, pl)
            st = stills(p, new, pl, reuse=True)
            entry = {"index": idx, "time": time.strftime("%Y-%m-%d %H:%M:%S"), "name": pl["name"], "id": pl["id"],
                     "target": pl["target"], "new_id": new.GetUniqueId(), "stream": pl["stream"], "mode": "reverify (read-only)",
                     "verify": v, "stills": st, "status": "built" if v["ok"] and st["ok"] else "FAILED_CHECK"}
            append_result(entry)
            print("REVERIFY", idx, entry["status"], new.GetUniqueId(), "verify_ok", v["ok"], v["original_vs_baseline_diffs"][:5],
                  {k: (x.get("match_top"), x.get("match_low"), x.get("hair_px_facecam_box"), x.get("ok"))
                   for k, x in st.items() if isinstance(x, dict)}, flush=True)
            rc |= entry["status"] != "built"
    return int(rc)


def main():
    apply = "--apply" in sys.argv
    existing = sys.argv[sys.argv.index("--existing") + 1] if "--existing" in sys.argv else None
    if "--reverify" in sys.argv:
        return reverify([a.split(":") for a in sys.argv[1:] if not a.startswith("--")])
    targets = [a.split(":") for a in sys.argv[1:] if not a.startswith("--") and ":" in a]
    check(not existing or len(targets) == 1, "--existing takes exactly one target")
    r = connect_resolve()
    pm, p = health(r)
    OUT.mkdir(parents=True, exist_ok=True)
    rc = 0
    with preserved_state(r):
        protect_ids = [PILOT_ID]  # _FAILED_BUILD_RETAINED (RETAINED_ID) was deleted at the user's request
        prot_before = read_protected(p, protect_ids)
        if apply:
            r.OpenPage("edit")
            time.sleep(2)
            check(r.GetCurrentPage() == "edit", "not on Edit page")
        for idx, pre in targets:
            idx = int(idx)
            pm, p = health(r)
            entry = {"index": idx, "time": time.strftime("%Y-%m-%d %H:%M:%S")}
            try:
                orig, pl = plan(p, idx, pre, existing_ok=bool(existing))
            except Flag as e:
                entry.update(status="flagged", reason=str(e), name=p.GetTimelineByIndex(idx).GetName(),
                             id=p.GetTimelineByIndex(idx).GetUniqueId())
                print("FLAGGED", idx, e, flush=True)
                if apply:
                    append_result(entry)
                continue
            entry.update(name=pl["name"], id=pl["id"], target=pl["target"], stream=pl["stream"],
                         focus=pl["focus"], gifs=[g[0] for g in pl["gifs"]])
            print("PLAN", json.dumps(pl, ensure_ascii=False), flush=True)
            if not apply:
                continue
            log = {}
            try:
                check(r.GetCurrentPage() == "edit", "not on Edit page")
                new, base_sig = build(r, pm, p, orig, pl, log, existing, "--late-activate" in sys.argv)
                step("verify")
                entry["new_id"] = log["new_id"]
                v = verify(p, orig, new, base_sig, pl)
                step("stills")
                s = stills(p, new, pl)
                entry.update(build=log, verify=v, stills=s, status="built" if v["ok"] and s["ok"] else "FAILED_CHECK")
            except Exception as e:  # noqa: BLE001 - recorded, then hard stop
                entry.update(build=log, status="ERROR", error=repr(e))
            append_result(entry)
            print("RESULT", idx, entry["status"], entry.get("new_id"), json.dumps(entry.get("stills", {}), default=str)[:900],
                  "verify_ok", entry.get("verify", {}).get("ok"), entry.get("error", ""), flush=True)
            if entry["status"] != "built":
                rc = 1
                break
        prot_after = read_protected(p, protect_ids)
        pd = {t: diff(prot_before[t], prot_after[t]) for t in protect_ids}
        print("PROTECTED_TIMELINES_DIFFS", {t[:8]: len(v) for t, v in pd.items()}, [x for v in pd.values() for x in v][:10], flush=True)
        if any(pd.values()):
            rc = 1
    print("PAGE_AFTER_RESTORE", r.GetCurrentPage(), p.GetCurrentTimeline().GetName(), flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
