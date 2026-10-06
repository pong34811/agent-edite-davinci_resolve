"""Resolve Python: capture/reapply exposed values from a GUI-loaded vdo clip.
This is NOT a native named-preset loader; no LoadVideoPreset API is invented.
MCP-GAP: live davinci-resolve catalog absent; use shared scripting connection.
Dry run default; explicit project/timeline/clip IDs and fresh DRP before writes.
"""
from __future__ import annotations
import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
import time
import zipfile

# Support both python -m scripts.apply_vdo_python and direct file execution.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.resolve_common import connect_resolve
from scripts.apply_video_style import (
    capture_style, validate_style, apply_style_batch, snapshot_timeline, verify_snapshot,
)


def validate_reference(style, project_id, raster):
    if style.get('source_project_id') != project_id:
        raise ValueError('Reference belongs to another project; refusing archived/foreign vdo values')
    if list(style.get('raster', [])) != list(raster):
        raise ValueError('Reference raster differs; approved layout must not be scaled silently')


def require(obj, methods):
    names = set(dir(obj))
    missing = [name for name in methods if name not in names]
    if missing:
        raise RuntimeError('Missing native API: ' + ', '.join(missing))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project-id', required=True)
    ap.add_argument('--timeline-id', required=True)
    ap.add_argument('--style-json', type=Path, required=True)
    ap.add_argument('--capture-from-clip-id', help='Capture an exact GIF already loaded with vdo in GUI')
    ap.add_argument('--target-clip-id', action='append', default=[])
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--backup-dir', type=Path)
    ap.add_argument('--report', type=Path)
    args = ap.parse_args(argv)
    if args.capture_from_clip_id:
        if args.apply or args.target_clip_id:
            ap.error('Capture and application are separate operations')
        if args.style_json.exists():
            ap.error('Capture refuses to overwrite an existing reference')
    elif not args.target_clip_id:
        ap.error('Require explicit --target-clip-id; no implicit all-timeline writes')
    if args.apply and args.backup_dir is None:
        ap.error('--apply requires --backup-dir')
    resolve = connect_resolve()
    if resolve is None:
        raise RuntimeError('Resolve connection unavailable')
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    if project is None or project.GetUniqueId() != args.project_id:
        raise ValueError('Current project ID mismatch')
    require(project, ['GetCurrentTimeline', 'SetCurrentTimeline', 'GetTimelineByIndex', 'IsRenderingInProgress'])
    require(pm, ['SaveProject', 'ExportProject'])
    if project.IsRenderingInProgress():
        raise RuntimeError('Refusing application during rendering')
    entry = project.GetCurrentTimeline()
    if entry is None:
        raise RuntimeError('No active timeline')
    entry_id, entry_tc = entry.GetUniqueId(), entry.GetCurrentTimecode()
    entry_page = resolve.GetCurrentPage()
    pool = project.GetMediaPool()
    entry_folder = pool.GetCurrentFolder()
    tl = next((project.GetTimelineByIndex(i) for i in range(1, project.GetTimelineCount() + 1)
               if project.GetTimelineByIndex(i).GetUniqueId() == args.timeline_id), None)
    if tl is None:
        raise ValueError('Exact timeline ID missing')
    result = {'project_id': args.project_id, 'timeline_id': args.timeline_id,
              'method': 'TimelineItem.SetProperty using a captured reference',
              'native_named_preset_loaded_by_python': False}
    try:
        project.SetCurrentTimeline(tl)
        time.sleep(0.5)
        if project.GetCurrentTimeline().GetUniqueId() != args.timeline_id:
            raise RuntimeError('Timeline activation readback failed')
        raster = [tl.GetSetting('timelineResolutionWidth'), tl.GetSetting('timelineResolutionHeight')]
        clips = [clip for k in range(1, tl.GetTrackCount('video') + 1)
                 for clip in (tl.GetItemListInTrack('video', k) or [])]
        by_id = {clip.GetUniqueId(): clip for clip in clips}
        ids = [args.capture_from_clip_id] if args.capture_from_clip_id else args.target_clip_id
        if len(ids) != len(set(ids)) or any(uid not in by_id for uid in ids):
            raise ValueError('Missing/duplicate explicit GIF clip IDs')
        for uid in ids:
            clip = by_id[uid]
            require(clip, ['SetProperty', 'GetProperty', 'GetMediaPoolItem'])
            media = clip.GetMediaPoolItem()
            if media is None or not str(media.GetClipProperty('File Path')).lower().endswith('.gif'):
                raise ValueError('Target/reference must be a media-backed GIF')
        if args.capture_from_clip_id:
            style = capture_style(by_id[args.capture_from_clip_id])
            style.update({'source_project_id': args.project_id, 'source_timeline_id': args.timeline_id,
                          'raster': raster, 'reference_label': 'vdo',
                          'provenance_limit': 'Reads clip values; does not itself verify/load a named preset'})
            args.style_json.parent.mkdir(parents=True, exist_ok=True)
            args.style_json.write_text(json.dumps(style, ensure_ascii=False, indent=2), encoding='utf-8')
            result.update({'captured': str(args.style_json.resolve()), 'captured_properties': style['properties']})
        else:
            style = json.loads(args.style_json.read_text(encoding='utf-8'))
            validate_reference(style, args.project_id, raster)
            values = validate_style(style)
            result.update(apply_style_batch(clips, style, ids, apply=False))
            if args.apply and result['changed_count']:
                before = snapshot_timeline(tl)
                args.backup_dir.mkdir(parents=True, exist_ok=True)
                backup = args.backup_dir / ('before_python_vdo_' + datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.drp')
                if not pm.SaveProject() or not pm.ExportProject(project.GetName(), str(backup), False):
                    raise RuntimeError('Fresh native DRP export failed; no properties written')
                if not backup.is_file() or backup.stat().st_size == 0:
                    raise RuntimeError('Backup empty; no properties written')
                with zipfile.ZipFile(backup) as archive:
                    if archive.testzip() is not None:
                        raise RuntimeError('DRP archive failed validation')
                result['backup'] = str(backup)
                result.update(apply_style_batch(clips, style, ids, apply=True))
                verify_snapshot(before, snapshot_timeline(tl), ids, values)
                if not pm.SaveProject():
                    raise RuntimeError('SaveProject failed')
                if apply_style_batch(clips, style, ids, apply=False)['changed_count']:
                    raise RuntimeError('Post-save property readback mismatch')
                result.update({'saved': True, 'protected_content_verified': True})
            else:
                result['dry_run'] = not args.apply
    finally:
        project.SetCurrentTimeline(entry)
        time.sleep(0.5)
        if project.GetCurrentTimeline().GetUniqueId() == entry_id:
            entry.SetCurrentTimecode(entry_tc)
            time.sleep(0.3)
        pool.SetCurrentFolder(entry_folder)
        if resolve.GetCurrentPage() != entry_page:
            resolve.OpenPage(entry_page)
            time.sleep(1.0)
        result['restoration_verified'] = (project.GetCurrentTimeline().GetUniqueId() == entry_id
            and project.GetCurrentTimeline().GetCurrentTimecode() == entry_tc
            and pool.GetCurrentFolder().GetUniqueId() == entry_folder.GetUniqueId()
            and resolve.GetCurrentPage() == entry_page)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        if not result['restoration_verified']:
            raise RuntimeError('Working state restoration failed')
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
