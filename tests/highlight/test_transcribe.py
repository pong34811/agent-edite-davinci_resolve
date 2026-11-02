import numpy as np
from types import SimpleNamespace
import transcribe

def _rms_db(x): return 20 * np.log10(np.sqrt((x.astype(np.float64) ** 2).mean()) + 1e-12)

def test_boost_raises_quiet_speechlike_signal_by_6db():
    sr = 16000; rng = np.random.default_rng(0)
    t = np.arange(sr * 8) / sr
    x = (0.01 * np.sin(2 * np.pi * 220 * t) * (1 + np.sin(2 * np.pi * 3 * t)) + rng.normal(0, 0.001, t.size)).astype(np.float32)
    y = transcribe.boost(x)
    assert _rms_db(y) - _rms_db(x) >= 6

def test_spans_pad_clip_and_merge():
    wins = [(100, 160, .9), (200, 260, .5), (5000, 5060, .4)]
    assert transcribe.spans(wins, duration_s=5100, pad=90) == [(10.0, 350.0), (4910.0, 5100.0)]

def test_segments_for_span_offsets_and_empty():
    class M:
        def transcribe(self, audio, **kw):
            return iter([SimpleNamespace(start=1.0, end=2.5, text=" สวัสดี ")]), None
    out = transcribe.segments_for_span(M(), np.zeros(16000, dtype=np.float32), offset=100.0)
    assert out == [{"start": 101.0, "end": 102.5, "text": "สวัสดี"}]
    class E:
        def transcribe(self, audio, **kw): return iter([]), None
    assert transcribe.segments_for_span(E(), np.zeros(16000, dtype=np.float32), offset=0) == []
