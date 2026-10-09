"""Independent read-only verification of p2 enrichment against baseline and cue sheets.
Run from repo root: python -m scripts.p2_verify_all
Checks per timeline: original tracks/items unchanged, ENRICH_* items match the cue sheet
exactly (no missing/extra/duplicate), BGM covers the timeline, gains/fades, GIF vdo values,
original tracks unlocked, active timeline/playhead/page restored.
"""
from __future__ import annotations
import json
import math
import time
from pathlib import Path

from scripts.resolve_common import connect_resolve, preserved_state
from scripts.p2_apply_cues import ART, PROJECT_ID, TRACKS, original_signature, saved_signature

ZOOM = 0.5


def main():
    inv = json.loads((ART / 'inventory.json').read_text(encoding='utf-8'))
    rows = {r['ordinal']: r for f in ('sample-cues.json', 'all-cues.json')
            for r in json.loads((ART / f).read_text(encoding='utf-8'))['timelines']}
    r = connect_resolve()
    pm = r.GetProjectManager()
    p = pm.GetCurrentProject()
    assert p.GetUniqueId() == PROJECT_ID, 'project mismatch'
    by = {p.GetTimelineByIndex(i).GetUniqueId(): p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1)}
    entry = p.GetCurrentTimeline()
    entry_id, entry_tc, page = entry.GetUniqueId(), entry.GetCurrentTimecode(), r.GetCurrentPage()
    report = {'timeline_count': len(by), 'results': []}
    with preserved_state(r):
        for s in inv['timelines']:
            o = s['ordinal']
            tl = by[s['timeline_id']]
            p.SetCurrentTimeline(tl)
            time.sleep(0.4)
            row, bad = rows[o], []
            if json.loads(json.dumps(original_signature(tl))) != json.loads(json.dumps(saved_signature(s))):
                bad.append('original tracks/items differ from baseline')
            if tl.GetEndFrame() != s['end'] or tl.GetStartFrame() != s['start']:
                bad.append('timeline bounds changed')
            base_lock = {(t['kind'], t['index']): bool(t['locked']) for t in s['tracks']}
            for (kind, k), was in base_lock.items():
                if bool(tl.GetIsTrackLocked(kind, k)) != was:
                    bad.append(f'original {kind}{k} lock state differs from baseline ({was})')
            expected = {('bgm', Path(row['bgm']['path']).name.casefold(), row['start'])}
            expected |= {(c['kind'], Path(c['path']).name.casefold(), c['record_start']) for c in row['cues']}
            found = set()
            for key, (kind, label) in TRACKS.items():
                idx = [k for k in range(1, tl.GetTrackCount(kind) + 1) if tl.GetTrackName(kind, k) == label]
                if len(idx) > 1:
                    bad.append('duplicate ' + label)
                for k in idx[:1]:
                    for it in tl.GetItemListInTrack(kind, k) or []:
                        name = Path(it.GetMediaPoolItem().GetClipProperty('File Path')).name.casefold()
                        tup = (key, name, it.GetStart())
                        if tup in found:
                            bad.append('duplicate item ' + name)
                        found.add(tup)
                        if key == 'bgm' and (it.GetStart() != s['start'] or it.GetEnd() != s['end']):
                            bad.append('BGM does not cover timeline')
                        if it.GetEnd() > s['end']:
                            bad.append('item past timeline end: ' + name)
                        if key == 'gif':
                            vals = [it.GetProperty(x) for x in ('ZoomX', 'ZoomY', 'Pan', 'Tilt')]
                            if not (math.isclose(vals[0], ZOOM) and math.isclose(vals[1], ZOOM) and vals[2] == 0 and vals[3] == 0 and it.GetProperty('ZoomGang') is True):
                                bad.append('GIF vdo values wrong: ' + name)
                            if not 85 <= it.GetEnd() - it.GetStart() <= 153:
                                bad.append('GIF hold outside ~1.5-2.5s: ' + name)
                        else:
                            want = row['bgm']['gain_db'] if key == 'bgm' else next(
                                (c['gain_db'] for c in row['cues'] if c['kind'] == 'sfx' and Path(c['path']).name.casefold() == name and c['record_start'] == it.GetStart()), None)
                            if want is None or abs(float(it.GetProperty('AudioVolume')) - want) > 0.05:
                                bad.append(f'gain mismatch {name}: {it.GetProperty("AudioVolume")} vs {want}')
            if found != expected:
                bad.append(f'missing={sorted(expected - found)} extra={sorted(found - expected)}')
            report['results'].append({'ordinal': o, 'name': s['name'], 'items': len(found), 'problems': bad})
        report['problems_total'] = sum(len(x['problems']) for x in report['results'])
    now = p.GetCurrentTimeline()
    report['restored'] = (now.GetUniqueId() == entry_id and now.GetCurrentTimecode() == entry_tc and r.GetCurrentPage() == page)
    (ART / 'verify-all.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'timelines': len(report['results']), 'items': sum(x['items'] for x in report['results']),
                      'problems_total': report['problems_total'], 'restored': report['restored']}))
    for x in report['results']:
        if x['problems']:
            print(x['ordinal'], x['problems'])


if __name__ == '__main__':
    main()
