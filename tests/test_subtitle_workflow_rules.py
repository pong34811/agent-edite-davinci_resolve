"""Regression checks for the documented native-caption workflow; no Resolve calls."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class SubtitleWorkflowRuleTests(unittest.TestCase):
    def read(self, relative):
        return (ROOT / relative).read_text(encoding='utf-8')

    def test_native_track_and_migration_reference(self):
        text = self.read('.agents/skills/thai-subtitles-resolve/SKILL.md')
        self.assertIn('## Subtitle-track-only workflow', text)
        self.assertIn('references/native-caption-migration.md', text)
        self.assertIn('Do not substitute Text+ / TextPlus', text)

    def test_state_dependent_reads_and_async_page(self):
        text = self.read('.agents/skills/thai-subtitles-resolve/SKILL.md')
        self.assertIn('inactive `Timeline.GetCurrentTimecode()`', text)
        self.assertIn('`OpenPage()` can return True before', text)
        self.assertIn('serialize', text)

    def test_preserving_legacy_and_delegated_style(self):
        text = self.read('.agents/skills/thai-subtitles-resolve/references/native-caption-migration.md')
        for rule in ['captions-only', 'exact text', 'absolute start/end frames',
                     'Do not shorten', 'user handles fonts/styles', 'separate verdicts',
                     'Never execute', 'fresh verified `.drp`']:
            self.assertIn(rule, text)

    def test_house_style_respects_caption_only_scope(self):
        text = self.read('.agents/skills/house-style/SKILL.md')
        self.assertIn('user handles fonts/styles', text)
        self.assertIn('permission to modify every historical Text+ timeline', text)

    def test_preview_and_audio_claims_are_bounded(self):
        text = self.read('.agents/skills/resolve-video-enrichment/SKILL.md')
        self.assertIn('Migration success is not publication-legibility approval', text)
        self.assertIn('AAC renders can decode to different PCM', text)
        self.assertIn('inactive `Timeline.GetCurrentTimecode()`', text)

if __name__ == '__main__':
    unittest.main()
