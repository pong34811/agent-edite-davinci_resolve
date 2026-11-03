import re
import numpy as np
import briefs, config, proposals, readpack

SENTS = [{"start": 65.0, "end": 70.5, "text": "บอสมาแล้ว"}, {"start": 130.0, "end": 133.0, "text": "ชนะแล้วทุกคน"}]

def test_packs_overlap_and_fold_short_tail():
    assert readpack.packs(5000, 1800, 120) == [(0.0, 1800.0), (1680.0, 3480.0), (3360.0, 5000.0)]
    assert readpack.packs(3900, 1800, 120) == [(0.0, 1800.0), (1680.0, 3900.0)]
    assert readpack.packs(600, 1800, 120) == [(0.0, 600.0)]

def test_minute_signals_flags_loud_jump_talk_and_shortlist():
    rms = np.full(180, -40.0); rms[120:130] = -10.0
    sig = readpack.minute_signals(rms, [[60, 100, 0.5]], SENTS)
    assert [s["t"] for s in sig] == [0, 60, 120]
    assert sig[2]["loud"] > 1 and sig[2]["jump"] >= 20
    assert sig[1]["talk"] > 0 and sig[0]["talk"] == 0
    assert [s["short"] for s in sig] == [False, True, False]
    assert "!!" in readpack.signal_line(sig[2]) and "shortlist" in readpack.signal_line(sig[1])

def test_format_pack_interleaves_signals_and_sentences_in_span():
    sig = readpack.minute_signals(np.full(180, -40.0), [], SENTS)
    txt = readpack.format_pack("v05", 1, 2, (60, 180), SENTS, sig)
    lines = txt.splitlines()
    i1, i2 = lines.index(next(l for l in lines if l.startswith("── 0:01:00"))), lines.index(next(l for l in lines if "บอสมาแล้ว" in l))
    assert i1 < i2 and "[ends 133.0]" in txt and "── 0:00:00" not in txt

def _item(**kw):
    it = {"id": "v05-read-01-01", "source_id": "v05", "pack": "v05-read-01", "start_s": 60.0, "end_s": 140.0, "setup_s": 65.0,
          "payoff_s": 130.0, "category": config.CATEGORIES[0], "title_th": "ชนะบอส", "quote": "ชนะแล้ว ทุกคน",
          "reason": "setup -> win -> cheer", "confidence": 0.8}
    it.update(kw); return it

def test_problems_accepts_good_item_and_flags_bad_ones():
    text = "[0:02:10] ชนะแล้วทุกคน   [ends 133.0]"
    assert proposals.problems(_item(), text, 5000) == []
    assert "quote not in pack" in proposals.problems(_item(quote="ไม่มีจริง"), text, 5000)
    assert "needs start <= setup < payoff < end" in proposals.problems(_item(payoff_s=150.0), text, 5000)
    assert proposals.problems(_item(end_s=60.0 + config.CLIP_MAX_S + 10), text, 5000)[0].startswith("length")
    assert proposals.problems({"id": "x"}, text, 5000)[0].startswith("missing keys")

def test_merge_keeps_most_confident_of_overlapping_items():
    a, b, c = _item(id="a", confidence=0.6), _item(id="b", start_s=70.0, end_s=150.0, confidence=0.9), _item(id="c", start_s=400.0, end_s=480.0)
    assert [x["id"] for x in proposals.merge([a, b, c])] == ["b", "c"]

def test_reader_brief_has_no_unfilled_placeholders():
    txt = briefs.render_reader({"pack": "v05-read-01", "start_s": 0, "end_s": 1800}, "v05", 5000)
    assert not re.search(r"\$[A-Z_]+", txt)
    assert "v05-read-01.md" in txt and "snap.py v05 in:" in txt and "0:30:00" in txt
