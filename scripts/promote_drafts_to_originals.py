"""Promote approved draft enrichment into the ORIGINAL timelines, preserving IDs.
Reads each draft copy, replicates its added items onto the matching original, then
verifies the original equals the draft while every baseline item is untouched.
MCP-GAP: live Resolve MCP absent; uses shared connect_resolve and probed APIs.
Default dry-run. Requires a fresh verified .drp first. No UI automation, no DB edits.
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
from scripts.apply_video_style import capture_style, set_properties

ART = ROOT / '.hermes/artifacts/enrichment-review-2026-10-06-live2'
SUFFIX = ' [ENRICHMENT DRAFT OFFLINE]'


def baseline_tracks(row):
    return [{'kind': tr['kind'], 'index': tr['index'], 'name': tr['name'], 'enabled': tr['enabled'],
             'items': [{k: v for k, v in x.items() if k != 'id'} for x in tr['items']]}
            for tr in row['tracks']]


def counts_for(row):
    counts = {}
    for tr in row['tracks']:
        counts[tr['kind']] = max(counts.get(tr['kind'], 0), tr['index'])
    return counts


def added_items(copy_tl, row):
    base = {(tr['kind'], x['name'], x['start']) for tr in row['tracks'] for x in tr['items']}
    out = []
    for kind in ('video', 'audio', 'subtitle'):
        for k in range(1, copy_tl.GetTrackCount(kind) + 1):
            for item in copy_tl.GetItemListInTrack(kind, k) or []:
                if (kind, item.GetName(), item.GetStart()) in base:
                    continue
                out.append({'kind': kind, 'track_name': copy_tl.GetTrackName(kind, k), 'item': item})
    return out


def ensure_track(target, kind, name):
    for k in range(1, target.GetTrackCount(kind) + 1):
        if target.GetTrackName(kind, k) == name:
            return k
    if not target.AddTrack(kind):
        raise RuntimeError('AddTrack failed for ' + kind)
    time.sleep(1.2)
    index = target.GetTrackCount(kind)
    target.SetTrackName(kind, index, name)
    return index


def activate(project, timeline):
    project.SetCurrentTimeline(timeline)
    time.sleep(0.5)
    if project.GetCurrentTimeline().GetUniqueId() != timeline.GetUniqueId():
        raise RuntimeError('Activation mismatch')


def promote(r, project, row, copy_tl, dry_run):
    report_path = ART / 'promotion' / f'{row["ordinal"]:02d}.json'
    original = next(project.GetTimelineByIndex(i) for i in range(1, project.GetTimelineCount() + 1)
                    if project.GetTimelineByIndex(i).GetUniqueId() == row['timeline_id'])
    report = {'ordinal': row['ordinal'], 'original_id': row['timeline_id'], 'original_name': row['name'],
              'copy_id': copy_tl.GetUniqueId(), 'status': 'planned', 'added': [], 'existing': []}
    activate(project, original)
    counts = counts_for(row)
    if contents(original, counts) != baseline_tracks(row):
        raise RuntimeError('Original changed since baseline; refusing promotion')
    plan = []
    for entry in added_items(copy_tl, row):
        item = entry['item']
        pool = item.GetMediaPoolItem()
        if pool is None:
            raise RuntimeError('Draft item without Media Pool entry: ' + item.GetName())
        plan.append({'kind': entry['kind'], 'track_name': entry['track_name'], 'name': item.GetName(),
                     'media_id': pool.GetUniqueId(), 'media_path': pool.GetClipProperty('File Path'),
                     'record': item.GetStart(), 'source_start': item.GetSourceStartFrame(),
                     'source_end': item.GetSourceEndFrame(), 'duration': item.GetEnd() - item.GetStart(),
                     'volume': item.GetProperty('AudioVolume') if entry['kind'] == 'audio' else None,
                     'fades': item.GetFades() if entry['kind'] == 'audio' else None,
                     'style': capture_style(item)['properties'] if entry['kind'] == 'video' else None})
    report['plan'] = plan
    report['status'] = 'dry_run' if dry_run else 'applying'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    if dry_run:
        return report
    before = contents(original, counts)
    # Idempotent rerun: reuse only a fully promoted, verified original.
    already = {(a['name'], a['record']) for a in report.get('added', [])} if report.get('status') == 'promoted_verified' else set()
    if report_path.exists():
        previous = json.loads(report_path.read_text(encoding='utf-8'))
        if previous.get('status') == 'promoted_verified':
            already = {(a['name'], a['record']) for a in previous.get('added', [])}
    plan = [p for p in plan if (p['name'], p['record']) not in already]
    report['plan'] = plan
    pool_media = project.GetMediaPool()
    locks = []
    try:
        for kind in counts:
            for k in range(1, counts[kind] + 1):
                locks.append((kind, k, original.GetIsTrackLocked(kind, k)))
                original.SetTrackLock(kind, k, True)
        for entry in plan:
            kind = entry['kind']
            index = ensure_track(original, kind, entry['track_name'])
            existing = [x for x in (original.GetItemListInTrack(kind, index) or [])
                        if x.GetName() == entry['name'] and x.GetStart() == entry['record']]
            if existing:
                report['existing'].append({'name': entry['name'], 'record': entry['record']})
                continue
            media = None
            for folder in [pool_media.GetRootFolder()] + list(pool_media.GetRootFolder().GetSubFolderList()):
                media = next((x for x in folder.GetClipList() if x.GetUniqueId() == entry['media_id']), None)
                if media:
                    break
            if media is None:
                raise RuntimeError('Draft media not in pool: ' + str(entry['media_path']))
            result = pool_media.AppendToTimeline([{'mediaPoolItem': media, 'startFrame': entry['source_start'],
                'endFrame': entry['source_end'], 'mediaType': 1 if kind == 'video' else 2,
                'trackIndex': index, 'recordFrame': entry['record']}])
            time.sleep(1.2)
            if not result or len(result) != 1:
                raise RuntimeError('Append failed for ' + entry['name'])
            clip = result[0]
            if clip.GetStart() != entry['record'] or abs((clip.GetEnd() - clip.GetStart()) - entry['duration']) > 3:
                raise RuntimeError('Record/source range mismatch for ' + entry['name']
                                   + f' got {clip.GetStart()}-{clip.GetEnd()} want {entry["record"]}'
                                   + f'-{entry["record"] + entry["duration"]}')
            # Resolve can conform a GIF by a couple of frames; re-verify the hold rule on the real range.
            if kind == 'video' and not 1.5 <= (clip.GetEnd() - clip.GetStart()) / float(original.GetSetting('timelineFrameRate')) <= 2.5:
                raise RuntimeError('Conformed GIF hold outside approved range: ' + entry['name'])
            if kind == 'video':
                set_properties(clip, entry['style'])
            else:
                clip.SetProperty('AudioVolume', float(entry['volume']))
                if abs(float(clip.GetProperty('AudioVolume')) - entry['volume']) > 0.01:
                    raise RuntimeError('Volume readback failed')
                clip.SetFades(entry['fades'])
                if clip.GetFades() != entry['fades']:
                    raise RuntimeError('Fade readback failed')
            report['added'].append({'name': entry['name'], 'record': entry['record'],
                                    'track': f'{kind}{index}', 'item_id': clip.GetUniqueId()})
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        if original.GetEndFrame() != row['end']:
            raise RuntimeError('Original duration changed')
        after = contents(original, counts)
        baseline_names = {(tr['kind'], x['name'], x['start']) for tr in row['tracks'] for x in tr['items']}
        for track in after:
            for item in track['items']:
                if (track['kind'], item['name'], item['start']) in baseline_names:
                    continue
                if not any(a['name'] == item['name'] and a['record'] == item['start'] for a in report['added']):
                    raise RuntimeError('Unexpected item on original: ' + item['name'])
        for tr in row['tracks']:
            live = [x for x in after if x['kind'] == tr['kind'] and x['index'] == tr['index']]
            if len(live) != 1:
                raise RuntimeError('Original track layout changed')
            if [{k: v for k, v in x.items() if k != 'id'} for x in live[0]['items']] != \
               [{k: v for k, v in x.items() if k != 'id'} for x in tr['items']]:
                raise RuntimeError('Baseline track content changed: ' + tr['kind'] + str(tr['index']))
        report['status'] = 'promoted_verified'
    except Exception as exc:
        report['error'] = str(exc)
        report['status'] = 'partial_original_do_not_blindly_retry'
        raise
    finally:
        for kind, k, state in locks:
            original.SetTrackLock(kind, k, state)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument('--all', action='store_true')
    group.add_argument('--ordinals', help='e.g. 2,3')
    ap.add_argument('--project-id', required=True)
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args(argv)
    inventory = json.loads((ART / 'inventory.json').read_text(encoding='utf-8'))
    pilot = json.loads((ART / 'pilot-offline-01.json').read_text(encoding='utf-8'))
    rows = inventory['timelines']
    if args.ordinals:
        wanted = {int(x) for x in args.ordinals.split(',')}
        rows = [t for t in rows if t['ordinal'] in wanted]
        if {t['ordinal'] for t in rows} != wanted:
            raise ValueError('Requested ordinal missing from inventory')
    r = connect_resolve()
    if r is None:
        raise RuntimeError('Resolve unavailable')
    pm = r.GetProjectManager()
    project = pm.GetCurrentProject()
    if project is None or project.GetUniqueId() != args.project_id:
        raise RuntimeError('Project ID mismatch')
    if project.IsRenderingInProgress():
        raise RuntimeError('Render in progress')
    timelines = [project.GetTimelineByIndex(i) for i in range(1, project.GetTimelineCount() + 1)]
    by_id = {t.GetUniqueId(): t for t in timelines}
    copies = {}
    for row in rows:
        if row['ordinal'] == 1:
            copies[row['timeline_id']] = by_id.get(pilot['pilot_id'])
        else:
            copies[row['timeline_id']] = next((t for t in timelines
                                               if t.GetName() == row['name'] + SUFFIX), None)
        if copies[row['timeline_id']] is None:
            raise RuntimeError('Draft copy missing for ordinal ' + str(row['ordinal']))
        if row['timeline_id'] not in by_id:
            raise RuntimeError('Original missing for ordinal ' + str(row['ordinal']))
    entry, page = project.GetCurrentTimeline(), r.GetCurrentPage()
    entry_tc = entry.GetCurrentTimecode()
    pool = project.GetMediaPool()
    folder = pool.GetCurrentFolder()
    result = {'dry_run': not args.apply, 'project_id': args.project_id, 'rows': len(rows), 'reports': []}
    report_path = ART / 'promotion' / 'last-run.json'
    try:
        if args.apply:
            backups = ART / 'backups'
            backups.mkdir(exist_ok=True)
            backup = backups / ('before_promotion_' + datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.drp')
            if not pm.SaveProject() or not pm.ExportProject(project.GetName(), str(backup), False):
                raise RuntimeError('Fresh pre-promotion backup failed')
            with zipfile.ZipFile(backup) as archive:
                if archive.testzip() is not None:
                    raise RuntimeError('Backup archive failed validation')
            result['backup'] = str(backup)
        for row in rows:
            result['reports'].append(promote(r, project, row, copies[row['timeline_id']], not args.apply))
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
            print('PROMOTION_PROGRESS', row['ordinal'], flush=True)
        if args.apply and not pm.SaveProject():
            raise RuntimeError('SaveProject failed')
        result['saved'] = bool(args.apply)
    finally:
        activate(project, entry)
        entry.SetCurrentTimecode(entry_tc)
        time.sleep(0.3)
        pool.SetCurrentFolder(folder)
        if r.GetCurrentPage() != page:
            r.OpenPage(page)
            time.sleep(1.0)
        result['restoration_verified'] = (project.GetCurrentTimeline().GetUniqueId() == entry.GetUniqueId()
            and entry.GetCurrentTimecode() == entry_tc and r.GetCurrentPage() == page
            and pool.GetCurrentFolder().GetUniqueId() == folder.GetUniqueId())
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        if not result['restoration_verified']:
            raise RuntimeError('Working state restoration failed')
    print('PROMOTION_DONE', len(result['reports']), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
