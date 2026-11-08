import wave

import pytest

np = pytest.importorskip("numpy")  # the ASR venv has numpy; the base test env may not

from scripts.asr_words_th import load_audio


def _wav(path, rate=16000, channels=1, samples=(0, 16384, -32768)):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(np.array(samples, dtype=np.int16).tobytes())
    return path


def test_load_audio_decodes_16k_mono_wav(tmp_path):
    out = load_audio(_wav(tmp_path / "a.wav"))
    assert out.dtype == np.float32
    assert out.tolist() == [0.0, 0.5, -1.0]


def test_load_audio_rejects_other_wav_formats(tmp_path):
    with pytest.raises(ValueError):
        load_audio(_wav(tmp_path / "b.wav", rate=48000))


def test_load_audio_passes_non_wav_through():
    assert load_audio("clip.mp4") == "clip.mp4"
