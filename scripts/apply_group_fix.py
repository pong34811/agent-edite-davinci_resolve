"""Apply the verified source-right-crop fix to one timeline by track name.

Reused verified geometry (same camera/overlay template as the approved
armigon-2026-09 pilot/promotion): GAME_CROP, SUBJECT_CROP, FULLSCREEN_CROP
from scripts/vertical_layout_repair_pilot.py. Looks up tracks by name
("Game Top", "VTuber Bottom", "VTuber Focus Fullscreen") instead of a
hardcoded index, since track counts differ by timeline (some have no
fullscreen-focus track).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from scripts.resolve_common import require_resolve, preserved_state
from scripts.armigon_9x16_batch_one import protected_signature, set_clip_transform, dimensions
from scripts.vertical_layout_repair_pilot import GAME_CROP, SUBJECT_CROP, FULLSCREEN_CROP, layout_properties

OUT = Path(".hermes/reports/vertical-layout-qc/group-calibration")
OUT.mkdir(parents=True, exist_ok=True)
LOG = OUT / "batch-apply-log.json"


def track_index_by_name(tl, kind, name):
    for i in range(1, tl.GetTrackCount(kind) + 1):
        if tl.GetTrackName(kind, i) == name:
            return i
    return None


def bypass_mask(item):
    if item.GetFusionCompCount() < 1:
        return False
    comp = item.GetFusionCompByIndex(1)
    tools = {z.GetAttrs().get("TOOLS_Name"): z for z in (comp.GetToolList(False) or {}).values()}
    mi = tools.get("MediaIn1")
    if mi is None:
        return False
    port = next((v for v in (mi.GetInputList() or {}).values()
                 if v.GetAttrs().get("INPS_ID") == "EffectMask"), None)
    if port is None or port.GetConnectedOutput() is None:
        return False
    mi.ConnectInput("EffectMask", None)
    time.sleep(0.4)
    port2 = next(v for v in (mi.GetInputList() or {}).values()
                 if v.GetAttrs().get("INPS_ID") == "EffectMask")
    assert port2.GetConnectedOutput() is None, "mask disconnect failed"
    return True


def apply_fix(timeline_id):
    r = require_resolve()
    pm = r.GetProjectManager()
    p = pm.GetCurrentProject()
    assert p.GetUniqueId() == "9a7d3e92-e44c-4ba4-afba-7c2dbe1090e1"
    assert not p.IsRenderingInProgress()
    record = {"timeline_id": timeline_id}
    with preserved_state(r):
        t = next((p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1)
                   if p.GetTimelineByIndex(i).GetUniqueId() == timeline_id), None)
        assert t is not None, "timeline not found"
        record["name"] = t.GetName()
        assert p.SetCurrentTimeline(t)
        time.sleep(0.5)
        pb = protected_signature(t)

        v1_idx = track_index_by_name(t, "video", "Game Top")
        v3_idx = track_index_by_name(t, "video", "VTuber Bottom")
        v6_idx = track_index_by_name(t, "video", "VTuber Focus Fullscreen")
        assert v1_idx and v3_idx, "missing Game Top / VTuber Bottom tracks"

        v1 = t.GetItemListInTrack("video", v1_idx)[0]
        v3 = t.GetItemListInTrack("video", v3_idx)[0]
        assert dimensions(v1) == (1280, 702) and dimensions(v3) == (1280, 702)

        locks = {}
        for idx in (v1_idx, v3_idx) + ((v6_idx,) if v6_idx else ()):
            locks[idx] = t.GetIsTrackLocked("video", idx)
            if locks[idx]:
                assert t.SetTrackLock("video", idx, False)
                time.sleep(1.0)
        try:
            record["v1_mask_bypassed"] = bypass_mask(v1)
            record["v1_properties"] = set_clip_transform(v1, layout_properties(GAME_CROP, 0.0, 960.0))
            record["v3_mask_bypassed"] = bypass_mask(v3)
            record["v3_properties"] = set_clip_transform(v3, layout_properties(SUBJECT_CROP, 960.0, 960.0))
            if v6_idx:
                v6 = t.GetItemListInTrack("video", v6_idx)[0]
                if dimensions(v6) == (1280, 702):
                    record["v6_properties"] = set_clip_transform(
                        v6, layout_properties(FULLSCREEN_CROP, 0.0, 1920.0))
                else:
                    record["v6_skipped"] = f"unexpected dims {dimensions(v6)}"
        finally:
            for idx, was_locked in locks.items():
                if was_locked:
                    assert t.SetTrackLock("video", idx, True)
                    time.sleep(1.0)

        assert protected_signature(t) == pb, "protected signature changed"
        record["protected_unchanged"] = True

        start, end = t.GetStartFrame(), t.GetEndFrame()
        sample_frames = sorted({start, start + (end - start) // 2, max(start, end - 2)})
        frames = []
        for frame in sample_frames:
            fps = float(t.GetSetting("timelineFrameRate"))
            sec, ff = divmod(frame, int(round(fps)))
            mm, ss = divmod(sec, 60)
            hh, mm = divmod(mm, 60)
            code = f"{hh:02d}:{mm:02d}:{ss:02d}:{ff:02d}"
            assert t.SetCurrentTimecode(code)
            time.sleep(0.4)
            path = OUT / f"{timeline_id[:8]}-frame-{frame:08d}.png"
            assert p.ExportCurrentFrameAsStill(str(path.resolve()))
            frames.append(str(path.resolve()))
        record["frames"] = frames
        assert pm.SaveProject()
        record["saved"] = True
    record["status"] = "PASS"
    return record


def main():
    ids = sys.argv[1:]
    existing = json.loads(LOG.read_text(encoding="utf-8")) if LOG.is_file() else []
    done_ids = {row["timeline_id"] for row in existing if row.get("status") == "PASS"}
    for tid in ids:
        if tid in done_ids:
            print(json.dumps({"timeline_id": tid, "status": "SKIPPED_ALREADY_DONE"}))
            continue
        try:
            rec = apply_fix(tid)
        except Exception as exc:  # noqa: BLE001
            rec = {"timeline_id": tid, "status": "FAILED", "error": repr(exc)}
        existing.append(rec)
        LOG.write_text(json.dumps(existing, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        print(json.dumps(rec, ensure_ascii=False, default=str))
        time.sleep(1.0)


if __name__ == "__main__":
    main()
