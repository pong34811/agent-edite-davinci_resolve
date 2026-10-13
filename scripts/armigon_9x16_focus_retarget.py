"""Retarget only the approved 9:16 pilot Adjustment Clip to the in-game chibi.

MCP-GAP: fusion_comp.safe_set_inputs / set_input -> both actions returned success for
point-valued Pivot inputs, but live readback remained at the old/default coordinates;
use Resolve Python SetInput through resolve_common.py and verify the exact point values.
"""
from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

from scripts.backup_drp import verify_drp
from scripts.resolve_common import connect_resolve, preserved_state
from scripts.armigon_9x16_pilot import (
    AUDIO_PROPS,
    BACKUP,
    BASELINE,
    DRT_REFERENCE,
    FOCUS,
    ORIGINAL_ID,
    ORIGINAL_NAME,
    OUT_DIR,
    PROJECT_ID,
    PROJECT_NAME,
    VIDEO_PROPS,
    check,
    find_timeline,
    folder_id,
    full_original_signature,
    fusion_signature,
    fusion_transform,
    normalize,
    protected_signature,
    subtitle_drt_signature,
    track_rows,
    track_sig,
)


TARGET_ID = "8e8d12d6-a2a3-40a7-97b9-aff090641b2e"
TARGET_NAME = ORIGINAL_NAME + "_9x16"
FOCUS_ITEM_ID = "025ce455-e80d-4184-ae02-e08c4a437792"
FOCUS_TRACK = 4
FOCUS_RANGE = (1613, 2065)
DELAY = 1.25
SAMPLE_COMP_TIMES = (0.0, 225.0, 451.0)


def same_point(value, expected, tolerance=0.0001):
    if not isinstance(value, dict):
        return False
    for axis, wanted in expected.items():
        actual = value.get(str(axis), value.get(axis))
        if actual is None or abs(float(actual) - float(wanted)) > tolerance:
            return False
    return True


def input_snapshot(transform):
    # Keep raw Fusion point dictionaries (including integer component keys) so they
    # can be passed back to SetInput during rollback. Normalize only in the log.
    return {key: transform.GetInput(key) for key in ("Size", "Pivot", "Center", "Edges", "MotionBlur")}


def assert_focus_values(snapshot):
    check(abs(float(snapshot["Size"]) - FOCUS["Size"]) <= 0.0001,
          f"Size readback mismatch: {snapshot}")
    check(same_point(snapshot["Pivot"], FOCUS["Pivot"]), f"Pivot readback mismatch: {snapshot}")
    check(same_point(snapshot["Center"], FOCUS["Center"]), f"Center readback mismatch: {snapshot}")


def set_and_read(transform, key, value):
    transform.SetInput(key, value, 0.0)
    time.sleep(0.35)
    actual = normalize(transform.GetInput(key))
    if key == "Size":
        check(abs(float(actual) - float(value)) <= 0.0001, f"{key} readback mismatch: {actual}")
    else:
        check(same_point(actual, value), f"{key} readback mismatch: {actual}")
    return actual


def main():
    backup_bytes = verify_drp(BACKUP)
    check(BASELINE.is_file(), f"preflight baseline missing: {BASELINE}")
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    check(baseline.get("project", {}).get("name") == PROJECT_NAME,
          "preflight baseline belongs to another project")
    target_rows = [row for row in baseline.get("timelines", []) if row.get("timeline_id") == ORIGINAL_ID]
    check(len(target_rows) == 1 and target_rows[0].get("name") == ORIGINAL_NAME,
          "baseline source timeline identity mismatch")
    check((target_rows[0].get("start_frame"), target_rows[0].get("end_frame")) == (0, 6658),
          "baseline source duration changed")

    resolve = connect_resolve()
    check(resolve is not None, "cannot connect to Resolve")
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    check(project is not None and project.GetName() == PROJECT_NAME and project.GetUniqueId() == PROJECT_ID,
          "active project is not the approved project")
    check(not project.IsRenderingInProgress(), "Resolve is rendering; refusing the pilot adjustment")
    original_hits = find_timeline(project, timeline_id=ORIGINAL_ID, name=ORIGINAL_NAME)
    target_hits = find_timeline(project, timeline_id=TARGET_ID, name=TARGET_NAME)
    check(len(original_hits) == 1 and len(target_hits) == 1,
          "source and pilot timelines must each resolve uniquely by ID and name")
    original, target = original_hits[0], target_hits[0]

    initial_timeline = project.GetCurrentTimeline()
    check(initial_timeline is not None, "Resolve has no active timeline to preserve")
    initial_timeline_id = initial_timeline.GetUniqueId()
    initial_timecode = initial_timeline.GetCurrentTimecode()
    initial_page = resolve.GetCurrentPage()
    initial_folder = project.GetMediaPool().GetCurrentFolder()
    initial_folder_id = folder_id(initial_folder)
    result = {
        "project": PROJECT_NAME,
        "project_id": PROJECT_ID,
        "target_timeline_id": TARGET_ID,
        "target_timeline_name": TARGET_NAME,
        "focus_item_id": FOCUS_ITEM_ID,
        "focus_range": list(FOCUS_RANGE),
        "target_focus": FOCUS,
        "backup_path": str(BACKUP),
        "backup_bytes_verified": backup_bytes,
        "mcp_gap": "Fusion point-valued inputs were acknowledged by MCP but did not read back the requested coordinates.",
        "steps": [],
    }
    transform = None
    before = None
    mutation_started = False
    target_video_before = None
    target_protected_before = None
    target_track_locks = None
    try:
        with preserved_state(resolve):
            check(project.SetCurrentTimeline(original), "could not activate source for baseline readback")
            time.sleep(DELAY)
            original_before = full_original_signature(original)
            result["source_signature_captured"] = True

            check(project.SetCurrentTimeline(target), "could not activate the 9:16 pilot")
            time.sleep(DELAY)
            check(project.GetCurrentTimeline().GetUniqueId() == TARGET_ID,
                  "pilot activation readback mismatch")
            check(tuple(target.GetSetting(key) for key in ("timelineResolutionWidth", "timelineResolutionHeight"))
                  == ("1080", "1920"), "pilot raster is not 1080x1920")
            check(float(target.GetSetting("timelineFrameRate")) == 60.0, "pilot frame rate is not 60 fps")
            check((target.GetStartFrame(), target.GetEndFrame()) == (0, 6658), "pilot duration changed")
            check(target.GetTrackCount("video") == 4 and target.GetTrackCount("audio") == 3 and
                  target.GetTrackCount("subtitle") == 1, "pilot track counts changed")

            target_video_before = [track_rows(target, "video", VIDEO_PROPS)[i - 1]["items"]
                                   for i in range(1, target.GetTrackCount("video") + 1)]
            target_protected_before = protected_signature(target)
            check(len(target_protected_before["subtitle_tracks"]) == 1 and
                  len(target_protected_before["subtitle_tracks"][0]["items"]) == 90,
                  "pilot subtitle cue count changed")
            check(len(target_protected_before["audio_tracks"]) == 3,
                  "pilot audio track inventory changed")
            check([(row["start"], row["end"]) for row in target_video_before[0]] == [(0, 6658)],
                  "V1 source range changed")
            check([(row["start"], row["end"], row["source_start"], row["source_end"])
                   for row in target_video_before[1]] == [(606, 721, 0, 47)], "GIF timing/source range changed")
            check([(row["start"], row["end"]) for row in target_video_before[2]] == [(0, 6658)],
                  "VTuber Bottom range changed")

            focus_items = sorted(target.GetItemListInTrack("video", FOCUS_TRACK) or [], key=lambda item: item.GetStart())
            check(len(focus_items) == 1 and focus_items[0].GetName() == "Adjustment Clip" and
                  (focus_items[0].GetStart(), focus_items[0].GetEnd()) == FOCUS_RANGE,
                  "focus Adjustment Clip identity or range changed")
            check(focus_items[0].GetUniqueId() == FOCUS_ITEM_ID,
                  "focus Adjustment Clip unique ID changed")
            transform = fusion_transform(focus_items[0])
            before = input_snapshot(transform)
            result["focus_inputs_before"] = normalize(before)
            target_track_locks = {index: target.GetIsTrackLocked("video", index) for index in (1, 2, 3, 4)}
            if target_track_locks[FOCUS_TRACK]:
                check(target.SetTrackLock("video", FOCUS_TRACK, False), "could not temporarily unlock V4")
                time.sleep(0.35)
                check(not target.GetIsTrackLocked("video", FOCUS_TRACK), "V4 unlock readback mismatch")

            try:
                # Minimal pilot update: only the existing Adjustment Clip's Transform inputs.
                mutation_started = True
                result["focus_inputs_after_set"] = {}
                for key in ("Size", "Pivot", "Center"):
                    result["focus_inputs_after_set"][key] = set_and_read(transform, key, FOCUS[key])
                time.sleep(DELAY)
                after = input_snapshot(transform)
                assert_focus_values(after)
                check(after["Edges"] == before["Edges"], "Fusion edge handling changed")
                check(float(after["MotionBlur"]) == float(before["MotionBlur"]) == 0.0,
                      "Motion Blur changed or was enabled")
                for sample_time in SAMPLE_COMP_TIMES:
                    sample = {key: normalize(transform.GetInput(key, sample_time)) for key in ("Size", "Pivot", "Center")}
                    assert_focus_values(sample)
                result["focus_inputs_after"] = normalize(after)
                result["focus_sample_times"] = list(SAMPLE_COMP_TIMES)
                result["focus_samples_static"] = True

                target_video_after = [track_rows(target, "video", VIDEO_PROPS)[i - 1]["items"]
                                      for i in range(1, target.GetTrackCount("video") + 1)]
                check(target_video_after == target_video_before,
                      "video item ranges or clip properties changed outside Fusion inputs")
                check(protected_signature(target) == target_protected_before,
                      "audio, subtitle text/timing, or protected track state changed")
                result["protected_audio_subtitle_equal"] = True
                result["video_items_equal"] = True

                stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                drt_path = OUT_DIR / f"armigon_9x16_focus_retarget_{stamp}.drt"
                OUT_DIR.mkdir(parents=True, exist_ok=True)
                check(target.Export(str(drt_path), resolve.EXPORT_DRT, resolve.EXPORT_NONE),
                      "updated pilot DRT export failed")
                drt_before = subtitle_drt_signature(DRT_REFERENCE)
                drt_after = subtitle_drt_signature(drt_path)
                check(drt_after == drt_before, "subtitle text, timing, or style differs from source DRT")
                result["subtitle_drt_check"] = {
                    "cue_count": len(drt_after["cues"]),
                    "text_timing_style_equal": True,
                    "drt_path": str(drt_path),
                }

                check(pm.SaveProject(), "SaveProject failed for the updated pilot")
                time.sleep(DELAY)
                check(protected_signature(target) == target_protected_before,
                      "protected tracks changed after saving")
                result["saved"] = True

                check(project.SetCurrentTimeline(original), "could not reactivate original for preservation audit")
                time.sleep(DELAY)
                result["original_unchanged"] = full_original_signature(original) == original_before
                check(result["original_unchanged"], "original 16:9 timeline changed")
                check(project.SetCurrentTimeline(target), "could not restore pilot after preservation audit")
                time.sleep(DELAY)
                check(project.GetCurrentTimeline().GetUniqueId() == TARGET_ID,
                      "pilot not active after readback audit")
                result["resolve_running"] = connect_resolve() is not None
                check(result["resolve_running"], "Resolve scripting bridge is no longer reachable")
            except Exception:
                if mutation_started and before is not None and transform is not None:
                    try:
                        current = project.GetCurrentTimeline()
                        if not current or current.GetUniqueId() != TARGET_ID:
                            project.SetCurrentTimeline(target)
                            time.sleep(DELAY)
                        if target.GetIsTrackLocked("video", FOCUS_TRACK):
                            target.SetTrackLock("video", FOCUS_TRACK, False)
                            time.sleep(0.35)
                        for key in ("Size", "Pivot", "Center"):
                            transform.SetInput(key, before[key], 0.0)
                            time.sleep(0.35)
                        check(input_snapshot(transform) == before,
                              "rollback did not restore the exact pre-adjustment Fusion inputs")
                        check(pm.SaveProject(), "rollback SaveProject returned False")
                        result["rollback"] = "restored pre-adjustment Fusion inputs and saved"
                    except Exception as rollback_error:
                        result["rollback_error"] = repr(rollback_error)
                raise
            finally:
                if target_track_locks is not None:
                    current = project.GetCurrentTimeline()
                    if current and current.GetUniqueId() == TARGET_ID:
                        for index, was_locked in target_track_locks.items():
                            if target.GetIsTrackLocked("video", index) != was_locked:
                                target.SetTrackLock("video", index, was_locked)
                                time.sleep(0.35)
                            check(target.GetIsTrackLocked("video", index) == was_locked,
                                  f"V{index} lock state did not restore")

        restored = project.GetCurrentTimeline()
        result["resolve_state_restored"] = bool(
            restored and restored.GetUniqueId() == initial_timeline_id and
            restored.GetCurrentTimecode() == initial_timecode and
            resolve.GetCurrentPage() == initial_page and
            folder_id(project.GetMediaPool().GetCurrentFolder()) == initial_folder_id)
        if not result["resolve_state_restored"]:
            result["state_restore_warning"] = "Resolve did not return to the exact pre-edit timeline/timecode/page/folder."
            if before is not None and target_track_locks is not None:
                try:
                    # If restoration fails after the pilot was saved, undo the saved
                    # retarget before trying to restore the user's session again.
                    with preserved_state(resolve):
                        check(project.SetCurrentTimeline(target), "could not activate pilot for state-failure rollback")
                        time.sleep(DELAY)
                        if target.GetIsTrackLocked("video", FOCUS_TRACK):
                            check(target.SetTrackLock("video", FOCUS_TRACK, False), "could not unlock V4 for rollback")
                            time.sleep(0.35)
                        for key in ("Size", "Pivot", "Center"):
                            transform.SetInput(key, before[key], 0.0)
                            time.sleep(0.35)
                        check(input_snapshot(transform) == before,
                              "rollback after state failure did not restore pre-adjustment inputs")
                        for index, was_locked in target_track_locks.items():
                            if target.GetIsTrackLocked("video", index) != was_locked:
                                check(target.SetTrackLock("video", index, was_locked),
                                      f"could not restore V{index} lock during rollback")
                                time.sleep(0.35)
                        check(pm.SaveProject(), "could not save pilot rollback after state failure")
                    timeline_to_restore = next(
                        (project.GetTimelineByIndex(i) for i in range(1, project.GetTimelineCount() + 1)
                         if project.GetTimelineByIndex(i).GetUniqueId() == initial_timeline_id), None)
                    check(timeline_to_restore is not None, "initial Resolve timeline no longer exists")
                    check(project.SetCurrentTimeline(timeline_to_restore), "could not restore initial timeline after rollback")
                    time.sleep(DELAY)
                    timeline_to_restore.SetCurrentTimecode(initial_timecode)
                    time.sleep(0.35)
                    check(timeline_to_restore.GetCurrentTimecode() == initial_timecode,
                          "initial timecode readback failed after rollback")
                    check(project.GetMediaPool().SetCurrentFolder(initial_folder),
                          "could not restore initial Media Pool folder after rollback")
                    if initial_page and resolve.GetCurrentPage() != initial_page:
                        check(resolve.OpenPage(initial_page), "could not reopen initial Resolve page after rollback")
                        time.sleep(DELAY)
                    final_timeline = project.GetCurrentTimeline()
                    result["resolve_state_restored_after_rollback"] = bool(
                        final_timeline and final_timeline.GetUniqueId() == initial_timeline_id and
                        final_timeline.GetCurrentTimecode() == initial_timecode and
                        resolve.GetCurrentPage() == initial_page and
                        folder_id(project.GetMediaPool().GetCurrentFolder()) == initial_folder_id)
                    check(result["resolve_state_restored_after_rollback"],
                          "Resolve session state still failed to restore after pilot rollback")
                    result["rollback_after_state_failure"] = True
                except Exception as rollback_error:
                    result["rollback_after_state_failure"] = False
                    result["rollback_after_state_failure_error"] = repr(rollback_error)
            check(False, "Resolve state restore failed; pilot retarget was rolled back")
        result["status"] = "PASS"
    except Exception as exc:
        result["status"] = "FAILED"
        result["error"] = repr(exc)
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        log = OUT_DIR / f"armigon_9x16_focus_retarget_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
        result["log_path"] = str(log)
        log.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        print(json.dumps(result, ensure_ascii=True, indent=2, default=str))
        raise

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    log = OUT_DIR / f"armigon_9x16_focus_retarget_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
    result["log_path"] = str(log)
    log.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=True, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
