import importlib
import subprocess
import sys
import unittest
from pathlib import Path


class ResolveVdoPythonTests(unittest.TestCase):
    def test_rejects_reference_from_other_project(self):
        m = importlib.import_module('scripts.apply_vdo_python')
        with self.assertRaises(ValueError):
            m.validate_reference({'source_project_id': 'other', 'raster': ['1920', '1080']}, 'here', ['1920', '1080'])

    def test_rejects_reference_from_other_raster(self):
        m = importlib.import_module('scripts.apply_vdo_python')
        with self.assertRaises(ValueError):
            m.validate_reference({'source_project_id': 'here', 'raster': ['1080', '1920']}, 'here', ['1920', '1080'])
        m.validate_reference({'source_project_id': 'here', 'raster': ['1920', '1080']}, 'here', ['1920', '1080'])

    def test_cli_help_runs_without_resolve(self):
        path = Path(__file__).resolve().parents[1] / 'scripts/apply_vdo_python.py'
        result = subprocess.run([sys.executable, str(path), '--help'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--target-clip-id', result.stdout)


if __name__ == '__main__':
    unittest.main()
