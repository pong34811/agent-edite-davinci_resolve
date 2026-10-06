"""Re-apply the Timeline-1 pilot enrichment into the original (missed by the ordinal-1 rule)."""
import json
import math
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.resolve_common import connect_resolve
from scripts.apply_offline_enrichment_pilot import pool_available_frames

ART = ROOT / '.hermes/artifacts/enrichment-review-2026-10-06-live2'
ASSETS = {
    'bgm': r'G:\My Drive\Projects\1.bgm\NCSน่ารัก.mp3',
    'sfx': r'G:\My Drive\Projects\2.1_sfx\10 ตกใจฉาก 10.mp3',
    'gif': r'G:\My Drive\Projects\3.gif\Anime - Shocked Reaction.gif',
}
CUE = 4980


def main():
    pilot = json.loads((ART / 'pilot-offline-01.json').read_text(encoding='utf-8'))
    r = connect_resolve()
    if r is None:
        raise RuntimeError('Resolve unavailable')
    pm = r.GetProjectManager()
    p = pm.GetCurrentProject()
    o = next(p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1)
             if p.GetTimelineByIndex(i).GetUniqueId() == pilot['source_timeline_id'])
    mp = p.GetMediaPool()
    folder = next(f for f in mp.GetRootFolder().GetSubFolderList()
                  if f.GetName() == 'OfflineEnrichment_20261006')
    entry, page = p.GetCurrentTimeline(), r.GetCurrentPage()
    tc = entry.GetCurrentTimecode()
    p.SetCurrentTimeline(o)
    time.sleep(0.5)
    if p.GetCurrentTimeline().GetUniqueId() != pilot['source_timeline_id']:
        raise RuntimeError('Wrong active timeline')
    if any(o.GetTrackName('video', k).startswith('OFFLINE_DRAFT')
           or o.GetTrackName('audio', k).startswith('OFFLINE_DRAFT')
           for k in range(1, o.GetTrackCount('video') + 1)
           for _ in [0]):
        raise RuntimeError('Enrichment tracks already present; refusing duplicate work')
    for k in range(1, o.GetTrackCount('audio') + 1):
        if o.GetTrackName('audio', k).startswith('OFFLINE_DRAFT'):
            raise RuntimeError('Enrichment audio tracks already present')
    fps = float(o.GetSetting('timelineFrameRate'))
    start, end = o.GetStartFrame(), o.GetEndFrame()

    def media(path):
        match = [x for x in folder.GetClipList()
                 if str(Path(x.GetClipProperty('File Path'))).casefold() == str(Path(path)).casefold()]
        loaded = match or mp.ImportMedia([path])
        time.sleep(1.2)
        if not loaded:
            raise RuntimeError('Asset import failed: ' + path)
        return loaded[0]

    counts = {k: o.GetTrackCount(k) for k in ('video', 'audio', 'subtitle')}
    locks = []
    added = []
    try:
        for kind, c in counts.items():
            for k in range(1, c + 1):
                locks.append((kind, k, o.GetIsTrackLocked(kind, k)))
                o.SetTrackLock(kind, k, True)
        jobs = [('bgm', 'audio', start), ('sfx', 'audio', CUE), ('gif', 'video', CUE)]
        for kind, track_type, at in jobs:
            pool = media(ASSETS[kind])
            mfps = float(pool.GetClipProperty('FPS'))
            available = pool_available_frames(pool, mfps)
            if kind == 'bgm':
                source_frames = round((end - start) * mfps / fps)
                duration = end - start
            elif kind == 'sfx':
                source_frames = min(round(1 * mfps), available)
                duration = math.floor(source_frames * fps / mfps)
            else:
                source_frames = min(round(2 * mfps), available)
                duration = math.floor(source_frames * fps / mfps)
            label = 'OFFLINE_DRAFT_' + kind.upper()
            index = next((k for k in range(1, o.GetTrackCount(track_type) + 1)
                          if o.GetTrackName(track_type, k) == label), None)
            if index is None:
                if not o.AddTrack(track_type):
                    raise RuntimeError('AddTrack failed: ' + kind)
                time.sleep(1.2)
                index = o.GetTrackCount(track_type)
                o.SetTrackName(track_type, index, label)
            result = mp.AppendToTimeline([{'mediaPoolItem': pool, 'startFrame': 0,
                'endFrame': source_frames, 'mediaType': 1 if kind == 'gif' else 2,
                'trackIndex': index, 'recordFrame': at}])
            time.sleep(1.2)
            if not result or len(result) != 1:
                raise RuntimeError('Append failed: ' + kind)
            clip = result[0]
            if clip.GetStart() != at or clip.GetEnd() > end:
                raise RuntimeError('Append range outside timeline: ' + kind)
            if kind == 'bgm' and (clip.GetStart() != start or clip.GetEnd() != end):
                raise RuntimeError('BGM does not cover the exact timeline')
            added.append({'kind': kind, 'item_id': clip.GetUniqueId(), 'start': clip.GetStart(),
                          'end': clip.GetEnd(), 'track': f'{track_type}{index}', 'name': clip.GetName(),
                          'volume': clip.GetProperty('AudioVolume')})
            print('added', kind, clip.GetStart(), clip.GetEnd(), flush=True)
        for kind, k, state in locks:
            o.SetTrackLock(kind, k, state)
        locks.clear()
        if not pm.SaveProject():
            raise RuntimeError('SaveProject failed')
        print('saved', flush=True)
    finally:
        if locks:
            for kind, k, state in locks:
                o.SetTrackLock(kind, k, state)
        p.SetCurrentTimeline(entry)
        time.sleep(0.5)
        if p.GetCurrentTimeline().GetUniqueId() == entry.GetUniqueId():
            entry.SetCurrentTimecode(tc)
            time.sleep(0.3)
        if r.GetCurrentPage() != page:
            r.OpenPage(page)
            time.sleep(1.0)
    report = {'ordinal': 1, 'timeline_id': o.GetUniqueId(), 'name': o.GetName(), 'added': added,
              'status': 'reapplied_original_needs_gain_and_vdo_followup',
              'restoration_verified': (p.GetCurrentTimeline().GetUniqueId() == entry.GetUniqueId()
                                       and r.GetCurrentPage() == page)}
    (ART / 'promotion' / '01.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
