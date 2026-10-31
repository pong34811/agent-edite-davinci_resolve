"""Place a HyperFrames illustration reel on a copy of a timeline and verify protected tracks.

Generalises the Armigon intro/name/why-VTuber apply scripts. placements.json rows:
{id, start, end, sourceStart, sourceEnd, file}; record range [start, end), reel range [sourceStart, sourceEnd).

Usage (Resolve open, project already current):
  py -3.13 scripts/illustration_reel.py baseline|pilot|apply|verify --source-id <uuid> \
      --root <task dir> [--target "FirstPass v2_illustrated"] [--bin "<bin>"] [--pilot <id>] [--track-name REACTIONS]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def validate_plan(plan, timeline_end):
    """Return total reel frames or raise ValueError."""
    if not plan:
        raise ValueError('empty plan')
    ids = [x['id'] for x in plan]
    if len(set(ids)) != len(ids):
        raise ValueError(f'duplicate ids: {ids}')
    prev_end, cursor = None, plan[0]['sourceStart']
    for x in plan:
        if x['end'] <= x['start']:
            raise ValueError(f"{x['id']}: empty record range")
        if prev_end is not None and x['start'] < prev_end:
            raise ValueError(f"{x['id']}: overlap with previous placement")
        if x['end'] > timeline_end:
            raise ValueError(f"{x['id']}: past timeline end {timeline_end}")
        if x['sourceStart'] != cursor or x['sourceEnd'] - x['sourceStart'] != x['end'] - x['start']:
            raise ValueError(f"{x['id']}: source range not contiguous or length mismatch")
        prev_end, cursor = x['end'], x['sourceEnd']
    return cursor - plan[0]['sourceStart']


def check(cond, msg):
    """Explicit gate that survives `python -O` (unlike assert)."""
    if not cond:
        raise RuntimeError(msg)


def norm_path(path):
    """Resolved, case-normalised full path used to compare media files."""
    return os.path.normcase(str(Path(path).resolve()))


def matches(item, x, root):
    return (item['start'] == x['start'] and item['end'] == x['end'] and item['left'] == x['sourceStart']
            and bool(item['path']) and norm_path(item['path']) == norm_path(Path(root) / x['file']))


def inventory(t):
    data = {'name': t.GetName(), 'id': t.GetUniqueId(), 'start': t.GetStartFrame(), 'end': t.GetEndFrame(), 'tracks': {}}
    for kind in ('video', 'audio', 'subtitle'):
        data['tracks'][kind] = []
        for i in range(1, t.GetTrackCount(kind) + 1):
            items = []
            for c in t.GetItemListInTrack(kind, i) or []:
                m = c.GetMediaPoolItem()
                items.append({'name': c.GetName(), 'start': c.GetStart(), 'end': c.GetEnd(), 'left': c.GetLeftOffset(),
                              'right': c.GetRightOffset(), 'path': m.GetClipProperty('File Path') if m else None,
                              'properties': c.GetProperty() if kind != 'subtitle' else {}})
            data['tracks'][kind].append({'index': i, 'name': t.GetTrackName(kind, i), 'enabled': t.GetIsTrackEnabled(kind, i),
                                         'locked': t.GetIsTrackLocked(kind, i), 'items': items})
    return data


def run(a):
    from scripts.resolve_common import require_resolve, preserved_state
    from scripts.backup_drp import export_verified
    root = Path(a.root).resolve()
    r = require_resolve(); pm = r.GetProjectManager(); p = pm.GetCurrentProject()
    tls = [p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1)]
    source = next((t for t in tls if t.GetUniqueId() == a.source_id), None)
    if source is None:
        raise SystemExit(f'source timeline id {a.source_id!r} not found in current project')
    if a.mode == 'baseline':
        out = root / 'baseline.json'
        if out.exists():
            raise SystemExit('baseline.json exists; do not overwrite')
        with preserved_state(r):
            p.SetCurrentTimeline(source)
            size = export_verified(pm, p, root / 'backup_before_illustrations.drp')
            data = inventory(source)
            out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps({'backup_bytes': size, 'counts': {k: sum(len(x['items']) for x in v) for k, v in data['tracks'].items()}}))
        return
    base = json.loads((root / 'baseline.json').read_text(encoding='utf-8'))
    plan = json.loads((root / 'placements.json').read_text(encoding='utf-8'))
    validate_plan(plan, base['end'])
    want = [x for x in plan if x['id'] == a.pilot] if a.mode == 'pilot' else plan
    if not want:
        raise SystemExit(f'pilot id {a.pilot!r} not in placements.json')
    vi = len(base['tracks']['video']) + 1  # new overlay track index
    with preserved_state(r):
        p.SetCurrentTimeline(source)
        if inventory(source)['tracks'] != base['tracks']:
            raise SystemExit('source tracks changed since baseline')
        targets = [t for t in tls if t.GetName() == a.target]
        if len(targets) > 1:
            raise SystemExit(f'{len(targets)} timelines named {a.target}')
        if a.mode == 'verify' and not targets:
            raise SystemExit('target missing')
        target = targets[0] if targets else source.DuplicateTimeline(a.target)
        check(target, f'DuplicateTimeline {a.target!r} failed'); time.sleep(1.2)
        p.SetCurrentTimeline(target)
        mp = p.GetMediaPool()
        if a.mode != 'verify':
            export_verified(pm, p, root / f'backup_before_{a.mode}_{int(time.time())}.drp')
            if target.GetTrackCount('video') == vi - 1:
                check(target.AddTrack('video'), 'AddTrack failed'); time.sleep(1.2)
                check(target.SetTrackName('video', vi, a.track_name), 'SetTrackName failed')
            check(target.GetTrackCount('video') == vi, f'expected {vi} video tracks, got {target.GetTrackCount("video")}')
            try:
                for kind, tracks in base['tracks'].items():
                    for tr in tracks:
                        target.SetTrackLock(kind, tr['index'], True)
                target.SetTrackLock('video', vi, False)
                bins = [f for f in mp.GetRootFolder().GetSubFolderList() if f.GetName() == a.bin]
                folder = bins[0] if bins else mp.AddSubFolder(mp.GetRootFolder(), a.bin)
                check(folder, f'bin {a.bin!r} missing and AddSubFolder failed')
                check(mp.SetCurrentFolder(folder), f'SetCurrentFolder {a.bin!r} failed')
                # keyed by full normalised path so a same-named clip from another folder is never reused
                media = {norm_path(fp): c for c in folder.GetClipList() if (fp := c.GetClipProperty('File Path'))}
                for name in sorted({x['file'] for x in want}):
                    key = norm_path(root / name)
                    if key not in media:
                        loaded = mp.ImportMedia([str(root / name)])
                        check(loaded, f'ImportMedia failed: {root / name}')
                        media[key] = loaded[0]
                for x in want:
                    existing = [c for c in target.GetItemListInTrack('video', vi) or [] if c.GetStart() == x['start']]
                    if existing:
                        c = existing[0]
                        m = c.GetMediaPoolItem()
                        item = {'start': c.GetStart(), 'end': c.GetEnd(), 'left': c.GetLeftOffset(),
                                'path': m.GetClipProperty('File Path') if m else None}
                        if len(existing) == 1 and matches(item, x, root):
                            continue
                        check(target.DeleteClips(existing, False), f"DeleteClips failed at {x['start']}"); time.sleep(1.2)
                    m = media[norm_path(root / x['file'])]
                    check(float(m.GetClipProperty('FPS')) == float(target.GetSetting('timelineFrameRate')),
                          f"clip FPS {m.GetClipProperty('FPS')} != timeline {target.GetSetting('timelineFrameRate')}")
                    # endFrame is exclusive on 60 fps 21.1.0.17 (hyperframes-illustration-workflow.md)
                    added = mp.AppendToTimeline([{'mediaPoolItem': m, 'startFrame': x['sourceStart'], 'endFrame': x['sourceEnd'],
                                                  'recordFrame': x['start'], 'trackIndex': vi, 'mediaType': 1}])
                    check(added and len(added) == 1, f'AppendToTimeline failed: {x}')
                    c = added[0]
                    check((c.GetStart(), c.GetEnd(), c.GetLeftOffset()) == (x['start'], x['end'], x['sourceStart']),
                          f'placement read-back mismatch: {(x, c.GetStart(), c.GetEnd(), c.GetLeftOffset())}')
                    time.sleep(1.2)
            finally:
                for kind, tracks in base['tracks'].items():
                    for tr in tracks:
                        target.SetTrackLock(kind, tr['index'], tr['locked'])
            check(pm.SaveProject(), 'SaveProject failed')
        data = inventory(target)
        check(data['end'] == base['end'], f"timeline end changed: {data['end']} != {base['end']}")
        for kind, tracks in base['tracks'].items():
            for i, tr in enumerate(tracks):
                check(data['tracks'][kind][i] == tr, f'protected track mismatch: {kind} {i + 1}')
        placed = data['tracks']['video'][vi - 1]['items'] if len(data['tracks']['video']) >= vi else []
        missing = [x['id'] for x in want if not any(matches(c, x, root) for c in placed)]
        check(not missing, f'placements missing or wrong media: {missing}')
        if a.mode != 'pilot':
            check(len(placed) == len(plan), f'overlay count {len(placed)} != plan {len(plan)}')
        p.SetCurrentTimeline(source)
        check(inventory(source)['tracks'] == base['tracks'], 'source tracks changed during run')
        (root / f'readback-{a.mode}.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        if a.mode == 'verify':
            export_verified(pm, p, root / 'illustrated_project.drp')
    print(json.dumps({'mode': a.mode, 'target': a.target, 'id': target.GetUniqueId(), 'overlays': len(placed),
                      'end': data['end'], 'protected_tracks': 'identical'}, ensure_ascii=False))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('mode', choices=['baseline', 'pilot', 'apply', 'verify'])
    ap.add_argument('--source-id', required=True, help='unique ID of the untouched source timeline')
    ap.add_argument('--root', required=True, help='task dir holding placements.json, reel and baseline')
    ap.add_argument('--target', default='FirstPass v2_illustrated', help='copy timeline name')
    ap.add_argument('--bin', default='Illustrations', help='Media Pool bin for the reel')
    ap.add_argument('--pilot', help='placement id for pilot mode')
    ap.add_argument('--track-name', default='REACTIONS')
    a = ap.parse_args(argv)
    if a.mode == 'pilot' and not a.pilot:
        ap.error('--pilot is required for pilot mode')
    run(a)


if __name__ == '__main__':
    main()
