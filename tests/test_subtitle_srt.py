import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import subtitle_srt as s  # noqa: E402


def blk(i, a, b, text):
    return {"index": str(i), "start": a, "end": b, "lines": [text]}


def test_srt_time_roundtrip_and_parse():
    assert s.fmt_srt(61.2346) == "00:01:01,235"
    assert abs(s.parse_srt_time("00:01:01,235") - 61.235) < 1e-9
    cues = s.parse_srt("1\n00:00:01,000 --> 00:00:02,000\nสวัสดี\n\n2\n00:00:02,100 --> 00:00:03,000\nครับ\n")
    assert [c["index"] for c in cues] == ["1", "2"] and cues[1]["lines"] == ["ครับ"]


def test_visible_len_ignores_combining_marks():
    assert s.visible_len("ไม่ได้") == 4  # ไ ม ไ ด ; ่ ้ are marks
    assert s.visible_len("ab c") == 3


def test_split_words_merges_mai_yamok_and_lone_chars():
    tok = {"ชิวๆ": ["ชิว", "ๆ"], "แม่ง": ["แม่", "ง"]}
    words = s.split_words("ชิวๆ แม่ง", tokenizer=lambda t: tok[t])
    assert words == ["ชิวๆ", "แม่ง"]


def test_join_display_spaces_only_around_latin():
    assert s.join_display(["ไม่", "ได้", "โม้"]) == "ไม่ได้โม้"
    assert s.join_display(["เล่น", "Valorant", "กัน"]) == "เล่น Valorant กัน"


def test_validator_accepts_good_and_flags_each_rule():
    good = [blk(1, 1.0, 2.0, "ไม่ได้โม้"), blk(2, 2.034, 3.0, "จริงๆ")]
    assert s.validate_cues(good, speech_start=0.9) == []
    bad = [blk(1, 0.5, 2.2, "ไม่ ได้"), blk(3, 2.1, 3.0, "ab漢"), blk(4, 3.01, 56.0, "x\n")]
    errs = " | ".join(s.validate_cues(bad, speech_start=0.9))
    for needle in ("> 1.5s", "space between Thai", "not consecutive", "overlaps", "foreign",
                   "gap", "before speech", "> 55.0"):
        assert needle in errs, needle


def test_validator_word_and_char_caps():
    long_text = "กขคงจฉชซฌญฎฏฐฑฒ"  # 15 visible chars
    errs = s.validate_cues([blk(1, 0, 1, long_text)], tokenizer=lambda t: [t])
    assert any("chars" in e for e in errs)
    errs = s.validate_cues([blk(1, 0, 1, "กขค")], tokenizer=lambda t: ["กก", "ขข", "คค", "งง"])
    assert any("words" in e for e in errs)


def test_align_times_uses_source_and_interpolates_inserts():
    src = [{"ch": c, "start": 1.0 + i * 0.1, "end": 1.1 + i * 0.1} for i, c in enumerate("ไม่ได้โม้")]
    timed = s.align_times("ไม่ได้โม้เลย", src, 1.0, 2.5)
    assert timed[0][1] == 1.0 and abs(timed[8][2] - 1.9) < 1e-9
    assert timed[-1][2] >= timed[-2][1] >= timed[8][2] - 1e-9  # inserted chars after last anchor
    lin = s.align_times("กข", [], 0.0, 1.0)
    assert lin == [("ก", 0.0, 0.5), ("ข", 0.5, 1.0)]


def W(text, a, b, boundary=True):
    return {"text": text, "start": a, "end": b, "boundary": boundary}


def test_natural_words_attach_prefixes_and_particles():
    toks = {"ไม่มีนะครับ": ["ไม่", "มี", "นะ", "ครับ"], "ไม่ได้โม้เลย": ["ไม่", "ได้", "โม้", "เลย"],
            "เขาบอกว่าเป็น": ["เขา", "บอก", "ว่า", "เป็น"], "จะไปกินข้าว": ["จะ", "ไป", "กิน", "ข้าว"],
            "ได้เลย": ["ได้", "เลย"], "แบบไม่": ["แบบ", "ไม่"]}
    tk = lambda t: toks[t]  # noqa: E731
    assert s.natural_words("ไม่มีนะครับ", tk) == ["ไม่มีนะครับ"]
    assert s.natural_words("ไม่ได้โม้เลย", tk) == ["ไม่ได้โม้เลย"]
    assert s.natural_words("เขาบอกว่าเป็น", tk) == ["เขา", "บอกว่า", "เป็น"]
    assert s.natural_words("จะไปกินข้าว", tk) == ["จะไป", "กิน", "ข้าว"]
    assert s.natural_words("ได้เลย", tk) == ["ได้เลย"]
    assert s.natural_words("แบบไม่", tk) == ["แบบ", "ไม่"]  # dangling prefix stays a word


def test_segment_merges_to_target_breaks_on_pause_and_phrase_end():
    tk = lambda t: [t[i:i + 2] for i in range(0, len(t), 2)]  # noqa: E731  2-char words
    # four 0.3 s words in one phrase: merged into one ~1.2 s cue (3-word cap -> 3 + 1 avoided)
    words = [W("กก", 0.0, 0.3), W("ขข", 0.3, 0.6), W("คค", 0.6, 0.9), W("จจ", 2.0, 2.3)]
    groups = s.segment_words(words, tokenizer=tk)
    assert [[w["text"] for w in g] for g in groups] == [["กก", "ขข", "คค"], ["จจ"]]  # pause split
    # curated-phrase boundary with a gap >= 0.25 s is a hard break, a tiny gap is not
    a = [dict(W("กก", 0.0, 0.4), phrase=0), dict(W("ขข", 0.7, 1.0), phrase=1)]
    assert len(s.segment_words(a, tokenizer=tk)) == 2
    # two very short pieces across a tiny gap are rescued into one cue
    b = [dict(W("กก", 0.0, 0.1), phrase=0), dict(W("ขข", 0.15, 0.25), phrase=1)]
    assert len(s.segment_words(b, tokenizer=tk)) == 1
    # but longer curated phrases keep their own cues (phrase end treated as a sentence end)
    c = [dict(W("กก", 0.0, 0.5), phrase=0), dict(W("ขข", 0.55, 1.0), phrase=1)]
    assert len(s.segment_words(c, tokenizer=tk)) == 2
    # an omitted span between words is a hard break
    assert len(s.segment_words(b, tokenizer=tk, omitted=[(0.1, 0.15)])) == 2
    # duration cap 1.5 s
    words = [W("กก", 0.0, 0.8), W("ขข", 0.8, 1.6)]
    assert len(s.segment_words(words, tokenizer=tk)) == 2
    # never cut a particle away from its head when the merged cue fits
    words = [W("ไม่", 0.0, 0.3), W("มี", 0.3, 0.6), W("ครับ", 0.6, 0.9)]
    toks = {"ไม่มีครับ": ["ไม่", "มี", "ครับ"], "ไม่มี": ["ไม่", "มี"], "มีครับ": ["มี", "ครับ"],
            "ไม่": ["ไม่"], "มี": ["มี"], "ครับ": ["ครับ"]}
    assert len(s.segment_words(words, tokenizer=lambda t: toks[t])) == 1

def test_build_cues_gap_cap_min_dur_end_limit_and_vad_clamp():
    pw = [[W("กก", 0.0, 0.5), W("ขข", 0.5, 2.4)], [W("คค", 2.4, 2.5)], [W("งง", 54.8, 56.0)]]
    cues = s.build_cues(pw, regions=[[0.2, 3.0], [54.7, 60]], tokenizer=lambda t: [t])
    errs = s.validate_cues([blk(i + 1, c["start"], c["end"], c["text"]) for i, c in enumerate(cues)],
                           tokenizer=lambda t: [t])
    assert errs == [], errs
    assert cues[0]["start"] == 0.2          # pulled into speech
    assert cues[-1]["end"] <= 55.0


def test_rebalance_short_gives_min_read_within_run_only():
    cues = [{"text": "a", "start": 1.0, "end": 1.1}, {"text": "b", "start": 1.134, "end": 1.6},
            {"text": "c", "start": 1.634, "end": 2.9}, {"text": "d", "start": 5.0, "end": 5.1}]
    s.rebalance_short(cues)
    assert all(c["end"] - c["start"] >= s.MIN_READ - 1e-9 for c in cues[:3])
    assert cues[0]["start"] == 1.0 and abs(cues[2]["end"] - 2.9) < 1e-9
    assert cues[3]["end"] - cues[3]["start"] < s.MIN_READ  # isolated cue untouched


def test_repeated_tokens_count_individually():
    toks = {"ไม่ไม่ไม่ใช่": ["ไม่", "ไม่", "ไม่", "ใช่"], "ไม่มีอะไรอ่ะไม่มี": ["ไม่", "มี", "อะไร", "อ่ะ", "ไม่", "มี"],
            "ไม่มีนะครับ": ["ไม่", "มี", "นะ", "ครับ"]}
    tk = lambda t: toks[t]  # noqa: E731
    assert s.count_words("ไม่ไม่ไม่ใช่", tk) == 4
    assert s.count_words("ไม่มีอะไรอ่ะไม่มี", tk) == 6
    assert s.count_words("ไม่มีนะครับ", tk) == 1  # no repetition: natural-word rule


def test_build_cues_never_linger_past_speech():
    tk = lambda t: [t]  # noqa: E731
    pw = [[W("กก", 1.0, 1.3)], [W("ขข", 3.0, 3.2)]]
    cues = s.build_cues(pw, regions=[[1.0, 1.3], [3.0, 3.2]], tokenizer=tk)
    assert all(c["end"] <= c["speech_end"] + 0.1 + 1e-9 for c in cues)
    assert cues[0]["end"] <= 1.3 + 0.1 and cues[1]["end"] <= 3.2 + 0.1   # no padding to 0.8 s
    assert s.cue_speech_checks(cues, [[1.0, 1.3], [3.0, 3.2]]) == []


def test_adjacent_vad_speech_attached_far_speech_reported():
    tk = lambda t: [t]  # noqa: E731
    regions = [[1.0, 1.9], [5.0, 6.0]]
    cues = s.build_cues([[W("กก", 1.0, 1.4)]], regions=regions, tokenizer=tk)
    assert cues[0]["end"] >= 1.85            # VAD tail of the same word is shown, not lingering
    unc = s.uncovered_speech(regions, cues, [])
    assert [(a, b) for a, b, why in unc] == [(5.0, 6.0)] and unc[0][2] is None
    logged = s.uncovered_speech(regions, cues, [{"t0": 4.9, "t1": 6.1, "reason": "laughter"}])
    assert logged[0][2] == "laughter"
