import unittest
import importlib


class OfflinePacketTests(unittest.TestCase):
    def test_caption_clock_uses_each_timeline_fps(self):
        m = importlib.import_module('scripts.build_offline_review')
        row = {'start': 100, 'record_fps': '25', 'tracks': [
            {'kind': 'subtitle', 'index': 1, 'items': [
                {'start': 125, 'end': 150, 'name': 'ตกใจ'}]}]}
        result = m.caption_map(row)
        self.assertEqual(result[0]['relative_start_seconds'], 1.0)
        self.assertEqual(result[0]['relative_end_seconds'], 2.0)
        self.assertEqual(result[0]['text'], 'ตกใจ')

    def test_audio_values_do_not_claim_speech_loudness(self):
        m = importlib.import_module('scripts.build_offline_review')
        result = m.audio_metrics('mean_volume: -20.5 dB\nmax_volume: -1.0 dB\nsilence_start: 2\nsilence_end: 3 | silence_duration: 1')
        self.assertEqual(result['mixed_mean_dbfs'], -20.5)
        self.assertEqual(result['mixed_max_dbfs'], -1.0)
        self.assertEqual(result['silences'], [{'start': 2.0, 'end': 3.0, 'duration': 1.0}])
        self.assertIn('not isolated speech', result['measurement_limit'])


if __name__ == '__main__':
    unittest.main()
