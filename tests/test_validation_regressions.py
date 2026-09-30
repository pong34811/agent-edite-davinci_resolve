"""Negative checks against isolated copies; never modify the real bundle."""
import importlib.util
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('bundle_validator_regressions', ROOT / 'scripts/verify_skill_bundle.py')
assert spec is not None and spec.loader is not None
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class ValidationRegressionTests(unittest.TestCase):
    def setUp(self):
        home = Path(os.environ.get('HERMES_HOME') or Path.home() / (
            'AppData/Local/hermes' if os.name == 'nt' else '.hermes'
        ))
        scratch = Path(os.environ.get('TMPDIR') or home / 'cache/scratch')
        scratch.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = json.loads((ROOT / 'docs/skills-manifest.json').read_text(encoding='utf-8'))
        for record in self.manifest['files']:
            dst = self.root / record['path']
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / record['path'], dst)
            record['sha256'] = hashlib.sha256(dst.read_bytes()).hexdigest()
        self.write_manifest()

    def write_manifest(self):
        (self.root / 'docs/skills-manifest.json').write_text(
            json.dumps(self.manifest, ensure_ascii=False), encoding='utf-8'
        )

    def validate(self):
        with patch.object(verify, 'ROOT', self.root):
            return verify.validate()

    def test_unlisted_core_skill_file_is_rejected(self):
        omitted = '.agents/skills/house-style/SKILL.md'
        self.manifest['files'] = [r for r in self.manifest['files'] if r['path'] != omitted]
        self.manifest['counts']['manifest_files'] = len(self.manifest['files'])
        self.write_manifest()
        result = self.validate()
        self.assertFalse(result['ok'])
        self.assertIn('Unlisted bundle file: ' + omitted, result['errors'])

    def test_duplicate_skill_declaration_is_rejected(self):
        declared = [s for s in self.manifest['skills'] if s['tier'] == 'editing']
        declared[1]['path'] = declared[0]['path']
        self.write_manifest()
        result = self.validate()
        self.assertFalse(result['ok'])
        self.assertIn('Core skill declarations do not match active paths', result['errors'])

    def test_wrong_declared_file_count_is_rejected(self):
        self.manifest['counts']['manifest_files'] += 1
        self.write_manifest()
        result = self.validate()
        self.assertFalse(result['ok'])
        self.assertIn('Manifest count mismatch: manifest_files', result['errors'])

    def test_nonexistent_archive_declaration_is_rejected(self):
        archived = next(s for s in self.manifest['skills'] if s['tier'] == 'related_archive')
        archived['path'] = 'docs/related-skills/not-installed/SKILL.md'
        self.write_manifest()
        result = self.validate()
        self.assertFalse(result['ok'])
        self.assertIn('Archive skill declarations do not match disk', result['errors'])

    def test_duplicate_manifest_file_is_rejected(self):
        self.manifest['files'].append(dict(self.manifest['files'][0]))
        self.manifest['counts']['manifest_files'] = len(self.manifest['files'])
        self.write_manifest()
        result = self.validate()
        self.assertFalse(result['ok'])
        self.assertIn('Duplicate manifest file paths', result['errors'])

    def test_unlisted_review_role_is_rejected(self):
        omitted = '.agents/roles/cut-reviewer.md'
        self.manifest['files'] = [r for r in self.manifest['files'] if r['path'] != omitted]
        self.manifest['counts']['manifest_files'] = len(self.manifest['files'])
        self.write_manifest()
        result = self.validate()
        self.assertFalse(result['ok'])
        self.assertIn('Unlisted bundle file: ' + omitted, result['errors'])


    def test_healthy_isolated_bundle_passes(self):
        result = self.validate()
        self.assertTrue(result['ok'], result['errors'])

    def test_text_checksum_accepts_git_newline_conversion(self):
        relative = '.agents/skills/house-style/SKILL.md'
        path = self.root / relative
        record = next(r for r in self.manifest['files'] if r['path'] == relative)
        lf = path.read_bytes().replace(bytes([13, 10]), bytes([10]))
        crlf = lf.replace(bytes([10]), bytes([13, 10]))
        for expected, checked_out in [(lf, crlf), (crlf, lf)]:
            with self.subTest(expected_crlf=bytes([13, 10]) in expected):
                record['sha256'] = hashlib.sha256(expected).hexdigest()
                path.write_bytes(checked_out)
                self.write_manifest()
                result = self.validate()
                self.assertTrue(result['ok'], result['errors'])

    def test_binary_checksum_keeps_exact_bytes(self):
        relative = 'docs/binary-fixture.bin'
        path = self.root / relative
        original = bytes([0, 255, 13, 10, 65])
        path.write_bytes(original.replace(bytes([13, 10]), bytes([10])))
        self.manifest['files'].append({
            'path': relative,
            'sha256': hashlib.sha256(original).hexdigest(),
        })
        self.manifest['counts']['manifest_files'] = len(self.manifest['files'])
        self.write_manifest()
        result = self.validate()
        self.assertFalse(result['ok'])
        self.assertIn('Checksum mismatch: ' + relative, result['errors'])

    def test_empty_inventory_is_rejected(self):
        self.manifest['files'] = []
        self.manifest['counts']['manifest_files'] = 0
        self.write_manifest()
        result = self.validate()
        self.assertFalse(result['ok'])
        self.assertIn('Unlisted bundle file: .agents/skills/house-style/SKILL.md', result['errors'])

    def test_changed_file_checksum_is_rejected(self):
        path = self.root / '.agents/skills/house-style/SKILL.md'
        with path.open('a', encoding='utf-8') as handle:
            handle.write('\nUnexpected amendment.\n')
        result = self.validate()
        self.assertFalse(result['ok'])
        self.assertIn('Checksum mismatch: .agents/skills/house-style/SKILL.md', result['errors'])

    def test_archive_frontmatter_identity_is_checked(self):
        relative = 'docs/related-skills/computer-use/SKILL.md'
        path = self.root / relative
        parts = path.read_text(encoding='utf-8').split('---', 2)
        fm = yaml.safe_load(parts[1])
        fm['name'] = 'incorrect-name'
        path.write_text('---\n' + yaml.safe_dump(fm) + '---' + parts[2], encoding='utf-8')
        record = next(r for r in self.manifest['files'] if r['path'] == relative)
        record['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.write_manifest()
        result = self.validate()
        self.assertFalse(result['ok'])
        self.assertTrue(any(e.startswith('Archive name/frontmatter mismatch:') for e in result['errors']))


if __name__ == '__main__':
    unittest.main()