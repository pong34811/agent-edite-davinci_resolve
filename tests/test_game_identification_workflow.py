"""Check the written review contract, not a classifier or live Resolve behavior."""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / '.agents/skills/video-footage-review/SKILL.md'
REFERENCE = SKILL.parent / 'references/game-identification.md'

# Actionable instructions, not unrelated keywords found anywhere in a document.
CONTRACTS = {
    'read_only': ('Never modify source footage or Resolve state for identification.',
                  'Inventory and analysis do not authorize edits, renders, uploads, markers or metadata changes.',
                  'If a no-write mode cannot be established, do not run it.'),
    'permission': ('Do not send footage, audio, transcripts or private information to an external provider without explicit permission covering the material, recipient and purpose.',),
    'offline': ('if Resolve or media is offline, unavailable, or inaccessible, record what was not inspected and use unknown.',),
    'multi_game': ('Multiple games may occur: preserve a multi-game timeline as separate observed ranges; do not invent exact transition boundaries from sparse samples.',
                   'Mark gaps and uninspected ranges unknown.'),
    'identity': ('Keep game identity and channel identity as separate evidence and decisions.',
                 'An avatar or game alone does not establish which channel owns footage.',
                 'Use separate statuses for game and channel when their evidence differs:',
                 'game_status, game_evidence, channel_status, channel_evidence'),
    'timebase': ('explicit source or timeline time base (including frame rate when using frames)',
                 'State how source and timeline ranges map if both are reported.'),
    'safe_options': ('publish_metadata=false', 'timed_markers=no',
                     'include_visuals=false', 'include_transcription=false'),
}


def missing_requirements(text, group):
    return [requirement for requirement in CONTRACTS[group] if requirement not in text]


@pytest.fixture
def reference():
    return REFERENCE.read_text(encoding='utf-8')


@pytest.mark.parametrize('group', CONTRACTS)
def test_reference_contains_actionable_contract(reference, group):
    assert not missing_requirements(reference, group), missing_requirements(reference, group)


@pytest.mark.parametrize('group', CONTRACTS)
def test_mock_document_missing_each_requirement_is_rejected(reference, group):
    # Mutate the document into incomplete mock documents, one omission at a time.
    for requirement in CONTRACTS[group]:
        assert requirement in reference
        incomplete = reference.replace(requirement, '[omitted]')
        assert requirement in missing_requirements(incomplete, group)


def test_reference_defines_statuses(reference):
    for definition in ('**confirmed** only when adequately corroborated or explicitly confirmed by the user',
                       '**candidate** for a plausible but unverified identification',
                       '**unknown** for insufficient evidence',
                       '**conflict** for contradictory evidence'):
        assert definition in reference


def test_skill_routes_identity_review_to_reference():
    assert 'references/game-identification.md' in SKILL.read_text(encoding='utf-8')
