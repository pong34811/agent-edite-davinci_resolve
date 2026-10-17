"""Refresh docs/skills-manifest.json after repository changes, then re-validate.

Adds new bundle files, drops deleted ones, records supplied edits, and
recomputes checksums. Requires PyYAML only. Does not commit or push.
"""
import argparse
import hashlib
import fnmatch
import json
from pathlib import Path
import subprocess
import sys
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_skill_bundle import git_ignored  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'docs/skills-manifest.json'
DIRS = ('.agents', 'docs', 'resolve-advanced', 'scripts', 'tests')
TOP = ('.gitignore', 'AGENTS.md', 'README.md', 'CHANGELOG.md', 'VERSION')
NEW_KIND = {
    'scripts/': 'project_helper',
    'tests/': 'integration_or_validation',
}
CORE_SKILL_COUNT = 17


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def kind_for(relative):
    if relative.startswith('.agents/skills/'):
        return 'editing_skill_reference' if relative.count('/') > 3 else 'editing_skill'
    if relative.startswith('tests/'):
        return 'integration_or_validation'
    if relative.startswith('docs/related-skills/') or relative.startswith('docs/skill-variants/'):
        return 'related_skill_archive'
    for prefix, kind in NEW_KIND.items():
        if relative.startswith(prefix):
            return kind
    return 'project_helper'


def sync_skill_declarations(manifest):
    """Keep the curated core and supporting active skills distinct in the manifest."""
    existing = {record['path']: record for record in manifest.get('skills', [])
                if record['tier'] not in ('editing', 'supporting') or (ROOT / record['path']).is_file()}
    for skill_file in sorted((ROOT / '.agents/skills').glob('*/SKILL.md')):
        relative = skill_file.relative_to(ROOT).as_posix()
        if relative in existing:
            continue
        parts = skill_file.read_text(encoding='utf-8').split('---', 2)
        if len(parts) != 3:
            raise ValueError(f'Invalid skill frontmatter: {relative}')
        metadata = yaml.safe_load(parts[1]) or {}
        if not metadata.get('name') or not metadata.get('description'):
            raise ValueError(f'Missing skill name/description: {relative}')
        if skill_file.parent.name.startswith('superpowers-'):
            source = 'superpowers plugin v7.0.0 (commit 7df7bd9)'
        else:
            source = 'profile skill sync (commit 10370a1)'
        existing[relative] = {
            'name': metadata['name'], 'tier': 'supporting', 'path': relative,
            'source': source, 'history_evidence': [], 'history_loads': 0,
            'history_sessions': 0,
        }
    manifest['skills'] = [existing[key] for key in sorted(existing)]
    core = sum(record['tier'] == 'editing' for record in manifest['skills'])
    supporting = sum(record['tier'] == 'supporting' for record in manifest['skills'])
    manifest['counts']['editing_skills'] = core
    manifest['counts']['supporting_skills'] = supporting
    manifest['counts']['active_skills'] = core + supporting
    manifest['counts']['related_archive_skills'] = sum(
        record['tier'] == 'related_archive' for record in manifest['skills'])
    manifest['counts']['history_evidenced_editing_skills'] = sum(
        record.get('history_loads', 0) > 0 for record in manifest['skills']
        if record['tier'] == 'editing')
    if core != CORE_SKILL_COUNT:
        raise ValueError(f'Expected {CORE_SKILL_COUNT} curated editing skills, found {core}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--edit', nargs=2, action='append', metavar=('PATH', 'REASON'),
                        default=[], help='Record a changed file and reason (repeatable)')
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    records = {record['path']: record for record in manifest['files']}
    excluded_rules = {record['path']: record['reason']
                      for record in manifest.get('excluded_repository_paths', [])}
    def is_excluded(relative):
        return any(fnmatch.fnmatchcase(relative, pattern) for pattern in excluded_rules)
    changed = []
    # A path that an exclusion rule covers must not also be listed in the bundle.
    for relative in sorted(records):
        if is_excluded(relative):
            del records[relative]
            changed.append({'action': 'unlisted_excluded', 'path': relative})
    # Remove records whose file no longer exists.
    for relative in sorted(records):
        if not (ROOT / relative).is_file():
            del records[relative]
            changed.append({'action': 'removed', 'path': relative})
    candidates = [path for directory in DIRS for path in sorted((ROOT / directory).rglob('*'))
                  if path.is_file() and '__pycache__' not in path.parts]
    ignored = git_ignored(ROOT, [path.relative_to(ROOT).as_posix() for path in candidates])
    for relative in sorted(records):
        if relative in ignored:
            del records[relative]
            changed.append({'action': 'unlisted_gitignored', 'path': relative})
    for path in candidates:
        relative = path.relative_to(ROOT).as_posix()
        if relative in ignored:
            continue
        if relative in ('docs/skills-manifest.json', 'docs/validation-report.json'):
            continue
        if is_excluded(relative):
            continue
        record = records.get(relative)
        digest = sha(path)
        if record is None:
            records[relative] = {'path': relative, 'source': 'project-authored',
                                 'kind': kind_for(relative), 'sha256': digest}
            changed.append({'action': 'added', 'path': relative})
        elif record['sha256'] != digest:
            record['sha256'] = digest
            changed.append({'action': 'rechecksummed', 'path': relative})
    for relative in TOP:
        path = ROOT / relative
        if not path.is_file():
            continue
        record = records.get(relative)
        digest = sha(path)
        if record is None:
            records[relative] = {'path': relative, 'source': 'project-authored',
                                 'kind': 'integration_or_validation', 'sha256': digest}
            changed.append({'action': 'added', 'path': relative})
        elif record['sha256'] != digest:
            record['sha256'] = digest
            changed.append({'action': 'rechecksummed', 'path': relative})
    manifest['files'] = [records[key] for key in sorted(records)]
    manifest['counts']['manifest_files'] = len(manifest['files'])
    sync_skill_declarations(manifest)
    edits = []
    seen = set()
    for record in [*manifest.get('edits', []),
                   *({'path': path, 'reason': reason} for path, reason in args.edit)]:
        key = (record['path'], record['reason'])
        if key not in seen:
            edits.append(record)
            seen.add(key)
    manifest['edits'] = edits
    manifest['bundle_version'] = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'files': len(manifest['files']), 'changed': len(changed),
                      'changes': changed[:40]}, ensure_ascii=False, indent=2))
    subprocess.run([sys.executable, str(ROOT / 'scripts/verify_skill_bundle.py')], check=False)


if __name__ == '__main__':
    main()
