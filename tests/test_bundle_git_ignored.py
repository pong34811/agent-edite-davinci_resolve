import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from verify_skill_bundle import git_ignored

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")


def _git(root, *args):
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


def test_ignored_untracked_files_only(tmp_path):
    _git(tmp_path, "init", "-q")
    (tmp_path / ".gitignore").write_text("scratch/*\nreference/\n", encoding="utf-8")
    for rel in ("scratch/a.py", "scratch/ไทย.py", "docs/reference/kept.md", "docs/x.md"):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text("x", encoding="utf-8")
    _git(tmp_path, "add", "-f", "docs/reference/kept.md")
    got = git_ignored(tmp_path, ["scratch/a.py", "scratch/ไทย.py", "docs/reference/kept.md", "docs/x.md"])
    assert got == {"scratch/a.py", "scratch/ไทย.py"}


def test_outside_git_checkout_ignores_nothing(tmp_path):
    assert git_ignored(tmp_path, ["a.py"]) == set()
