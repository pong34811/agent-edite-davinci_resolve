import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_dynamic_srt as b  # noqa: E402
import caption_lint as cl  # noqa: E402


class BuildDynamicSrtTests(unittest.TestCase):
    def test_digits_only_cue_is_not_cut_to_default_minimum(self):
        # "1,950" has no Thai letters; it once got a 0.3 s hold although it is spoken for ~1.5 s.
        cues = b.build([(19.55, "1,950", None), (21.07, "คนแล้ว", None)], fps=60)
        s, e, _ = cues[0]
        self.assertGreater(e - s, 30)  # old Thai-only count gave 18 frames
        # a number spoken as words needs an explicit end; it must be honoured
        cues = b.build([(19.55, "1,950", 21.05)], fps=60)
        self.assertEqual(cues[0][1] - cues[0][0], 90)

    def test_end_clamped_before_next_start_and_cap(self):
        cues = b.build([(0.0, "ปลูกข้าวจนกว่า", None), (0.5, "ต่อไป", None)], fps=60, gap_frames=2)
        self.assertEqual(cues[0][1], 30 - 2)
        cues = b.build([(0.0, "ปลูกข้าวจนกว่า", None)], fps=60)
        self.assertLessEqual(cues[0][1] - cues[0][0], 90)

    def test_output_lints_clean(self):
        rows = [(1.0, "สวัสดี", None), (3.0, "ทุกคน", None)]
        cues = b.build(rows, fps=60)
        text = "\n".join("%d\n%s --> %s\n%s\n" % (i, b.fmt(s, 60), b.fmt(e, 60), t) for i, (s, e, t) in enumerate(cues, 1))
        self.assertEqual(cl.lint(text), [])


if __name__ == "__main__":
    unittest.main()
