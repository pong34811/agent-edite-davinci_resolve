"""Shared DaVinci Resolve scripting-API connection for NEW scripts.

Per AGENTS.md "Tool selection": use the davinci-resolve MCP first. A script
that imports this module is the fallback, written only after
`scripts/resolve_preflight.py` (or an equivalent MCP check) shows the MCP lacks
the needed tool/action. Do not copy-paste another `get_resolve()`.

Install locations come from the standard Resolve env vars when set, else the
default Windows install paths.
"""
from __future__ import annotations

import contextlib
import os
import sys

DEFAULT_RESOLVE_DIR = r"C:\Program Files\Blackmagic Design\DaVinci Resolve"
DEFAULT_MODULES_DIR = os.path.join(DEFAULT_RESOLVE_DIR, "ResolvePython", "lib", "modules")
DEFAULT_SCRIPT_API = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"


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
    candidates.append(os.path.join(DEFAULT_SCRIPT_API, "Modules"))
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


def require_resolve():
    """Return the Resolve object or exit with one clear message (for CLI scripts)."""
    resolve = connect_resolve()
    if not resolve:
        raise SystemExit("Cannot connect to DaVinci Resolve (is it running with external scripting enabled?)")
    return resolve


@contextlib.contextmanager
def preserved_state(resolve):
    """Restore active project, timeline, playhead and page on exit.

    AGENTS.md handoff rule: leave the user's session as found. Restoration
    is best-effort and never masks an exception raised in the body.
    """
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    name = project.GetName() if project else None
    timeline = project.GetCurrentTimeline() if project else None
    tl_id = timeline.GetUniqueId() if timeline else None
    tc = timeline.GetCurrentTimecode() if timeline else None
    page = resolve.GetCurrentPage()
    try:
        yield
    finally:
        try:
            cur = pm.GetCurrentProject()
            if name and (not cur or cur.GetName() != name):
                cur = pm.LoadProject(name)
            if cur and tl_id:
                for i in range(1, cur.GetTimelineCount() + 1):
                    tl = cur.GetTimelineByIndex(i)
                    if tl.GetUniqueId() == tl_id:
                        cur.SetCurrentTimeline(tl)
                        if tc:
                            tl.SetCurrentTimecode(tc)
                        break
            if page:
                resolve.OpenPage(page)
        except Exception:
            pass


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
