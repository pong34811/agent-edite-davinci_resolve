"""Apply approved BGM/SFX/GIF cue sheets to ORIGINAL timelines of aomimama-2026-09-p2.
MCP-GAP: davinci-resolve MCP has no verified bulk append-with-fades/gain/readback path for
this batch (MCP covered read-only timeline.list/get_current); uses shared connect_resolve.

Default is a dry run (validates live state against the saved inventory, no writes).
  --backup-only   export + verify a fresh .drp, record SHA-256, then stop.
  --apply         requires --ordinals; takes a fresh backup first, then writes.
Idempotent: a cue whose (asset basename, record start) already sits on its ENRICH_* track
is skipped. Original tracks are locked while writing and every original item is compared to
the saved baseline afterwards. No UI automation, SQL, render or source-media changes.
Run from repo root: python -m scripts.p2_apply_cues --cues <sample-cues.json> --ordinals 1,19,23
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import time
from datetime import datetime
from pathlib import Path

from scripts.backup_drp import export_verified
from scripts.resolve_common import connect_resolve, preserved_state
from scripts.apply_video_style import validate_style, apply_style_batch
from scripts.apply_vdo_python import validate_reference
from scripts.apply_offline_enrichment_pilot import source_frames, validate_range, pool_available_frames

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / '.hermes' / 'artifacts' / 'enrichment-p2-2026-10-09'
PROJECT_NAME = 'aomimama-2026-09-p2'
PROJECT_ID = 'b8a08265-8355-4d35-8dc8-21928b689051'
BIN_NAME = 'P2Enrichment_20261009'
TRACKS = {'bgm': ('audio', 'ENRICH_BGM'), 'sfx': ('audio', 'ENRICH_SFX'), 'gif': ('video', 'ENRICH_GIF')}
ENRICH_LABELS = {label for _, label in TRACKS.values()}
PAUSE = 1.2


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding='utf-8')


def original_signature(tl):
    """Per-track (name, enabled, [(item name, start, end)]) for tracks that are not ENRICH_*."""
    rows = []
    for kind in ('video', 'audio', 'subtitle'):
        for k in range(1, tl.GetTrackCount(kind) + 1):
            name = tl.GetTrackName(kind, k)
            if name in ENRICH_LABELS:
                continue
            items = [(i.GetName(), i.GetStart(), i.GetEnd()) for i in (tl.GetItemListInTrack(kind, k) or [])]
            rows.append([kind, k, name, bool(tl.GetIsTrackEnabled(kind, k)), items])
    return rows


def saved_signature(saved):
    return [[t['kind'], t['index'], t['name'], bool(t['enabled']),
             [(i['name'], i['start'], i['end']) for i in t['items']]]
            for t in saved['tracks'] if t['name'] not in ENRICH_LABELS]


def jobs_for(row):
    fps = row['fps']
    bgm = row['bgm']
    jobs = [{'kind': 'bgm', 'path': bgm['path'], 'at': row['start'], 'duration': row['end'] - row['start'],
             'gain': bgm['gain_db'], 'fade_in': bgm['fade_in_frames'], 'fade_out': bgm['fade_out_frames']}]
    for c in row['cues']:
        job = {'kind': c['kind'], 'path': c['path'], 'at': c['record_start'],
               'duration': c['record_end'] - c['record_start']}
        if c['kind'] == 'sfx':
            job.update(gain=c['gain_db'], fade_in=0, fade_out=min(round(0.15 * fps), job['duration']))
        jobs.append(job)
    for j in jobs:
        if j['kind'] != 'gif' and j['gain'] is None:
            raise ValueError('Missing measured gain for ' + j['path'])
        validate_range(row['start'], row['end'], j['at'], j['duration'])
        if j['kind'] == 'gif' and not round(1.5 * fps) - 3 <= j['duration'] <= round(2.5 * fps) + 3:
            raise ValueError('GIF hold outside 1.5-2.5s: ' + j['path'])
    return jobs


def activate(project, tl):
    project.SetCurrentTimeline(tl)
    time.sleep(0.5)
    if project.GetCurrentTimeline().GetUniqueId() != tl.GetUniqueId():
        raise RuntimeError('Timeline activation mismatch')


def ensure_track(tl, kind, label):
    for k in range(1, tl.GetTrackCount(kind) + 1):
        if tl.GetTrackName(kind, k) == label:
            return k
    if not tl.AddTrack(kind):
        raise RuntimeError('AddTrack failed: ' + label)
    time.sleep(PAUSE)
    k = tl.GetTrackCount(kind)
    tl.SetTrackName(kind, k, label)
    if tl.GetTrackName(kind, k) != label:
        raise RuntimeError('Track name readback failed: ' + label)
    return k


def existing_keys(tl, kind, index):
    return {(Path(i.GetMediaPoolItem().GetClipProperty('File Path')).name.casefold(), i.GetStart())
            for i in (tl.GetItemListInTrack(kind, index) or []) if i.GetMediaPoolItem() is not None}


def import_asset(mp, folder, path):
    match = [x for x in folder.GetClipList()
             if str(Path(x.GetClipProperty('File Path'))).casefold() == str(Path(path)).casefold()]
    if len(match) > 1:
        raise RuntimeError('Duplicate bin asset; reconcile manually: ' + path)
    loaded = match or mp.ImportMedia([path])
    time.sleep(PAUSE)
    if not loaded or len(loaded) != 1:
        raise RuntimeError('Import failed: ' + path)
    pool = loaded[0]
    fps = float(pool.GetClipProperty('FPS'))
    return pool, fps, pool_available_frames(pool, fps)


def apply_timeline(project, pm, mp, folder, tl, row, saved, style, report):
    fps = float(tl.GetSetting('timelineFrameRate'))
    if abs(fps - row['fps']) > 1e-6 or tl.GetStartFrame() != row['start'] or tl.GetEndFrame() != row['end']:
        raise RuntimeError('Live timeline differs from cue sheet bounds/fps')
    validate_reference(style, PROJECT_ID, [tl.GetSetting('timelineResolutionWidth'), tl.GetSetting('timelineResolutionHeight')])
    baseline = original_signature(tl)
    if json.loads(json.dumps(baseline)) != json.loads(json.dumps(saved_signature(saved))):
        raise RuntimeError('Live originals differ from saved baseline; refresh inventory first')
    jobs = jobs_for(row)
    todo, done = [], []
    for j in jobs:
        kind, label = TRACKS[j['kind']]
        idx = next((k for k in range(1, tl.GetTrackCount(kind) + 1) if tl.GetTrackName(kind, k) == label), None)
        have = existing_keys(tl, kind, idx) if idx else set()
        (done if (Path(j['path']).name.casefold(), j['at']) in have else todo).append(j)
    report['already_present'] = [Path(j['path']).name for j in done]
    if not todo:
        return
    locks = []
    try:
        pools = {}
        for j in todo:
            pool, mfps, avail = import_asset(mp, folder, j['path'])
            n = source_frames(j['duration'], fps, mfps)
            if n > avail:
                raise RuntimeError('Asset too short for planned range: ' + j['path'])
            pools[j['path']] = (pool, n)
        tracks = {k: ensure_track(tl, *TRACKS[k]) for k in {j['kind'] for j in todo}}
        for kind in ('video', 'audio', 'subtitle'):
            for k in range(1, tl.GetTrackCount(kind) + 1):
                if tl.GetTrackName(kind, k) not in ENRICH_LABELS:
                    locks.append((kind, k, tl.GetIsTrackLocked(kind, k)))
                    tl.SetTrackLock(kind, k, True)
        for j in todo:
            pool, n = pools[j['path']]
            got = mp.AppendToTimeline([{'mediaPoolItem': pool, 'startFrame': 0, 'endFrame': n,
                                        'mediaType': 1 if j['kind'] == 'gif' else 2,
                                        'trackIndex': tracks[j['kind']], 'recordFrame': j['at']}])
            time.sleep(PAUSE)
            if not got or len(got) != 1:
                raise RuntimeError('Append failed; inspect before retry: ' + j['path'])
            clip = got[0]
            rec = {'kind': j['kind'], 'path': j['path'], 'item_id': clip.GetUniqueId(),
                   'start': clip.GetStart(), 'end': clip.GetEnd(), 'expected_start': j['at'],
                   'expected_end': j['at'] + j['duration']}
            report['inserted'].append(rec)
            actual = clip.GetEnd() - clip.GetStart()
            if clip.GetStart() != j['at'] or clip.GetEnd() > row['end'] or abs(actual - j['duration']) > 3:
                raise RuntimeError('Append range mismatch: ' + j['path'])
            if j['kind'] == 'bgm' and (clip.GetStart() != row['start'] or clip.GetEnd() != row['end']):
                raise RuntimeError('BGM must cover the exact timeline')
            if j['kind'] == 'gif':
                apply_style_batch([clip], style, [clip.GetUniqueId()], apply=True)
            else:
                clip.SetProperty('AudioVolume', float(j['gain']))
                if abs(float(clip.GetProperty('AudioVolume')) - j['gain']) > 0.01:
                    raise RuntimeError('Audio gain readback failed: ' + j['path'])
                fades = {'FadeIn': j['fade_in'], 'FadeOut': j['fade_out']}
                clip.SetFades(fades)
                if clip.GetFades() != fades:
                    raise RuntimeError('Fade readback mismatch: ' + j['path'])
        for kind, k, state in locks:
            tl.SetTrackLock(kind, k, state)
        locks.clear()
        after = original_signature(tl)
        if json.loads(json.dumps(after)) != json.loads(json.dumps(baseline)) or tl.GetEndFrame() != row['end']:
            raise RuntimeError('Original content changed during apply')
        if not pm.SaveProject():
            raise RuntimeError('SaveProject failed')
        report['status'] = 'applied_saved'
    finally:
        for kind, k, state in locks:
            tl.SetTrackLock(kind, k, state)


def do_backup(pm, project):
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    path = ART / 'backups' / f'pre-enrichment-{stamp}.drp'
    size = export_verified(pm, project, path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    info = {'backup': str(path), 'bytes': size, 'sha256': digest, 'project': project.GetName(),
            'project_id': project.GetUniqueId(), 'restore_tested': False}
    write_json(ART / 'backups' / f'pre-enrichment-{stamp}.json', info)
    return info


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cues', type=Path, default=ART / 'sample-cues.json')
    ap.add_argument('--style-json', type=Path, default=ART / 'vdo-p2.json')
    ap.add_argument('--ordinals', help='e.g. 1,19,23 (required for --apply)')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--backup-only', action='store_true')
    args = ap.parse_args(argv)
    if args.apply and not args.ordinals:
        ap.error('--apply requires explicit --ordinals; no implicit all-timeline writes')
    cues = json.loads(args.cues.read_text(encoding='utf-8'))
    inventory = json.loads((ART / 'inventory.json').read_text(encoding='utf-8'))
    rows = cues['timelines']
    if args.ordinals:
        wanted = {int(x) for x in args.ordinals.split(',')}
        rows = [r for r in rows if r['ordinal'] in wanted]
        if {r['ordinal'] for r in rows} != wanted:
            raise ValueError('Requested ordinal missing from cue sheet')
    for r in rows:
        if r['problems']:
            raise ValueError('Cue sheet has unresolved problems for ordinal %s' % r['ordinal'])
    style = json.loads(args.style_json.read_text(encoding='utf-8'))
    validate_style(style)
    resolve = connect_resolve()
    if resolve is None:
        raise RuntimeError('Resolve unavailable')
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    if project is None or project.GetName() != PROJECT_NAME or project.GetUniqueId() != PROJECT_ID:
        raise RuntimeError('Exact project mismatch')
    if project.IsRenderingInProgress():
        raise RuntimeError('Render in progress')
    result = {'dry_run': not args.apply, 'project_id': PROJECT_ID, 'timelines': [],
              'vdo_provenance': style.get('provenance_limit')}
    if args.backup_only:
        result['backup'] = do_backup(pm, project)
        write_json(ART / 'backup-latest.json', result['backup'])
        print(json.dumps(result['backup'], ensure_ascii=False, indent=2))
        return 0
    by_id = {project.GetTimelineByIndex(i).GetUniqueId(): project.GetTimelineByIndex(i)
             for i in range(1, project.GetTimelineCount() + 1)}
    mp = project.GetMediaPool()
    with preserved_state(resolve):
        if args.apply:
            result['backup'] = do_backup(pm, project)
            write_json(ART / 'backup-latest.json', result['backup'])
        folder = None
        if args.apply:
            root = mp.GetRootFolder()
            folder = next((f for f in root.GetSubFolderList() if f.GetName() == BIN_NAME), None) \
                or mp.AddSubFolder(root, BIN_NAME)
            time.sleep(PAUSE)
            if folder is None or not mp.SetCurrentFolder(folder):
                raise RuntimeError('Task bin unavailable')
        for row in rows:
            tl = by_id.get(row['timeline_id'])
            if tl is None:
                raise RuntimeError('Timeline ID missing live: ' + row['timeline_id'])
            report = {'ordinal': row['ordinal'], 'timeline_id': row['timeline_id'], 'name': row['name'],
                      'status': 'dry_run_ok', 'inserted': []}
            result['timelines'].append(report)
            activate(project, tl)
            saved = inventory['timelines'][row['ordinal'] - 1]
            if saved['timeline_id'] != row['timeline_id']:
                raise RuntimeError('Inventory ordinal/ID mismatch')
            if args.apply:
                try:
                    apply_timeline(project, pm, mp, folder, tl, row, saved, style, report)
                except Exception as exc:
                    report.update(status='failed_inspect_before_retry', error=str(exc))
                    raise
                finally:
                    write_json(ART / 'apply-report.json', result)
            else:
                fps = float(tl.GetSetting('timelineFrameRate'))
                if tl.GetStartFrame() != row['start'] or tl.GetEndFrame() != row['end'] or fps != row['fps']:
                    raise RuntimeError('Live bounds differ from cue sheet')
                if json.loads(json.dumps(original_signature(tl))) != json.loads(json.dumps(saved_signature(saved))):
                    raise RuntimeError('Live originals differ from saved baseline')
                report['planned'] = [{'kind': j['kind'], 'file': Path(j['path']).name, 'at': j['at'],
                                      'frames': j['duration'], 'gain': j.get('gain')} for j in jobs_for(row)]
    write_json(ART / ('apply-report.json' if args.apply else 'dry-run-report.json'), result)
    print(json.dumps({'dry_run': result['dry_run'], 'timelines': [
        {k: t[k] for k in ('ordinal', 'status')} | {'items': len(t.get('planned', t['inserted']))}
        for t in result['timelines']]}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
