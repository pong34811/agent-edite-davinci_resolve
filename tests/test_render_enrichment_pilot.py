import importlib
import unittest


class PilotRenderTests(unittest.TestCase):
    def test_rejects_audio_only_or_wrong_duration(self):
        m = importlib.import_module('scripts.render_enrichment_pilot')
        with self.assertRaises(ValueError):
            m.verify_media({'streams':[{'codec_type':'audio'}], 'format':{'duration':'90.6'}},90.6)
        with self.assertRaises(ValueError):
            m.verify_media({'streams':[{'codec_type':'video','width':1280,'height':720,'avg_frame_rate':'60/1'}, {'codec_type':'audio'}], 'format':{'duration':'80'}},90.6)

    def test_accepts_exact_preview_spec(self):
        m = importlib.import_module('scripts.render_enrichment_pilot')
        m.verify_media({'streams':[{'codec_type':'video','width':1280,'height':720,'avg_frame_rate':'60/1'}, {'codec_type':'audio'}], 'format':{'duration':'90.602667'}},90.6)


if __name__ == '__main__':
    unittest.main()
