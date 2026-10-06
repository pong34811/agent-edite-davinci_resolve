"""Delete only the redundant draft/pilot copies; verify originals are untouched.
MCP-GAP: live Resolve MCP absent; MediaPool.DeleteTimelines probed on this build.
Default dry-run. Requires a fresh verified .drp before any deletion.
"""
from __future__ import annotations
import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.resolve_common import connect_resolve
from scripts.apply_offline_enrichment_pilot import contents

ART = ROOT / '.hermes/artifacts/enrichment-review-2026-10-06-live2'
SUFFIX = ' [ENRICHMENT DRAFT OFFLINE]'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project-id', required=True)
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args(argv)
    inventory = json.loads((ART / 'inventory.json').read_text(encoding='utf-8'))
    pilot = json.loads((ART / 'pilot-offline-01.json').read_text(encoding='utf-8'))
    r = connect_resolve()
    if r is None:
        raise RuntimeError('Resolve unavailable')
    pm = r.GetProjectManager()
    project = pm.GetCurrentProject()
    if project is None or project.GetUniqueId() != args.project_id:
        raise RuntimeError('Project ID mismatch')
    if project.IsRenderingInProgress():
        raise RuntimeError('Render in progress')
    pool = project.GetMediaPool()
    if 'DeleteTimelines' not in dir(pool):
        raise RuntimeError('DeleteTimelines unavailable on this build; do not guess another route')
    tls = [project.GetTimelineByIndex(i) for i in range(1, project.GetTimelineCount() + 1)]
    by_id = {t.GetUniqueId(): t for t in tls}
    originals = []
    for row in inventory['timelines']:
        original = by_id.get(row['timeline_id'])
        if original is None:
            raise RuntimeError('Original missing for ordinal ' + str(row['ordinal']))
        originals.append((row, original))
    targets = [t for t in tls if t.GetName().endswith(SUFFIX) or t.GetUniqueId() == pilot['pilot_id']]
    original_ids = {row['timeline_id'] for row in inventory['timelines']}
    if not targets:
        raise RuntimeError('No draft copies found; nothing to delete')
    unexpected = [t.GetName() for t in tls
                  if t not in targets and t.GetUniqueId() not in original_ids]
    if unexpected:
        raise RuntimeError('Unknown timelines present; refusing: ' + '; '.join(unexpected))
    if len(targets) + len(original_ids) != len(tls):
        raise RuntimeError('Timeline count does not reconcile; refusing deletion')
    entry, page = project.GetCurrentTimeline(), r.GetCurrentPage()
    tc = entry.GetCurrentTimecode()
    folder = pool.GetCurrentFolder()
    counts = {row['ordinal']: {tr['kind']: max(x['index'] for x in row['tracks'] if x['kind'] == tr['kind'])
                               for tr in row['tracks']} for row in inventory['timelines']}
    baseline = {}
    for row, original in originals:
        project.SetCurrentTimeline(original)
        time.sleep(0.25)
        baseline[row['ordinal']] = contents(original, counts[row['ordinal']])
    result = {'dry_run': not args.apply, 'project_id': args.project_id,
              'draft_targets': sorted(t.GetName() for t in targets),
              'original_count': len(originals), 'deleted': [], 'status': 'planned'}
    report_path = ART / 'cleanup-timelines.json'
    if not args.apply:
        report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps({'dry_run': True, 'targets': len(targets), 'originals': len(originals)},
                         ensure_ascii=False), flush=True)
        return 0
    backups = ART / 'backups'
    backups.mkdir(exist_ok=True)
    backup = backups / ('before_draft-delete-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.drp')
    if not pm.SaveProject() or not pm.ExportProject(project.GetName(), str(backup), False):
        raise RuntimeError('Fresh backup failed; deleting nothing')
    with zipfile.ZipFile(backup) as archive:
        if archive.testzip() is not None:
            raise RuntimeError('Backup archive invalid; deleting nothing')
    result['backup'] = str(backup)
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    try:
        project.SetCurrentTimeline(originals[0][1])
        time.sleep(0.5)
        # Delete in small groups so a single failure cannot remove everything at once.
        for start in range(0, len(targets), 6):
            group = targets[start:start + 6]
            if not pool.DeleteTimelines(group):
                raise RuntimeError('DeleteTimelines returned False for group starting ' + str(start))
            result['deleted'].extend(t.GetName() for t in group)
            report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
            time.sleep(1.2)
            print('DELETED_GROUP', start // 6 + 1, flush=True)
        remaining = [project.GetTimelineByIndex(i) for i in range(1, project.GetTimelineCount() + 1)]
        live_ids = {t.GetUniqueId() for t in remaining}
        if live_ids != set(by_id):
            raise RuntimeError('Original ID set changed after deletion')
        if len(remaining) != len(originals):
            raise RuntimeError('Unexpected remaining timeline count')
        for row, original in originals:
            project.SetCurrentTimeline(original)
            time.sleep(0.25)
            if contents(original, counts[row['ordinal']]) != baseline[row['ordinal']]:
                raise RuntimeError('Original content changed: ordinal ' + str(row['ordinal']))
        if not pm.SaveProject():
            raise RuntimeError('SaveProject failed')
        result.update({'status': 'deleted_originals_verified', 'remaining_timelines': len(remaining),
                       'originals_verified': len(originals)})
    except Exception as exc:
        result['error'] = str(exc)
        result['status'] = 'partial_deletion_stopped'
        raise
    finally:
        project.SetCurrentTimeline(entry)
        time.sleep(0.5)
        if project.GetCurrentTimeline().GetUniqueId() == entry.GetUniqueId():
            entry.SetCurrentTimecode(tc)
            time.sleep(0.3)
        pool.SetCurrentFolder(folder)
        if r.GetCurrentPage() != page:
            r.OpenPage(page)
            time.sleep(1.0)
        result['restoration_verified'] = (project.GetCurrentTimeline().GetUniqueId() == entry.GetUniqueId()
            and entry.GetCurrentTimecode() == tc and r.GetCurrentPage() == page
            and pool.GetCurrentFolder().GetUniqueId() == folder.GetUniqueId())
        report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'deleted': len(result['deleted']), 'remaining': result.get('remaining_timelines'),
                      'restoration_verified': result['restoration_verified']}, ensure_ascii=False), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
