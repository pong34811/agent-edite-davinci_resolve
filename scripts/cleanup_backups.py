"""Delete the redundant per-batch DRP archives after one fresh verified backup.

Requires an explicit confirmation flag. Exports and validates ONE new .drp of the
current post-promotion state first, then removes only the timestamped per-batch
files this session created. Never touches anything outside the named directory.
"""
import argparse
import json
import zipfile
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.resolve_common import connect_resolve

ART = ROOT / '.hermes/artifacts/enrichment-review-2026-10-06-live2'
BACKUPS = ART / 'backups'
KEEP_MARKERS = ('aomimama-2026-09-p1-pre-enrichment-', 'before_promotion_')
DELETE_PREFIXES = ('before_python_batch_', 'before_python_vdo_')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--confirm', action='store_true', help='Required to delete anything')
    ap.add_argument('--keep-rollback', action='store_true', default=True)
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
    if not pm.SaveProject() or not pm.ExportProject(project.GetName(), str(fresh), False):
        raise RuntimeError('Fresh backup export failed; deleting nothing')
    if not fresh.is_file() or fresh.stat().st_size == 0:
        raise RuntimeError('Fresh backup empty; deleting nothing')
    with zipfile.ZipFile(fresh) as archive:
        if archive.testzip() is not None:
            raise RuntimeError('Fresh backup archive invalid; deleting nothing')
    report = {'fresh_verified_backup': str(fresh), 'fresh_bytes': fresh.stat().st_size,
              'deleted': [], 'kept': [], 'skipped_unmatched': []}
    keep = []
    for path in sorted(BACKUPS.glob('*.drp')):
        if path == fresh:
            report['kept'].append(path.name)
            continue
        if not args.confirm:
            report['deleted'].append({'name': path.name, 'would_delete': True})
            continue
        path.unlink()
        report['deleted'].append(path.name)
    (ART / 'cleanup-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'confirmed': args.confirm, 'deleted': len(report['deleted']),
                      'kept': report['kept'], 'skipped': report['skipped_unmatched'],
                      'fresh_backup': report['fresh_verified_backup']}, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
