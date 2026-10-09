import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import caption_lint as cl  # noqa: E402


def srt(*cues):
    return "\n\n".join("%d\n%s\n%s" % (i, t, b) for i, (t, b) in enumerate(cues, 1))


class CaptionLintTests(unittest.TestCase):
    def test_clean_cue_passes(self):
        text = srt(("00:00:00,000 --> 00:00:01,200", "เก่งมากเลย"))
        self.assertEqual(cl.lint(text), [])

    def test_too_long_duration(self):
        text = srt(("00:00:00,000 --> 00:00:01,600", "เก่งมาก"))
        self.assertEqual([m for _, m in cl.lint(text)], ["too long: 1.60s > 1.50s"])

    def test_boundary_is_allowed(self):
        text = srt(("00:00:00,000 --> 00:00:01,500", "เก่งมาก"))
        self.assertEqual(cl.lint(text), [])

    def test_too_many_thai_chars(self):
        text = srt(("00:00:00,000 --> 00:00:01,000", "ก" * 15))
        self.assertIn("too many Thai characters: 15 > 14", [m for _, m in cl.lint(text)])

    def test_space_between_thai_flagged_but_latin_name_ok(self):
        bad = srt(("00:00:00,000 --> 00:00:01,000", "เก่ง มาก"))
        ok = srt(("00:00:00,000 --> 00:00:01,000", "เล่น Minecraft กัน"))
        self.assertIn("space between Thai characters", [m for _, m in cl.lint(bad)])
        self.assertEqual(cl.lint(ok), [])

    def test_bom_crlf_and_empty_cue(self):
        text = "﻿1\r\n00:00:00,000 --> 00:00:01,000\r\n\r\n"
        self.assertEqual([m for _, m in cl.lint(text)], ["empty cue"])


if __name__ == "__main__":
    unittest.main()
