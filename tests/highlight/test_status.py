import json
import status

def _job(tmp, ids=("v01", "v02")):
    (tmp / "inventory.json").write_text(json.dumps([{"source_id": s} for s in ids]))
    for d in ("audio", "scores", "transcripts", "review", "frames"):
        (tmp / d).mkdir()
    return tmp

def _touch(p, text="x"):
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text, encoding="utf-8")

def _through_shortlist(w, sid):
    _touch(w / "audio" / f"{sid}.wav"); _touch(w / "scores" / f"{sid}.features.npz")
    _touch(w / "scores" / f"{sid}.top.json", json.dumps([[60, 120, 0.5]]))

def test_no_inventory_points_to_inventory(tmp_path):
    assert status.job_state(tmp_path)["next"].startswith("python pipeline.py inventory")

def test_next_is_first_missing_stage_with_its_videos(tmp_path):
    w = _job(tmp_path); _through_shortlist(w, "v01")
    st = status.job_state(w)
    assert st["next"].startswith("python pipeline.py features") and "[v02]" in st["next"]
    _through_shortlist(w, "v02")
    assert status.job_state(w)["next"].startswith("python pipeline.py fulltext")

def test_missing_reader_packs_are_named(tmp_path):
    w = _job(tmp_path, ("v01",)); _through_shortlist(w, "v01")
    _touch(w / "transcripts" / "v01.sentences.json", "[]")
    plan = {"v01": [{"pack": f"v01-read-0{i}", "file": f"v01-read-0{i}.md"} for i in (1, 2)]}
    _touch(w / "review" / "read-plan.json", json.dumps(plan))
    for i in (1, 2):
        _touch(w / "review" / f"v01-read-0{i}.md"); _touch(w / "review" / f"v01-read-0{i}.brief.md")
    _touch(w / "review" / "v01-read-01.json", "[]")
    nxt = status.job_state(w)["next"]
    assert nxt.startswith("spawn one reader") and "missing: v01-read-02" in nxt and "v01-read-01," not in nxt

def test_read_whole_stream_false_skips_reading_steps(tmp_path):
    w = _job(tmp_path, ("v01",)); _through_shortlist(w, "v01")
    assert status.job_state(w, read_whole_stream=False)["next"].startswith("python pipeline.py sheets")

def test_after_reviews_goes_to_gate_then_plan_then_resolve(tmp_path):
    w = _job(tmp_path, ("v01",)); _through_shortlist(w, "v01")
    _touch(w / "frames" / "v01_000060.jpg"); _touch(w / "review" / "v01.packet.md"); _touch(w / "review" / "v01.brief.md")
    _touch(w / "review" / "v01.json", "[]")
    assert "resolve_clips.py" in status.job_state(w, False)["next"]
    _touch(w / "resolve_clips.json", "{}")
    assert status.job_state(w, False)["next"].startswith("python build_timelines.py")
    _touch(w / "timeline_plan.json", "[]")
    assert "verify_timelines.py" in status.job_state(w, False)["next"]
    _touch(w / "timeline_verification.json", "{}")
    assert status.job_state(w, False)["next"].startswith("done")

def test_format_table_has_row_per_video_and_next():
    txt = status.format_table({"videos": {"v01": {k: True for k, _, _ in status.STEPS}}, "next": "x"})
    assert "v01" in txt and txt.endswith("NEXT: x")

def test_only_scopes_videos_and_puts_ids_in_command_and_warns_on_approved_review(tmp_path):
    w = _job(tmp_path); _through_shortlist(w, "v01"); _through_shortlist(w, "v02")
    _touch(w / "review" / "v01.json", "[]")
    st = status.job_state(w, only=["v01"])
    assert list(st["videos"]) == ["v01"]
    assert st["next"].startswith("python pipeline.py fulltext v01 ") and "NOTE: v01 already have an approved" in st["next"]
    assert "NOTE" not in status.job_state(w, only=["v02"])["next"]
