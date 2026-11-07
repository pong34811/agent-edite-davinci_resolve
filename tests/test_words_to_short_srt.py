import json

from scripts import words_to_short_srt as m


def w(text, s, e, seg=0):
    return {"w": text, "s": s, "e": e, "seg": seg}


def test_groups_by_chars_and_pause_not_by_stretched_word_end():
    words = [w("สวัสดี", 0.0, 1.2), w("ทุกคน", 0.5, 2.5), w("นะ", 3.4, 3.6)]
    cues = m.group(words)
    assert [m.join_words(c) for c in cues] == ["สวัสดีทุกคน", "นะ"]


def test_breaks_on_segment_and_char_limit():
    words = [w("ประเทศไทย", 0, 0.3), w("น้ำท่วมหนัก", 0.3, 0.6), w("มาก", 0.6, 0.7, seg=1)]
    texts = [m.join_words(c) for c in m.group(words)]
    assert texts == ["ประเทศไทย", "น้ำท่วมหนัก", "มาก"]


def test_frames_cap_gap_and_latin_spacing():
    rows = m.to_frames([[w("ดู", 0, 5)], [w("VTuber", 1.0, 1.2), w("ไทย", 1.2, 1.4)]], 60, 0)
    assert rows[0][1] - rows[0][0] <= 90 and rows[0][1] == rows[1][0] - 2
    assert rows[1][2] == "VTuber ไทย"


def test_cli_drops_latin_and_bad_segments(tmp_path):
    data = {"segments": [{"id": 0, "start": 0, "end": 2, "text": "ดีจ้า So", "avg_logprob": -0.3},
                         {"id": 1, "start": 3, "end": 4, "text": "ขยะ", "avg_logprob": -2.9}],
            "words": [w("ดีจ้า", 0, 0.5), w("So", 0.5, 0.7), w("VTuber", 0.7, 0.9),
                      w("ขยะ", 3, 4, seg=1)]}
    src = tmp_path / "a.json"
    src.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    out = tmp_path / "o.srt"
    rep = tmp_path / "r.json"
    m.main([str(src), str(out), "--min-logprob", "-2.5", "--drop-latin",
            "--keep-latin", "VTuber", "--report", str(rep)])
    text = out.read_text(encoding="utf-8")
    assert "ดีจ้า VTuber" in text and "So" not in text and "ขยะ" not in text
    report = json.loads(rep.read_text(encoding="utf-8"))
    assert report["dropped_latin"] == ["So"] and len(report["skipped_segments"]) == 1
