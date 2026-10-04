"""Capture/apply native video properties, not Resolve's named Video Presets.

The public API on observed Resolve 21.1.0.17 has no LoadVideoPreset method.
This helper copies an explicitly approved reference clip's exposed properties.
It never reads or writes Resolve databases and does not copy OFX/keyframes.
"""
from __future__ import annotations

import math

VIDEO_KEYS = (
    'Pan', 'Tilt', 'ZoomX', 'ZoomY', 'ZoomGang', 'RotationAngle',
    'AnchorPointX', 'AnchorPointY', 'Pitch', 'Yaw', 'FlipX', 'FlipY',
    'CropLeft', 'CropRight', 'CropTop', 'CropBottom', 'CropSoftness', 'CropRetain',
    'DynamicZoomEase', 'CompositeMode', 'Opacity', 'Distortion',
    'RetimeProcess', 'MotionEstimation', 'Scaling', 'ResizeFilter',
    'TransformEnabled', 'CroppingEnabled', 'DynamicZoomEnabled',
    'CompositeEnabled', 'LensCorrectionEnabled', 'RetimeAndScalingEnabled',
)


def capture_style(clip):
    """Read only the clip's exposed, explicitly supported video properties."""
    properties = clip.GetProperty()
    if not isinstance(properties, dict):
        raise ValueError('Reference clip exposes no property dictionary')
    values = {key: properties[key] for key in VIDEO_KEYS if key in properties}
    if not values or any(not isinstance(value, (bool, int, float)) or
                         (isinstance(value, float) and not math.isfinite(value))
                         for value in values.values()):
        raise ValueError('Video properties must be finite numeric/boolean values')
    return {'schema_version': 1, 'kind': 'resolve_video_properties',
            'source_clip_id': clip.GetUniqueId(), 'source_clip_name': clip.GetName(),
            'properties': values}


def validate_style(style):
    if not isinstance(style, dict) or style.get('schema_version') != 1 or style.get('kind') != 'resolve_video_properties':
        raise ValueError('Expected a captured native video-property style, not a named preset')
    values = style.get('properties')
    if not isinstance(values, dict) or not values or set(values) - set(VIDEO_KEYS):
        raise ValueError('Style contains empty or unsupported properties')
    for value in values.values():
        if not isinstance(value, (bool, int, float)) or not math.isfinite(value):
            raise ValueError('Style values must be finite numeric/boolean values')
    return dict(values)


def property_equal(actual, expected):
    if isinstance(expected, bool):
        return actual is expected
    return isinstance(actual, (int, float)) and math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-7)


def set_properties(clip, values):
    # Temporarily unlink zooms so a coupled setter cannot overwrite the other axis.
    if 'ZoomGang' in values and ('ZoomX' in values or 'ZoomY' in values):
        clip.SetProperty('ZoomGang', False)
    for key, value in values.items():
        if key != 'ZoomGang':
            clip.SetProperty(key, value)
    if 'ZoomGang' in values:
        clip.SetProperty('ZoomGang', values['ZoomGang'])
    failures = {key: clip.GetProperty(key) for key, value in values.items()
                if not property_equal(clip.GetProperty(key), value)}
    if failures:
        raise RuntimeError(f'Property readback failed for {clip.GetUniqueId()}: {failures}')


def apply_style_batch(clips, style, target_ids, *, apply=False, delay=1.2):
    """Plan by stable IDs; optionally set/read back only authorized properties."""
    import time
    values = validate_style(style)
    ids = list(target_ids)
    if not ids or len(ids) != len(set(ids)):
        raise ValueError('Require unique explicit target clip IDs')
    by_id = {clip.GetUniqueId(): clip for clip in clips}
    if len(by_id) != len(clips) or set(ids) - set(by_id):
        raise ValueError('Target clip missing or duplicate clip IDs')
    targets = [by_id[uid] for uid in ids]
    changed = [clip for clip in targets if any(not property_equal(clip.GetProperty(key), value)
                                              for key, value in values.items())]
    result = {'dry_run': not apply, 'target_ids': ids, 'matched_count': len(targets),
              'changed_count': len(changed), 'changed_ids': [x.GetUniqueId() for x in changed]}
    if not apply:
        return result
    before = {clip.GetUniqueId(): capture_style(clip)['properties'] for clip in changed}
    try:
        for clip in changed:
            set_properties(clip, values)
            if delay:
                time.sleep(delay)
        for clip in targets:
            if any(not property_equal(clip.GetProperty(key), value) for key, value in values.items()):
                raise RuntimeError(f'Final readback failed for {clip.GetUniqueId()}')
    except Exception as exc:
        rollback_errors = []
        for clip in changed:
            try:
                set_properties(clip, before[clip.GetUniqueId()])
            except Exception as rollback:
                rollback_errors.append(str(rollback))
        raise RuntimeError(f'{exc}; rollback_errors={rollback_errors}') from exc
    return result


def verify_snapshot(before, after, target_ids, property_keys):
    """Permit only selected video-property changes; protect all other state."""
    import copy
    def stripped(snapshot):
        value = copy.deepcopy(snapshot)
        for track in value['tracks']:
            for item in track['items']:
                if item['id'] in target_ids:
                    for key in property_keys:
                        item['props'].pop(key, None)
        return value
    if stripped(before) != stripped(after):
        raise RuntimeError('Protected timeline content/settings changed')


def snapshot_timeline(timeline):
    tracks = []
    for kind in ('video', 'audio', 'subtitle'):
        for index in range(1, timeline.GetTrackCount(kind) + 1):
            items = []
            for clip in timeline.GetItemListInTrack(kind, index) or []:
                media = clip.GetMediaPoolItem()
                items.append({'id': clip.GetUniqueId(), 'name': clip.GetName(),
                              'start': clip.GetStart(True), 'end': clip.GetEnd(True),
                              'source_start': clip.GetSourceStartFrame(),
                              'source_end': clip.GetSourceEndFrame(),
                              'enabled': clip.GetClipEnabled(), 'fades': clip.GetFades(),
                              'props': clip.GetProperty() or {},
                              'path': media.GetClipProperty('File Path') if media else None})
            tracks.append({'type': kind, 'index': index,
                           'name': timeline.GetTrackName(kind, index),
                           'enabled': timeline.GetIsTrackEnabled(kind, index),
                           'locked': timeline.GetIsTrackLocked(kind, index), 'items': items})
    return {'timeline_id': timeline.GetUniqueId(), 'start': timeline.GetStartFrame(),
            'end': timeline.GetEndFrame(), 'settings': {key: timeline.GetSetting(key) for key in
            ('timelineFrameRate', 'timelinePlaybackFrameRate',
             'timelineResolutionWidth', 'timelineResolutionHeight')}, 'tracks': tracks}


def main(argv=None):
    import argparse
    import datetime
    import json
    from pathlib import Path
    import time
    import zipfile
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--source-clip-id', help='Approved reference VIDEO timeline item ID')
    source.add_argument('--style-json', type=Path, help='Previously captured video properties')
    parser.add_argument('--target-clip-id', action='append', required=True,
                        help='Explicit VIDEO item ID; repeat for each target')
    parser.add_argument('--project-id', required=True)
    parser.add_argument('--timeline-id', required=True)
    parser.add_argument('--capture-style', type=Path, help='Write reference JSON (refuses overwrite)')
    parser.add_argument('--backup-dir', type=Path)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--apply', action='store_true', help='Write native properties; default dry run')
    args = parser.parse_args(argv)
    if args.apply and args.backup_dir is None:
        parser.error('--apply requires --backup-dir')
    if args.capture_style and args.capture_style.exists():
        parser.error('--capture-style refuses to overwrite an existing file')
    from load_subtitle_preset import connect_resolve, wait_page
    resolve = connect_resolve()
    manager = resolve.GetProjectManager()
    project = manager.GetCurrentProject()
    if not project or project.GetUniqueId() != args.project_id:
        raise ValueError('Current project ID does not match; no project switch performed')
    timeline = project.GetCurrentTimeline()
    if not timeline or timeline.GetUniqueId() != args.timeline_id:
        raise ValueError('Current timeline ID does not match; no timeline switch performed')
    if project.IsRenderingInProgress():
        raise RuntimeError('Refusing changes during rendering')
    clips = [clip for index in range(1, timeline.GetTrackCount('video') + 1)
             for clip in timeline.GetItemListInTrack('video', index) or []]
    by_id = {clip.GetUniqueId(): clip for clip in clips}
    if args.source_clip_id:
        if args.source_clip_id not in by_id:
            raise ValueError('Reference is not a video item on this timeline')
        style = capture_style(by_id[args.source_clip_id])
    else:
        style = json.loads(args.style_json.read_text(encoding='utf-8'))
    values = validate_style(style)
    result = apply_style_batch(clips, style, args.target_clip_id, apply=False)
    result.update({'project_id': project.GetUniqueId(), 'timeline_id': timeline.GetUniqueId(),
                   'source': style.get('source_clip_id'), 'native_named_preset_loaded': False})
    if args.capture_style:
        args.capture_style.parent.mkdir(parents=True, exist_ok=True)
        args.capture_style.write_text(json.dumps(style, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        result['captured_style'] = str(args.capture_style)
    if not args.apply or result['changed_count'] == 0:
        result['dry_run'] = not args.apply
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        return 0
    before = snapshot_timeline(timeline)
    timecode, page = timeline.GetCurrentTimecode(), resolve.GetCurrentPage()
    pool = project.GetMediaPool()
    folder = pool.GetCurrentFolder()
    prior_styles = {uid: capture_style(by_id[uid])['properties'] for uid in args.target_clip_id}
    args.backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backup = args.backup_dir / ('before_video_style_' + stamp + '.drp')
    if not manager.SaveProject() or not manager.ExportProject(project.GetName(), str(backup), False):
        raise RuntimeError('Project save/export failed; no properties written')
    if not backup.is_file() or backup.stat().st_size == 0:
        raise RuntimeError('Empty DRP backup; no properties written')
    with zipfile.ZipFile(backup) as archive:
        if archive.testzip() is not None:
            raise RuntimeError('Invalid DRP archive; no properties written')
    result['backup'] = str(backup)
    try:
        applied = apply_style_batch(clips, style, args.target_clip_id, apply=True)
        verify_snapshot(before, snapshot_timeline(timeline), args.target_clip_id, values)
        if not manager.SaveProject():
            raise RuntimeError('SaveProject failed after style apply')
        for uid in args.target_clip_id:
            if any(not property_equal(by_id[uid].GetProperty(key), value) for key, value in values.items()):
                raise RuntimeError('Post-save property readback mismatch')
        result.update(applied)
        result.update({'saved': True, 'protected_content_verified': True})
    except Exception as exc:
        errors = []
        for uid, properties in prior_styles.items():
            try:
                set_properties(by_id[uid], properties)
            except Exception as rollback:
                errors.append(str(rollback))
        result.update({'error': str(exc), 'rollback_errors': errors})
        raise
    finally:
        restoration_errors = []
        for label, action in (
            ('playhead', lambda: timeline.SetCurrentTimecode(timecode)),
            ('page', lambda: wait_page(resolve, page)),
            ('folder', lambda: pool.SetCurrentFolder(folder)),
            ('save', manager.SaveProject),
        ):
            try:
                returned = action()
                if label == 'save' and not returned:
                    restoration_errors.append('SaveProject returned False')
            except Exception as error:
                restoration_errors.append(label + ': ' + str(error))
        time.sleep(0.3)
        if timeline.GetCurrentTimecode() != timecode or resolve.GetCurrentPage() != page or pool.GetCurrentFolder().GetUniqueId() != folder.GetUniqueId():
            restoration_errors.append('UI readback mismatch')
        result['restoration_errors'] = restoration_errors
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if result['restoration_errors']:
        raise RuntimeError('Style verified but UI restoration failed: ' + str(result['restoration_errors']))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
