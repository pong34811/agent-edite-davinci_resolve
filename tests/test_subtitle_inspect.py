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


def test_energy_checks_flag_early_linger_and_no_burst():
    import numpy as np
    en = np.full(100, -40.0)      # 5 s of 50 ms frames
    per = np.full(100, 0.1)
    en[40:44] = -10.0             # loud noise, not voiced (2.00-2.20 s)
    en[50:56] = -10.0             # voiced speech 2.50-2.80 s
    per[50:56] = 0.9
    en[49] = -12.0                # loud unvoiced consonant frame just before the voicing
    env = (en, per)
    ok = si.energy_checks([{"start": 2.45, "end": 2.88, "text": "a"}], env)
    assert ok == {"early": [], "linger": [], "no_burst": []}
    r = si.energy_checks([{"start": 1.95, "end": 2.88, "text": "early"},      # starts on the noise
                          {"start": 2.45, "end": 3.2, "text": "linger"},
                          {"start": 4.0, "end": 4.4, "text": "none"}], env)
    assert r["early"] == [("early", 1.95, 2.45)] and r["linger"] == [("linger", 3.2, 2.8)]
    assert r["no_burst"] == [("none", 4.0)]


def test_energy_envelope_reads_raw_wav(tmp_path):
    import wave
    import numpy as np
    (tmp_path / "audio").mkdir()
    t = np.arange(16000) / 16000.0
    x = np.zeros(16000)
    x[8000:12000] = 0.3 * np.sign(np.sin(2 * np.pi * 150 * t[8000:12000]))   # voiced buzz 0.5-0.75 s
    w = wave.open(str(tmp_path / "audio" / "job1.wav"), "wb")
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)  # noqa: E702
    w.writeframes((x * 32767).astype(np.int16).tobytes())
    w.close()
    en, per = si.energy_envelope(str(tmp_path), 1)
    assert len(en) == 20 and en[12] > en[2] + 40 and per[12] > 0.6
