
def apply_plan(t, pl, log=print):
    """t must be an ACTIVE timeline. Adds V2 REACTIONS, A2 SFX, A3 BGM only if absent; skips existing path+frame."""
    fps = float(t.GetSetting("timelineFrameRate")); tl_end = t.GetEndFrame()
    W_, H_ = 1920, 1080
    # lock protected tracks
    locks = {}
    for typ in ("video", "audio", "subtitle"):
        for k in range(1, t.GetTrackCount(typ)+1):
            locks[(typ, k)] = t.GetIsTrackLocked(typ, k)
    base = {typ: t.GetTrackCount(typ) for typ in ("video", "audio", "subtitle")}
    log("base tracks", base, "locks", locks)
    for (typ, k), v in locks.items():
        time.sleep(0.3); t.SetTrackLock(typ, k, True)
    try:
        if base["video"] < 2:
            time.sleep(D); assert t.AddTrack("video");
        if base["audio"] < 3:
            for _ in range(3 - base["audio"]):
                time.sleep(D); assert t.AddTrack("audio", "stereo")
        time.sleep(D)
        t.SetTrackName("video", 2, "REACTIONS"); t.SetTrackName("audio", 2, "SFX"); t.SetTrackName("audio", 3, "BGM")
        log("tracks now", {typ: t.GetTrackCount(typ) for typ in ("video", "audio", "subtitle")})
        paths = [os.path.join(B, pl["bgm"])] + [os.path.join(S, x["file"]) for x in pl["sfx"]] + [os.path.join(G, x["file"]) for x in pl["gif"]]
        m, f = ensure_imported(paths)
        def existing(typ, k):
            return {(it.GetName(), it.GetStart()) for it in (t.GetItemListInTrack(typ, k) or [])}
        res = {"bgm": None, "sfx": [], "gif": []}
        # BGM
        bpath = os.path.join(B, pl["bgm"]); bc = m[bpath]
        if not existing("audio", 3):
            end = int(round((tl_end - t.GetStartFrame()) ))
            time.sleep(D)
            got = mp.AppendToTimeline([{"mediaPoolItem": bc, "startFrame": 0, "endFrame": end, "mediaType": 2, "trackIndex": 3, "recordFrame": t.GetStartFrame()}])
            log("bgm append", bool(got))
        # SFX
        ex = existing("audio", 2)
        for x in pl["sfx"]:
            c = m[os.path.join(S, x["file"])]
            if (x["file"], x["frame"]) in {(n.rsplit(".",1)[0] if False else n, s) for n, s in ex} or any(s == x["frame"] for _, s in ex):
                log("skip sfx", x["frame"]); continue
            n = int(min(x["dur"], 3.0) * fps) - 1
            time.sleep(0.5)
            got = mp.AppendToTimeline([{"mediaPoolItem": c, "startFrame": 0, "endFrame": n, "mediaType": 2, "trackIndex": 2, "recordFrame": x["frame"]}])
            log("sfx", x["frame"], x["file"][:25], bool(got))
        # GIF
        ex = existing("video", 2)
        for x in pl["gif"]:
            c = m[os.path.join(G, x["file"])]
            if any(s == x["frame"] for _, s in ex):
                log("skip gif", x["frame"]); continue
            sf = float(c.GetClipProperty("FPS")); fr = int(c.GetClipProperty("Frames"))
            n = min(fr, max(1, int(round(2.0 * sf))))
            time.sleep(0.5)
            got = mp.AppendToTimeline([{"mediaPoolItem": c, "startFrame": 0, "endFrame": n - 1, "mediaType": 1, "trackIndex": 2, "recordFrame": x["frame"]}])
            log("gif", x["frame"], x["file"][:25], bool(got), "srcframes", n)
    finally:
        time.sleep(D)
        for (typ, k), v in locks.items():
            t.SetTrackLock(typ, k, v); time.sleep(0.2)
    return locks

def place_and_mix(t, pl, log=print):
    fps = float(t.GetSetting("timelineFrameRate"))
    # BGM
    for it in t.GetItemListInTrack("audio", 3) or []:
        time.sleep(0.5); log("bgm vol", it.SetProperty("AudioVolume", float(pl["bgm_gain"])), "fades", it.SetFades({"FadeIn": 60, "FadeOut": 180}))
    gains = {x["frame"]: min(0.0, x["gain"]) for x in pl["sfx"]}
    for it in t.GetItemListInTrack("audio", 2) or []:
        g = gains.get(it.GetStart())
        time.sleep(0.5)
        ok = it.SetProperty("AudioVolume", float(g if g is not None else -12.0))
        ok2 = it.SetFades({"FadeIn": 0, "FadeOut": 9}) if it.GetDuration() >= 120 else True
        log("sfx vol", it.GetStart(), g, ok, ok2)
    meta = {x["frame"]: x for x in pl["gif"]}
    for it in t.GetItemListInTrack("video", 2) or []:
        rw, rh = [float(v) for v in it.GetMediaPoolItem().GetClipProperty("Resolution").split("x")]
        fit = min(1920 / rw, 1080 / rh); fw, fh = rw * fit, rh * fit
        s = min(420 / fw, 300 / fh)
        ow, oh = fw * s, fh * s
        # measured on this build: on-screen shift px = Pan*fw/1920 (X), Tilt*fh/1080 (Y, + is up)
        pan = (-960 + 40 + ow / 2) * 1920 / fw; tilt = (540 - 40 - oh / 2) * 1080 / fh
        time.sleep(0.5)
        r1 = it.SetProperty("ZoomX", float(s)); r2 = it.SetProperty("ZoomY", float(s))
        r3 = it.SetProperty("Pan", float(pan)); r4 = it.SetProperty("Tilt", float(tilt))
        r5 = it.SetFades({"FadeIn": 6, "FadeOut": 6}) if hasattr(it, "SetFades") else None
        log("gif xform", it.GetStart(), round(s, 3), round(pan), round(tilt), r1, r2, r3, r4, r5)

def audit(t):
    out = {}
    for typ, k in (("video", 1), ("video", 2), ("audio", 1), ("audio", 2), ("audio", 3)):
        if k > t.GetTrackCount(typ): continue
        rows = []
        for it in t.GetItemListInTrack(typ, k) or []:
            row = {"n": it.GetName()[:28], "s": it.GetStart(), "e": it.GetEnd(), "d": it.GetDuration()}
            if typ == "audio" or k == 2:
                row["vol"] = it.GetProperty("AudioVolume") if typ == "audio" else None
                if typ == "video": row.update({"zx": it.GetProperty("ZoomX"), "pan": it.GetProperty("Pan"), "tilt": it.GetProperty("Tilt")})
                row["fades"] = it.GetFades()
            rows.append(row)
        out[f"{typ[0].upper()}{k}"] = rows
    out["ST1"] = len(t.GetItemListInTrack("subtitle", 1) or [])
    out["names"] = {f"{typ}{k}": t.GetTrackName(typ, k) for typ in ("video", "audio") for k in range(1, t.GetTrackCount(typ)+1)}
    return out
