"""Verify saved review previews against live Resolve without edit/save/render.
MCP-GAP: live davinci-resolve catalog absent; GetTimelineByIndex probed.
"""
from __future__ import annotations
import json
import time
from datetime import datetime
from scripts.resolve_common import connect_resolve
from scripts.review_enrichment_readonly import OUT

# Probe each API surface once, not dir() for every field of every item.
_SURFACES = {}

def surface_read(obj, surface, method, *args):
    if obj is None:
        return {'unavailable': method}
    if surface not in _SURFACES:
        _SURFACES[surface] = set(dir(obj))
    if method not in _SURFACES[surface]:
        return {'unavailable': method}
    return getattr(obj, method)(*args)


def read(obj, method, *args):
    surface = 'resolve' if method in ('GetCurrentPage', 'GetVersion') else 'timeline'
    return surface_read(obj, surface, method, *args)


def item_record(item):
    def ir(method, *args):
        return surface_read(item, 'item', method, *args)
    pool = ir('GetMediaPoolItem')
    usable = pool is not None and not isinstance(pool, dict)
    def pr(method, *args):
        return surface_read(pool, 'pool', method, *args) if usable else None
    return {
        'id': ir('GetUniqueId'), 'name': ir('GetName'),
        'start': ir('GetStart'), 'end': ir('GetEnd'), 'duration': ir('GetDuration'),
        'source_start': ir('GetSourceStartFrame'), 'source_end': ir('GetSourceEndFrame'),
        'left_offset': ir('GetLeftOffset'), 'right_offset': ir('GetRightOffset'),
        'properties': ir('GetProperty'), 'media_id': pr('GetUniqueId'),
        'media_path': pr('GetClipProperty', 'File Path'),
        'media_fps': pr('GetClipProperty', 'FPS'),
        'media_resolution': pr('GetClipProperty', 'Resolution'),
        'pool_reference_status': 'available' if usable else 'none_or_unavailable_not_offline_proof',
    }


def main():
    saved = json.loads((OUT / 'inventory.json').read_text(encoding='utf-8'))
    resolve = connect_resolve()
    if resolve is None:
        raise RuntimeError('Resolve unavailable')
    project = resolve.GetProjectManager().GetCurrentProject()
    if project is None or project.GetName() != saved['project_name']:
        raise RuntimeError('Current project does not match review target')
    entry = project.GetCurrentTimeline()
    entry_id = read(entry, 'GetUniqueId')
    entry_tc = read(entry, 'GetCurrentTimecode')
    page = read(resolve, 'GetCurrentPage')
    (OUT / 'resume-entry.json').write_text(json.dumps({
        'project_name': project.GetName(), 'timeline_id': entry_id,
        'timecode': entry_tc, 'page': page,
        'captured_at': datetime.now().astimezone().isoformat()
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    expected = {row['timeline_id']: row for row in saved['timelines']}
    timelines = [project.GetTimelineByIndex(i) for i in range(1, project.GetTimelineCount() + 1)]
    live = {read(t, 'GetUniqueId'): t for t in timelines}
    if set(live) != set(expected) or len(live) != len(timelines):
        raise RuntimeError('Timeline identity set changed')
    differences = []
    checked = []
    try:
        for ident, old in expected.items():
            tl = live[ident]
            project.SetCurrentTimeline(tl)
            time.sleep(0.25)
            if read(project.GetCurrentTimeline(), 'GetUniqueId') != ident:
                raise RuntimeError('Active target mismatch')
            values = {
                'name': read(tl, 'GetName'), 'start': read(tl, 'GetStartFrame'),
                'end': read(tl, 'GetEndFrame'), 'record_fps': read(tl, 'GetSetting', 'timelineFrameRate'),
                'width': read(tl, 'GetSetting', 'timelineResolutionWidth'),
                'height': read(tl, 'GetSetting', 'timelineResolutionHeight'),
            }
            tracks = []
            for kind in ('video', 'audio', 'subtitle'):
                count = read(tl, 'GetTrackCount', kind)
                if not isinstance(count, int):
                    raise RuntimeError('Track count unavailable')
                for index in range(1, count + 1):
                    items = read(tl, 'GetItemListInTrack', kind, index)
                    if not isinstance(items, list):
                        raise RuntimeError('Track items unavailable')
                    tracks.append({
                        'kind': kind, 'index': index, 'name': read(tl, 'GetTrackName', kind, index),
                        'enabled': read(tl, 'GetIsTrackEnabled', kind, index),
                        'locked': read(tl, 'GetIsTrackLocked', kind, index),
                        'items': [item_record(item) for item in items], 'read_error': None,
                    })
            values['tracks'] = tracks
            changed = [key for key, value in values.items() if value != old[key]]
            preview = json.loads((OUT / f'preview-{old["ordinal"]:02d}.json').read_text(encoding='utf-8'))
            if preview['timeline_id'] != ident or not preview['structure_unchanged']:
                changed.append('preview_identity_or_structure')
            if changed:
                differences.append({'timeline_id': ident, 'ordinal': old['ordinal'], 'changed_fields': changed})
            checked.append(ident)
            print('CHECKED', old['ordinal'], 'MATCH' if not changed else changed, flush=True)
    finally:
        project.SetCurrentTimeline(entry)
        time.sleep(0.4)
        if read(entry, 'GetCurrentTimecode') != entry_tc:
            if 'SetCurrentTimecode' not in dir(entry):
                raise RuntimeError('Cannot restore timecode')
            entry.SetCurrentTimecode(entry_tc)
            time.sleep(0.3)
        restored = (read(project.GetCurrentTimeline(), 'GetUniqueId') == entry_id
                    and read(entry, 'GetCurrentTimecode') == entry_tc
                    and read(resolve, 'GetCurrentPage') == page)
        report = {'captured_at': datetime.now().astimezone().isoformat(),
                  'project_name': project.GetName(), 'resolve_build': read(resolve, 'GetVersion'),
                  'checked_ids': checked, 'differences': differences, 'restoration_verified': restored,
                  'all_match': len(checked) == len(expected) and not differences and restored,
                  'route': 'scripting API fallback; live MCP absent; no edits/save/render'}
        (OUT / 'resume-freshness.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    if not report['all_match']:
        raise RuntimeError('Preview freshness or restoration failed; see resume-freshness.json')
    print('RESUME VERIFIED', len(checked), flush=True)


if __name__ == '__main__':
    main()
