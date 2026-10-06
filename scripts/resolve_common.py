"""Shared DaVinci Resolve scripting-API connection for NEW scripts.

Per AGENTS.md "Tool selection": use the davinci-resolve MCP first. A script
that imports this module is the fallback, written only after
`scripts/resolve_preflight.py` (or an equivalent MCP check) shows the MCP lacks
the needed tool/action. Do not copy-paste another `get_resolve()`.

Install locations come from the standard Resolve env vars when set, else the
default Windows install paths.
"""
from __future__ import annotations

import os
import sys

DEFAULT_RESOLVE_DIR = r"C:\Program Files\Blackmagic Design\DaVinci Resolve"
DEFAULT_MODULES_DIR = os.path.join(DEFAULT_RESOLVE_DIR, "ResolvePython", "lib", "modules")


def _prepare_environment() -> None:
    if sys.platform != "win32":
        return
    lib = os.environ.get("RESOLVE_SCRIPT_LIB") or os.path.join(DEFAULT_RESOLVE_DIR, "fusionscript.dll")
    os.environ.setdefault("RESOLVE_SCRIPT_LIB", lib)
    resolve_dir = os.path.dirname(os.environ["RESOLVE_SCRIPT_LIB"]) or DEFAULT_RESOLVE_DIR
    if hasattr(os, "add_dll_directory") and os.path.isdir(resolve_dir):
        try:
            os.add_dll_directory(resolve_dir)
        except Exception:
            pass
    api = os.environ.get("RESOLVE_SCRIPT_API")
    candidates = []
    if api:
        candidates.append(os.path.join(api, "Modules"))
    candidates.append(DEFAULT_MODULES_DIR)
    for path in candidates:
        if os.path.isdir(path) and path not in sys.path:
            sys.path.append(path)


def connect_resolve():
    """Return the running Resolve scripting object, or None (never raises)."""
    _prepare_environment()
    try:
        import DaVinciResolveScript as dvr_script
        return dvr_script.scriptapp("Resolve")
    except Exception:
        return None


def api_has_method(name: str, resolve=None) -> bool:
    """True if `name` is on Resolve or its main objects.

    Uses `name in dir(obj)`; bare hasattr returns True for every attribute on
    Resolve objects (see OPERATING-NOTES).
    """
    resolve = resolve or connect_resolve()
    if resolve is None:
        return False
    objs = [resolve]
    try:
        pm = resolve.GetProjectManager()
        objs.append(pm)
        project = pm.GetCurrentProject()
        if project:
            objs.append(project)
            objs.append(project.GetMediaPool())
            timeline = project.GetCurrentTimeline()
            if timeline:
                objs.append(timeline)
                items = timeline.GetItemListInTrack("video", 1)
                if items:
                    objs.append(items[0])
    except Exception:
        pass
    return any(name in dir(obj) for obj in objs)
