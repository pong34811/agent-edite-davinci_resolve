"""Prepare and publish a Thai, SemVer-tagged project release."""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "VERSION"
CHANGELOG_FILE = ROOT / "CHANGELOG.md"
VERSION_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def bump_version(version: str, bump: str = "patch") -> str:
    """Return the next SemVer version; patch is the default release increment."""
    match = VERSION_RE.fullmatch(version.strip())
    if not match:
        raise ValueError(f"Invalid SemVer version: {version!r}")
    major, minor, patch = map(int, match.groups())
    if bump == "major":
        return f"{major + 1}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    if bump == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError(f"Unknown bump type: {bump}")


def format_changelog(version: str, title: str, notes: str) -> str:
    bullets = [line.strip() for line in notes.splitlines() if line.strip()]
    if not bullets or any(not line.startswith("-") for line in bullets):
        raise ValueError("Release notes must contain Thai bullet lines beginning with '-'.")
    return f"## v{version} — {title.strip()}\n\n### รายละเอียด\n" + "\n".join(bullets) + "\n"


def run(*args: str, cwd: Path = ROOT) -> str:
    result = subprocess.run(args, cwd=cwd, check=True, text=True, capture_output=True)
    return result.stdout.strip()


def preflight(version: str, root: Path = ROOT) -> None:
    """Refuse publication unless repository and release inputs are safe."""
    tag = f"v{version}"
    stage = "branch"
    try:
        branch = run("git", "branch", "--show-current", cwd=root)
        if branch != "main":
            raise RuntimeError(f"expected main, found {branch or '(detached)'}")
        stage = "working tree"
        if run("git", "status", "--porcelain", "--untracked-files=all", cwd=root):
            raise RuntimeError("working tree or index is not clean")
        stage = "synchronization"
        if run("git", "rev-parse", "HEAD", cwd=root) != run("git", "rev-parse", "origin/main", cwd=root):
            raise RuntimeError("local main is not synchronized with origin/main")
        stage = "local tag"
        if run("git", "tag", "--list", tag, cwd=root):
            raise RuntimeError(f"tag already exists: {tag}")
        stage = "remote tag"
        if run("git", "ls-remote", "--tags", "origin", f"refs/tags/{tag}", cwd=root):
            raise RuntimeError(f"remote tag already exists: {tag}")
        stage = "CHANGELOG"
        changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
        if len(re.findall(r"(?m)^# Changelog\s*$", changelog)) != 1:
            raise RuntimeError("expected exactly one '# Changelog' header")
    except (OSError, subprocess.CalledProcessError, RuntimeError) as exc:
        raise RuntimeError(f"preflight [{stage}] failed: {exc}") from exc


def publish(version: str, title: str, changelog_entry: str) -> str:
    tag = f"v{version}"
    preflight(version, ROOT)
    VERSION_FILE.write_text(version + "\n", encoding="utf-8")
    prior = CHANGELOG_FILE.read_text(encoding="utf-8")
    CHANGELOG_FILE.write_text(prior.replace("# Changelog\n", "# Changelog\n\n" + changelog_entry, 1), encoding="utf-8")
    run("git", "add", "--", "VERSION", "CHANGELOG.md")
    run("git", "commit", "--only", "VERSION", "CHANGELOG.md", "-m", f"chore(release): {tag} — {title}")
    run("git", "tag", tag)
    run("git", "push", "origin", "main")
    run("git", "push", "origin", tag)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".md", delete=False) as notes_file:
        notes_file.write(f"## 🚀 Release {tag} — {title}\n\n{changelog_entry.split('### รายละเอียด', 1)[1].strip()}\n")
        notes_path = Path(notes_file.name)
    try:
        run("gh", "release", "create", tag, "--verify-tag", "--latest", "--title", f"{tag} — {title}", "--notes-file", str(notes_path))
    finally:
        notes_path.unlink(missing_ok=True)
    return tag


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True, help="หัวข้อ release ภาษาไทย")
    parser.add_argument("--notes-file", required=True, type=Path, help="ไฟล์ bullet point ภาษาไทย")
    parser.add_argument("--bump", choices=("patch", "minor", "major"), default="patch")
    parser.add_argument("--publish", action="store_true", help="เขียน version/changelog แล้ว commit, tag, push และสร้าง GitHub Release")
    args = parser.parse_args()
    current = VERSION_FILE.read_text(encoding="utf-8").strip()
    version = bump_version(current, args.bump)
    entry = format_changelog(version, args.title, args.notes_file.read_text(encoding="utf-8"))
    if not args.publish:
        print(f"DRY RUN: {current} -> {version}\n{entry}")
        return 0
    tag = publish(version, args.title, entry)
    print(f"Published {tag}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, subprocess.CalledProcessError, ValueError, RuntimeError) as exc:
        print(f"release failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
