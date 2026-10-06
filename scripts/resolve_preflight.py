"""MCP-first preflight for DaVinci Resolve work (read-only).

    python scripts/resolve_preflight.py --need timeline.get_items
    python scripts/resolve_preflight.py --need SetStartTimecode --probe-api --json

Verdicts:
  USE_MCP          the davinci-resolve MCP has the tool (and action) and its
                   server is installed -> use the MCP.
  FALLBACK_SCRIPT  the MCP lacks it but the scripting API has the method ->
                   a script in scripts/ is justified. Report a
                   `MCP-GAP: <need> -> <reason>` line first.
  BLOCKED          neither is confirmed (or Resolve is not running) -> do not
                   write a script on a guess.

Limit: this reads the saved MCP tool schemas and the server config. It cannot
see the live tool catalog attached to the agent; the agent must still read its
own catalog (AGENTS.md "Tool selection").
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MCP_CONFIG = ROOT / ".mcp.json"
SERVER_NAME = "davinci-resolve"


def default_catalog_dir() -> Path:
    env = os.environ.get("RESOLVE_MCP_CATALOG")
    if env:
        return Path(env)
    return Path.home() / ".gemini" / "antigravity" / "mcp" / SERVER_NAME


def resolve_is_running() -> bool:
    try:
        if sys.platform == "win32":
            out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Resolve.exe"],
                                 capture_output=True, text=True, timeout=15).stdout
            return "resolve.exe" in out.lower()
        out = subprocess.run(["pgrep", "-ix", "resolve"], capture_output=True, text=True, timeout=15)
        return out.returncode == 0
    except Exception:
        return False


def _server_check(mcp_config: Path):
    """Return (ok, reason)."""
    try:
        cfg = json.loads(Path(mcp_config).read_text(encoding="utf-8"))
        server = cfg["mcpServers"][SERVER_NAME]
    except Exception as exc:
        return False, f"MCP server config unreadable ({type(exc).__name__}): {mcp_config}"
    command = server.get("command", "")
    args = server.get("args") or []
    if not command or not Path(command).is_file():
        return False, f"MCP server command not found: {command}"
    if args and not Path(args[0]).is_file():
        return False, f"MCP server script not found: {args[0]}"
    return True, "MCP server files present"


def _catalog_check(need: str, catalog_dir: Path):
    """Return (found, reason, api_name). `api_name` is what to probe in the API."""
    tool, _, action = need.partition(".")
    api_name = action or tool
    schema = Path(catalog_dir) / f"{tool}.json"
    if not Path(catalog_dir).is_dir():
        return False, f"MCP catalog directory not found: {catalog_dir}", api_name
    if not schema.is_file():
        return False, f"MCP tool '{tool}' not in catalog", api_name
    if not action:
        return True, f"MCP tool '{tool}' in catalog", api_name
    text = schema.read_text(encoding="utf-8")
    if re.search(r"(?<![A-Za-z0-9_])" + re.escape(action) + r"(?![A-Za-z0-9_])", text):
        return True, f"MCP tool '{tool}' lists action '{action}'", api_name
    return False, f"MCP tool '{tool}' has no action '{action}' in its schema", api_name


def evaluate(need, mcp_config=DEFAULT_MCP_CONFIG, catalog_dir=None,
             resolve_running=resolve_is_running, api_has=None) -> dict:
    catalog_dir = Path(catalog_dir) if catalog_dir else default_catalog_dir()
    reasons: list[str] = []
    if not resolve_running():
        reasons.append("DaVinci Resolve is not running")
        return {"need": need, "verdict": "BLOCKED", "reasons": reasons}

    found, why, api_name = _catalog_check(need, catalog_dir)
    reasons.append(why)
    server_ok, server_why = _server_check(Path(mcp_config))
    reasons.append(server_why)
    if found and server_ok:
        return {"need": need, "verdict": "USE_MCP", "reasons": reasons}

    if api_has is None:
        reasons.append("scripting API not probed (use --probe-api); no script justified yet")
        return {"need": need, "verdict": "BLOCKED", "reasons": reasons}
    if api_has(api_name):
        reasons.append(f"scripting API has '{api_name}'")
        return {"need": need, "verdict": "FALLBACK_SCRIPT", "reasons": reasons,
                "mcp_gap": f"MCP-GAP: {need} -> {why if not found else server_why}"}
    reasons.append(f"scripting API has no '{api_name}'")
    return {"need": need, "verdict": "BLOCKED", "reasons": reasons}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--need", required=True, help="MCP 'tool' or 'tool.action', or an API method name")
    ap.add_argument("--catalog-dir", help="dir of MCP tool schemas (env RESOLVE_MCP_CATALOG)")
    ap.add_argument("--mcp-config", default=str(DEFAULT_MCP_CONFIG))
    ap.add_argument("--probe-api", action="store_true", help="connect to Resolve and probe the scripting API")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    api_has = None
    if args.probe_api:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from resolve_common import api_has_method
        api_has = api_has_method
    result = evaluate(args.need, mcp_config=Path(args.mcp_config),
                      catalog_dir=args.catalog_dir, api_has=api_has)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result["verdict"])
        for r in result["reasons"]:
            print(" -", r)
        if result.get("mcp_gap"):
            print(result["mcp_gap"])
    return {"USE_MCP": 0, "FALLBACK_SCRIPT": 10, "BLOCKED": 2}[result["verdict"]]


if __name__ == "__main__":
    sys.exit(main())
