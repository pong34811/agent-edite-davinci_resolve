from types import SimpleNamespace as NS
import fulltext, packets, snap
from windows import snap_to_sentence

SENTS = [{"start": 10.0, "end": 14.0, "text": "a"}, {"start": 20.0, "end": 26.0, "text": "b"}]

def _seg(words):
    return {"words": [[t, s, e, 0.9] for t, s, e in words]}

def test_sentences_split_at_pauses_not_segment_edges():
    segs = [_seg([("สวัส", 1.0, 1.3), ("ดี", 1.3, 1.6), ("ต", 2.5, 2.8)]), _seg([("อนนี้", 2.9, 3.2)]), _seg([("โอ้", 4.0, 4.2)])]
    assert fulltext.sentences(segs) == [{"start": 1.0, "end": 1.6, "text": "สวัสดี"},
                                        {"start": 2.5, "end": 3.2, "text": "ตอนนี้"},
                                        {"start": 4.0, "end": 4.2, "text": "โอ้"}]

def test_sentences_split_long_runs_at_largest_pause():
    words = [(f"w{i}", i * 1.0, i * 1.0 + 0.9) for i in range(10)] + [(f"x{i}", 10.3 + i, 11.2 + i) for i in range(10)]
    out = fulltext.sentences([_seg(words)])
    assert all(s["end"] - s["start"] <= fulltext.MAX_SENT_S for s in out) and len(out) >= 2
    assert "".join(s["text"] for s in out) == "".join(w[0] for w in words)

def test_sentences_collapse_loops_and_drop_empty():
    out = fulltext.sentences([_seg([("ขอบคุณ" * 30, 0.0, 5.0)]), _seg([(" ", 6.0, 6.1)])])
    assert out == [{"start": 0.0, "end": 5.0, "text": "ขอบคุณ" * 3}]

def test_format_text_has_clock_and_ends():
    txt = fulltext.format_text("v01", [{"start": 3723.4, "end": 3725.06, "text": "ชนะแล้ว"}])
    assert "[1:02:03] ชนะแล้ว   [ends 3725.1]" in txt

def test_segments_offsets_words():
    out = fulltext._segments([NS(start=1.0, end=2.0, text=" hi ", words=[NS(word="hi", start=1.0, end=1.5, probability=0.5)])], 600)
    assert out == [{"start": 601.0, "end": 602.0, "text": "hi", "words": [["hi", 601.0, 601.5, 0.5]]}]

def test_snap_to_sentence_moves_mid_sentence_cuts():
    assert snap_to_sentence(12.0, SENTS, "in") == 10.0
    assert snap_to_sentence(21.0, SENTS, "out") == 26.3

def test_snap_to_sentence_none_between_sentences_or_too_far():
    assert snap_to_sentence(17.0, SENTS, "out") is None
    assert snap_to_sentence(21.0, SENTS, "out", max_shift=3) is None

def test_snap_arg_prefers_sentence_then_silence(monkeypatch):
    monkeypatch.setattr(snap, "snap_in_wav", lambda wav, t: t + 0.5)
    assert snap.snap_arg("out:21", SENTS, None) == (26.3, "sentence")
    assert snap.snap_arg("out:17", SENTS, None) == (17.5, "silence")
    assert snap.snap_arg("21", SENTS, None) == (21.5, "silence")
    assert snap.snap_arg("in:12", None, None) == (12.5, "silence")

def test_packet_shows_sentence_ends():
    txt = packets.format_packet("v01", [(10.0, 30.0, 0.5)], SENTS, {}, ends=True)
    assert "[ends 26.0]" in txt
