"""Delete redundant per-batch DRP archives after one fresh verified backup.

Dry-run by default; deletion needs --confirm. Exports and validates ONE new .drp
of the current state first. Only files whose names start with a DELETE prefix are
removed; rollback archives (KEEP markers) and anything unmatched are always kept
and reported. Never touches anything outside the backups directory.
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.backup_drp import export_verified  # noqa: E402
from scripts.resolve_common import connect_resolve  # noqa: E402

ART = ROOT / '.hermes/artifacts/enrichment-review-2026-10-06-live2'
BACKUPS = ART / 'backups'
KEEP_MARKERS = ('aomimama-2026-09-p1-pre-enrichment-', 'before_promotion_')
DELETE_PREFIXES = ('before_python_batch_', 'before_python_vdo_')


def classify(name):
    """Return 'keep', 'delete' or 'unmatched'. Keep markers win over delete prefixes."""
    if any(marker in name for marker in KEEP_MARKERS):
        return 'keep'
    if name.startswith(DELETE_PREFIXES):
        return 'delete'
    return 'unmatched'


def sweep(backups_dir, fresh, confirm):
    """Classify (and with confirm, delete) archives in backups_dir; return the report."""
    report = {'deleted': [], 'would_delete': [], 'kept': [], 'skipped_unmatched': []}
    for path in sorted(Path(backups_dir).glob('*.drp')):
        if path == fresh:
            report['kept'].append(path.name)
            continue
        kind = classify(path.name)
        if kind == 'keep':
            report['kept'].append(path.name)
        elif kind == 'unmatched':
            report['skipped_unmatched'].append(path.name)
        elif confirm:
            path.unlink()
            report['deleted'].append(path.name)
        else:
            report['would_delete'].append(path.name)
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--confirm', action='store_true', help='Required to delete anything')
    args = ap.parse_args(argv)
    r = connect_resolve()
    if r is None:
        raise RuntimeError('Resolve unavailable')
    pm = r.GetProjectManager()
    project = pm.GetCurrentProject()
    if project is None:
        raise RuntimeError('No current project')
    if project.IsRenderingInProgress():
        raise RuntimeError('Render in progress')
    fresh = BACKUPS / ('current-state-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.drp')
    fresh_bytes = export_verified(pm, project, fresh)  # raises before anything is deleted
    report = {'fresh_verified_backup': str(fresh), 'fresh_bytes': fresh_bytes}
    report.update(sweep(BACKUPS, fresh, args.confirm))
    (ART / 'cleanup-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'confirmed': args.confirm, 'deleted': len(report['deleted']),
                      'would_delete': len(report['would_delete']), 'kept': report['kept'],
                      'skipped': report['skipped_unmatched'],
                      'fresh_backup': report['fresh_verified_backup']}, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
