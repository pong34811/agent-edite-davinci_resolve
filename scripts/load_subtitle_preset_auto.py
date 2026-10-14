"""One command: load a saved Subtitle-track preset onto a named timeline (Resolve 21.1 has no scripting API for it).

Sequence: refuse if a render is running -> SaveProject -> verified .drp export -> graceful Resolve close (CloseMainWindow, never a kill) -> `patch_subtitle_preset_offline --apply` -> relaunch Resolve ->
reload the project (folder tree search) -> read back every cue (text + frames) and the track state against the pre-patch
snapshot.  Only the named timeline's subtitle-track style row changes.

Usage:
    python -m scripts.load_subtitle_preset_auto --timeline "Timeline 1_9x16" --preset "Mitr-short-001" [--apply]
    (default: dry run, read-only; run from the repository root)
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

from scripts import patch_subtitle_preset_offline as patcher
from scripts.backup_drp import export_verified
from scripts.load_subtitle_preset import find_project_db, find_user_db, library_roots
from scripts.p2_9x16_build import items
from scripts.p2_9x16_common import find
from scripts.resolve_common import connect_resolve

RESOLVE_EXE = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\Resolve.exe"


def snapshot(tl) -> dict:
    return {"cues": [(x.GetName(), x.GetStart(), x.GetEnd()) for x in items(tl, "subtitle", 1)],
            "video": [(x.GetName(), x.GetStart(), x.GetEnd()) for n in range(1, tl.GetTrackCount("video") + 1) for x in items(tl, "video", n)],
            "audio": [(x.GetName(), x.GetStart(), x.GetEnd()) for n in range(1, tl.GetTrackCount("audio") + 1) for x in items(tl, "audio", n)]}


def close_resolve(timeout=90):
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "(Get-Process Resolve -ErrorAction SilentlyContinue) | ForEach-Object { $null = $_.CloseMainWindow() }"],
                   check=False)
    end = time.time() + timeout
    while time.time() < end:
        if not patcher.resolve_running():
            time.sleep(3)
            return
        time.sleep(2)
    raise RuntimeError("Resolve did not close gracefully (a dialog may be open); nothing was written")


def wait_resolve(timeout=180):
    end = time.time() + timeout
    while time.time() < end:
        r = connect_resolve()
        if r is not None and r.GetProjectManager() is not None:
            return r
        time.sleep(3)
    raise RuntimeError("Resolve did not come back")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeline", required=True)
    ap.add_argument("--preset", required=True)
    ap.add_argument("--user", default="guest")
    ap.add_argument("--backup-dir", type=Path, default=Path("exports/_backups").resolve())
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    r = connect_resolve()
    if r is None:
        raise SystemExit("Resolve is not running/connected")
    pm = r.GetProjectManager()
    p = pm.GetCurrentProject()
    if p.IsRenderingInProgress():
        raise SystemExit("render in progress: wait for it to finish")
    tl = find(p, name=a.timeline)
    if tl is None:
        raise SystemExit(f"timeline not found: {a.timeline}")
    tid, pname = tl.GetUniqueId(), p.GetName()
    db = pm.GetCurrentDatabase() or {}
    root = library_roots()[db["DbName"]]
    user_db = find_user_db(root, a.user)
    project_db = find_project_db(root, a.user, pname, [tid])
    before = snapshot(tl)
    cmd = [sys.executable, "-m", "scripts.patch_subtitle_preset_offline", "--project-db", str(project_db),
           "--user-db", str(user_db), "--timeline-id", tid, "--preset", a.preset]
    if not a.apply:
        print(subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8").stdout)
        print(f"dry run: {pname!r} / {a.timeline!r}, {len(before['cues'])} cues; use --apply")
        return 0
    if not pm.SaveProject():
        raise RuntimeError("SaveProject failed")
    bak = a.backup_dir / f"{pname[:20]}_pre_subpreset_{time.strftime('%Y%m%d-%H%M%S')}.drp".replace(" ", "_")
    print("drp backup bytes:", export_verified(pm, p, bak))
    close_resolve()
    out = subprocess.run(cmd + ["--apply"], capture_output=True, text=True, encoding="utf-8")
    print(out.stdout, out.stderr)
    subprocess.Popen([RESOLVE_EXE])
    r2 = wait_resolve()
    pm2 = r2.GetProjectManager()
    # the project lives in a sub-folder of the library: search the folder tree from the root
    pm2.GotoRootFolder()
    _open_containing_folder(pm2, pname)
    time.sleep(5)
    p2 = pm2.GetCurrentProject()
    if p2 is None or p2.GetName() != pname:
        raise RuntimeError("project did not reload; open it manually (the patch itself succeeded)" if out.returncode == 0 else out.stderr)
    after = snapshot(find(p2, name=a.timeline))
    if after != before:
        raise RuntimeError("readback differs from the pre-patch snapshot")
    print(f"LOAD_OK {a.preset} on {a.timeline}: {len(after['cues'])} cues, video/audio ranges unchanged")
    return out.returncode


def _open_containing_folder(pm, pname, depth=0):
    """Depth-first search of the folder tree for the project, leaving the right folder open."""
    if pname in (pm.GetProjectListInCurrentFolder() or []):
        return pm.LoadProject(pname)
    if depth > 4:
        return False
    for f in pm.GetFolderListInCurrentFolder() or []:
        if pm.OpenFolder(f):
            if _open_containing_folder(pm, pname, depth + 1):
                return True
            pm.GotoParentFolder()
    return False


if __name__ == "__main__":
    sys.exit(main())
