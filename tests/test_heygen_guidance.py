from pathlib import Path


def test_heygen_guidance_keeps_resolve_boundary_and_privacy():
    text = Path('.agents/skills/resolve-video-enrichment/SKILL.md').read_text(encoding='utf-8')
    assert 'https://mcp.heygen.com/mcp/v1/' in text
    assert 'HeyGen output is not a Resolve edit decision list' in text
    assert 'explicit permission' in text
