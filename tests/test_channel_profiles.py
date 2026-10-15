"""Every channel the agent edits has a profile with the same sections."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANNELS = ROOT / 'docs' / 'channels'
SLUGS = ['katy404', 'aomimama', 'armigon', 'tygarina', 'sakuyako-cheris', 'laffy', 'kael']
SECTIONS = [
    '## ตัวตนและคอนเทนต์',
    '## ที่เก็บไฟล์',
    '## โปรเจคและ timeline ใน Resolve',
    '## รูปแบบและ layout',
    '## ซับ เสียง และ enrichment',
    '## Script และ skill ที่เกี่ยวข้อง',
    '## กับดักและงานค้าง',
    '## ยังไม่ทราบ (ถามผู้ใช้ก่อนเดา)',
]


def test_every_channel_has_a_profile_with_all_sections():
    for slug in SLUGS:
        text = (CHANNELS / f'{slug}.md').read_text(encoding='utf-8')
        for section in SECTIONS:
            assert section in text, f'{slug}.md missing {section}'


def test_index_lists_every_channel_and_agents_md_points_to_it():
    index = (CHANNELS / 'README.md').read_text(encoding='utf-8')
    for slug in SLUGS:
        assert f'({slug}.md)' in index, slug
    assert 'docs/channels/' in (ROOT / 'AGENTS.md').read_text(encoding='utf-8')


def test_profiles_reference_only_existing_scripts():
    import re
    existing = {p.name for p in (ROOT / 'scripts').glob('*.py')}
    for slug in SLUGS:
        text = (CHANNELS / f'{slug}.md').read_text(encoding='utf-8')
        for name in re.findall(r'`(?:scripts/)?([A-Za-z0-9_]+\.py)`', text):
            assert name in existing, f'{slug}.md names missing script {name}'
