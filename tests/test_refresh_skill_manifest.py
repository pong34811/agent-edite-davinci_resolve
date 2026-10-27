import hashlib

from scripts.refresh_skill_manifest import digest_for


def test_digest_for_preserves_existing_lf_or_crlf_checksum(tmp_path):
    content = b"first line\nsecond line\n"
    path = tmp_path / "skill.md"
    path.write_bytes(content.replace(b"\n", b"\r\n"))

    expected_lf = hashlib.sha256(content).hexdigest()
    assert digest_for(path, expected_lf) == expected_lf


def test_digest_for_rechecksums_changed_content(tmp_path):
    path = tmp_path / "skill.md"
    path.write_bytes(b"changed content\n")

    assert digest_for(path, "stale-checksum") == hashlib.sha256(path.read_bytes()).hexdigest()
