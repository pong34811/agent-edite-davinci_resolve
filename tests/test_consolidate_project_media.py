import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import consolidate_project_media as cpm  # noqa: E402

DEST = "Z:\\armigon\\Why Vtuber"


class SubfolderTests(unittest.TestCase):
    def test_kinds(self):
        self.assertEqual(cpm.subfolder_for("G:\\x\\3.gif\\a.gif"), "gif")
        self.assertEqual(cpm.subfolder_for("C:/d/sub.srt"), "subtitles")
        self.assertEqual(cpm.subfolder_for("D:\\p\\v1.mov"), "illustrations")
        self.assertEqual(cpm.subfolder_for("G:\\Projects\\1.1 bgm\\song.wav"), "bgm")
        self.assertEqual(cpm.subfolder_for("Z:\\SFX\\pop.wav"), "sfx")
        self.assertEqual(cpm.subfolder_for("Z:\\x\\clip.mp4"), "footage")


class PlanTests(unittest.TestCase):
    def test_skips_dest_timelines_and_clashes(self):
        clips = [
            dict(id="1", name="a", file=DEST + "\\a.mp4"),
            dict(id="2", name="tl", file=""),
            dict(id="3", name="p", file="Z:\\SFX\\pop.wav"),
            dict(id="4", name="p2", file="Z:\\SFX_processed\\pop.wav"),
            dict(id="5", name="p", file="z:/sfx/POP.wav"),
        ]
        moves, skipped = cpm.plan(clips, DEST)
        self.assertEqual([m["id"] for m in moves], ["3", "5"])
        self.assertEqual(moves[0]["target"], DEST + "\\sfx\\pop.wav")
        self.assertEqual(sorted(c["id"] for c, _ in skipped), ["1", "4"])


if __name__ == "__main__":
    unittest.main()
