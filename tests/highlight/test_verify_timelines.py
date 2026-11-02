import verify_timelines as vt

PLAN = [{"name": "a-G-vdo", "clip_infos": [{"clip_id": "c1", "start_frame": 100, "end_frame": 160, "record_frame": 0}],
         "candidate": "v01-01"},
        {"name": "b-G-vdo", "clip_infos": [{"clip_id": "c2", "start_frame": 30, "end_frame": 60, "record_frame": 0}],
         "candidate": "v02-01"}]
FPS = {"c1": 60, "c2": 30}

def _tl(name, clip, src_start, dur, start=0, audio=True, video_n=1):
    v = [{"clip_id": clip, "start": start, "duration": dur, "source_start": src_start}] * video_n
    a = [{"clip_id": clip, "start": start, "duration": dur}] if audio else []
    return {"name": name, "video": v, "audio": a}

def test_matching_timelines_pass_including_a_30fps_source_on_a_60fps_timeline():
    got = [_tl("a-G-vdo", "c1", 100, 60), _tl("b-G-vdo", "c2", 30, 60)]
    rows = vt.compare(PLAN, got, FPS, timeline_fps=60)
    assert [r["ok"] for r in rows] == [True, True]

def test_missing_wrong_range_and_extra_items_are_reported():
    got = [_tl("b-G-vdo", "c2", 31, 60, audio=False, video_n=2)]
    rows = {r["name"]: r for r in vt.compare(PLAN, got, FPS, timeline_fps=60)}
    assert rows["a-G-vdo"]["problems"] == ["timeline missing"]
    p = " ".join(rows["b-G-vdo"]["problems"])
    assert "video items" in p and "source_start" in p and "audio" in p

def test_duplicate_timeline_names_are_reported():
    got = [_tl("a-G-vdo", "c1", 100, 60), _tl("a-G-vdo", "c1", 100, 60), _tl("b-G-vdo", "c2", 30, 60)]
    rows = {r["name"]: r for r in vt.compare(PLAN, got, FPS, timeline_fps=60)}
    assert "2 timelines with this name" in rows["a-G-vdo"]["problems"]
