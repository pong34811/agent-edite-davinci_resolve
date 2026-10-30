"""Export and verify a Resolve project archive (.drp).

Shared by every script that needs a fresh rollback point before it writes.
`export_verified` saves, exports, then checks the file exists, is non-empty and
is a valid zip. It raises instead of returning a half-trusted path.
"""
from __future__ import annotations

import zipfile
from pathlib import Path


def verify_drp(path) -> int:
    """Return the size in bytes of a valid, non-empty .drp or raise RuntimeError."""
    path = Path(path)
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError("Backup missing or empty: %s" % path)
    try:
        with zipfile.ZipFile(path) as archive:
            bad = archive.testzip()
    except zipfile.BadZipFile as exc:
        raise RuntimeError("Backup is not a valid archive: %s" % path) from exc
    if bad is not None:
        raise RuntimeError("Backup archive member is corrupt (%s): %s" % (bad, path))
    return path.stat().st_size


def export_verified(project_manager, project, path) -> int:
    """Save the project, export it to `path`, verify it, and return its size.

    `path` is made absolute: Resolve's ExportProject returns False for a relative path.
    """
    path = Path(path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not project_manager.SaveProject():
        raise RuntimeError("SaveProject failed; no backup written")
    if not project_manager.ExportProject(project.GetName(), str(path), False):
        raise RuntimeError("ExportProject failed for %s" % project.GetName())
    return verify_drp(path)
