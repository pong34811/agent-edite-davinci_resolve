import importlib
import unittest


class BatchPlanTests(unittest.TestCase):
    def test_no_cue_does_not_invent_an_effect(self):
        m = importlib.import_module('scripts.enrich_timelines_python')
        row = {'ordinal':2,'timeline_id':'source','name':'clip','duration_seconds':20,
               'cue_points':[], 'bgm_candidates':[{'name':'NCSน่ารัก.mp3','path':'music','duration_seconds':30}]}
        plan = m.make_plan(row, exists=lambda p: True)
        self.assertEqual(plan['effects'], [])
        self.assertEqual(plan['bgm']['path'], 'music')
        self.assertEqual(plan['status'], 'provisional_draft_only')

    def test_preserves_exact_frames_and_filters_missing_assets(self):
        m = importlib.import_module('scripts.enrich_timelines_python')
        row = {'ordinal':3,'timeline_id':'source','name':'clip','duration_seconds':20,
               'cue_points':[{'absolute_start_frame':123,'text':'เฮ้ย', 'asset_candidates':{
                   'sfx':[{'path':'missing'},{'path':'sound'}], 'illustration':[{'path':'gif'}]}}],
               'bgm_candidates':[{'name':'NCSน่ารัก.mp3','path':'music','duration_seconds':30}]}
        plan = m.make_plan(row, exists=lambda p: p != 'missing')
        self.assertEqual(plan['effects'][0]['record_frame'],123)
        self.assertEqual(plan['effects'][0]['sfx_candidates'], ['sound'])
        self.assertEqual(plan['effects'][0]['gif_candidates'], ['gif'])


if __name__ == '__main__':
    unittest.main()
