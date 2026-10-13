"""16:9 game+facecam timeline -> `<name>_9x16`: game panel on top (y 0..960), facecam panel below.

Duplicate -> raster 1080x1920 -> V1 = game panel (layout9x16.game_params) -> V3 (new) = the same clip again
cropped to the facecam region (layout9x16.avatar_params), reaction GIFs stay on V2 and are re-placed upper-left.
Subtitles, audio, V1/V2 ranges untouched; the original timeline is never modified.

Usage: python scripts/convert_game_9x16.py --project NAME --ids ids.json --stills DIR --scale 1.6 --cx 240 IDX
"""
import argparse, json, os, sys, time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import layout9x16 as L
import convert_talk_9x16 as T

D = T.D


def face_panel(scale, cx, top=800.0):
    """Facecam panel covering canvas y `top`..1920; shows the bottom-left facecam at `scale` canvas px per source px."""
    hp = L.CANVAS_H - top
    zoom = scale / L.FIT
    w_src, h_src = L.CANVAS_W / scale, hp / scale
    y0 = L.SRC_H - h_src
    x0 = min(max(cx - w_src / 2, 0.0), L.SRC_W - w_src)
    cxs, cys = x0 + w_src / 2, y0 + h_src / 2
    center_x = L.CANVAS_W / 2 + (L.SRC_W / 2 - cxs) * scale
    center_y = top + hp / 2 + (L.SRC_H / 2 - cys) * scale
    return dict(ZoomX=zoom, ZoomY=zoom, Pan=L._pan(center_x), Tilt=L._tilt(center_y), CropTop=y0 * L.FIT)


def convert(r, pm, proj, orig, scale, cx, stills, top=800.0, game_scale=None, game_cx=960.0):
    name = orig.GetName() + "_9x16"
    if T.find_tl(proj, name=name):
        raise SystemExit(f"{name} exists")
    before = T.snapshot(orig)
    assert proj.SetCurrentTimeline(orig); time.sleep(D)
    new = orig.DuplicateTimeline(name); time.sleep(D)
    assert new and proj.SetCurrentTimeline(new); time.sleep(D)
    for k, v in (("useCustomSettings", "1"), ("timelineResolutionWidth", "1080"), ("timelineResolutionHeight", "1920"),
                 ("timelineOutputResMatchTimelineRes", "1"), ("timelineOutputResolutionWidth", "1080"),
                 ("timelineOutputResolutionHeight", "1920"), ("timelinePixelAspectRatio", "square"),
                 ("timelineInputResMismatchBehavior", "scaleToFit"), ("timelineOutputResMismatchBehavior", "scaleToFit")):
        new.SetSetting(k, v); time.sleep(0.2)
    assert (new.GetSetting("timelineResolutionWidth"), new.GetSetting("timelineResolutionHeight")) == ("1080", "1920")
    v1 = new.GetItemListInTrack("video", 1)[0]
    T.setp(v1, L.game_params() if not game_scale else dict(ZoomX=game_scale / L.FIT, ZoomY=game_scale / L.FIT, Pan=(L.SRC_W / 2 - game_cx) * game_scale, Tilt=L._tilt(L.SRC_H / 2 * game_scale)))
    mpi = v1.GetMediaPoolItem(); off = v1.GetLeftOffset(); dur = v1.GetDuration(); st = v1.GetStart()
    time.sleep(D)
    if new.GetTrackCount("video") < 3:
        assert new.AddTrack("video"); time.sleep(D)
    mp = proj.GetMediaPool()
    got = mp.AppendToTimeline([{"mediaPoolItem": mpi, "startFrame": off, "endFrame": off + dur,
                                "mediaType": 1, "trackIndex": 3, "recordFrame": st}])
    assert got; time.sleep(D)
    v3 = new.GetItemListInTrack("video", 3)[0]
    assert (v3.GetStart(), v3.GetEnd()) == (v1.GetStart(), v1.GetEnd()), ((v3.GetStart(), v3.GetEnd()), (v1.GetStart(), v1.GetEnd()))
    T.setp(v3, face_panel(scale, cx, top))
    new.SetTrackName("video", 1, "Game Top"); time.sleep(0.5); new.SetTrackName("video", 3, "VTuber Bottom")
    for g in new.GetItemListInTrack("video", 2) or []:
        w, h = [float(x) for x in g.GetMediaPoolItem().GetClipProperty("Resolution").split("x")]
        T.setp(g, T.gif_params(w, h))
    after = T.snapshot(new)
    same = {k: before[k] == after[k] for k in before}
    print("protected unchanged:", same)
    os.makedirs(stills, exist_ok=True)
    fps = float(new.GetSetting("timelineFrameRate")); outs = {}
    gifs = new.GetItemListInTrack("video", 2) or []
    for label, f in (("a", 300), ("b", 1200), ("gif", gifs[0].GetStart() + 20 if gifs else 600)):
        time.sleep(D); new.SetCurrentTimecode("00:00:%02d:%02d" % (int(f // fps), int(f % fps))); time.sleep(0.8)
        p = os.path.join(stills, f"g{orig.GetUniqueId()[:6]}_{label}.png"); proj.ExportCurrentFrameAsStill(p); outs[label] = p
    time.sleep(D); print("save", pm.SaveProject())
    return same, outs


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("idx", type=int, nargs="+")
    ap.add_argument("--project", required=True); ap.add_argument("--ids", required=True)
    ap.add_argument("--stills", default="stills"); ap.add_argument("--scale", type=float, default=2.2)
    ap.add_argument("--cx", type=float, default=260.0); ap.add_argument("--top", type=float, default=800.0); ap.add_argument("--game-cx", type=float, default=960.0); ap.add_argument("--game-scale", type=float, default=None, help="show the whole source width centre at this scale from canvas y=0 (default: layout9x16 crop)")
    a = ap.parse_args()
    r = T.dvr.scriptapp("Resolve"); pm = r.GetProjectManager(); proj = pm.GetCurrentProject()
    assert proj.GetName() == a.project
    ids = json.load(open(a.ids)); page = r.GetCurrentPage(); cur = proj.GetCurrentTimeline()
    for i in a.idx:
        same, outs = convert(r, pm, proj, T.find_tl(proj, uid=ids[str(i)]["orig"]), a.scale, a.cx, a.stills, a.top, a.game_scale, a.game_cx)
        print(i, "RESULT", all(same.values()), outs)
        if not all(same.values()): raise SystemExit("protected content changed")
    proj.SetCurrentTimeline(cur); r.OpenPage(page); pm.SaveProject()


if __name__ == "__main__":
    main()
