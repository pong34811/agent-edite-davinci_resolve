import unittest
import importlib


class AssetDraftTests(unittest.TestCase):
    def test_emotional_words_are_only_provisional_hints(self):
        m = importlib.import_module('scripts.build_offline_asset_draft')
        self.assertEqual(m.search_terms('เฮ้ยเดี๋ยวนะ'), ['ตกใจ', 'shocked', 'surprised'])
        self.assertEqual(m.search_terms('ทำไมเป็นแบบนี้'), ['งง', 'confused', 'what'])
        self.assertEqual(m.search_terms('ข้อความทั่วไป'), [])

    def test_choose_points_preserves_frames_and_avoids_dense_shortlist(self):
        m = importlib.import_module('scripts.build_offline_asset_draft')
        rows = [{'relative_start_seconds': t, 'absolute_start_frame': t * 60, 'text': 'เฮ้ย'} for t in [1, 3, 25, 50, 80]]
        result = m.choose_points(rows)
        self.assertEqual([r['relative_start_seconds'] for r in result], [1, 25, 50])
        self.assertEqual(result[1]['absolute_start_frame'], 1500)


if __name__ == '__main__':
    unittest.main()
