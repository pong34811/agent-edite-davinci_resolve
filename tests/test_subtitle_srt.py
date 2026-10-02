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
    assert cues[0]["end"] <= 1.3 + 0.1                     # no padding to 0.8 s
    assert abs(cues[1]["end"] - 3.35) < 1e-9 and cues[1]["floor"]  # 0.2 s cue raised to 0.35 s
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


def C(text, a, b, ph, ss=None):
    return {"text": text, "start": a, "end": b, "speech_end": b, "speech_start": a if ss is None else ss,
            "phrases": {ph}}


def test_read_floor_merges_same_phrase_else_extends_never_starts_early():
    tk = lambda t: [t[i:i + 2] for i in range(0, len(t), 2)]  # noqa: E731
    cues = [C("กก", 1.0, 1.15, 0), C("ขข", 1.2, 1.8, 0)]
    s.enforce_floor(cues, tokenizer=tk)
    assert len(cues) == 1 and cues[0]["text"] == "กกขข" and cues[0]["end"] == 1.8
    long16 = "งงงงงงงงงงงงงงงง"
    cues = [C("กก", 1.0, 1.1, 0), C("ขข", 1.5, 2.0, 1), C("คค", 3.0, 3.1, 2), C(long16, 3.3, 3.7, 3)]
    s.enforce_floor(cues, tokenizer=tk)
    assert abs(cues[0]["end"] - 1.35) < 1e-9 and cues[0]["floor"]          # free gap extension
    assert abs(cues[2]["end"] - cues[2]["start"] - 0.35) < 1e-6            # next cue delayed...
    n = cues[3]
    assert n["start"] <= n["speech_start"] + s.BORROW_MAX + 1e-9 and n["end"] - n["start"] >= 0.35 - 1e-9
    assert all(c["start"] >= c["speech_start"] - 1e-9 for c in cues)       # ...no early starts
    # blocked on both sides: next cue already at its +0.2 s limit -> cue stays short
    cues = [C("กก", 1.0, 1.1, 0), C(long16, 1.334, 1.9, 1, ss=1.134), C("ขข", 1.934, 2.6, 2)]
    s.enforce_floor(cues, tokenizer=tk)
    assert cues[0]["end"] - cues[0]["start"] < 0.35 and cues[0]["start"] == 1.0
    assert s.cue_speech_checks(cues, None) == []


def test_end_limit_comes_from_jobs_json_duration(tmp_path):
    import json
    (tmp_path / "jobs.json").write_text(json.dumps([{"job": 1, "duration_s": 60.0}, {"job": 2, "duration_s": 55.0}]),
                                        encoding="utf-8")
    assert s.job_end_limit(str(tmp_path), 1) == 60.0
    assert s.job_end_limit(str(tmp_path), 2) == 55.0
    assert s.job_end_limit(str(tmp_path), 9) == s.END_LIMIT          # no entry -> fallback
    assert s.job_end_limit(str(tmp_path / "none"), 1) == s.END_LIMIT  # no jobs.json
    # a 60 s job may hold cues past 55 s; the validator honours the passed limit
    tk = lambda t: [t]  # noqa: E731
    cues = s.build_cues([[W("กก", 57.0, 57.6)]], regions=[[57.0, 57.6]], end_limit=60.0, tokenizer=tk)
    blocks = [blk(i + 1, c["start"], c["end"], c["text"]) for i, c in enumerate(cues)]
    assert len(cues) == 1 and s.validate_cues(blocks, end_limit=60.0, tokenizer=tk) == []
    assert any("> 55.0" in e for e in s.validate_cues(blocks, tokenizer=tk))


def test_blocked_short_cue_records_reason_and_stats():
    tk = lambda t: [t[i:i + 2] for i in range(0, len(t), 2)]  # noqa: E731
    long16 = "งงงงงงงงงงงงงงงง"
    cues = [C("กก", 1.0, 1.1, 0), C(long16, 1.334, 1.9, 1, ss=1.134), C("ขข", 1.934, 2.6, 2)]
    s.enforce_floor(cues, tokenizer=tk)
    assert "already delayed" in cues[0]["short_reason"]
    st = s.cue_stats(cues)
    assert st["n"] == 3 and st["short"] == 1 and abs(st["max"] - 0.666) < 1e-6


def test_add_custom_words_counts_name_as_one_word():
    s.add_custom_words(["ทดสอบชื่อพิเศษ"])
    assert "ทดสอบชื่อพิเศษ" in s.CUSTOM_WORDS and s._TRIE is None
    assert s.split_words("ทดสอบชื่อพิเศษ") == ["ทดสอบชื่อพิเศษ"]


def test_start_snaps_forward_to_nearby_vad_onset_only():
    regions = [[1.0, 2.0], [5.0, 6.0]]
    cues = [C("กก", 0.8, 1.5, 0), C("ขข", 3.5, 4.2, 1)]
    s.snap_start_into_speech(cues, regions)
    assert cues[0]["start"] == 1.0 and cues[0]["speech_start"] == 1.0   # 0.2 s early -> snapped
    assert cues[1]["start"] == 3.5                                       # 1.5 s early -> left alone
    tiny = [C("กก", 0.75, 0.95, 0), C("ขข", 1.5, 2.0, 1)]                # ends before the onset
    s.snap_start_into_speech(tiny, regions)
    assert tiny[0]["start"] == 1.0 and abs(tiny[0]["end"] - 1.1) < 1e-9 and tiny[0]["end"] < tiny[1]["start"]


def test_max_chars_counts_spacing_glyphs_not_code_points():
    # MAX_CHARS counts spacing characters: Thai above/below vowels and tone marks are not
    # counted, so 'แต่เพื่อนไม่รอดอ่ะ' (18 code points) is 13; a 15-glyph cue always fails.
    assert len("แต่เพื่อนไม่รอดอ่ะ") == 18 and s.visible_len("แต่เพื่อนไม่รอดอ่ะ") == 13
    tk = lambda t: [t]  # noqa: E731
    errs = s.validate_cues([blk(1, 1.0, 2.0, "กขคงจฉชซฌญฎฏฐฑฒ")], tokenizer=tk)
    assert any("15 chars > 14" in e for e in errs)


def test_split_before_forces_break_and_blocks_floor_merge():
    tk = lambda t: [t]  # noqa: E731
    a, b = [W("กก", 1.0, 1.2)], [W("ขข", 1.2, 1.6)]
    assert len(s.build_cues([a, b], tokenizer=tk)) == 1          # joined (gap < PHRASE_JOIN_GAP)
    b2 = [dict(W("ขขขขขขขข", 1.2, 1.9), split_before=True)]
    cues = s.build_cues([a, b2], tokenizer=tk)
    assert [c["text"] for c in cues] == ["กก", "ขขขขขขขข"]  # forced break, no floor merge
    assert cues[0]["end"] - cues[0]["start"] >= 0.35 - 1e-9        # floor met by delaying the next
    assert cues[1]["start"] <= 1.2 + s.BORROW_MAX + 1e-9 and cues[1]["start"] - cues[0]["end"] >= s.MIN_GAP - 1e-9


def test_vad_clamp_false_drops_vad_speech_start_check(tmp_path):
    import json
    (tmp_path / "asr").mkdir()
    (tmp_path / "srt").mkdir()
    (tmp_path / "jobs.json").write_text(json.dumps([{"job": 1, "duration_s": 55.0}]), encoding="utf-8")
    (tmp_path / "asr" / "job1.json").write_text(json.dumps({"passes": {"raw": {"segments": []}}}), encoding="utf-8")
    (tmp_path / "asr" / "job1_extra.json").write_text(json.dumps(
        {"passes": {}, "vad_raw": [[10.7, 10.8]], "vad_voice": []}), encoding="utf-8")
    cur = {"job": 1, "phrases": [{"text": "โอ้ว", "t0": 10.38, "t1": 10.7}],
           "no_vad_justified": [], "omitted": []}
    p = tmp_path / "srt" / "job1.curation.json"
    p.write_text(json.dumps(cur, ensure_ascii=False), encoding="utf-8")
    _, cues, errs = s.build_job(str(tmp_path), 1)
    assert any("before speech start" in e for e in errs)          # VAD onset 10.7 is the reference
    cur["vad_clamp"] = False
    p.write_text(json.dumps(cur, ensure_ascii=False), encoding="utf-8")
    _, cues, errs = s.build_job(str(tmp_path), 1)
    assert errs == [] and cues[0]["start"] == 10.38


def test_attach_skip_omitted_keeps_cue_off_logged_speech():
    tk = lambda t: [t]  # noqa: E731
    regions = [[2.98, 3.94], [4.22, 5.66]]
    words = [[W("ใครอ่ะ", 4.25, 4.9)]]
    om = [{"t0": 2.15, "t1": 3.85, "reason": "unresolved"}]
    base = s.build_cues(words, regions, tokenizer=tk, omitted=om)
    assert base[0]["start"] < 4.0                      # default: attaches onto the omitted piece
    skip = s.build_cues(words, regions, tokenizer=tk, omitted=om, attach_skip_omitted=True)
    assert skip[0]["start"] >= 4.22 - 1e-9
