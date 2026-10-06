"""Read-only audit of draft copies vs saved inventory; no edits or saves."""
import json
import time
from pathlib import Path
from scripts.resolve_common import connect_resolve

ART = Path(__file__).resolve().parents[1] / '.hermes/artifacts/enrichment-review-2026-10-06-live2'
SUFFIX = ' [ENRICHMENT DRAFT OFFLINE]'


def main():
    inv = json.loads((ART / 'inventory.json').read_text(encoding='utf-8'))
    pilot = json.loads((ART / 'pilot-offline-01.json').read_text(encoding='utf-8'))
    r = connect_resolve()
    if r is None:
        raise RuntimeError('Resolve unavailable')
    p = r.GetProjectManager().GetCurrentProject()
    tls = [p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1)]
    by_id = {t.GetUniqueId(): t for t in tls}
    entry, tc, page = p.GetCurrentTimeline(), None, r.GetCurrentPage()
    tc = entry.GetCurrentTimecode()
    problems = []
    checked = []
    for row in inv['timelines']:
        original = by_id.get(row['timeline_id'])
        if original is None:
            problems.append({'ordinal': row['ordinal'], 'issue': 'original_missing'})
            continue
        if row['ordinal'] == 1:
            draft = by_id.get(pilot['pilot_id'])
        else:
            draft = next((t for t in tls if t.GetName() == row['name'] + SUFFIX), None)
        if draft is None:
            problems.append({'ordinal': row['ordinal'], 'issue': 'draft_missing'})
            continue
        # protected state: original untouched, draft keeps its end and adds only new tracks
        if original.GetEndFrame() != row['end'] or original.GetStartFrame() != row['start']:
            problems.append({'ordinal': row['ordinal'], 'issue': 'original_bounds_changed'})
        if draft.GetEndFrame() != row['end']:
            problems.append({'ordinal': row['ordinal'], 'issue': 'draft_end_changed'})
        for tr in row['tracks']:
            live_items = original.GetItemListInTrack(tr['kind'], tr['index']) or []
            if len(live_items) != len(tr['items']):
                problems.append({'ordinal': row['ordinal'], 'issue': 'original_items_changed',
                                 'track': f"{tr['kind']}{tr['index']}"})
            draft_items = draft.GetItemListInTrack(tr['kind'], tr['index']) or []
            if len(draft_items) != len(tr['items']):
                problems.append({'ordinal': row['ordinal'], 'issue': 'draft_base_items_changed',
                                 'track': f"{tr['kind']}{tr['index']}"})
        checked.append(row['ordinal'])
    p.SetCurrentTimeline(entry)
    time.sleep(0.5)
    if entry.GetCurrentTimecode() != tc:
        entry.SetCurrentTimecode(tc)
        time.sleep(0.3)
    if r.GetCurrentPage() != page:
        r.OpenPage(page)
        time.sleep(1.0)
    report = {'checked_ordinals': len(checked), 'problems': problems,
              'restoration_verified': (p.GetCurrentTimeline().GetUniqueId() == entry.GetUniqueId()
                                       and r.GetCurrentPage() == page),
              'note': 'count/bounds comparison only; visual and listening QC still pending'}
    (ART / 'batch-python' / 'audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
