"""Entry points shared by Claude Code, Codex and Hermes must stay consistent.

AGENTS.md holds the rules, CLAUDE.md only points to it, scripts/INDEX.md lists every
script so an agent finds the existing tool instead of writing a new one.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'
INDEX = SCRIPTS / 'INDEX.md'
SCRIPT_REF = re.compile(r'`([A-Za-z0-9_]+\.py)`')


def _script_files():
    return {p.name for p in SCRIPTS.glob('*.py')}


def test_every_script_is_listed_in_index():
    listed = set(SCRIPT_REF.findall(INDEX.read_text(encoding='utf-8')))
    missing = sorted(_script_files() - listed)
    assert not missing, f'scripts missing from scripts/INDEX.md: {missing}'


def test_index_lists_no_missing_script():
    listed = set(SCRIPT_REF.findall(INDEX.read_text(encoding='utf-8')))
    ghosts = sorted(listed - _script_files())
    assert not ghosts, f'scripts/INDEX.md names scripts that do not exist: {ghosts}'


def test_claude_md_points_to_agents_md():
    text = (ROOT / 'CLAUDE.md').read_text(encoding='utf-8')
    assert '@AGENTS.md' in text
    assert 'scripts/INDEX.md' in text
    assert len(text.splitlines()) <= 40, 'CLAUDE.md must stay a thin pointer'


def test_agents_md_has_agent_workflow_sections():
    text = (ROOT / 'AGENTS.md').read_text(encoding='utf-8')
    for heading in ('## Start of task checklist', '## Finish of task: record what you learned'):
        assert heading in text, heading
    assert 'scripts/scratch/' in text
    assert 'scripts/INDEX.md' in text


def test_scratch_dir_is_ignored_but_kept():
    ignore = (ROOT / '.gitignore').read_text(encoding='utf-8').splitlines()
    assert 'scripts/scratch/*' in ignore
    assert '!scripts/scratch/.gitkeep' in ignore
    assert (SCRIPTS / 'scratch' / '.gitkeep').exists()


def test_project_learning_skill_is_registered():
    skill = ROOT / '.agents/skills/project-learning/SKILL.md'
    text = skill.read_text(encoding='utf-8')
    assert text.startswith('---')
    assert 'name: project-learning' in text
    manifest = json.loads((ROOT / 'docs/skills-manifest.json').read_text(encoding='utf-8'))
    paths = {record['path'] for record in manifest.get('skills', [])}
    assert '.agents/skills/project-learning/SKILL.md' in paths
