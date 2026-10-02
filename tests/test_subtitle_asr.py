import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import subtitle_asr as s  # noqa: E402


def toks(parts, t0=1.0, step=0.1):
    return [{"word": w, "start": t0 + i * step, "end": t0 + (i + 1) * step, "probability": 0.9}
            for i, w in enumerate(parts)]


def test_char_index_interpolates_and_concat_matches():
    ch = s.char_index(toks(["เล", "ื", "อ"]))
    assert "".join(c["ch"] for c in ch) == "เลือ"
    assert abs(ch[0]["start"] - 1.0) < 1e-9 and abs(ch[-1]["end"] - 1.3) < 1e-9
    assert abs(ch[1]["start"] - 1.05) < 1e-9


def test_foreign_glyph_dropped_with_its_time_and_rejoin():
    ch = s.char_index(toks(["เต็ม", "膈", "ับ"]))
    clean = s.clean_chars(ch)
    assert "".join(c["ch"] for c in clean) == "เต็มับ"
    assert any(s.is_foreign(c["ch"]) for c in ch)
    assert abs(clean[-1]["end"] - 1.3) < 1e-9  # later chars keep original times
    words = s.words_from_chars(clean, tokenizer=lambda t: ["เต็ม", "ับ"])
    assert len(words) == 1 and words[0]["text"] == "เต็มับ"


def test_latin_kept_and_lone_thai_and_mai_yamok_merge():
    ch = s.char_index(toks(["แม่", "ง", "ได้", "ๆ"]))
    words = s.words_from_chars(ch, tokenizer=lambda t: ["แม่", "ง", "ได้", "ๆ"])
    assert [w["text"] for w in words] == ["แม่ง", "ได้ๆ"]
    assert not s.is_foreign("A")


def st(lp, w, fg=0, rep=0):
    return {"stats": {"mean_avg_logprob": lp, "n_words": w, "foreign_glyphs": fg, "repetition": rep}}


def test_choose_pass():
    assert s.choose_pass({"raw": st(-0.9, 100), "voice": st(-0.4, 95)})[0] == "voice"
    # speech loss makes the pass ineligible
    assert s.choose_pass({"raw": st(-0.9, 100), "voice": st(-0.4, 20)})[0] == "raw"
    # repetition loop with deceptively good logprob loses
    assert s.choose_pass({"raw": st(-0.06, 20, rep=1), "chunk": st(-0.3, 40)})[0] == "chunk"


def test_repeat_run_regex():
    assert s.REPEAT_RE.search("โทษ" + "ๆ" * 8)
    assert not s.REPEAT_RE.search("ไม่ได้โม้เลย")
