"""Read-only anomaly sweep across every timeline. Reports, never fixes.
MCP-GAP: live Resolve MCP absent; uses shared connect_resolve and probed APIs.
No edits, no saves, no renders; navigation is captured and restored.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.resolve_common import connect_resolve

ART = ROOT / '.hermes/artifacts/enrichment-review-2026-10-06-live2'
GIF_HOLD_MIN, GIF_HOLD_MAX = 1.5, 2.5
VDO_KEYS = ('ZoomX', 'ZoomY', 'Pan', 'Tilt')


def surface(obj):
    return set(dir(obj)) if obj is not None else set()


def media_path(item, kind):
    # Native subtitle items legitimately have no Media Pool entry; that is not an anomaly.
    if 'GetMediaPoolItem' not in surface(item):
        return None, None if kind == 'subtitle' else 'no_GetMediaPoolItem'
    pool = item.GetMediaPoolItem()
    if pool is None:
        return None, None if kind == 'subtitle' else 'offline_or_no_pool_entry'
    if 'GetClipProperty' not in surface(pool):
        return None, 'no_GetClipProperty'
    return pool.GetClipProperty('File Path'), None


def main():
    inventory = json.loads((ART / 'inventory.json').read_text(encoding='utf-8'))
    style = json.loads((ART / 'vdo-current-project.json').read_text(encoding='utf-8'))['properties']
    r = connect_resolve()
    if r is None:
        raise RuntimeError('Resolve unavailable')
    project = r.GetProjectManager().GetCurrentProject()
    if project is None:
        raise RuntimeError('No current project')
    timelines = [project.GetTimelineByIndex(i) for i in range(1, project.GetTimelineCount() + 1)]
    by_id = {t.GetUniqueId(): t for t in timelines}
    entry, page = project.GetCurrentTimeline(), r.GetCurrentPage()
    entry_tc = entry.GetCurrentTimecode()
    findings = []
    per_timeline = []
    for row in inventory['timelines']:
        tl = by_id.get(row['timeline_id'])
        if tl is None:
            findings.append({'ordinal': row['ordinal'], 'severity': 'high', 'issue': 'timeline_missing'})
            continue
        project.SetCurrentTimeline(tl)
        time.sleep(0.22)
        if project.GetCurrentTimeline().GetUniqueId() != row['timeline_id']:
            findings.append({'ordinal': row['ordinal'], 'severity': 'high', 'issue': 'activation_failed'})
            continue
        name = tl.GetName()
        fps = float(tl.GetSetting('timelineFrameRate') or 0)
        start, end = tl.GetStartFrame(), tl.GetEndFrame()
        summary = {'ordinal': row['ordinal'], 'name': name, 'fps': fps, 'range': [start, end],
                   'tracks': {}, 'items': 0, 'issues': 0}
        if fps <= 0:
            findings.append({'ordinal': row['ordinal'], 'severity': 'high', 'issue': 'invalid_fps', 'value': fps})
        if tl.GetSetting('timelineResolutionWidth') != row['width'] or \
           tl.GetSetting('timelineResolutionHeight') != row['height']:
            findings.append({'ordinal': row['ordinal'], 'severity': 'medium', 'issue': 'raster_changed'})
        baseline = {(tr['kind'], tr['index']): tr for tr in row['tracks']}
        for kind in ('video', 'audio', 'subtitle'):
            count = tl.GetTrackCount(kind)
            for index in range(1, count + 1):
                items = tl.GetItemListInTrack(kind, index) or []
                label = f'{kind}{index}'
                track_name = tl.GetTrackName(kind, index)
                summary['tracks'][label] = {'name': track_name, 'count': len(items),
                                            'locked': tl.GetIsTrackLocked(kind, index),
                                            'enabled': tl.GetIsTrackEnabled(kind, index)}
                base = baseline.get((kind, index))
                if base is not None:
                    if len(items) < len(base['items']):
                        findings.append({'ordinal': row['ordinal'], 'severity': 'high',
                                         'issue': 'baseline_items_lost', 'track': label,
                                         'live': len(items), 'expected': len(base['items'])})
                    if track_name != base['name']:
                        findings.append({'ordinal': row['ordinal'], 'severity': 'low',
                                         'issue': 'track_renamed', 'track': label,
                                         'live': track_name, 'baseline': base['name']})
                seen = {}
                prev_end = None
                for item in items:
                    summary['items'] += 1
                    istart, iend = item.GetStart(), item.GetEnd()
                    iname = item.GetName()
                    if iend <= istart:
                        findings.append({'ordinal': row['ordinal'], 'severity': 'high',
                                         'issue': 'non_positive_duration', 'track': label,
                                         'name': iname, 'range': [istart, iend]})
                    if istart < start or iend > end:
                        findings.append({'ordinal': row['ordinal'], 'severity': 'high',
                                         'issue': 'outside_timeline_bounds', 'track': label,
                                         'name': iname, 'range': [istart, iend], 'bounds': [start, end]})
                    if prev_end is not None and istart < prev_end:
                        findings.append({'ordinal': row['ordinal'], 'severity': 'medium',
                                         'issue': 'overlapping_items', 'track': label,
                                         'name': iname, 'previous_end': prev_end, 'start': istart})
                    prev_end = max(prev_end or 0, iend)
                    key = (iname, istart)
                    if key in seen:
                        findings.append({'ordinal': row['ordinal'], 'severity': 'medium',
                                         'issue': 'duplicate_item', 'track': label, 'name': iname,
                                         'start': istart})
                    seen[key] = True
                    path, problem = media_path(item, kind)
                    if problem:
                        findings.append({'ordinal': row['ordinal'], 'severity': 'high',
                                         'issue': 'media_reference_problem', 'track': label,
                                         'name': iname, 'detail': problem})
                    elif path and not Path(path).exists():
                        findings.append({'ordinal': row['ordinal'], 'severity': 'high',
                                         'issue': 'media_file_missing', 'track': label,
                                         'name': iname, 'path': path})
                    if kind == 'video' and str(path or '').lower().endswith('.gif'):
                        hold = (iend - istart) / fps if fps else 0
                        if not GIF_HOLD_MIN <= hold <= GIF_HOLD_MAX:
                            findings.append({'ordinal': row['ordinal'], 'severity': 'medium',
                                             'issue': 'gif_hold_outside_approved_range', 'track': label,
                                             'name': iname, 'hold_seconds': round(hold, 3)})
                        props = item.GetProperty() or {}
                        diff = {k: (props.get(k), style[k]) for k in VDO_KEYS if props.get(k) != style[k]}
                        if diff:
                            findings.append({'ordinal': row['ordinal'], 'severity': 'medium',
                                             'issue': 'vdo_values_mismatch', 'track': label,
                                             'name': iname, 'diff': diff})
                    if kind == 'audio' and track_name.startswith('OFFLINE_DRAFT'):
                        props = item.GetProperty() or {}
                        if props.get('AudioVolumeEnabled') and float(props.get('AudioVolume') or 0) == 0.0:
                            findings.append({'ordinal': row['ordinal'], 'severity': 'medium',
                                             'issue': 'enrichment_audio_at_zero_db', 'track': label,
                                             'name': iname})
                if kind == 'audio' and track_name.startswith('OFFLINE_DRAFT_BGM') and items:
                    if len(items) != 1:
                        findings.append({'ordinal': row['ordinal'], 'severity': 'medium',
                                         'issue': 'bgm_not_single_item', 'track': label,
                                         'count': len(items)})
                    else:
                        if items[0].GetStart() != start or items[0].GetEnd() != end:
                            findings.append({'ordinal': row['ordinal'], 'severity': 'medium',
                                             'issue': 'bgm_does_not_cover_timeline', 'track': label,
                                             'range': [items[0].GetStart(), items[0].GetEnd()],
                                             'bounds': [start, end]})
        subtitle_tracks = summary['tracks'].get('subtitle1', {}).get('count')
        if subtitle_tracks is not None and row['tracks']:
            want = next((len(tr['items']) for tr in row['tracks']
                         if tr['kind'] == 'subtitle' and tr['index'] == 1), None)
            if want is not None and subtitle_tracks != want:
                findings.append({'ordinal': row['ordinal'], 'severity': 'medium',
                                 'issue': 'subtitle_count_changed', 'live': subtitle_tracks,
                                 'expected': want})
        if not any(v['name'].startswith('OFFLINE_DRAFT') for v in summary['tracks'].values()):
            findings.append({'ordinal': row['ordinal'], 'severity': 'medium',
                             'issue': 'no_enrichment_tracks_present'})
        summary['issues'] = sum(1 for f in findings if f['ordinal'] == row['ordinal'])
        per_timeline.append(summary)
    project.SetCurrentTimeline(entry)
    time.sleep(0.5)
    if entry.GetCurrentTimecode() != entry_tc:
        entry.SetCurrentTimecode(entry_tc)
        time.sleep(0.3)
    if r.GetCurrentPage() != page:
        r.OpenPage(page)
        time.sleep(1.0)
    report = {'project': project.GetName(), 'timelines_checked': len(per_timeline),
              'items_checked': sum(t['items'] for t in per_timeline),
              'findings': findings,
              'severity_counts': {sev: sum(1 for f in findings if f['severity'] == sev)
                                  for sev in ('high', 'medium', 'low')},
              'per_timeline': per_timeline,
              'restoration_verified': (project.GetCurrentTimeline().GetUniqueId() == entry.GetUniqueId()
                                       and r.GetCurrentPage() == page),
              'scope': 'structural/media-reference checks only; no visual, audio or rights QC'}
    (ART / 'anomaly-sweep.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'timelines_checked': report['timelines_checked'],
                      'items_checked': report['items_checked'],
                      'severity_counts': report['severity_counts'],
                      'restoration_verified': report['restoration_verified'],
                      'top_findings': findings[:12]}, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
