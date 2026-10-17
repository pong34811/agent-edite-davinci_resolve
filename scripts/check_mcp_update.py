"""Check (and optionally apply) updates of the community davinci-resolve MCP.

Run at the start of every task (AGENTS.md "Start of task checklist"):

    python scripts/check_mcp_update.py            # report only
    python scripts/check_mcp_update.py --apply    # update the install to the newest tag

Upstream: https://github.com/samuelgursky/davinci-resolve-mcp
The install directory is read from `.mcp.json`. The check is read-only; --apply
only runs `git fetch --tags`, `git checkout <tag>` and `pip install -r requirements.txt`
inside that directory, and refuses to touch a working tree with local changes.
It never talks to Resolve.
"""
import argparse
import json
import re
import subprocess
import sys
from collections import namedtuple
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = "https://github.com/samuelgursky/davinci-resolve-mcp.git"
TAG_RE = re.compile(r"refs/tags/(v\d+\.\d+\.\d+)$")

Decision = namedtuple("Decision", "action reason")


def parse_version(text):
    return tuple(int(part) for part in text.lstrip("v").split("."))


def latest_tag(ls_remote_output):
    tags = [m.group(1) for line in ls_remote_output.splitlines()
            if (m := TAG_RE.search(line.split("\t")[-1].strip()))]
    return max(tags, key=parse_version) if tags else None


def install_dir(mcp_json=ROOT / ".mcp.json"):
    config = json.loads(Path(mcp_json).read_text(encoding="utf-8"))
    server = config["mcpServers"]["davinci-resolve"]["args"][0]
    return Path(server).parents[1]


def installed_version(directory):
    text = (Path(directory) / "src" / "server.py").read_text(encoding="utf-8")
    match = re.search(r'^VERSION\s*=\s*"([^"]+)"', text, re.M)
    return match.group(1) if match else None


def _git(directory, *args):
    return subprocess.run(["git", *args], cwd=directory, check=True,
                          capture_output=True, text=True).stdout


def is_dirty(directory):
    return bool(_git(directory, "status", "--porcelain").strip())


def decide(installed, latest, dirty):
    if latest is None:
        return Decision("unknown", "no version tags found upstream")
    if installed and parse_version(installed) >= parse_version(latest):
        return Decision("up-to-date", f"installed {installed} >= upstream {latest}")
    if dirty:
        return Decision("blocked", "install has local changes; commit or stash them first")
    return Decision("update", f"installed {installed} -> upstream {latest}")


def apply_update(directory, tag, install_requirements=True):
    _git(directory, "fetch", "--tags", "--quiet")
    _git(directory, "checkout", "--quiet", tag)
    requirements = Path(directory) / "requirements.txt"
    if install_requirements and requirements.exists():
        python = Path(directory) / "venv" / "Scripts" / "python.exe"
        if not python.exists():
            python = Path(directory) / "venv" / "bin" / "python"
        subprocess.run([str(python), "-m", "pip", "install", "-q", "-r", str(requirements)], check=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true", help="update the install to the newest tag")
    parser.add_argument("--mcp-json", default=str(ROOT / ".mcp.json"))
    args = parser.parse_args(argv)

    directory = install_dir(args.mcp_json)
    version_file = directory / "src" / "server.py"
    if not version_file.is_file():
        print(f"BLOCKED: configured MCP install is missing {version_file} (check .mcp.json)")
        return 1

    installed = installed_version(directory)
    remote = subprocess.run(["git", "ls-remote", "--tags", UPSTREAM], capture_output=True,
                            text=True, timeout=60)
    if remote.returncode != 0:
        print(f"UNKNOWN: cannot reach upstream ({remote.stderr.strip()[:120]}); installed {installed}")
        return 0
    latest = latest_tag(remote.stdout)
    decision = decide(installed, latest, is_dirty(directory))
    print(f"{decision.action.upper()}: {decision.reason} ({directory})")
    if decision.action == "update" and args.apply:
        apply_update(directory, latest)
        print(f"UPDATED: installed version is now {installed_version(directory)}. "
              "Restart the agent session so the MCP reloads, then probe resolve_control get_version.")
    elif decision.action == "update":
        print("Run again with --apply to update (read release notes in the upstream CHANGELOG.md first).")
    return 1 if decision.action == "blocked" else 0


if __name__ == "__main__":
    sys.exit(main())
