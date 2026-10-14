"""Load a saved Subtitle-track preset into ONE timeline by patching Project.db while Resolve is CLOSED.

`load_subtitle_preset.py` documents the blob format and exits before any write because it cannot prove Resolve has
released the database.  This wrapper supplies that proof: it refuses to write while a Resolve process exists, takes a
SQLite backup first, touches only the named timeline's Subtitle-track row(s), and reads every other timeline's
subtitle track back unchanged.  Default is a read-only dry run (works with Resolve open or closed).

Usage:
    python -m scripts.patch_subtitle_preset_offline --project-db <Project.db> --user-db <User.db> \
        --timeline-id <Sm2Timeline_id> --preset "Mitr-short-001" [--apply] [--backup-dir <abs dir>]
"""
from __future__ import annotations

import argparse
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

from scripts.load_subtitle_preset import (STYLE_KEY, _ro, get_bytearray, plan_updates, read_presets,
                                          subtitle_tracks, verify_db, write_plan)


def resolve_running() -> bool:
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Resolve.exe", "/NH"], capture_output=True, text=True).stdout
    return "Resolve.exe" in out


def sqlite_backup(src: Path, dst_dir: Path) -> Path:
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / f"Project_{time.strftime('%Y%m%d-%H%M%S')}.db"
    s, d = sqlite3.connect(f"file:{src.as_posix()}?mode=ro", uri=True), sqlite3.connect(dst)
    try:
        s.backup(d)
    finally:
        d.close()
        s.close()
    if dst.stat().st_size == 0:
        raise RuntimeError("empty SQLite backup")
    return dst


def all_subtitle_styles(project_db: Path) -> dict[str, bytes | None]:
    con = _ro(project_db)
    try:
        ids = [r[0] for r in con.execute("SELECT Sm2Timeline_id FROM Sm2Timeline")]
        return {r[0]: (get_bytearray(r[3], STYLE_KEY) if r[3] else None) for r in subtitle_tracks(con, ids)}
    finally:
        con.close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-db", type=Path, required=True)
    ap.add_argument("--user-db", type=Path, required=True)
    ap.add_argument("--timeline-id", required=True)
    ap.add_argument("--preset", required=True)
    ap.add_argument("--backup-dir", type=Path, default=Path("exports/_backups/subtitle-preset").resolve())
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    presets = read_presets(a.user_db)
    if a.preset not in presets:
        raise SystemExit(f"preset {a.preset!r} not found; have {list(presets)}")
    style = presets[a.preset]
    con = _ro(a.project_db)
    try:
        rows = subtitle_tracks(con, [a.timeline_id])
    finally:
        con.close()
    if len(rows) != 1:
        raise SystemExit(f"expected exactly 1 subtitle track on the timeline, found {len(rows)}")
    plan = plan_updates(rows, style)
    print(f"timeline {plan[0]['timeline']!r}: already_matches={plan[0]['already_matches']}")
    if not a.apply:
        print("dry run only")
        return 0
    if resolve_running():
        raise SystemExit("Resolve.exe is running: close DaVinci Resolve completely, then re-run --apply")
    before = all_subtitle_styles(a.project_db)
    bak = sqlite_backup(a.project_db, a.backup_dir)
    print("sqlite backup:", bak)
    if not plan[0]["already_matches"]:
        write_plan(a.project_db, plan, style)
    verify_db(a.project_db, [a.timeline_id], style, 1)
    after = all_subtitle_styles(a.project_db)
    changed = [k for k in before if before[k] != after.get(k)]
    if changed != ([] if plan[0]["already_matches"] else [plan[0]["track_id"]]):
        raise RuntimeError(f"unexpected rows changed: {changed}")
    print("PATCH_OK; rows changed:", changed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
