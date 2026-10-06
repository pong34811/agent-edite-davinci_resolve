"""Read-only audit after promotion: originals must equal their drafts, baseline intact."""
import json
import time
from pathlib import Path
from scripts.resolve_common import connect_resolve

ART = Path(__file__).resolve().parents[1] / '.hermes/artifacts/enrichment-review-2026-10-06-live2'
SUFFIX = ' [ENRICHMENT DRAFT OFFLINE]'
KEYS = ('name', 'start', 'end', 'source_start', 'source_end', 'track')


def added_from_report(row):
    report = json.loads((ART / 'promotion' / f'{row["ordinal"]:02d}.json').read_text(encoding='utf-8'))
    return {(a['name'], a['record']) for a in report.get('added', [])}


def track_items(tl, kind, index):
    out = []
    for item in tl.GetItemListInTrack(kind, index) or []:
        media = item.GetMediaPoolItem()
        out.append({'name': item.GetName(), 'start': item.GetStart(), 'end': item.GetEnd(),
                    'source_start': item.GetSourceStartFrame(), 'source_end': item.GetSourceEndFrame(),
                    'track': f'{kind}{index}',
                    'path': str(Path(media.GetClipProperty('File Path')).name) if media else None,
                    'volume': item.GetProperty('AudioVolume') if kind == 'audio' else None,
                    'fades': item.GetFades() if kind == 'audio' else None,
                    'zoom': item.GetProperty('ZoomX') if kind == 'video' else None})
    return out


def main():
    inv = json.loads((ART / 'inventory.json').read_text(encoding='utf-8'))
    pilot = json.loads((ART / 'pilot-offline-01.json').read_text(encoding='utf-8'))
    r = connect_resolve()
    if r is None:
        raise RuntimeError('Resolve unavailable')
    p = r.GetProjectManager().GetCurrentProject()
    tls = [p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1)]
    by_id = {t.GetUniqueId(): t for t in tls}
    entry, page = p.GetCurrentTimeline(), r.GetCurrentPage()
    tc = entry.GetCurrentTimecode()
    problems, checked = [], []
    for row in inv['timelines']:
        original = by_id.get(row['timeline_id'])
        if original is None:
            problems.append({'ordinal': row['ordinal'], 'issue': 'original_missing'})
            continue
        draft = by_id.get(pilot['pilot_id']) if row['ordinal'] == 1 else \
            next((t for t in tls if t.GetName() == row['name'] + SUFFIX), None)
        p.SetCurrentTimeline(original)
        time.sleep(0.25)
        if original.GetStartFrame() != row['start'] or original.GetEndFrame() != row['end']:
            problems.append({'ordinal': row['ordinal'], 'issue': 'bounds_changed'})
        # baseline tracks must be byte-for-byte identical in content
        for tr in row['tracks']:
            live = track_items(original, tr['kind'], tr['index'])
            want = [{'name': x['name'], 'start': x['start'], 'end': x['end'],
                     'source_start': x['source_start'], 'source_end': x['source_end'],
                     'track': f"{tr['kind']}{tr['index']}",
                     'path': Path(x['media_path']).name if x['media_path'] else None,
                     'volume': x['properties'].get('AudioVolume') if tr['kind'] == 'audio' else None,
                     'fades': x.get('fades'),
                     'zoom': x['properties'].get('ZoomX') if tr['kind'] == 'video' else None}
                    for x in tr['items']]
            if len(live) != len(want):
                problems.append({'ordinal': row['ordinal'], 'issue': 'baseline_item_count',
                                 'track': f"{tr['kind']}{tr['index']}", 'live': len(live), 'want': len(want)})
                continue
            for a, b in zip(live, want):
                for key in KEYS:
                    if a[key] != b[key]:
                        problems.append({'ordinal': row['ordinal'], 'issue': 'baseline_item_changed',
                                         'track': a['track'], 'key': key, 'live': a[key], 'want': b[key]})
        # every promoted item must exist with the recorded record frame
        added = added_from_report(row) if row['ordinal'] != 1 else \
            {(i['kind'], i['start']) for i in []} or set()
        if row['ordinal'] == 1:
            added = {(x['name'], x['start']) for x in [json.loads((ART / 'pilot-offline-01.json')
                                                              .read_text(encoding='utf-8'))] for x in []} or set()
        present = {(i['name'], i['start']) for kind in ('video', 'audio')
                   for index in range(1, original.GetTrackCount(kind) + 1)
                   for i in track_items(original, kind, index)}
        report = json.loads((ART / 'promotion' / f'{row["ordinal"]:02d}.json').read_text(encoding='utf-8')) \
            if (ART / 'promotion' / f'{row["ordinal"]:02d}.json').exists() else None
        if report:
            for a in report.get('added', []):
                if (a['name'], a['record']) not in present:
                    problems.append({'ordinal': row['ordinal'], 'issue': 'promoted_item_missing',
                                     'name': a['name'], 'record': a['record']})
            for e in report.get('existing', []):
                if (e['name'], e['record']) not in present:
                    problems.append({'ordinal': row['ordinal'], 'issue': 'reused_item_missing',
                                     'name': e['name'], 'record': e['record']})
        checked.append(row['ordinal'])
    p.SetCurrentTimeline(entry)
    time.sleep(0.5)
    if entry.GetCurrentTimecode() != tc:
        entry.SetCurrentTimecode(tc)
        time.sleep(0.3)
    if r.GetCurrentPage() != page:
        r.OpenPage(page)
        time.sleep(1.0)
    result = {'checked_ordinals': len(checked), 'problems': problems,
              'restoration_verified': (p.GetCurrentTimeline().GetUniqueId() == entry.GetUniqueId()
                                       and r.GetCurrentPage() == page),
              'scope': 'baseline content/bounds and promoted-item presence; not visual or listening QC'}
    (ART / 'promotion' / 'audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'checked': len(checked), 'problems': len(problems),
                      'restoration_verified': result['restoration_verified'],
                      'sample': problems[:5]}, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
