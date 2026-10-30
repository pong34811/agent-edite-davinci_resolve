"""Documentation contracts, not proof of automatic channel memory."""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = [
    ROOT / 'docs/channels/README.md',
    ROOT / '.agents/skills/project-learning/SKILL.md',
]


@pytest.mark.parametrize('path', DOCUMENTS, ids=['channel-index', 'project-learning'])
def test_channel_learning_documents_include_evidence_statuses_and_privacy(path):
    text = path.read_text(encoding='utf-8').lower()
    for term in ('evidence', 'confirmed', 'hypothesis', 'superseded', 'privacy'):
        assert term in text, f'{path.name} missing {term}'


def test_channel_index_defines_provenance_and_isolation_contract():
    text = DOCUMENTS[0].read_text(encoding='utf-8').lower()
    for term in ('applicability', 'project/timeline id', 'ผู้ยืนยัน', 'ตัวอย่างสมมติ', 'ไม่ยืม'):
        assert term in text, f'channel index missing {term}'
