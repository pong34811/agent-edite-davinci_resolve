"""Apply calibrated layout to the pilot _9x16 timeline ONLY and export 3 QC stills (scratch).

Rollback values for the previous state live in scratch/preflight_live.json.
"""
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import m2_convert_pilot as m2  # noqa: E402
import layout9x16 as L  # noqa: E402

PILOT_9X16_ID = "2b0779e3-6b5d-4fd2-91b3-2d55ffaed2a3"
CHECK = ["ZoomX", "ZoomY", "Pan", "Tilt", "CropTop", "CropBottom"]
OUT = os.path.abspath("scratch/pilot_iter3")
FRAMES = [("split_screen_normal", 216500), ("reaction_gif_safe", 218650), ("vtuber_focus_zoom", 219300)]


def main(export_only=False):
    resolve = m2.get_resolve()
    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    tl = m2.find_timeline_by_name(proj, m2.TARGET_NAME)
    assert tl.GetUniqueId() == PILOT_9X16_ID, "unexpected timeline id"
    assert proj.GetCurrentTimeline().GetUniqueId() == PILOT_9X16_ID
    entry_tc = tl.GetCurrentTimecode()
    v1 = tl.GetItemListInTrack("video", 1)[0]
    v2 = tl.GetItemListInTrack("video", 2)[0]
    v3 = tl.GetItemListInTrack("video", 3) or []
    if not export_only:
        L._set(v1, {**L.game_params(), "CropTop": 0.0, "CropLeft": 0.0, "CropRight": 0.0})
        L._set(v2, {**L.avatar_params(), "CropBottom": 0.0, "CropLeft": 0.0, "CropRight": 0.0})
        for adj in v3:
            comp = adj.GetFusionCompByIndex(1)
            for t in (comp.GetToolList() or {}).values():
                if "Transform" in t.GetAttrs().get("TOOLS_Name", ""):
                    t.SetInput("Size", L.FOCUS["Size"])
                    t.SetInput("Pivot", {1: L.FOCUS["Pivot"][0], 2: L.FOCUS["Pivot"][1], 3: 0.0})
                    t.SetInput("Center", {1: L.FOCUS["Center"][0], 2: L.FOCUS["Center"][1], 3: 0.0})
            time.sleep(0.3)
    print("V1", L.readback(v1, CHECK))
    print("V2", L.readback(v2, CHECK))
    for adj in v3:
        comp = adj.GetFusionCompByIndex(1)
        for t in (comp.GetToolList() or {}).values():
            if "Transform" in t.GetAttrs().get("TOOLS_Name", ""):
                print("V3", adj.GetStart(), t.GetInput("Size"), t.GetInput("Pivot"), t.GetInput("Center"))
    os.makedirs(OUT, exist_ok=True)
    for name, f in FRAMES:
        tl.SetCurrentTimecode(m2.frame_to_timecode(f, 60.0))
        time.sleep(0.5)
        p = os.path.join(OUT, f"{name}_{f}.png")
        print(name, proj.ExportCurrentFrameAsStill(p), os.path.exists(p))
        time.sleep(0.3)
    tl.SetCurrentTimecode(entry_tc)
    time.sleep(0.4)
    print("tc restored", tl.GetCurrentTimecode())


if __name__ == "__main__":
    main(export_only="--export-only" in sys.argv)
