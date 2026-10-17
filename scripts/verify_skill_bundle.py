"""Validate vendored skills without connecting to DaVinci Resolve.
Run: python scripts/verify_skill_bundle.py
Requires PyYAML. Hermes's own scanner is used when importable.
"""
from pathlib import Path
import ast
import fnmatch
import hashlib
import json
import re
import subprocess
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CORE_SKILLS = 17
EXPECTED_ARCHIVE_SKILLS = 13
# The imported writing-skills reference contains hyperlinks in illustrative
# sample packages for unrelated skills. These are not local dependencies of
# this bundle; keep the narrow, source-specific allowlist visible in reports.
DOCUMENTED_EXAMPLE_LINKS = {
    '.agents/skills/superpowers-writing-skills/anthropic-best-practices.md': {
        'DOCX-JS.md', 'EXAMPLES.md', 'FORMS.md', 'OOXML.md', 'REDLINING.md',
        'REFERENCE.md', 'advanced.md', 'details.md', 'examples.md', 'reference.md',
        'reference/finance.md', 'reference/marketing.md',
        'reference/product.md', 'reference/sales.md',
    },
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def checksum_matches(path, expected):
    if sha(path) == expected:
        return True
    text_suffixes = {'', '.cjs', '.dot', '.html', '.js', '.json', '.md', '.py',
                     '.pyi', '.sh', '.ts', '.txt', '.yaml', '.yml'}
    data = path.read_bytes()
    if path.suffix.lower() not in text_suffixes or bytes([0]) in data:
        return False
    try:
        data.decode('utf-8')
    except UnicodeDecodeError:
        return False
    # Git can convert LF/CRLF on checkout and archive; change no other bytes.
    lf = data.replace(bytes([13, 10]), bytes([10]))
    crlf = lf.replace(bytes([10]), bytes([13, 10]))
    return expected in {hashlib.sha256(lf).hexdigest(),
                        hashlib.sha256(crlf).hexdigest()}

def git_ignored(root, relatives):
    """Return the repo-relative paths that .gitignore excludes; tracked files never count as ignored.

    Outside a git checkout (an exported bundle) nothing is treated as ignored.
    """
    if not relatives:
        return set()
    # -z: NUL-separated, so Windows newlines and Thai paths come back unquoted.
    try:
        result = subprocess.run(['git', 'check-ignore', '-z', '--stdin'], cwd=root,
                                capture_output=True, input='\0'.join(relatives).encode('utf-8'))
    except OSError:
        return set()
    if result.returncode not in (0, 1):
        return set()
    return {item for item in result.stdout.decode('utf-8').split('\0') if item}


def validate():
    manifest = json.loads((ROOT / 'docs/skills-manifest.json').read_text(encoding='utf-8'))
    errors = []
    active = sorted((ROOT / '.agents/skills').glob('*/SKILL.md'))
    declared = [s for s in manifest['skills'] if s['tier'] in ('editing', 'supporting')]
    core = [s for s in declared if s['tier'] == 'editing']
    supporting = [s for s in declared if s['tier'] == 'supporting']
    counts = {
        'editing_skills': len(core),
        'supporting_skills': len(supporting),
        'active_skills': len(declared),
        'related_archive_skills': sum(s['tier'] == 'related_archive' for s in manifest['skills']),
        'history_evidenced_editing_skills': sum(s['history_loads'] > 0 for s in core),
        'manifest_files': len(manifest['files']),
    }
    for name, count in counts.items():
        if manifest['counts'].get(name) != count:
            errors.append('Manifest count mismatch: ' + name)
    if len(core) != EXPECTED_CORE_SKILLS or len(declared) != len(active):
        errors.append(f'Active skill count does not match {EXPECTED_CORE_SKILLS} core / manifest')
    active_paths = {path.relative_to(ROOT).as_posix() for path in active}
    if {s['path'] for s in declared} != active_paths:
        errors.append('Core skill declarations do not match active paths')
    declarations = {s['path']: s for s in declared}
    names = []
    checked_links = []
    documented_example_links = []
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
        expected_directory_name = path.parent.name.removeprefix('superpowers-')
        if fm['name'] != expected_directory_name:
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
    if len(archives) != EXPECTED_ARCHIVE_SKILLS or len(archive_declarations) != len(archives) or declared_archives != on_disk:
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
        # Code-span paths in supporting reference documents are often examples,
        # not links. Check those only in SKILL.md entry points.
        if path.name == 'SKILL.md':
            refs.update(re.findall(r'`((?:docs/|references/|resolve-advanced/|scripts/|\.agents/)[^`\s]+\.(?:md|py|txt|pyi))`', text))
        # Bare kernel filenames are deliberate table shorthand.
        if path.name == 'SKILL.md':
            refs.update(re.findall(r'`([a-z-]+-kernel\.md)`', text))
        for ref in sorted(refs):
            if '://' in ref or ref.startswith('#'):
                continue
            ref = ref.split('#')[0]
            if ('<' in ref or '>' in ref or 'YYYY-MM-DD' in ref or '...' in ref
                    or ('/' not in ref and '\\' not in ref and '.' not in ref)):
                continue  # illustrative path or placeholder, not a local dependency
            candidates = [path.parent / ref, ROOT / ref, ROOT / 'docs/kernels' / ref, ROOT / 'docs/guides' / ref]
            # Reference files cite siblings skill-root-relative (skill_view file_path style).
            skill_root = next((p for p in path.parents if (p / 'SKILL.md').is_file()), None)
            if skill_root is not None:
                candidates.append(skill_root / ref)
            found = next((c for c in candidates if c.is_file()), None)
            if found is None:
                source = path.relative_to(ROOT).as_posix()
                if ref in DOCUMENTED_EXAMPLE_LINKS.get(source, set()):
                    documented_example_links.append({'from':source, 'to':ref,
                        'reason':'Illustrative link in an imported reference describing an unrelated sample skill package.'})
                else:
                    errors.append(f'Missing local reference: {source} -> {ref}')
            else:
                checked_links.append({'from':path.relative_to(ROOT).as_posix(), 'to':found.relative_to(ROOT).as_posix()})
    listed_files = {record['path'] for record in manifest['files']}
    if len(listed_files) != len(manifest['files']):
        errors.append('Duplicate manifest file paths')
    excluded_rules = {}
    for record in manifest.get('excluded_repository_paths', []):
        if not isinstance(record, dict) or not record.get('path') or not record.get('reason'):
            errors.append('Invalid excluded repository path declaration')
            continue
        excluded_rules[record['path']] = record['reason']
    def exclusion_for(relative):
        return next((pattern for pattern in excluded_rules
                     if fnmatch.fnmatchcase(relative, pattern)), None)

    # The manifest is not its own checksum authority; reports are generated.
    excluded = {'docs/skills-manifest.json', 'docs/validation-report.json'}
    walked = [path for directory in ['.agents', 'docs', 'resolve-advanced', 'scripts', 'tests']
              for path in (ROOT / directory).rglob('*') if path.is_file() and '__pycache__' not in path.parts]
    excluded |= git_ignored(ROOT, [path.relative_to(ROOT).as_posix() for path in walked])
    for path in walked:
        relative = path.relative_to(ROOT).as_posix()
        if relative in excluded:
            continue
        exclusion = exclusion_for(relative)
        if exclusion is not None:
            if relative in listed_files:
                errors.append('Manifest file also excluded from bundle: ' + relative)
        elif relative not in listed_files:
            errors.append('Unlisted bundle file: ' + relative)
    for relative in ['.gitignore', 'AGENTS.md', 'README.md']:
        if relative not in listed_files:
            errors.append('Unlisted bundle file: ' + relative)
    for record in manifest['files']:
        dst = ROOT / record['path']
        if not dst.is_file():
            errors.append('Missing manifest file: ' + record['path'])
        elif not checksum_matches(dst, record['sha256']):
            errors.append('Checksum mismatch: ' + record['path'])
    for path in [ROOT/'scripts/contact_sheet.py', ROOT/'scripts/verify_skill_bundle.py',
                 ROOT/'scripts/apply_video_style.py', ROOT/'tests/test_skill_bundle.py',
                 ROOT/'tests/test_apply_video_style.py']:
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
                errors.append('Quarantined active skill: '+path.parent.name)
    return {'ok':not errors, 'core_skill_count':len(core), 'supporting_skill_count':len(supporting), 'active_skill_count':len(active), 'related_archive_count':len(archives), 'history_evidenced_core_count':sum(s['history_loads']>0 for s in core), 'manifest_file_count':len(manifest['files']), 'excluded_repository_path_count':len(excluded_rules), 'local_reference_count':len(checked_links), 'documented_example_link_exception_count':len(documented_example_links), 'documented_example_link_exceptions':documented_example_links, 'scanner':scanner, 'security_scans':scans, 'errors':errors, 'live_resolve_tested':False, 'project_trust_changed':False}

if __name__ == '__main__':
    result = validate()
    (ROOT / 'docs/validation-report.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result['ok'] else 1)
