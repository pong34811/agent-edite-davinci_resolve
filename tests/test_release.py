from pathlib import Path
import importlib.util


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "release.py"
SPEC = importlib.util.spec_from_file_location("release", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


def test_patch_is_default_and_increments_patch():
    assert release.bump_version("0.16.0") == "0.16.1"


def test_explicit_minor_and_major_bumps():
    assert release.bump_version("1.2.3", "minor") == "1.3.0"
    assert release.bump_version("1.2.3", "major") == "2.0.0"


def test_rejects_non_semver_versions():
    try:
        release.bump_version("v1.2.3")
    except ValueError as exc:
        assert "SemVer" in str(exc)
    else:
        raise AssertionError("invalid version should be rejected")


def test_changelog_entry_requires_thai_bullet_notes():
    entry = release.format_changelog("0.16.1", "ปรับปรุงขั้นตอน", "- เพิ่มเครื่องมือ release ภาษาไทย")
    assert entry.startswith("## v0.16.1 — ")
    assert "- เพิ่มเครื่องมือ release ภาษาไทย" in entry


def test_changelog_entry_rejects_non_bulleted_notes():
    try:
        release.format_changelog("0.16.1", "Release", "รายละเอียดที่ไม่มี bullet")
    except ValueError as exc:
        assert "bullet" in str(exc).lower()
    else:
        raise AssertionError("notes without bullets should be rejected")


def test_preflight_rejects_wrong_branch_before_publish(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(release, "run", lambda *args, cwd=None: calls.append(args) or "feature")
    try:
        release.preflight("1.2.3", tmp_path)
    except RuntimeError as exc:
        assert "branch" in str(exc).lower()
    else:
        raise AssertionError("wrong branch should be rejected")
    assert calls == [("git", "branch", "--show-current")]


def test_preflight_rejects_dirty_tree_before_publish(monkeypatch, tmp_path):
    calls = []
    def fake_run(*args, cwd=None):
        calls.append(args)
        return "main" if args == ("git", "branch", "--show-current") else "?? stray.txt"
    monkeypatch.setattr(release, "run", fake_run)
    try:
        release.preflight("1.2.3", tmp_path)
    except RuntimeError as exc:
        assert "working tree" in str(exc).lower()
    else:
        raise AssertionError("dirty tree should be rejected")


def test_preflight_rejects_remote_tag(monkeypatch, tmp_path):
    calls = []
    def fake_run(*args, cwd=None):
        calls.append(args)
        if args == ("git", "branch", "--show-current"):
            return "main"
        if args == ("git", "rev-parse", "HEAD") or args == ("git", "rev-parse", "origin/main"):
            return "same"
        if args[:2] == ("git", "status"):
            return ""
        if args[:2] == ("git", "tag"):
            return ""
        if args[:3] == ("git", "ls-remote", "--tags"):
            return "abc123 refs/tags/v1.2.3"
        raise AssertionError(args)
    monkeypatch.setattr(release, "run", fake_run)
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\\n", encoding="utf-8")
    try:
        release.preflight("1.2.3", tmp_path)
    except RuntimeError as exc:
        assert "remote tag" in str(exc).lower()
    else:
        raise AssertionError("existing remote tag should be rejected")


def test_preflight_requires_exactly_one_changelog_header(monkeypatch, tmp_path):
    calls = []
    def fake_run(*args, cwd=None):
        calls.append(args)
        if args == ("git", "branch", "--show-current"):
            return "main"
        if args == ("git", "rev-parse", "HEAD") or args == ("git", "rev-parse", "origin/main"):
            return "same"
        if args[:2] == ("git", "status"):
            return ""
        return ""
    monkeypatch.setattr(release, "run", fake_run)
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n# Changelog\n", encoding="utf-8")
    try:
        release.preflight("1.2.3", tmp_path)
    except RuntimeError as exc:
        assert "changelog" in str(exc).lower()
    else:
        raise AssertionError("duplicate changelog headers should be rejected")
