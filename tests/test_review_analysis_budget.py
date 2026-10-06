from typing import Any
import unittest
from scripts import analyze_review_previews as module


class GenerationBudgetTests(unittest.TestCase):
    def test_video_request_reserves_tokens_for_complete_json(self):
        factory: Any = getattr(module, 'generation_options', None)
        if not callable(factory):
            self.fail('Missing complete-JSON generation options')
        options = factory()
        self.assertGreaterEqual(options['max_tokens'], 8192)
        self.assertEqual(options['response_format'], {'type': 'json_object'})
        self.assertEqual(options['extra_body']['thinking_config']['thinkingBudget'], 0)

    def test_options_generate_native_json_and_no_thinking_payload(self):
        factory: Any = getattr(module, 'generation_options', None)
        if not callable(factory):
            self.fail('Missing complete-JSON generation options')
        from agent.gemini_native_adapter import build_gemini_request
        options = factory()
        payload = build_gemini_request(
            messages=[{'role': 'user', 'content': 'Return JSON.'}],
            model='gemini-2.5-flash',
            max_tokens=options['max_tokens'],
            response_format=options['response_format'],
            thinking_config=options['extra_body']['thinking_config'])
        self.assertEqual(payload['generationConfig']['responseMimeType'], 'application/json')
        self.assertEqual(payload['generationConfig']['thinkingConfig']['thinkingBudget'], 0)
        self.assertGreaterEqual(payload['generationConfig']['maxOutputTokens'], 8192)


class CueBoundsTests(unittest.TestCase):
    def test_out_of_range_cues_are_retained_as_rejections_not_accepted(self):
        partition: Any = getattr(module, 'partition_cues', None)
        if not callable(partition):
            self.fail('Missing cue quarantine')
        good = {'relative_seconds': 10.5, 'kind': 'sfx'}
        bad = {'relative_seconds': 95.0, 'kind': 'illustration'}
        result: Any = partition([good, bad], 90.6)
        accepted, rejected = result
        self.assertEqual(accepted, [good])
        self.assertEqual(rejected[0]['cue'], bad)
        self.assertEqual(rejected[0]['reason'], 'outside_timeline_or_invalid_timestamp')


if __name__ == '__main__':
    unittest.main()
