"""One command: load a saved Subtitle-track preset onto a named timeline (Resolve 21.1 has no scripting API for it).

Sequence: refuse if a render is running -> SaveProject -> verified .drp export -> graceful Resolve close (CloseMainWindow, never a kill) -> `patch_subtitle_preset_offline --apply` -> relaunch Resolve ->
reload the project (folder tree search) -> read back every cue (text + frames) and the track state against the pre-patch
snapshot.  Only the named timeline's subtitle-track style row changes.

Usage:
    python -m scripts.load_subtitle_preset_auto --timeline "Timeline 1_9x16" [--timeline "Timeline 2_9x16" ...] --preset "Mitr-short-001" [--apply]
    (each --timeline is patched in the same single close/relaunch)
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


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeline", required=True, action="append",
                    help="timeline name; repeat to patch several timelines with one Resolve restart")
    ap.add_argument("--preset", required=True)
    ap.add_argument("--user", default="guest")
    ap.add_argument("--backup-dir", type=Path, default=Path("exports/_backups").resolve())
    ap.add_argument("--apply", action="store_true")
    return ap


def main(argv=None) -> int:
    ap = build_parser()
    a = ap.parse_args(argv)

    r = connect_resolve()
    if r is None:
        raise SystemExit("Resolve is not running/connected")
    pm = r.GetProjectManager()
    p = pm.GetCurrentProject()
    if p.IsRenderingInProgress():
        raise SystemExit("render in progress: wait for it to finish")
    names = list(dict.fromkeys(a.timeline))
    tls = {n: find(p, name=n) for n in names}
    missing = [n for n, t in tls.items() if t is None]
    if missing:
        raise SystemExit(f"timeline not found: {missing}")
    tids, pname = {n: t.GetUniqueId() for n, t in tls.items()}, p.GetName()
    db = pm.GetCurrentDatabase() or {}
    root = library_roots()[db["DbName"]]
    user_db = find_user_db(root, a.user)
    project_db = find_project_db(root, a.user, pname, list(tids.values()))
    before = {n: snapshot(t) for n, t in tls.items()}

    def cmd(tid):
        return [sys.executable, "-m", "scripts.patch_subtitle_preset_offline", "--project-db", str(project_db),
                "--user-db", str(user_db), "--timeline-id", tid, "--preset", a.preset]
    if not a.apply:
        for n in names:
            print(subprocess.run(cmd(tids[n]), capture_output=True, text=True, encoding="utf-8").stdout)
            print(f"dry run: {pname!r} / {n!r}, {len(before[n]['cues'])} cues; use --apply")
        return 0
    if not pm.SaveProject():
        raise RuntimeError("SaveProject failed")
    bak = a.backup_dir / f"{pname[:20]}_pre_subpreset_{time.strftime('%Y%m%d-%H%M%S')}.drp".replace(" ", "_")
    print("drp backup bytes:", export_verified(pm, p, bak))
    close_resolve()
    rc = 0
    for n in names:
        out = subprocess.run(cmd(tids[n]) + ["--apply"], capture_output=True, text=True, encoding="utf-8")
        print(n, out.stdout, out.stderr)
        rc = rc or out.returncode
    # launch through Explorer: a Resolve started as a child of the agent's shell never answered scripting (2026-10-23)
    subprocess.Popen(["explorer.exe", RESOLVE_EXE])
    r2 = wait_resolve()
    pm2 = r2.GetProjectManager()
    # the project lives in a sub-folder of the library: search the folder tree from the root
    pm2.GotoRootFolder()
    _open_containing_folder(pm2, pname)
    time.sleep(5)
    p2 = pm2.GetCurrentProject()
    if p2 is None or p2.GetName() != pname:
        raise RuntimeError("project did not reload; open it manually (the patch itself succeeded)" if rc == 0 else "patch failed")
    for n in names:
        after = snapshot(find(p2, name=n))
        if after != before[n]:
            raise RuntimeError(f"readback differs from the pre-patch snapshot: {n}")
        print(f"LOAD_OK {a.preset} on {n}: {len(after['cues'])} cues, video/audio ranges unchanged")
    return rc


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
