"""Pure-logic tests for scripts/resolve_recover.py (no Resolve needed)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import resolve_recover as rr  # noqa: E402


def test_decide():
    assert rr.decide(False, False) == "launch"
    assert rr.decide(True, True) == "ok"
    assert rr.decide(True, False) == "kill_then_launch"


def test_parse_dblist_restores_drive_colon():
    text = "google drive:G\\My Drive\\Projects\\Resolve Project Library:*:::DISK\n"
    assert rr.parse_dblist(text) == {"google drive": "G:\\My Drive\\Projects\\Resolve Project Library"}


def test_parse_dblist_ignores_non_disk_and_blank():
    assert rr.parse_dblist("\ncloud:server:*:::PG\n") == {}


def test_missing_libraries_uses_prefs(tmp_path, monkeypatch):
    here, gone = str(tmp_path).replace(":", "", 1), str(tmp_path / "nope").replace(":", "", 1)
    (tmp_path / "dblist.conf").write_text(f"here:{here}:*:::DISK\ngone:{gone}:*:::DISK\n", encoding="utf-8")
    monkeypatch.setattr(rr, "PREFS", tmp_path)
    assert list(rr.missing_libraries()) == ["gone"]
    assert rr.missing_libraries("here") == {}


def test_project_library_from_recentprojects():
    text = ("disk:google drive:google drive:Sakuyako-Cheris\\2026-06\\2026-06-Sakuyako:"
            "2026-06-Sakuyako:Sakuyako-Cheris\\2026-06:171396b2\n")
    assert rr.project_library(text, "2026-06-Sakuyako") == "google drive"
    assert rr.project_library(text, "other") is None
