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


def format_changelog(version: str, title: str, notes: str, changes: str = "") -> str:
    bullets = [line.strip() for line in notes.splitlines() if line.strip()]
    if not bullets or any(not line.startswith("-") for line in bullets):
        raise ValueError("Release notes must contain Thai bullet lines beginning with '-'.")
    entry = f"## v{version} — {title.strip()}\n\n### รายละเอียด\n" + "\n".join(bullets) + "\n"
    return entry + ("\n" + changes.strip() + "\n" if changes.strip() else "")


SKILLS_PREFIX = ".agents/skills/"
BOOKKEEPING = {"VERSION", "CHANGELOG.md"}
MAX_FILES = 40
STATUS_TH = {"A": "เพิ่ม", "M": "แก้ไข", "D": "ลบ", "R": "เปลี่ยนชื่อ", "C": "คัดลอก", "T": "เปลี่ยนชนิด"}


def summarize_changes(name_status: str) -> str:
    """Thai 'skills updated' + 'files changed' sections from `git diff --name-status` output."""
    files, skills = [], {}
    for line in name_status.splitlines():
        parts = line.strip().split("\t")
        if len(parts) < 2:
            continue
        code, paths = parts[0][:1], parts[1:]
        path = paths[-1]
        if path in BOOKKEEPING:
            continue
        label = STATUS_TH.get(code, code)
        files.append(f"- {label} `{paths[0]}` → `{paths[1]}`" if len(paths) == 2 else f"- {label} `{path}`")
        for p in paths:
            if p.startswith(SKILLS_PREFIX) and p.count("/") >= 3:
                name, rel = p[len(SKILLS_PREFIX):].split("/", 1)
                entry = skills.setdefault(name, {"files": [], "status": "แก้ไข"})
                if rel not in entry["files"]:
                    entry["files"].append(rel)
                if rel == "SKILL.md" and code in ("A", "D"):
                    entry["status"] = "ใหม่" if code == "A" else "ลบ"
    skill_lines = [f"- `{n}` ({s['status']}): " + ", ".join(f"`{f}`" for f in s["files"])
                   for n, s in sorted(skills.items())] or ["- ไม่มี"]
    shown = files[:MAX_FILES] or ["- ไม่มี"]
    if len(files) > MAX_FILES:
        shown.append(f"- ... และอีก {len(files) - MAX_FILES} ไฟล์ (ดู `git diff --name-status` ของ tag นี้)")
    return "### Skill ที่อัปเดต\n" + "\n".join(skill_lines) + "\n\n### ไฟล์ที่เปลี่ยน\n" + "\n".join(shown) + "\n"


def changes_since_last_tag(root: Path = ROOT) -> str:
    """Summary of everything committed since the previous release tag (empty if there is no tag)."""
    try:
        last = run("git", "describe", "--tags", "--abbrev=0", "HEAD", cwd=root)
    except subprocess.CalledProcessError:
        return ""
    return summarize_changes(run("git", "diff", "--name-status", "-M", last, "HEAD", cwd=root))


def run(*args: str, cwd: Path = ROOT) -> str:
    result = subprocess.run(args, cwd=cwd, check=True, text=True, capture_output=True,
                            encoding="utf-8", errors="replace")
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
    # Thai titles/notes must print on a Windows console whose codepage cannot encode them
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True, help="หัวข้อ release ภาษาไทย")
    parser.add_argument("--notes-file", required=True, type=Path, help="ไฟล์ bullet point ภาษาไทย")
    parser.add_argument("--bump", choices=("patch", "minor", "major"), default="patch")
    parser.add_argument("--publish", action="store_true", help="เขียน version/changelog แล้ว commit, tag, push และสร้าง GitHub Release")
    args = parser.parse_args()
    current = VERSION_FILE.read_text(encoding="utf-8").strip()
    version = bump_version(current, args.bump)
    entry = format_changelog(version, args.title, args.notes_file.read_text(encoding="utf-8"),
                             changes_since_last_tag())
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
