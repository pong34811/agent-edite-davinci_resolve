import build_timelines as b

def test_to_clip_infos_frames_at_60fps():
    c = {"start_s": 10, "end_s": 70}
    assert b.to_clip_infos(c, "CID", fps=60) == [{"clip_id": "CID", "start_frame": 600, "end_frame": 4200, "record_frame": 0}]

def test_to_clip_infos_rounds_fractional_seconds():
    out = b.to_clip_infos({"start_s": 10.504, "end_s": 71.0}, "X", fps=60)[0]
    assert out["start_frame"] == 630 and out["end_frame"] == 630 + round(60.496 * 60)

def test_to_clip_infos_requires_fps():
    import pytest
    with pytest.raises(TypeError):
        b.to_clip_infos({"start_s": 1, "end_s": 2}, "X")

def test_to_clip_infos_uses_source_fps_30():
    out = b.to_clip_infos({"start_s": 10, "end_s": 70}, "X", fps=30)[0]
    assert out["start_frame"] == 300 and out["end_frame"] == 2100

def test_timeline_name_format_title_game_vdo(monkeypatch):
    c = {"id": "v01-03", "category": "meme", "title_th": "ชื่อคลิป"}
    monkeypatch.setattr(b.config, "TIMELINE_NAME_FORMAT", "{title}-{game}-vdo", raising=False)
    assert b.timeline_name(c, "Backrooms") == "ชื่อคลิป-Backrooms-vdo"

def test_timeline_name_respects_job_format(monkeypatch):
    c = {"id": "v01-03", "category": "meme", "title_th": "ชื่อคลิป"}
    monkeypatch.setattr(b.config, "TIMELINE_NAME_FORMAT", "{ชื่อคลิป}-vdo", raising=False)
    assert b.timeline_name(c, "") == "ชื่อคลิป-vdo"

def test_timeline_name_sanitizes_template_literals(monkeypatch):
    c = {"title_th": "ชื่อคลิป"}
    monkeypatch.setattr(b.config, "TIMELINE_NAME_FORMAT", "{title}|{game}/vdo", raising=False)
    name = b.timeline_name(c, "Backrooms")
    assert name == "ชื่อคลิป Backrooms vdo"
    assert not any(ch in name for ch in '\\/:*?"<>|')

def test_timeline_name_sanitized_and_max_60_keeps_suffix(monkeypatch):
    monkeypatch.setattr(b.config, "TIMELINE_NAME_FORMAT", "{title}-{game}-vdo", raising=False)
    c = {"id": "v01-03", "category": "meme", "title_th": "จดชื่อ/ไว้ใน:เดธโน้ต" + "ก" * 80}
    n = b.timeline_name(c, "League of Legends")
    assert len(n) <= 60 and n.endswith("-League of Legends-vdo") and not any(ch in n for ch in '\\/:*?"<>|')
    assert "v01-03" not in n and "meme" not in n

def test_timeline_name_requires_game(monkeypatch):
    import pytest
    monkeypatch.setattr(b.config, "TIMELINE_NAME_FORMAT", "{title}-{game}-vdo", raising=False)
    with pytest.raises(ValueError):
        b.timeline_name({"title_th": "x"}, "")

def test_game_from_filename_variants():
    g = b.game_from_filename
    assert g("20260922_【LIVE】Becastled - 001_[zYxbwwAxtzA].mp4") == "Becastled"
    assert g("20260919_【LIVE】strinova - 005 #aomimama_[iX6UZWmqueE].mp4") == "strinova"
    assert g("20260906_【LIVE】alien shooter last hope_[7LTPPtZMUcU].mp4") == "alien shooter last hope"
    assert g("20260910_【LIVE】alien shooter 2_[M0oO81RLbA8].mp4") == "alien shooter 2"

def test_game_overrides_win_over_filename():
    ov = {"หงุดหงิด": "League of Legends", "Minecraft": "Minecraft"}
    assert b.game_from_filename("20260911_หงุดหงิด ฉุนเฉียว_[hskX-AdzKFw].mp4", ov) == "League of Legends"
    assert b.game_from_filename("20260907_【LIVE】Minecraft  Server Dreamlight - 001 #aomimama_[X6E3DjqX8c8].mp4", ov) == "Minecraft"

def test_project_for_source():
    m = {"p1": ["v01", "v02"], "p2": ["v03"]}
    assert b.project_for_source("v03", m) == "p2"
    assert b.project_for_source("v01", {}) is None
    import pytest
    with pytest.raises(KeyError):
        b.project_for_source("v09", m)

def test_calls_filters_by_project():
    plan = [{"name": "a", "clip_infos": [], "project": "p1"}, {"name": "b", "clip_infos": [], "project": "p2"}]
    out = b.calls(plan, project="p2")
    assert [x["arguments"]["params"]["name"] for x in out] == ["b"]

def test_config_requires_highlight_job():
    import subprocess, sys, os, pathlib
    env = {k: v for k, v in os.environ.items() if k != "HIGHLIGHT_JOB"}
    code_dir = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "highlight"
    r = subprocess.run([sys.executable, "-c", "import config"], cwd=code_dir, env=env, capture_output=True, text=True)
    assert r.returncode != 0 and "HIGHLIGHT_JOB" in r.stderr

def test_merge_reviews_orders_and_counts(tmp_path):
    import json
    (tmp_path / "v02.json").write_text(json.dumps([{"id": "v02-01", "start_s": 5}]), encoding="utf-8")
    (tmp_path / "v01.json").write_text(json.dumps([{"id": "v01-02", "start_s": 9}, {"id": "v01-01", "start_s": 1}]), encoding="utf-8")
    merged = b.merge_reviews(tmp_path)
    assert [c["id"] for c in merged] == ["v01-01", "v01-02", "v02-01"]
