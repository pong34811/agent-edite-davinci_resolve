"""Refresh docs/skills-manifest.json after repository changes, then re-validate.

Adds new bundle files, drops deleted ones, records this session's edits, and
recomputes checksums. Requires PyYAML only. Does not commit or push.
"""
import hashlib
import fnmatch
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'docs/skills-manifest.json'
DIRS = ('.agents', 'docs', 'resolve-advanced', 'scripts', 'tests')
TOP = ('.gitignore', 'AGENTS.md', 'README.md', 'CHANGELOG.md', 'VERSION')
NEW_KIND = {
    'scripts/': 'project_helper',
    'tests/': 'integration_or_validation',
}


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


def main():
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
    for directory in DIRS:
        for path in sorted((ROOT / directory).rglob('*')):
            if not path.is_file() or '__pycache__' in path.parts:
                continue
            relative = path.relative_to(ROOT).as_posix()
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
    manifest['edits'].extend([
        {'path': 'docs/OPERATING-NOTES.md',
         'reason': 'Offline review workflow (ffprobe/ffmpeg + saved subtitle map), native Python '
                   'vdo reference capture/apply, draft-copy then promote-to-original sequence, '
                   'idempotent promotion, anomaly sweep, and backup-cleanup rules.'},
        {'path': 'scripts/enrich_timelines_python.py',
         'reason': 'Native Python batch enrichment: dry-run by default, explicit inventory IDs, '
                   'BGM-only when no cue is defensible, GIF overlap preservation, per-item caps.'},
        {'path': 'scripts/promote_drafts_to_originals.py',
         'reason': 'Promotes verified drafts into originals by exact IDs, reusing existing items '
                   'and re-verifying baseline tracks; refuses when an original drifted.'},
        {'path': 'scripts/anomaly_sweep.py',
         'reason': 'Read-only structural sweep across every timeline; native subtitle items are '
                   'correctly treated as having no Media Pool entry.'},
        {'path': '.gitignore',
         'reason': 'Ignore the local .hermes working-artifact tree alongside other scratch dirs.'},
    ])
    manifest['bundle_version'] = '0.8.0'
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'files': len(manifest['files']), 'changed': len(changed),
                      'changes': changed[:40]}, ensure_ascii=False, indent=2))
    subprocess.run([sys.executable, str(ROOT / 'scripts/verify_skill_bundle.py')], check=False)


if __name__ == '__main__':
    main()
