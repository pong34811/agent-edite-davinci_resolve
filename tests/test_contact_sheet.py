"""Exercise the contact-sheet helper only on generated scratch images."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('contact_sheet_tests', ROOT / 'scripts/contact_sheet.py')
assert spec is not None and spec.loader is not None
contact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contact)


class ContactSheetTests(unittest.TestCase):
    def setUp(self):
        home = Path(os.environ.get('HERMES_HOME') or Path.home() / (
            'AppData/Local/hermes' if os.name == 'nt' else '.hermes'
        ))
        scratch = Path(os.environ.get('TMPDIR') or home / 'cache/scratch')
        scratch.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.frames = self.root / 'frames'
        self.frames.mkdir()

    def image(self, name='frame_01.jpg'):
        path = self.frames / name
        Image.new('RGB', (80, 40), (200, 40, 80)).save(path)
        return path

    def test_existing_source_frame_is_not_overwritten(self):
        source = self.image('sheet_01.jpg')
        before = source.read_bytes()
        with self.assertRaises(FileExistsError):
            contact.build_sheets(str(self.root), str(self.frames))
        self.assertEqual(source.read_bytes(), before)

    def test_missing_pending_frame_cannot_shift_vision_indices(self):
        source = self.image()
        (self.root / 'visual.json').write_text(json.dumps({
            'frame_paths': [str(self.frames / 'missing.jpg'), str(source)],
            'frame_metadata': [
                {'frame_index': 1, 'time_seconds': 1},
                {'frame_index': 2, 'time_seconds': 2},
            ],
        }), encoding='utf-8')
        with self.assertRaises(FileNotFoundError):
            contact.build_sheets(str(self.root), str(self.root / 'output'))
        self.assertFalse((self.root / 'output').exists())

    def test_cli_builds_complete_sheets_without_changing_frames(self):
        sources = [self.image('frame_%02d.jpg' % i) for i in range(1, 6)]
        before = {path: path.read_bytes() for path in sources}
        output = self.root / 'output'
        result = subprocess.run([
            sys.executable, str(ROOT / 'scripts/contact_sheet.py'),
            str(self.root), str(output), '--columns', '2', '--rows', '1',
            '--tile-width', '60',
        ], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('frames=5 sheets=3', result.stdout)
        for first, last in [(1, 2), (3, 4), (5, 5)]:
            self.assertIn('frames %d-%d' % (first, last), result.stdout)
        sheets = sorted(output.glob('sheet_*.jpg'))
        self.assertEqual(len(sheets), 3)
        for path in sheets:
            with Image.open(path) as sheet:
                sheet.load()
                self.assertEqual(sheet.size, (120, 56))
        for path in sources:
            self.assertEqual(path.read_bytes(), before[path])


    def test_nonpositive_dimensions_are_rejected_before_output(self):
        self.image()
        for key in ['tile_width', 'columns', 'rows']:
            for value in [-2, 0]:
                with self.subTest(key=key, value=value):
                    output = self.root / ('output_%s_%s' % (key, value))
                    with self.assertRaisesRegex(ValueError, 'must be positive'):
                        contact.build_sheets(str(self.root), str(output), **{key: value})
                    self.assertFalse(output.exists())


    def test_cli_reports_invalid_grid_as_usage_error(self):
        self.image()
        output = self.root / 'output'
        result = subprocess.run([
            sys.executable, str(ROOT / 'scripts/contact_sheet.py'),
            str(self.root), str(output), '--columns', '-2',
        ], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn('columns must be positive', result.stderr)
        self.assertNotIn('Traceback', result.stderr)
        self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
