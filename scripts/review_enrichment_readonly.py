"""Read-only review inventory; no imports, renders, edits or project saves.
Run from repo root: python -m scripts.review_enrichment_readonly
Live MCP absent; GetTimelineByIndex API probe confirmed before creation.
"""
from __future__ import annotations
import json
import time
from datetime import datetime
from pathlib import Path
from scripts.resolve_common import connect_resolve

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.hermes' / 'artifacts' / 'enrichment-review-2026-10-06-live2'
ASSET_ROOTS = {
    'sfx': Path(r'G:\My Drive\Projects\2.1_sfx'),
    'bgm': Path(r'G:\My Drive\Projects\1.bgm'),
    'illustration': Path(r'G:\My Drive\Projects\3.gif'),
}

def read(obj, method, *args):
    if obj is None or method not in dir(obj):
        return {'unavailable': method}
    try:
        return getattr(obj, method)(*args)
    except Exception as exc:
        return {'error': type(exc).__name__, 'method': method}

def store(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str), encoding='utf-8')

def item_record(item):
    pool = read(item, 'GetMediaPoolItem')
    usable_pool = pool is not None and not isinstance(pool, dict)
    return {
        'id': read(item, 'GetUniqueId'), 'name': read(item, 'GetName'),
        'start': read(item, 'GetStart'), 'end': read(item, 'GetEnd'),
        'duration': read(item, 'GetDuration'),
        'source_start': read(item, 'GetSourceStartFrame'),
        'source_end': read(item, 'GetSourceEndFrame'),
        'left_offset': read(item, 'GetLeftOffset'),
        'right_offset': read(item, 'GetRightOffset'),
        'properties': read(item, 'GetProperty'),
        'media_id': read(pool, 'GetUniqueId') if usable_pool else None,
        'media_path': read(pool, 'GetClipProperty', 'File Path') if usable_pool else None,
        'media_fps': read(pool, 'GetClipProperty', 'FPS') if usable_pool else None,
        'media_resolution': read(pool, 'GetClipProperty', 'Resolution') if usable_pool else None,
        'pool_reference_status': 'available' if usable_pool else 'none_or_unavailable_not_offline_proof',
    }

def main():
    resolve = connect_resolve()
    if resolve is None:
        raise RuntimeError('Resolve connection unavailable')
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    if project is None:
        raise RuntimeError('No current project')
    required = ['GetTimelineCount', 'GetTimelineByIndex', 'GetCurrentTimeline', 'SetCurrentTimeline']
    if not all(m in dir(project) for m in required):
        raise RuntimeError('Missing required Project API')
    entry = project.GetCurrentTimeline()
    entry_tc = read(entry, 'GetCurrentTimecode')
    entry_id = read(entry, 'GetUniqueId')
    count = project.GetTimelineCount()
    targets = [project.GetTimelineByIndex(n) for n in range(1, count + 1)]
    ids = [read(t, 'GetUniqueId') for t in targets]
    if not all(isinstance(x, str) and x for x in ids) or len(set(ids)) != count:
        raise RuntimeError('Invalid or duplicate timeline IDs')
    session = {
        'captured_at': datetime.now().astimezone().isoformat(),
        'project_name': project.GetName(), 'project_id': read(project, 'GetUniqueId'),
        'resolve_build': read(resolve, 'GetVersion'),
        'active_timeline_id': entry_id, 'active_timecode': entry_tc,
        'page': read(resolve, 'GetCurrentPage'),
        'project_playback_fps': read(project, 'GetSetting', 'timelinePlaybackFrameRate'),
        'target_ids': ids,
        'route': 'scripting API; live MCP tools absent; read-only inventory',
    }
    store('session.json', session)
    rows = []
    try:
        for ordinal, timeline in enumerate(targets, 1):
            project.SetCurrentTimeline(timeline)
            time.sleep(0.25)
            actual = read(project.GetCurrentTimeline(), 'GetUniqueId')
            if actual != ids[ordinal - 1]:
                raise RuntimeError('Active timeline identity mismatch')
            row = {
                'ordinal': ordinal, 'timeline_id': actual, 'name': read(timeline, 'GetName'),
                'start': read(timeline, 'GetStartFrame'), 'end': read(timeline, 'GetEndFrame'),
                'start_timecode': read(timeline, 'GetStartTimecode'),
                'playhead': read(timeline, 'GetCurrentTimecode'),
                'record_fps': read(timeline, 'GetSetting', 'timelineFrameRate'),
                'width': read(timeline, 'GetSetting', 'timelineResolutionWidth'),
                'height': read(timeline, 'GetSetting', 'timelineResolutionHeight'),
                'tracks': [], 'review_status': 'metadata_only',
                'watched_ranges': [], 'heard_ranges': [],
            }
            for kind in ('video', 'audio', 'subtitle'):
                n_tracks = read(timeline, 'GetTrackCount', kind)
                if not isinstance(n_tracks, int):
                    row[kind + '_track_error'] = n_tracks
                    continue
                for index in range(1, n_tracks + 1):
                    items = read(timeline, 'GetItemListInTrack', kind, index)
                    row['tracks'].append({
                        'kind': kind, 'index': index,
                        'name': read(timeline, 'GetTrackName', kind, index),
                        'enabled': read(timeline, 'GetIsTrackEnabled', kind, index),
                        'locked': read(timeline, 'GetIsTrackLocked', kind, index),
                        'items': [item_record(x) for x in items] if isinstance(items, list) else [],
                        'read_error': items if isinstance(items, dict) else None,
                    })
            rows.append(row)
            store(f'timeline-{ordinal:02d}.json', row)
            store('inventory.json', {'schema_version': 1, 'project_name': session['project_name'],
                'timeline_count': count, 'timelines': rows, 'complete': len(rows) == count})
            print(f'Inventoried {ordinal}/{count}', flush=True)
        fresh = [read(project.GetTimelineByIndex(n), 'GetUniqueId')
                 for n in range(1, project.GetTimelineCount() + 1)]
        if set(fresh) != set(ids) or len(fresh) != count:
            raise RuntimeError('Timeline set changed during inventory')
    finally:
        if entry is not None:
            project.SetCurrentTimeline(entry)
            time.sleep(0.4)
            # Navigation never moved a playhead. Restore only if switching changed it.
            current = project.GetCurrentTimeline()
            current_tc = read(current, 'GetCurrentTimecode')
            if current_tc != entry_tc and isinstance(entry_tc, str):
                if 'SetCurrentTimecode' in dir(current):
                    current.SetCurrentTimecode(entry_tc)
                    time.sleep(0.3)
            restoration = {
                'timeline_id': read(project.GetCurrentTimeline(), 'GetUniqueId'),
                'timecode': read(project.GetCurrentTimeline(), 'GetCurrentTimecode'),
                'page': read(resolve, 'GetCurrentPage'),
            }
            restoration['verified'] = (restoration['timeline_id'] == entry_id
                and restoration['timecode'] == entry_tc and restoration['page'] == session['page'])
            store('restoration.json', restoration)
            print('Restoration verified:', restoration['verified'], flush=True)
    assets = []
    for kind, root in ASSET_ROOTS.items():
        for path in sorted(root.rglob('*')):
            if path.is_file():
                try:
                    assets.append({'kind': kind, 'path': str(path), 'name': path.name,
                        'extension': path.suffix.lower(), 'bytes': path.stat().st_size,
                        'rights_status': 'unknown', 'metadata_status': 'not_probed'})
                except OSError as exc:
                    assets.append({'kind': kind, 'path': str(path), 'error': type(exc).__name__})
    store('assets.json', {'assets': assets})
    print(json.dumps({'timelines': len(rows), 'assets': len(assets), 'output': str(OUT)}))

if __name__ == '__main__':
    main()
