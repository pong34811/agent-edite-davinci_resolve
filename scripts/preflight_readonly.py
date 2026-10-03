"""Read-only live preflight for the 9:16 conversion. Performs NO writes to Resolve.

Captures active project/timeline/page/playhead, lists all timelines (raster, fps,
duration, track counts, subtitle cue count) and compares the 30 originals with
the M1 baseline. Dumps pilot _9x16 item transforms. Output: JSON to stdout and
scratch/preflight_live.json.
"""
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import m2_convert_pilot as m2  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

PROPS = ["ZoomX", "ZoomY", "ZoomGang", "Pan", "Tilt", "CropTop", "CropBottom", "CropLeft", "CropRight", "Pitch", "Yaw", "RotationAngle", "AnchorPointX", "AnchorPointY"]


def main():
    resolve = m2.get_resolve()
    if not resolve:
        print(json.dumps({"error": "cannot connect to Resolve"}))
        return 1
    out = {"version": resolve.GetVersionString(), "product": resolve.GetProductName()}
    out["page"] = resolve.GetCurrentPage()
    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    out["project"] = proj.GetName()
    out["project_id"] = proj.GetUniqueId()
    cur = proj.GetCurrentTimeline()
    out["active_timeline"] = {"name": cur.GetName(), "id": cur.GetUniqueId(), "timecode": cur.GetCurrentTimecode()} if cur else None
    out["project_settings"] = {k: proj.GetSetting(k) for k in ("timelineFrameRate", "timelinePlaybackFrameRate", "timelineResolutionWidth", "timelineResolutionHeight")}

    base = m2.json.load(open(m2.BASELINE_JSON_PATH, encoding="utf-8"))
    base_by_id = {t["timeline_id"]: t for t in base["timelines"]}

    tls = []
    n = proj.GetTimelineCount()
    for i in range(1, n + 1):
        tl = proj.GetTimelineByIndex(i)
        row = {
            "index": i,
            "name": tl.GetName(),
            "id": tl.GetUniqueId(),
            "fps": tl.GetSetting("timelineFrameRate"),
            "w": tl.GetSetting("timelineResolutionWidth"),
            "h": tl.GetSetting("timelineResolutionHeight"),
            "start": tl.GetStartFrame(),
            "end": tl.GetEndFrame(),
            "video_tracks": tl.GetTrackCount("video"),
            "audio_tracks": tl.GetTrackCount("audio"),
            "subtitle_tracks": tl.GetTrackCount("subtitle"),
            "subtitle_cues": len(tl.GetItemListInTrack("subtitle", 1) or []) if tl.GetTrackCount("subtitle") else 0,
        }
        b = base_by_id.get(row["id"])
        if b:
            row["baseline_match"] = (
                b["resolution_width"] == int(row["w"]) and b["resolution_height"] == int(row["h"])
                and b["start_frame"] == row["start"] and b["end_frame"] == row["end"]
                and next(s for s in base["timelines_summary"] if s["id"] == row["id"])["subtitle_cues"] == row["subtitle_cues"]
            )
        tls.append(row)
    out["timelines"] = tls

    tgt = next((t for t in tls if t["name"] == m2.TARGET_NAME), None)
    if tgt:
        tl = proj.GetTimelineByIndex(tgt["index"])
        tracks = {}
        for tr in range(1, tl.GetTrackCount("video") + 1):
            items = []
            for it in tl.GetItemListInTrack("video", tr) or []:
                d = {"name": it.GetName(), "start": it.GetStart(), "end": it.GetEnd(), "id": it.GetUniqueId()}
                d["props"] = {p: m2.get_item_property(it, p) for p in PROPS}
                if tr == 3:
                    try:
                        comp = it.GetFusionCompByIndex(1)
                        tools = comp.GetToolList() or {} if comp else {}
                        d["fusion"] = {
                            t.GetAttrs().get("TOOLS_Name"): {
                                "Center": t.GetInput("Center"), "Pivot": t.GetInput("Pivot"), "Size": t.GetInput("Size"),
                            }
                            for t in tools.values()
                            if "Transform" in t.GetAttrs().get("TOOLS_Name", "")
                        }
                    except Exception as exc:  # noqa: BLE001
                        d["fusion_error"] = str(exc)
                items.append(d)
            tracks[tr] = items
        out["target_tracks"] = tracks
    os.makedirs("scratch", exist_ok=True)
    json.dump(out, open("scratch/preflight_live.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps(out, ensure_ascii=False, indent=1, default=str)[:9000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
