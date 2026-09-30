"""Validate vendored skills without connecting to DaVinci Resolve.
Run: python scripts/verify_skill_bundle.py
Requires PyYAML. Hermes's own scanner is used when importable.
"""
from pathlib import Path
import ast
import hashlib
import json
import re
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def validate():
    manifest = json.loads((ROOT / 'docs/skills-manifest.json').read_text(encoding='utf-8'))
    errors = []
    active = sorted((ROOT / '.agents/skills').glob('*/SKILL.md'))
    declared = [s for s in manifest['skills'] if s['tier'] == 'editing']
    counts = {
        'editing_skills': len(declared),
        'related_archive_skills': sum(s['tier'] == 'related_archive' for s in manifest['skills']),
        'history_evidenced_editing_skills': sum(s['history_loads'] > 0 for s in declared),
        'manifest_files': len(manifest['files']),
    }
    for name, count in counts.items():
        if manifest['counts'].get(name) != count:
            errors.append('Manifest count mismatch: ' + name)
    if len(active) != 16 or len(declared) != len(active):
        errors.append('Core skill count does not match expected 16 / manifest')
    active_paths = {path.relative_to(ROOT).as_posix() for path in active}
    if {s['path'] for s in declared} != active_paths:
        errors.append('Core skill declarations do not match active paths')
    declarations = {s['path']: s for s in declared}
    names = []
    checked_links = []
    for path in active:
        text = path.read_text(encoding='utf-8')
        parts = text.split('---', 2)
        if len(parts) != 3 or parts[0] or not parts[2].strip():
            errors.append(f'Invalid frontmatter/body: {path}')
            continue
        fm = yaml.safe_load(parts[1])
        if not isinstance(fm, dict) or not fm.get('name') or not fm.get('description'):
            errors.append(f'Missing name/description: {path}')
            continue
        names.append(fm['name'])
        if fm['name'] != path.parent.name:
            errors.append(f'Skill name/directory mismatch: {path}')
        declaration = declarations.get(path.relative_to(ROOT).as_posix())
        if declaration is not None and declaration['name'] != fm['name']:
            errors.append(f'Skill name/manifest mismatch: {path}')
    if len(names) != len(set(names)):
        errors.append('Duplicate active skill names')
    archives = sorted((ROOT / 'docs/related-skills').glob('*/SKILL.md'))
    archive_declarations = [s for s in manifest['skills'] if s['tier'] == 'related_archive']
    on_disk = {(p.parent.name, p.relative_to(ROOT).as_posix()) for p in archives}
    declared_archives = {(s['name'], s['path']) for s in archive_declarations}
    if len(archives) != 13 or len(archive_declarations) != len(archives) or declared_archives != on_disk:
        errors.append('Archive skill declarations do not match disk')
    for path in archives:
        parts = path.read_text(encoding='utf-8').split('---', 2)
        if len(parts) != 3 or parts[0] or not parts[2].strip():
            errors.append(f'Invalid archive frontmatter/body: {path}')
            continue
        fm = yaml.safe_load(parts[1])
        # Plugin archive folders are namespaced; preserve upstream frontmatter.
        expected_name = path.parent.name.removeprefix('superpowers-')
        if not isinstance(fm, dict) or fm.get('name') != expected_name or not fm.get('description'):
            errors.append(f'Archive name/frontmatter mismatch: {path}')
    # Validate every static local Markdown/quoted document reference from core skills.
    for path in sorted((ROOT / '.agents/skills').rglob('*.md')):
        text = path.read_text(encoding='utf-8')
        refs = set(re.findall(r'\]\(([^)]+)\)', text))
        refs.update(re.findall(r'`((?:docs/|references/|resolve-advanced/|scripts/|\.agents/)[^`\s]+\.(?:md|py|txt|pyi))`', text))
        # Bare kernel filenames are deliberate table shorthand.
        refs.update(re.findall(r'`([a-z-]+-kernel\.md)`', text))
        for ref in sorted(refs):
            if '://' in ref or ref.startswith('#'):
                continue
            ref = ref.split('#')[0]
            candidates = [path.parent / ref, ROOT / ref, ROOT / 'docs/kernels' / ref, ROOT / 'docs/guides' / ref]
            found = next((c for c in candidates if c.is_file()), None)
            if found is None:
                errors.append(f'Missing local reference: {path.relative_to(ROOT)} -> {ref}')
            else:
                checked_links.append({'from':path.relative_to(ROOT).as_posix(), 'to':found.relative_to(ROOT).as_posix()})
    listed_files = {record['path'] for record in manifest['files']}
    if len(listed_files) != len(manifest['files']):
        errors.append('Duplicate manifest file paths')
    # The manifest is not its own checksum authority; reports are generated.
    excluded = {'docs/skills-manifest.json', 'docs/validation-report.json'}
    for directory in ['.agents', 'docs', 'resolve-advanced', 'scripts', 'tests']:
        for path in (ROOT / directory).rglob('*'):
            if not path.is_file() or '__pycache__' in path.parts:
                continue
            relative = path.relative_to(ROOT).as_posix()
            if relative not in excluded and relative not in listed_files:
                errors.append('Unlisted bundle file: ' + relative)
    for relative in ['.gitignore', 'AGENTS.md', 'README.md']:
        if relative not in listed_files:
            errors.append('Unlisted bundle file: ' + relative)
    for record in manifest['files']:
        dst = ROOT / record['path']
        if not dst.is_file():
            errors.append('Missing manifest file: ' + record['path'])
        elif sha(dst) != record['sha256']:
            errors.append('Checksum mismatch: ' + record['path'])
    for path in [ROOT/'scripts/contact_sheet.py', ROOT/'scripts/verify_skill_bundle.py', ROOT/'tests/test_skill_bundle.py']:
        ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    scans = []
    try:
        from tools.skills_guard import scan_skill
    except ImportError:
        scanner = 'unavailable; structural/checksum checks only'
    else:
        scanner = 'Hermes tools.skills_guard.scan_skill'
        for path in active:
            result = scan_skill(path.parent, source='community')
            scans.append({'name':path.parent.name, 'verdict':result.verdict, 'findings':[{'pattern_id':f.pattern_id,'severity':f.severity,'file':f.file,'line':f.line,'description':f.description} for f in result.findings]})
            if result.verdict == 'dangerous':
                errors.append('Quarantined core skill: '+path.parent.name)
    return {'ok':not errors, 'core_skill_count':len(active), 'related_archive_count':len(archives), 'history_evidenced_core_count':sum(s['history_loads']>0 for s in declared), 'manifest_file_count':len(manifest['files']), 'local_reference_count':len(checked_links), 'scanner':scanner, 'security_scans':scans, 'errors':errors, 'live_resolve_tested':False, 'project_trust_changed':False}

if __name__ == '__main__':
    result = validate()
    (ROOT / 'docs/validation-report.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result['ok'] else 1)
