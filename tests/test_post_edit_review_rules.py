"""Documentation contracts, not an end-to-end research automation test."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / '.agents/skills/resolve-video-enrichment/references/post-edit-review.md'
ENTRY = ROOT / '.agents/skills/resolve-video-enrichment/references/youtube-packaging-and-feedback.md'
LEARNING = ROOT / '.agents/skills/project-learning/SKILL.md'


def test_review_reference_exists():
    assert REFERENCE.is_file(), 'post-edit review workflow is missing'


def test_entrypoints_link_review():
    for path in (ENTRY, LEARNING):
        assert 'post-edit-review.md' in path.read_text(encoding='utf-8')


def test_shared_start_checklist_routes_editing_to_research_workflow():
    agents = (ROOT / 'AGENTS.md').read_text(encoding='utf-8')
    start = agents.split('## Start of task checklist', 1)[1].split('\n## ', 1)[0]
    assert 'editing' in start.lower()
    assert '.agents/skills/project-learning/SKILL.md' in start
    assert 'post-edit-review.md' in start
    learning = LEARNING.read_text(encoding='utf-8')
    assert 'at the start' in learning.lower()
    assert 'after QC' in learning
    assert 'post-edit-review.md' in learning


def test_review_contract_and_official_sources():
    assert REFERENCE.is_file(), 'post-edit review workflow is missing'
    text = REFERENCE.read_text(encoding='utf-8').lower()
    for term in ('as-of', 'source url', 'access date', 'unknown', 'hypothesis',
                 'shorts', 'long-form', 'permission', 'no guarantee',
                 '16089387', '16559650', 'search query', 'timecode',
                 'fewer than 3', 'research unavailable', 'analytics',
                 'transcript', 'not edited', 'not published'):
        assert term in text, term


def test_entrypoint_exposes_dated_safeguards():
    text = ENTRY.read_text(encoding='utf-8').lower()
    for term in ('as-of', 'source url', 'access date', 'unknown', 'hypothesis',
                 'shorts', 'long-form', 'permission', 'no guarantee'):
        assert term in text, term
