import wave, numpy as np, pytest
import features

def _write(path, seconds, sr=features.SR):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(np.zeros(int(seconds * sr), dtype=np.int16).tobytes())

def _fake_ffmpeg(lengths):
    """Each call writes a wav of the next length to the output path (last argv)."""
    calls = []
    def run(cmd, **kw):
        calls.append(cmd); _write(cmd[-1], lengths[min(len(calls) - 1, len(lengths) - 1)])
    return run, calls

def _setup(tmp_path, monkeypatch, lengths, duration=10.0):
    src = tmp_path / "src.mp4"; src.write_bytes(b"x")
    monkeypatch.setattr(features, "_inventory", lambda: {"v01": {"file": str(src), "duration_s": duration}})
    monkeypatch.setattr(features, "wav_path", lambda sid: tmp_path / "audio" / f"{sid}.wav")
    run, calls = _fake_ffmpeg(lengths)
    monkeypatch.setattr(features.subprocess, "run", run)
    return calls

def test_truncated_demux_is_retried_and_never_left_as_the_cached_wav(tmp_path, monkeypatch):
    calls = _setup(tmp_path, monkeypatch, [6.0, 10.0])          # first read cut short (cloud drive), retry is whole
    out = features.extract_wav("v01")
    assert len(calls) == 2 and out.exists() and not list(out.parent.glob("*.part*"))
    with wave.open(str(out)) as w:
        assert abs(w.getnframes() / w.getframerate() - 10.0) < 0.01

def test_persistently_short_demux_raises_and_leaves_no_wav(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, [6.0])
    with pytest.raises(RuntimeError, match="v01"):
        features.extract_wav("v01")
    assert not (tmp_path / "audio" / "v01.wav").exists()
