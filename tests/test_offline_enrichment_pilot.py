import importlib
import unittest


class PilotFrameTests(unittest.TestCase):
    def test_source_frames_follow_media_fps(self):
        m = importlib.import_module('scripts.apply_offline_enrichment_pilot')
        self.assertEqual(m.source_frames(120, 60, 25), 50)
        self.assertEqual(m.source_frames(5436, 60, 60), 5436)

    def test_rejects_out_of_bounds_append(self):
        m = importlib.import_module('scripts.apply_offline_enrichment_pilot')
        with self.assertRaises(ValueError):
            m.validate_range(100, 200, 190, 20)
        m.validate_range(100, 200, 150, 20)


if __name__ == '__main__':
    unittest.main()
