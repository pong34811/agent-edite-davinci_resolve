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
    if len(active) != 16 or len(declared) != len(active):
        errors.append('Core skill count does not match expected 16 / manifest')
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
    if len(names) != len(set(names)):
        errors.append('Duplicate active skill names')
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
    return {'ok':not errors, 'core_skill_count':len(active), 'related_archive_count':sum(s['tier']=='related_archive' for s in manifest['skills']), 'history_evidenced_core_count':sum(s['history_loads']>0 for s in declared), 'manifest_file_count':len(manifest['files']), 'local_reference_count':len(checked_links), 'scanner':scanner, 'security_scans':scans, 'errors':errors, 'live_resolve_tested':False, 'project_trust_changed':False}

if __name__ == '__main__':
    result = validate()
    (ROOT / 'docs/validation-report.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result['ok'] else 1)
