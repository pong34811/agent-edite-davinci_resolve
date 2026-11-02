import json, pathlib
import config, build_timelines as b, briefs, resolve_clips

def test_ffmpeg_paths_resolve_to_something_runnable():
    assert pathlib.Path(config.FFMPEG).exists() or config.FFMPEG == "ffmpeg"
    assert config.FFPROBE.lower().endswith(("ffprobe.exe", "ffprobe"))

def test_calls_builds_mcp_payloads_for_slice():
    plan = [{"name": f"v01-0{i}_fun_x", "clip_infos": [{"clip_id": "C", "start_frame": i, "end_frame": i + 10, "record_frame": 0}]} for i in range(1, 4)]
    out = b.calls(plan, start=1, end=3)
    assert [c["arguments"]["params"]["name"] for c in out] == ["v01-02_fun_x", "v01-03_fun_x"]
    a = out[0]["arguments"]
    assert out[0]["name"] == "mcp__davinci_resolve__media_pool" and a["action"] == "create_timeline_from_clips"
    assert a["params"]["if_exists"] == "fail" and a["params"]["clip_infos"][0]["start_frame"] == 2

def test_map_clips_matches_inventory_paths_case_and_slash_insensitive():
    BS = chr(92)
    inv = [{"source_id": "v01", "file": "Z:/a/one.mp4"}, {"source_id": "v02", "file": "Z:" + BS + "a" + BS + "Two.mp4"}]
    probe = {"root": {"clips": [{"id": "id-2", "file_path": "z:" + BS + "a" + BS + "two.mp4"}, {"id": "id-1", "file_path": "Z:" + BS + "a" + BS + "one.mp4"}]}}
    assert resolve_clips.map_clips(probe, inv) == {"v01": "id-1", "v02": "id-2"}

def test_map_clips_raises_when_a_video_is_not_in_resolve():
    inv = [{"source_id": "v01", "file": "Z:/a/one.mp4"}, {"source_id": "v02", "file": "Z:/a/missing.mp4"}]
    probe = {"root": {"clips": [{"id": "id-1", "file_path": "Z:/a/one.mp4"}]}}
    try:
        resolve_clips.map_clips(probe, inv)
    except KeyError as e:
        assert "v02" in str(e)
    else:
        raise AssertionError("expected KeyError")

def test_render_brief_fills_every_variable():
    inv = [{"source_id": "v07", "file": "Z:/a/one.mp4", "duration_s": 1234.5}]
    txt = briefs.render("v07", inv, hint="a horror stream")
    assert "v07" in txt and "1234" in txt and "a horror stream" in txt
    assert "gameplay" in txt and str(config.CLIP_MIN_S) in txt and str(config.CLIP_MAX_S) in txt
    assert "$" not in txt
