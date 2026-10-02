import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import subtitle_inspect as si  # noqa: E402


def _ws(tmp_path, srt, duration=60.0):
    (tmp_path / "asr").mkdir()
    (tmp_path / "srt").mkdir()
    (tmp_path / "jobs.json").write_text(json.dumps([{"job": 1, "duration_s": duration}]), encoding="utf-8")
    (tmp_path / "asr" / "job1.json").write_text(json.dumps({"passes": {"raw": {"segments": []}}}), encoding="utf-8")
    (tmp_path / "asr" / "job1_extra.json").write_text(json.dumps(
        {"passes": {}, "vad_raw": [[1.0, 2.0], [57.0, 58.0]], "vad_voice": [[10.0, 11.0]]}), encoding="utf-8")
    (tmp_path / "srt" / "job1.srt").write_text(srt, encoding="utf-8")
    return str(tmp_path)


def test_check_uses_duration_and_flags_early_linger_uncovered(tmp_path):
    good = ("1\n00:00:01,000 --> 00:00:02,000\nสวัสดี\n\n2\n00:00:57,000 --> 00:00:58,000\nครับ\n")
    ws = _ws(tmp_path, good)
    r = si.check_job(ws, 1)
    assert r["end_limit"] == 60.0 and r["errors"] == [] and not r["early"] and not r["linger"]
    assert r["uncovered_unlogged"] == [(10.0, 11.0)]          # VAD speech without a cue
    bad = "1\n00:00:00,500 --> 00:00:02,500\nสวัสดี\n"          # starts 0.5 s early, lingers 0.5 s
    ws2 = _ws(tmp_path / "b", bad) if (tmp_path / "b").mkdir() is None else None
    r = si.check_job(ws2, 1)
    assert r["early"] and r["linger"] and any("> 1.5s" in e for e in r["errors"])
