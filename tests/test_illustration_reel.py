import importlib
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def plan(*rows):
    out, cursor = [], 0
    for cid, start, end in rows:
        out.append({'id': cid, 'start': start, 'end': end, 'sourceStart': cursor,
                    'sourceEnd': cursor + end - start, 'file': 'reel.mov'})
        cursor += end - start
    return out


class IllustrationReelTests(unittest.TestCase):
    def setUp(self):
        self.m = importlib.import_module('scripts.illustration_reel')

    def test_accepts_contiguous_ordered_plan(self):
        self.assertEqual(self.m.validate_plan(plan(('a', 10, 70), ('b', 80, 200)), 4151), 180)

    def test_rejects_overlap(self):
        with self.assertRaisesRegex(ValueError, 'overlap'):
            self.m.validate_plan(plan(('a', 10, 90), ('b', 80, 200)), 4151)

    def test_rejects_past_timeline_end(self):
        with self.assertRaisesRegex(ValueError, 'timeline end'):
            self.m.validate_plan(plan(('a', 4100, 4200)), 4151)

    def test_rejects_source_gap_or_length_mismatch(self):
        p = plan(('a', 10, 70), ('b', 80, 200))
        p[1]['sourceStart'] += 1
        with self.assertRaisesRegex(ValueError, 'source'):
            self.m.validate_plan(p, 4151)

    def test_rejects_duplicate_ids_and_empty(self):
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.m.validate_plan(plan(('a', 10, 70), ('a', 80, 200)), 4151)
        with self.assertRaisesRegex(ValueError, 'empty'):
            self.m.validate_plan([], 4151)

    def test_matches_placed_item(self):
        x = plan(('a', 10, 70))[0]
        self.assertTrue(self.m.matches({'start': 10, 'end': 70, 'left': 0, 'path': 'D:/x/reel.mov'}, x, 'D:/x'))
        self.assertFalse(self.m.matches({'start': 10, 'end': 69, 'left': 0, 'path': 'D:/x/reel.mov'}, x, 'D:/x'))
        self.assertFalse(self.m.matches({'start': 10, 'end': 70, 'left': 0, 'path': 'D:/x/other.mov'}, x, 'D:/x'))
        self.assertFalse(self.m.matches({'start': 10, 'end': 70, 'left': 0, 'path': None}, x, 'D:/x'))

    def test_matches_rejects_same_basename_in_other_dir(self):
        x = plan(('a', 10, 70))[0]
        item = {'start': 10, 'end': 70, 'left': 0, 'path': 'D:/old_task/reel.mov'}
        self.assertFalse(self.m.matches(item, x, 'D:/x'))

    def test_check_raises_runtime_error(self):
        self.m.check(True, 'unused')
        with self.assertRaisesRegex(RuntimeError, 'AddTrack failed'):
            self.m.check(False, 'AddTrack failed')

    def test_cli_help_runs_without_resolve(self):
        r = subprocess.run([sys.executable, str(ROOT / 'scripts/illustration_reel.py'), '--help'],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        for flag in ('--source-id', '--target', '--root', '--bin', '--pilot'):
            self.assertIn(flag, r.stdout)


if __name__ == '__main__':
    unittest.main()
