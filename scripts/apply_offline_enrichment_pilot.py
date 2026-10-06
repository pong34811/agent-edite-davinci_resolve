"""Approved offline-draft pilot on a recoverable timeline copy, originals untouched.
MCP-GAP: live Resolve MCP absent; installed API and live method probes checked.
Dry run default; --apply creates one pilot only. No external media APIs.
"""
from __future__ import annotations
import argparse
import json
import math
import subprocess
import time
from pathlib import Path
from scripts.resolve_common import connect_resolve
from scripts.verify_review_resume import item_record

ART = Path(__file__).resolve().parents[1] / '.hermes/artifacts/enrichment-review-2026-10-06-live2'


def source_frames(record_frames, record_fps, media_fps):
    if record_fps <= 0 or media_fps <= 0 or record_frames <= 0:
        raise ValueError('Invalid frame conversion')
    return round(record_frames * media_fps / record_fps)


def validate_range(timeline_start, timeline_end, start, duration):
    if duration <= 0 or start < timeline_start or start + duration > timeline_end:
        raise ValueError('Append outside timeline bounds')


def check(obj, names):
    available = set(dir(obj))
    missing = [n for n in names if n not in available]
    if missing:
        raise RuntimeError('Missing native methods: ' + ', '.join(missing))


def store(report):
    (ART / 'pilot-offline-01.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')


def contents(tl, counts):
    rows = []
    for kind, count in counts.items():
        for k in range(1, count + 1):
            items = []
            for item in tl.GetItemListInTrack(kind, k) or []:
                row = item_record(item)
                row.pop('id', None)  # DuplicateTimeline creates new item IDs.
                items.append(row)
            rows.append({'kind': kind, 'index': k, 'name': tl.GetTrackName(kind, k),
                         'enabled': tl.GetIsTrackEnabled(kind, k), 'items': items})
    return rows


def asset_mean(path):
    import re
    result = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(path), '-vn', '-af', 'volumedetect',
                             '-f', 'null', '-'], capture_output=True, text=True, errors='replace', check=True, timeout=60)
    found = re.search(r'mean_volume:\s*(-?[\d.]+)\s*dB', result.stderr)
    if not found:
        raise RuntimeError('No measurable asset audio')
    return float(found[1])


def pool_available_frames(pool, fps):
    frames = pool.GetClipProperty('Frames')
    if frames not in (None, ''):
        return int(float(frames))
    duration = pool.GetClipProperty('Duration')
    if not isinstance(duration, str):
        raise RuntimeError('Missing Media Pool duration')
    fields = duration.split(':')
    if len(fields) != 4:
        raise RuntimeError('Unrecognized Media Pool duration: ' + duration)
    h, m, s, f = map(int, fields)
    return round((h * 3600 + m * 60 + s) * fps + f)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    backup = json.loads((ART / 'fresh-backup.json').read_text(encoding='utf-8'))
    if not Path(backup['backup']).is_file() or Path(backup['backup']).stat().st_size != backup['bytes']:
        raise RuntimeError('Fresh backup missing or changed')
    fresh = json.loads((ART / 'resume-freshness.json').read_text(encoding='utf-8'))
    if not fresh['all_match']:
        raise RuntimeError('Live freshness audit did not pass')
    draft = json.loads((ART / 'offline-review/asset-draft.json').read_text(encoding='utf-8'))['timelines'][0]
    saved = json.loads((ART / 'inventory.json').read_text(encoding='utf-8'))['timelines'][0]
    cue = draft['cue_points'][0]
    chosen = {
        'sfx': cue['asset_candidates']['sfx'][0]['path'],
        'gif': cue['asset_candidates']['illustration'][0]['path'],
        'bgm': next(a['path'] for a in draft['bgm_candidates'] if a['name'] == 'NCSน่ารัก.mp3'),
    }
    if not all(Path(p).is_file() for p in chosen.values()):
        raise RuntimeError('Selected asset missing')
    r = connect_resolve()
    if r is None:
        raise RuntimeError('No Resolve connection')
    pm = r.GetProjectManager()
    p = pm.GetCurrentProject()
    if p.GetName() != backup['project']:
        raise RuntimeError('Project mismatch')
    mp = p.GetMediaPool()
    check(p, ['SetCurrentTimeline', 'GetCurrentTimeline'])
    check(pm, ['SaveProject'])
    check(mp, ['ImportMedia', 'AppendToTimeline', 'GetCurrentFolder', 'SetCurrentFolder', 'AddSubFolder'])
    originals = [p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1)]
    source = next(t for t in originals if t.GetUniqueId() == draft['timeline_id'])
    check(source, ['DuplicateTimeline', 'AddTrack', 'SetTrackName', 'SetTrackLock', 'GetIsTrackLocked'])
    name = source.GetName() + ' [ENRICHMENT PILOT OFFLINE]'
    if any(t.GetName() == name for t in originals):
        raise RuntimeError('Pilot already exists; inspect saved report, do not rerun blindly')
    report = {'project': p.GetName(), 'source_timeline_id': source.GetUniqueId(), 'pilot_name': name,
              'backup': backup['backup'], 'assets': chosen, 'cue_text': cue['text'],
              'cue_frame': cue['absolute_start_frame'], 'status': 'dry_run',
              'limitations': ['Offline subtitle-aligned draft, not performance-verified exact accent.',
                              'Levels use mixed preview audio reference, not isolated dialogue loudness.',
                              'GIF starting layout from live project example; native vdo load still required.',
                              'Private pilot; rights and listening/visual QC pending.']}
    if not args.apply:
        print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
        return
    entry = p.GetCurrentTimeline()
    entry_tc = entry.GetCurrentTimecode()
    entry_page = r.GetCurrentPage()
    entry_folder = mp.GetCurrentFolder()
    report['entry'] = {'timeline_id': entry.GetUniqueId(), 'timecode': entry_tc, 'page': entry_page,
                       'folder_id': entry_folder.GetUniqueId()}
    report['status'] = 'starting'
    store(report)
    pilot = None
    locks = []
    try:
        p.SetCurrentTimeline(source)
        time.sleep(0.5)
        if p.GetCurrentTimeline().GetUniqueId() != source.GetUniqueId():
            raise RuntimeError('Wrong active source')
        fps = float(source.GetSetting('timelineFrameRate'))
        start, end = source.GetStartFrame(), source.GetEndFrame()
        counts = {kind: source.GetTrackCount(kind) for kind in ('video', 'audio', 'subtitle')}
        baseline = contents(source, counts)
        # Recheck the protected live content immediately before mutation.
        expected = [{'kind': tr['kind'], 'index': tr['index'], 'name': tr['name'],
                     'enabled': tr['enabled'], 'items': [{k: v for k, v in x.items() if k != 'id'} for x in tr['items']]}
                    for tr in saved['tracks']]
        if baseline != expected:
            raise RuntimeError('Source changed after freshness audit')
        # Capture current example, not the archived Tygarina preset.
        example_tl = originals[48]
        p.SetCurrentTimeline(example_tl)
        time.sleep(0.5)
        reference = next(x for k in range(1, example_tl.GetTrackCount('video') + 1)
                         for x in (example_tl.GetItemListInTrack('video', k) or [])
                         if x.GetUniqueId() == '9219fb7d-36d3-4237-b736-0f970fe18d48')
        gif_properties = reference.GetProperty()
        p.SetCurrentTimeline(source)
        time.sleep(0.5)
        # Only three approved files imported into a task bin.
        mp.SetCurrentFolder(mp.GetRootFolder())
        task_bin = next((f for f in mp.GetRootFolder().GetSubFolderList() if f.GetName() == 'OfflineEnrichment_20261006'), None)
        if task_bin is None:
            task_bin = mp.AddSubFolder(mp.GetRootFolder(), 'OfflineEnrichment_20261006')
            time.sleep(1.2)
        if task_bin is None or not mp.SetCurrentFolder(task_bin):
            raise RuntimeError('Cannot select task bin')
        pools = {}
        for kind, path in chosen.items():
            matches = [x for x in task_bin.GetClipList()
                       if str(Path(x.GetClipProperty('File Path'))).casefold() == str(Path(path)).casefold()]
            if len(matches) > 1:
                raise RuntimeError('Duplicate task-bin asset: ' + kind)
            # Live build rejected dict FilePath import; legacy path list succeeded.
            loaded = matches or mp.ImportMedia([path])
            time.sleep(1.2)
            if not loaded or len(loaded) != 1:
                raise RuntimeError('Import failed: ' + kind)
            pools[kind] = loaded[0]
        media = {}
        for kind, pool in pools.items():
            mfps = float(pool.GetClipProperty('FPS'))
            available = pool_available_frames(pool, mfps)
            media[kind] = {'fps': mfps, 'frames': available, 'media_id': pool.GetUniqueId(),
                           'path': pool.GetClipProperty('File Path')}
        lengths = {'bgm': end - start,
                   'sfx': min(round(fps), math.floor(media['sfx']['frames'] * fps / media['sfx']['fps'])),
                   'gif': round(2 * fps)}
        for kind in chosen:
            needed = source_frames(lengths[kind], fps, media[kind]['fps'])
            if needed > media[kind]['frames']:
                raise RuntimeError('Asset too short for planned hold: ' + kind)
            validate_range(start, end, start if kind == 'bgm' else cue['absolute_start_frame'], lengths[kind])
        packet = json.loads((ART / 'offline-review/01/packet.json').read_text(encoding='utf-8'))
        mixed_mean = packet['audio_metrics']['mixed_mean_dbfs']
        if mixed_mean is None:
            raise RuntimeError('No base audio reference')
        gains = {'bgm': max(-60.0, min(-12.0, mixed_mean - 20.0 - asset_mean(chosen['bgm']))),
                 'sfx': max(-60.0, min(-6.0, mixed_mean - 6.0 - asset_mean(chosen['sfx'])))}
        pilot = source.DuplicateTimeline(name)
        time.sleep(1.2)
        if pilot is None:
            raise RuntimeError('DuplicateTimeline failed')
        report.update({'pilot_id': pilot.GetUniqueId(), 'media': media, 'gains_db': gains,
                       'status': 'copy_created', 'inserted': []})
        store(report)
        p.SetCurrentTimeline(pilot)
        time.sleep(0.5)
        if contents(pilot, counts) != baseline:
            raise RuntimeError('Copy content mismatch')
        for kind, count in counts.items():
            for k in range(1, count + 1):
                old = pilot.GetIsTrackLocked(kind, k)
                locks.append((kind, k, old))
                pilot.SetTrackLock(kind, k, True)
        tracks = {}
        for kind, track_type, label in [('gif', 'video', 'OFFLINE_PILOT_GIF'),
                                         ('sfx', 'audio', 'OFFLINE_PILOT_SFX'),
                                         ('bgm', 'audio', 'OFFLINE_PILOT_BGM')]:
            if not pilot.AddTrack(track_type):
                raise RuntimeError('AddTrack failed')
            time.sleep(1.2)
            index = pilot.GetTrackCount(track_type)
            pilot.SetTrackName(track_type, index, label)
            tracks[kind] = index
        for kind in ('bgm', 'sfx', 'gif'):
            at = start if kind == 'bgm' else cue['absolute_start_frame']
            n = source_frames(lengths[kind], fps, media[kind]['fps'])
            appended = mp.AppendToTimeline([{'mediaPoolItem': pools[kind], 'startFrame': 0,
                'endFrame': n, 'mediaType': 1 if kind == 'gif' else 2,
                'trackIndex': tracks[kind], 'recordFrame': at}])
            time.sleep(1.2)
            if not appended or len(appended) != 1:
                raise RuntimeError('Append failed: ' + kind)
            item = appended[0]
            report['inserted'].append({'kind': kind, 'item_id': item.GetUniqueId(),
                'start': item.GetStart(), 'end': item.GetEnd(), 'expected_start': at,
                'expected_end': at + lengths[kind], 'track': tracks[kind]})
            store(report)
            if item.GetStart() != at or item.GetEnd() != at + lengths[kind]:
                raise RuntimeError('Native source-end convention or conformed duration mismatch: ' + kind)
            if kind == 'gif':
                for key in ('ZoomGang', 'ZoomX', 'ZoomY', 'Pan', 'Tilt', 'CropLeft', 'CropRight', 'CropTop', 'CropBottom'):
                    value = gif_properties[key]
                    item.SetProperty(key, value)
                    if item.GetProperty(key) != value:
                        raise RuntimeError('GIF starting layout readback failed: ' + key)
            else:
                item.SetProperty('AudioVolume', float(gains[kind]))
                if abs(float(item.GetProperty('AudioVolume')) - gains[kind]) > 0.01:
                    raise RuntimeError('Audio gain readback failed')
                fades = {'FadeIn': round(0.5 * fps) if kind == 'bgm' else 0,
                         'FadeOut': round(fps) if kind == 'bgm' else round(0.15 * fps)}
                if not item.SetFades(fades) or item.GetFades() != fades:
                    raise RuntimeError('Fade readback failed')
        if contents(pilot, counts) != baseline or pilot.GetEndFrame() != end:
            raise RuntimeError('Protected copy content or duration changed')
        for kind, k, old in locks:
            pilot.SetTrackLock(kind, k, old)
        locks.clear()
        if not pm.SaveProject():
            raise RuntimeError('SaveProject failed')
        report['status'] = 'inserted_saved_pending_vdo_and_audiovisual_qc'
        report['protected_copy_content_verified'] = True
        p.SetCurrentTimeline(source)
        time.sleep(0.5)
        report['original_content_unchanged'] = contents(source, counts) == baseline
        if not report['original_content_unchanged']:
            raise RuntimeError('Original content changed')
        store(report)
    except Exception as exc:
        report['error'] = str(exc)
        report['status'] = 'partial_pilot_retained_do_not_repeat'
        store(report)
        raise
    finally:
        if pilot is not None and locks:
            p.SetCurrentTimeline(pilot)
            time.sleep(0.5)
            for kind, k, old in locks:
                pilot.SetTrackLock(kind, k, old)
        p.SetCurrentTimeline(entry)
        time.sleep(0.5)
        if p.GetCurrentTimeline().GetUniqueId() == entry.GetUniqueId():
            entry.SetCurrentTimecode(entry_tc)
            time.sleep(0.3)
        mp.SetCurrentFolder(entry_folder)
        if r.GetCurrentPage() != entry_page:
            r.OpenPage(entry_page)
            time.sleep(1.0)
        report['restoration_verified'] = (p.GetCurrentTimeline().GetUniqueId() == entry.GetUniqueId()
            and p.GetCurrentTimeline().GetCurrentTimecode() == entry_tc
            and r.GetCurrentPage() == entry_page and mp.GetCurrentFolder().GetUniqueId() == entry_folder.GetUniqueId())
        store(report)
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
