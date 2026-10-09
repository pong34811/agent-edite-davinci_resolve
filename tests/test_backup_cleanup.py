import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import backup_drp, cleanup_backups as cb  # noqa: E402


def make_zip(path):
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("Project.xml", "<x/>")


class VerifyDrpTests(unittest.TestCase):
    def test_valid_empty_and_bad(self):
        with tempfile.TemporaryDirectory() as d:
            good, empty, bad = Path(d, "g.drp"), Path(d, "e.drp"), Path(d, "b.drp")
            make_zip(good)
            empty.write_bytes(b"")
            bad.write_bytes(b"not a zip")
            self.assertGreater(backup_drp.verify_drp(good), 0)
            for path in (empty, bad, Path(d, "missing.drp")):
                with self.assertRaises(RuntimeError):
                    backup_drp.verify_drp(path)


class CleanupTests(unittest.TestCase):
    def test_classify_keeps_rollbacks(self):
        self.assertEqual(cb.classify("aomimama-2026-09-p1-pre-enrichment-1.drp"), "keep")
        self.assertEqual(cb.classify("before_promotion_x.drp"), "keep")
        self.assertEqual(cb.classify("before_python_batch_1.drp"), "delete")
        self.assertEqual(cb.classify("something_else.drp"), "unmatched")

    def test_sweep_deletes_only_matching_prefixes(self):
        with tempfile.TemporaryDirectory() as d:
            names = ["before_python_batch_a.drp", "before_python_vdo_b.drp",
                     "before_promotion_c.drp", "aomimama-2026-09-p1-pre-enrichment-d.drp",
                     "unknown.drp", "fresh.drp"]
            for n in names:
                Path(d, n).write_bytes(b"x")
            dry = cb.sweep(d, Path(d, "fresh.drp"), confirm=False)
            self.assertEqual(sorted(dry["would_delete"]), sorted(names[:2]))
            self.assertEqual(len(list(Path(d).glob("*.drp"))), 6)
            done = cb.sweep(d, Path(d, "fresh.drp"), confirm=True)
            self.assertEqual(sorted(done["deleted"]), sorted(names[:2]))
            left = {p.name for p in Path(d).glob("*.drp")}
            self.assertEqual(left, set(names[2:]))
            self.assertEqual(done["skipped_unmatched"], ["unknown.drp"])


if __name__ == "__main__":
    unittest.main()
