"""16:9 talk-only timeline -> `<name>_9x16` (1080x1920): VTuber face crop fills the canvas.

For streams with no game panel (VTuber + chat full frame).  Per timeline: DuplicateTimeline -> raster
1080x1920 -> V1 zoomed/panned so a full-height 607 px source window centred on the VTuber's eyes fills the
canvas -> reaction GIFs (V2) re-placed upper-left.  Subtitles, audio, V1/V2 item ranges are never touched.
The original 16:9 timeline is never modified.  Layout maths follow scripts/layout9x16.py.

Usage:
  python scripts/convert_talk_9x16.py --project <project name> --ids ids.json --eyes eyes.json 2
  (positional: 1-based original timeline indexes; --cx overrides the eye centre x in source px)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import layout9x16 as L  # noqa: E402

SCRIPT_API = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
os.environ.setdefault("RESOLVE_SCRIPT_LIB", r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll")
sys.path.append(os.path.join(SCRIPT_API, "Modules"))
try:
    import DaVinciResolveScript as dvr  # noqa: E402
except ImportError:  # offline use (tests, dry maths)
    dvr = None

D = 1.2
GAP = 0.45
GIF_ZOOM = 0.42
GIF_CENTER = (260.0, 330.0)


BAR_ZOOM = 1.075   # extra zoom + shift so the source's bottom status bar (below src y~1015) is cropped out


def face_params(cx: float, bar_crop: bool = True) -> dict:
    """Window of the 1920x1080 source centred on cx, filling the 1080x1920 canvas (bottom bar cropped)."""
    k = (L.CANVAS_H / L.SRC_H) * (BAR_ZOOM if bar_crop else 1.0)   # canvas px per source px
    half = L.CANVAS_W / k / 2
    cx = min(max(cx, half), L.SRC_W - half)
    cy = 10.0 + (L.CANVAS_H / k) / 2 if bar_crop else L.SRC_H / 2   # window centre row (window bottom ~ src y 1015)
    tilt_px = (L.SRC_H * L.FIT) / L.CANVAS_H
    zoom = k / L.FIT
    return dict(ZoomX=zoom, ZoomY=zoom, Pan=(L.SRC_W / 2 - cx) * k, Tilt=-((L.SRC_H / 2 - cy) * k) / tilt_px)


def find_tl(proj, uid=None, name=None):
    for i in range(1, proj.GetTimelineCount() + 1):
        t = proj.GetTimelineByIndex(i)
        if (uid and t.GetUniqueId() == uid) or (name and t.GetName() == name):
            return t
    return None


def snapshot(t):
    items = lambda k, n: t.GetItemListInTrack(k, n) or []
    return {
        "V1": [(i.GetStart(), i.GetEnd(), i.GetSourceStartFrame(), i.GetSourceEndFrame()) for i in items("video", 1)],
        "V2": [(i.GetStart(), i.GetEnd(), i.GetName()) for i in items("video", 2)],
        "A": {n: [(i.GetStart(), i.GetEnd(), i.GetName(), i.GetProperty("AudioVolume")) for i in items("audio", n)]
              for n in range(1, t.GetTrackCount("audio") + 1)},
        "ST": [(i.GetStart(), i.GetEnd(), i.GetName()) for i in items("subtitle", 1)] if t.GetTrackCount("subtitle") else [],
        "len": (t.GetStartFrame(), t.GetEndFrame()),
    }


def setp(item, props):
    for k, v in props.items():
        time.sleep(GAP)
        ok = item.SetProperty(k, float(v))
        if not ok:
            time.sleep(GAP)
            ok = item.SetProperty(k, float(v))
        got = item.GetProperty(k)
        if not ok or abs(float(got) - float(v)) > 1e-3 * max(1, abs(float(v))):
            raise RuntimeError(f"{item.GetName()} {k}: set {v} got {got}")


def gif_params(w, h):
    fit = min(L.CANVAS_W / w, L.CANVAS_H / h)
    fw, fh = w * fit, h * fit
    return dict(ZoomX=GIF_ZOOM, ZoomY=GIF_ZOOM,
                Pan=(GIF_CENTER[0] - L.CANVAS_W / 2) / (fw / L.CANVAS_W),
                Tilt=-(GIF_CENTER[1] - L.CANVAS_H / 2) / (fh / L.CANVAS_H))


def convert(proj, pm, orig, cx, stills_dir):
    name = orig.GetName() + "_9x16"
    if find_tl(proj, name=name):
        raise SystemExit(f"{name} already exists; refusing to duplicate")
    before = snapshot(orig)
    assert proj.SetCurrentTimeline(orig); time.sleep(D)
    new = orig.DuplicateTimeline(name)
    if not new:
        raise RuntimeError("DuplicateTimeline failed")
    time.sleep(D); assert proj.SetCurrentTimeline(new); time.sleep(D)
    for k, v in (("useCustomSettings", "1"), ("timelineResolutionWidth", "1080"), ("timelineResolutionHeight", "1920"),
                 ("timelineOutputResMatchTimelineRes", "1"), ("timelineOutputResolutionWidth", "1080"),
                 ("timelineOutputResolutionHeight", "1920"), ("timelinePixelAspectRatio", "square"),
                 ("timelineInputResMismatchBehavior", "scaleToFit"), ("timelineOutputResMismatchBehavior", "scaleToFit")):
        new.SetSetting(k, v); time.sleep(0.2)
    assert (new.GetSetting("timelineResolutionWidth"), new.GetSetting("timelineResolutionHeight")) == ("1080", "1920")
    assert float(new.GetSetting("timelineFrameRate")) == float(orig.GetSetting("timelineFrameRate"))
    v1 = new.GetItemListInTrack("video", 1)[0]
    p = face_params(cx)
    setp(v1, p)
    print("V1", {k: round(v, 3) for k, v in p.items()}, "cx", cx)
    for g in new.GetItemListInTrack("video", 2) or []:
        w, h = [float(x) for x in g.GetMediaPoolItem().GetClipProperty("Resolution").split("x")]
        setp(g, gif_params(w, h))
    after = snapshot(new)
    same = {k: before[k] == after[k] for k in before}
    print("protected unchanged:", same)
    os.makedirs(stills_dir, exist_ok=True)
    fps = float(new.GetSetting("timelineFrameRate"))
    marks = [("mid", (new.GetStartFrame() + new.GetEndFrame()) // 2)]
    gifs = new.GetItemListInTrack("video", 2) or []
    if gifs:
        marks.append(("gif", gifs[0].GetStart() + 20))
    out = {}
    for label, f in marks:
        h, m, s, fr = int(f // fps // 3600), int(f // fps // 60 % 60), int(f // fps % 60), int(f % fps)
        time.sleep(D); new.SetCurrentTimecode(f"{h:02d}:{m:02d}:{s:02d}:{fr:02d}"); time.sleep(0.8)
        path = os.path.join(stills_dir, f"{name}_{label}.png")
        ok = proj.ExportCurrentFrameAsStill(path)
        out[label] = path if ok else None
    time.sleep(D); print("save", pm.SaveProject())
    return new, same, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("idx", type=int, nargs="+")
    ap.add_argument("--project", required=True)
    ap.add_argument("--ids", required=True)
    ap.add_argument("--eyes", required=True)
    ap.add_argument("--cx", type=float)
    ap.add_argument("--stills", default="stills")
    a = ap.parse_args()
    r = dvr.scriptapp("Resolve"); pm = r.GetProjectManager(); proj = pm.GetCurrentProject()
    assert proj.GetName() == a.project, proj.GetName()
    ids = json.load(open(a.ids)); eyes = json.load(open(a.eyes))
    page = r.GetCurrentPage(); cur = proj.GetCurrentTimeline()
    for i in a.idx:
        orig = find_tl(proj, uid=ids[str(i)]["orig"])
        pts = [q[0] for q in eyes[str(i)] if q and q[2] >= 20]
        cx = a.cx or sorted(pts)[len(pts) // 2]
        _, same, stills = convert(proj, pm, orig, cx, a.stills)
        print(i, "RESULT", all(same.values()), stills)
        if not all(same.values()):
            raise SystemExit("protected content changed; stopping")
    proj.SetCurrentTimeline(cur); r.OpenPage(page); pm.SaveProject()


if __name__ == "__main__":
    main()
