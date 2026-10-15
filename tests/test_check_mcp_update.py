import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import check_mcp_update as cmu  # noqa: E402

LS_REMOTE = """\
aaa\trefs/tags/v4.9.3
bbb\trefs/tags/v4.10.3
ccc\trefs/tags/v4.13.0
ddd\trefs/tags/v4.13.1
eee\trefs/tags/v4.13.1^{}
fff\trefs/tags/not-a-version
"""


def test_latest_tag_uses_numeric_order_and_ignores_peeled_and_junk_tags():
    assert cmu.latest_tag(LS_REMOTE) == "v4.13.1"


def test_numeric_not_lexical_ordering():
    assert cmu.parse_version("4.10.3") < cmu.parse_version("4.13.1")
    assert cmu.parse_version("4.9.3") < cmu.parse_version("4.10.0")


def test_installed_version_read_from_server_py(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "server.py").write_text('import os\nVERSION = "4.10.3"\n', encoding="utf-8")
    assert cmu.installed_version(tmp_path) == "4.10.3"


def test_install_dir_comes_from_mcp_json(tmp_path):
    cfg = tmp_path / ".mcp.json"
    cfg.write_text(json.dumps({"mcpServers": {"davinci-resolve": {
        "command": "x", "args": [str(tmp_path / "mcp" / "src" / "server.py")]}}}), encoding="utf-8")
    assert cmu.install_dir(cfg) == tmp_path / "mcp"


def test_decide_up_to_date_update_and_dirty():
    assert cmu.decide("4.13.1", "v4.13.1", dirty=False).action == "up-to-date"
    assert cmu.decide("4.10.3", "v4.13.1", dirty=False).action == "update"
    blocked = cmu.decide("4.10.3", "v4.13.1", dirty=True)
    assert blocked.action == "blocked" and "local changes" in blocked.reason


def test_apply_checks_out_tag_in_clean_repo(tmp_path):
    def git(*a, cwd):
        subprocess.run(["git", *a], cwd=cwd, check=True, capture_output=True)
    up = tmp_path / "up"
    up.mkdir()
    git("init", "-q", cwd=up)
    git("config", "user.email", "t@t", cwd=up)
    git("config", "user.name", "t", cwd=up)
    (up / "src").mkdir()
    (up / "requirements.txt").write_text("", encoding="utf-8")
    (up / "src" / "server.py").write_text('VERSION = "1.0.0"\n', encoding="utf-8")
    git("add", "-A", cwd=up)
    git("commit", "-qm", "v1", cwd=up)
    git("tag", "v1.0.0", cwd=up)
    local = tmp_path / "local"
    subprocess.run(["git", "clone", "-q", str(up), str(local)], check=True, capture_output=True)
    (up / "src" / "server.py").write_text('VERSION = "1.1.0"\n', encoding="utf-8")
    git("commit", "-qam", "v1.1", cwd=up)
    git("tag", "v1.1.0", cwd=up)
    assert cmu.is_dirty(local) is False
    cmu.apply_update(local, "v1.1.0", install_requirements=False)
    assert cmu.installed_version(local) == "1.1.0"
