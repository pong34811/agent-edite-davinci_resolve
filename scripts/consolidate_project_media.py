"""Copy every file the current project uses into one folder and relink it there.

Originals are never moved or deleted (GIF/SFX/BGM libraries are shared with
other projects). Files are grouped by kind into subfolders of --dest; a file
already under --dest is left where it is. Dry-run by default; --apply exports a
verified .drp first, copies, relinks per subfolder with MediaPool.RelinkClips
and reads back every clip's File Path.

    python scripts/consolidate_project_media.py --dest "Z:\\armigon\\Why Vtuber"
    python scripts/consolidate_project_media.py --dest "Z:\\armigon\\Why Vtuber" --apply
"""
from __future__ import annotations

import argparse
import datetime as dt
import ntpath
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.backup_drp import export_verified  # noqa: E402
from scripts.resolve_common import preserved_state, require_resolve  # noqa: E402

GROUPS = (
    ("subtitles", {".srt", ".vtt", ".ass"}),
    ("gif", {".gif"}),
    ("illustrations", {".png", ".jpg", ".jpeg", ".webp", ".mov", ".psd"}),
    ("footage", {".mp4", ".mkv", ".m4v", ".avi"}),
)


def norm(path: str) -> str:
    return ntpath.normcase(ntpath.normpath(path.replace("/", "\\")))


def subfolder_for(path: str, bin_path: str = "") -> str:
    """Pick the destination subfolder from the extension (and bin for audio)."""
    ext = ntpath.splitext(path)[1].lower()
    for name, exts in GROUPS:
        if ext in exts:
            return name
    if ext in {".wav", ".mp3", ".aif", ".aiff", ".flac", ".m4a"}:
        lowered = (path + " " + bin_path).lower()
        return "bgm" if "bgm" in lowered or "music" in lowered else "sfx"
    return "other"


def plan(clips, dest: str):
    """Return (moves, skipped). clips: dicts with name/id/file/bin."""
    dest_n = norm(dest)
    moves, skipped, taken = [], [], {}
    for clip in clips:
        src = clip["file"]
        if not src:
            continue
        if norm(src).startswith(dest_n + "\\"):
            skipped.append((clip, "already under dest"))
            continue
        sub = subfolder_for(src, clip.get("bin", ""))
        target = ntpath.join(dest, sub, ntpath.basename(src))
        key = norm(target)
        if key in taken and taken[key] != norm(src):
            skipped.append((clip, "name clash with " + taken[key]))
            continue
        taken[key] = norm(src)
        moves.append(dict(clip, sub=sub, target=target))
    return moves, skipped


def walk(folder, path="Master"):
    for c in folder.GetClipList() or []:
        yield c, path
    for s in folder.GetSubFolderList() or []:
        yield from walk(s, path + "/" + s.GetName())


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dest", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--backup-dir", type=Path, default=ROOT / ".hermes/artifacts/backups")
    a = ap.parse_args()

    resolve = require_resolve()
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    mp = project.GetMediaPool()
    items = {c.GetUniqueId(): (c, b) for c, b in walk(mp.GetRootFolder())}
    clips = [dict(id=i, name=c.GetName(), bin=b, file=c.GetClipProperty("File Path") or "")
             for i, (c, b) in items.items()]
    moves, skipped = plan(clips, a.dest)
    print("project:", project.GetName())
    for m in moves:
        print("COPY  %-13s %s" % (m["sub"], m["file"]))
    for clip, why in skipped:
        print("SKIP  %s (%s)" % (clip["file"], why))
    missing = [m for m in moves if not Path(m["file"]).is_file()]
    for m in missing:
        print("MISSING SOURCE", m["file"])
    if not a.apply:
        print("dry-run: %d to copy, %d skipped, %d missing" % (len(moves), len(skipped), len(missing)))
        return 0
    if missing:
        raise SystemExit("refusing to apply: missing sources")

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    print("drp bytes", export_verified(pm, project, a.backup_dir / f"{project.GetName()}-before-consolidate-{stamp}.drp"))
    for m in moves:
        target = Path(m["target"])
        target.parent.mkdir(parents=True, exist_ok=True)
        if not (target.is_file() and target.stat().st_size == Path(m["file"]).stat().st_size):
            shutil.copy2(m["file"], target)
        if target.stat().st_size != Path(m["file"]).stat().st_size:
            raise SystemExit("copy size mismatch: %s" % target)

    failed = []
    with preserved_state(resolve):
        for sub in sorted({m["sub"] for m in moves}):
            group = [m for m in moves if m["sub"] == sub]
            ok = mp.RelinkClips([items[m["id"]][0] for m in group], ntpath.join(a.dest, sub))
            print("relink %-13s %d clips -> %s" % (sub, len(group), ok))
        for m in moves:
            now = items[m["id"]][0].GetClipProperty("File Path") or ""
            if norm(now) != norm(m["target"]):
                failed.append((m, now))
        pm.SaveProject()
    for m, now in failed:
        print("NOT RELINKED", m["name"], "->", now)
    print("relinked %d/%d" % (len(moves) - len(failed), len(moves)))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
