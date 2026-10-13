"""Offline tests for the 9:16 converters' layout maths and the SRT rule checker (no Resolve needed)."""
import importlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "pipeline"))

talk = importlib.import_module("convert_talk_9x16")
game = importlib.import_module("convert_game_9x16")
check_srt = importlib.import_module("check_srt")


class FacePanelTests(unittest.TestCase):
    def test_talk_face_params_fill_canvas_and_clamp(self):
        p = talk.face_params(1068)
        self.assertAlmostEqual(p["ZoomX"], 3.3975, places=3)       # 1.7778 * 1.075 / 0.5625
        self.assertAlmostEqual(p["Pan"], -206.4, places=1)
        self.assertAlmostEqual(p["Tilt"], -167.16, places=1)       # window bottom at src y ~1015
        left = talk.face_params(10)["Pan"]
        right = talk.face_params(1910)["Pan"]
        self.assertGreater(left, 0)                                 # clamped: window never leaves the frame
        self.assertLess(right, 0)
        self.assertAlmostEqual(left, -right, places=3)

    def test_talk_without_bar_crop_is_plain_full_height(self):
        p = talk.face_params(960, bar_crop=False)
        self.assertAlmostEqual(p["ZoomX"], 1920 / 1080 / 0.5625, places=4)
        self.assertAlmostEqual(p["Pan"], 0.0, places=6)
        self.assertAlmostEqual(p["Tilt"], 0.0, places=6)

    def test_game_face_panel_places_eyes_at_target_line(self):
        # facecam eyes at src (1692, 978); scale 3.0, panel from canvas y=960 => visible rows start at 760
        p = game.face_panel(3.0, 1692.0, top=960.0)
        self.assertAlmostEqual(p["ZoomX"], 3.0 / 0.5625, places=4)
        self.assertAlmostEqual(p["CropTop"], 760 * 0.5625, places=3)
        eye_canvas_y = 960 + (978 - 760) * 3.0
        self.assertAlmostEqual(eye_canvas_y, 1614.0)
        right_edge = game.face_panel(3.0, 1900.0, top=960.0)        # window clamps at the source's right edge
        self.assertAlmostEqual(right_edge["Pan"], game.face_panel(3.0, 1920.0, top=960.0)["Pan"], places=6)


class SrtCheckTests(unittest.TestCase):
    def _check(self, body):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "T1.srt"
            path.write_text(body, encoding="utf-8")
            return check_srt.check(str(path))

    def test_clean_file_passes(self):
        n, bad = self._check("1\n00:00:00,000 --> 00:00:01,000\nสวัสดี\n\n2\n00:00:01,100 --> 00:00:02,000\nครับ\n")
        self.assertEqual((n, bad), (2, []))

    def test_flags_replacement_char_long_cue_and_repetition(self):
        body = ("1\n00:00:00,000 --> 00:00:02,000\nยังเ\ufffdๆอีก\n\n"
                "2\n00:00:02,100 --> 00:00:03,000\nทุกสิ่งทุกอย่างทุกที\n\n"
                "3\n00:00:03,100 --> 00:00:04,000\nหาๆๆๆๆๆๆๆ\n")
        _, bad = self._check(body)
        kinds = {k.split(":")[0] for _, k in bad}
        self.assertTrue({"FFFD", "rep"} <= kinds)
        self.assertTrue(any(k.startswith("dur") for _, k in bad))
        self.assertTrue(any(k.startswith("len") for _, k in bad))

    def test_flags_hallucination_loop(self):
        body = "\n\n".join("%d\n00:00:%02d,000 --> 00:00:%02d,500\nเฮ้ยเฮ้ยเฮ้ย" % (i, i, i) for i in range(1, 11))
        _, bad = self._check(body + "\n")
        self.assertTrue(any(k.startswith("loop?") for _, k in bad))


if __name__ == "__main__":
    unittest.main()
