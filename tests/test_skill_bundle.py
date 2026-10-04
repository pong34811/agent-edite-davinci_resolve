import importlib.util
import json
import fnmatch
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('verify_skill_bundle', ROOT / 'scripts/verify_skill_bundle.py')
assert spec is not None and spec.loader is not None
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)

class SkillBundleTests(unittest.TestCase):
    def test_bundle_structure_references_and_checksums(self):
        result = verify.validate()
        self.assertEqual(result['errors'], [])
        self.assertTrue(result['ok'])
        self.assertEqual(result['core_skill_count'], 17)
        self.assertEqual(result['related_archive_count'], 13)

    def test_manifest_declares_all_active_skills_and_narrow_exclusions(self):
        m = json.loads((ROOT/'docs/skills-manifest.json').read_text(encoding='utf-8'))
        editing = {s['name']: s for s in m['skills'] if s['tier'] == 'editing'}
        self.assertIn('thai-proofread', editing)
        self.assertEqual(len(editing), 17)
        rules = m['excluded_repository_paths']
        self.assertTrue(any(r['path'] == '.agents/teamwork/**' for r in rules))
        for rule in rules:
            self.assertTrue(rule['reason'].strip())
            self.assertFalse(fnmatch.fnmatchcase('scripts/apply_video_style.py', rule['path']))
            self.assertFalse(fnmatch.fnmatchcase('tests/test_apply_video_style.py', rule['path']))

    def test_current_house_style_is_preserved(self):
        text = (ROOT/'.agents/skills/house-style/SKILL.md').read_text(encoding='utf-8')
        self.assertIn('1.5 seconds', text)
        self.assertIn('three short', text)
        self.assertIn('14 Thai characters', text)

    def test_subtitle_rules_agree_with_house_style(self):
        text = (ROOT/'.agents/skills/thai-subtitles-resolve/SKILL.md').read_text(encoding='utf-8')
        self.assertIn('MAX_DISPLAY_S = 1.5', text)
        self.assertNotIn('MAX_DISPLAY_S ≈ 2.2', text)
        self.assertIn('BARE', text)
        self.assertIn('at least ~1.2s', text)

    def test_cleanup_needs_approval(self):
        text = (ROOT/'.agents/skills/resolve-rough-cut/SKILL.md').read_text(encoding='utf-8')
        self.assertIn('delete only after explicit user approval', text)
        self.assertNotIn('Clean them up before handing over.', text)

    def test_archives_are_not_active_project_skills(self):
        active = {p.parent.name for p in (ROOT/'.agents/skills').glob('*/SKILL.md')}
        self.assertNotIn('brainstorming', active)
        self.assertNotIn('release-check', active)
        self.assertNotIn('codex', active)

    def test_manifest_has_only_real_usage_anchors(self):
        m = json.loads((ROOT/'docs/skills-manifest.json').read_text(encoding='utf-8'))
        for skill in m['skills']:
            for evidence in skill['history_evidence']:
                self.assertTrue(evidence['session_id'])
                self.assertIsInstance(evidence['message_id'], int)
        for name in ['resolve-color', 'resolve-conform']:
            row = next(s for s in m['skills'] if s['name']==name)
            self.assertEqual(row['history_loads'], 0)

    def test_backend_and_media_not_vendored(self):
        self.assertFalse((ROOT/'src/server.py').exists())
        self.assertFalse((ROOT/'Project.db').exists())
        self.assertFalse((ROOT/'.env').exists())
        m = json.loads((ROOT/'docs/skills-manifest.json').read_text(encoding='utf-8'))
        self.assertFalse(any(Path(x['path']).suffix.lower() in {'.mp4','.mov','.drp','.srt','.db'} for x in m['files']))

    def test_public_style_example_omits_live_clip_identity(self):
        sample = json.loads((ROOT/'presets/video/approved-gif-style.json').read_text(encoding='utf-8'))
        self.assertNotIn('source_clip_id', sample)
        self.assertNotIn('source_clip_name', sample)
        self.assertTrue(sample['properties'])

if __name__ == '__main__':
    unittest.main()
