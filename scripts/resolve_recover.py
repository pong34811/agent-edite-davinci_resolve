"""Recover a crashed or hung DaVinci Resolve and reopen the project being edited.

The user authorised agents (2026-10-28) to do this on their own whenever Resolve
closes itself or stops answering scripting mid-edit:

  0. every disk project library in Preferences/dblist.conf must be reachable; a
     library on Google Drive (G:) disappears when Drive for desktop stops, and
     Resolve then fails SaveProject and can crash. Start Drive and wait for it.
  1. probe: is Resolve.exe running, and does scripting answer within --probe-timeout?
  2. hung (running but silent on two probes) -> taskkill /F the Resolve.exe process
  3. closed -> launch through explorer.exe (a Resolve started as a child of the
     agent's shell never answers scripting; see OPERATING-NOTES)
  4. wait for scripting; if the project's library is missing from
     GetDatabaseList (Resolve started while the drive was absent) quit and relaunch
  5. load --project, trying every library and searching each project-folder tree
  6. print RECOVER_OK <project> <timeline count>

Usage: python scripts/resolve_recover.py --project "2026-06-Sakuyako" [--dry-run]
After recovery, re-verify the last item in flight: the crash can lose its unsaved
edit. Right after a relaunch some setters (SetCurrentTimeline, OpenPage) return
None even when they work: confirm by reading state back, not by the return value.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from resolve_common import DEFAULT_RESOLVE_DIR, connect_resolve  # noqa: E402

RESOLVE_EXE = str(Path(DEFAULT_RESOLVE_DIR) / "Resolve.exe")
PREFS = Path(os.environ.get("APPDATA", "")) / "Blackmagic Design" / "DaVinci Resolve" / "Preferences"
DRIVE_FS_DIR = Path(r"C:\Program Files\Google\Drive File Stream")
PROBE = (
    "import sys; sys.path.insert(0, {scripts!r});"
    "from resolve_common import connect_resolve;"
    "r = connect_resolve(); p = r and r.GetProjectManager().GetCurrentProject();"
    "print('PROBE', 'ok' if r else 'none', p.GetName() if p else '')"
)


def decide(running: bool, responsive: bool) -> str:
    """Pure decision: 'ok', 'launch' (closed) or 'kill_then_launch' (hung)."""
    if not running:
        return "launch"
    return "ok" if responsive else "kill_then_launch"


def parse_dblist(text: str) -> dict[str, str]:
    """dblist.conf lines 'name:G\\My Drive\\...:*:::DISK' -> {name: 'G:\\My Drive\\...'}."""
    libs = {}
    for line in text.splitlines():
        parts = line.strip().split(":")
        if len(parts) >= 2 and parts[-1].upper() == "DISK" and parts[1]:
            path = parts[1]
            if len(path) >= 2 and path[0].isalpha() and path[1] == "\\":
                path = path[0] + ":" + path[1:]
            libs[parts[0]] = path
    return libs


def missing_libraries(only: str | None = None) -> dict[str, str]:
    conf = PREFS / "dblist.conf"
    if not conf.is_file():
        return {}
    libs = parse_dblist(conf.read_text(encoding="utf-8", errors="replace"))
    return {k: v for k, v in libs.items() if (only is None or k == only) and not Path(v).exists()}


def project_library(text: str, project: str) -> str | None:
    """recentprojects.conf 'disk:<lib>:<lib>:<folder\\project>:<project>:...' -> library name."""
    for line in text.splitlines():
        parts = line.strip().split(":")
        if len(parts) >= 5 and parts[0].lower() == "disk" and parts[4] == project:
            return parts[1]
    return None


def library_of(project: str) -> str | None:
    conf = PREFS / "recentprojects.conf"
    if not conf.is_file():
        return None
    return project_library(conf.read_text(encoding="utf-8", errors="replace"), project)


def ensure_library_drives(only: str | None = None, limit: float = 120) -> dict[str, str]:
    """Start Google Drive for desktop when a library path is missing; return what is still missing."""
    missing = missing_libraries(only)
    if not missing:
        return {}
    exes = sorted(DRIVE_FS_DIR.glob("*/GoogleDriveFS.exe"))
    if exes:
        print("library path missing, starting Google Drive:", missing)
        subprocess.Popen(["explorer.exe", str(exes[-1])])
        end = time.time() + limit
        while time.time() < end and missing_libraries(only):
            time.sleep(5)
    return missing_libraries(only)


def resolve_running() -> bool:
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Resolve.exe", "/NH"],
                         capture_output=True, text=True).stdout
    return "resolve.exe" in out.lower()


def scripting_responsive(timeout: float) -> bool:
    """Probe in a child process: a hung Resolve blocks the API call forever."""
    code = PROBE.format(scripts=str(Path(__file__).resolve().parent))
    try:
        out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                             timeout=timeout, encoding="utf-8", errors="replace").stdout
    except subprocess.TimeoutExpired:
        return False
    return "PROBE ok" in out


def open_project(pm, name: str, depth: int = 0) -> bool:
    """Depth-first search of the project-folder tree; leaves the project loaded."""
    if depth == 0:
        cur = pm.GetCurrentProject()
        if cur and cur.GetName() == name:
            return True
        pm.GotoRootFolder()
    if name in (pm.GetProjectListInCurrentFolder() or []):
        return bool(pm.LoadProject(name))
    if depth > 5:
        return False
    for folder in pm.GetFolderListInCurrentFolder() or []:
        if pm.OpenFolder(folder):
            if open_project(pm, name, depth + 1):
                return True
            pm.GotoParentFolder()
    return False


def wait_for_scripting(limit: float):
    end = time.time() + limit
    while time.time() < end:
        if resolve_running() and scripting_responsive(20):
            r = connect_resolve()
            if r and r.GetProjectManager():
                return r
        time.sleep(5)
    return None


def open_in_any_library(pm, name: str) -> bool:
    if open_project(pm, name):
        return True
    for db in pm.GetDatabaseList() or []:
        if db != pm.GetCurrentDatabase() and pm.SetCurrentDatabase(db) and open_project(pm, name):
            return True
    return False


def launch_and_wait(limit: float):
    subprocess.Popen(["explorer.exe", RESOLVE_EXE])
    return wait_for_scripting(limit)


def quit_resolve(r) -> None:
    r.Quit()
    for _ in range(30):
        if not resolve_running():
            return
        time.sleep(2)


def main() -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--project", required=True)
    ap.add_argument("--probe-timeout", type=float, default=30)
    ap.add_argument("--launch-timeout", type=float, default=300)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    running = resolve_running()
    responsive = running and (scripting_responsive(a.probe_timeout) or scripting_responsive(a.probe_timeout))
    action = decide(running, responsive)
    lib = library_of(a.project)
    print(f"running={running} responsive={responsive} action={action} library={lib!r} "
          f"missing={missing_libraries(lib) if lib else 'unknown library'}")
    if a.dry_run:
        return 0
    still_missing = ensure_library_drives(lib) if lib else {}
    if still_missing:
        print(f"RECOVER_FAILED: library path still missing {still_missing}; ask the user to mount it")
        return 1
    if action == "kill_then_launch":
        subprocess.run(["taskkill", "/IM", "Resolve.exe", "/F"], capture_output=True)
        for _ in range(30):
            if not resolve_running():
                break
            time.sleep(2)
    r = launch_and_wait(a.launch_timeout) if action != "ok" else wait_for_scripting(a.launch_timeout)
    if r is None:
        print("RECOVER_FAILED: scripting never answered; ask the user to open Resolve")
        return 1
    pm = r.GetProjectManager()
    opened = any(open_in_any_library(pm, a.project) or time.sleep(10) for _ in range(3))
    if not opened:
        cur = pm.GetCurrentProject()
        if action == "ok" and cur is not None and cur.GetName() != "Untitled Project":
            print(f"RECOVER_FAILED: {a.project!r} not found and {cur.GetName()!r} is open; not restarting")
            return 1
        # Resolve drops a library whose drive was absent at startup: restart once now that it is back
        print("project not found in", pm.GetDatabaseList(), "- restarting Resolve to re-read libraries")
        quit_resolve(r)
        r = launch_and_wait(a.launch_timeout)
        if r is None:
            print("RECOVER_FAILED: scripting never answered after restart")
            return 1
        pm = r.GetProjectManager()
        any(open_in_any_library(pm, a.project) or time.sleep(10) for _ in range(3))
    p = pm.GetCurrentProject()
    if p is None or p.GetName() != a.project:
        print(f"RECOVER_FAILED: project {a.project!r} did not open (current: {p and p.GetName()!r})")
        return 1
    print(f"RECOVER_OK {p.GetName()} timelines={p.GetTimelineCount()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
