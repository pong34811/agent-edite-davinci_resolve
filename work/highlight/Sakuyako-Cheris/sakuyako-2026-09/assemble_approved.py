"""Job-local assembly of the user-approved checklist; no source modification."""
import argparse
import json
import os
from pathlib import Path
import sys
import time

JOB = Path(__file__).resolve().parent
sys.path.insert(0, 'C:/ProgramData/Blackmagic Design/DaVinci Resolve/Support/Developer/Scripting/Modules')
os.environ.setdefault('RESOLVE_SCRIPT_LIB', 'C:/Program Files/Blackmagic Design/DaVinci Resolve/fusionscript.dll')
import DaVinciResolveScript as dvr


def connect():
    resolve = dvr.scriptapp('Resolve')
    assert resolve, 'Resolve disconnected'
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    assert project.GetName() == 'sakuyako-2026-09', 'Wrong active project'
    assert project.GetUniqueId() == '7b43f381-5630-49f1-8d35-a13bf4d8a99e', 'Wrong project identity'
    assert float(project.GetSetting('timelineFrameRate')) == 30
    assert project.GetSetting('timelineResolutionWidth') == '1920'
    assert project.GetSetting('timelineResolutionHeight') == '1080'
    return pm, project, project.GetMediaPool()


def clips_in(folder):
    result = list(folder.GetClipList() or [])
    for sub in folder.GetSubFolderList() or []:
        result.extend(clips_in(sub))
    return result


def norm(path):
    return os.path.normcase(os.path.abspath(path))


def inspect_timeline(tl, row):
    videos = [x for i in range(1, tl.GetTrackCount('video') + 1) for x in (tl.GetItemListInTrack('video', i) or [])]
    audios = [x for i in range(1, tl.GetTrackCount('audio') + 1) for x in (tl.GetItemListInTrack('audio', i) or [])]
    assert len(videos) == 1 and len(audios) >= 1, 'Missing/extra picture or missing audio'
    expected = row['end_frame_exclusive'] - row['start_frame']
    frames = tl.GetEndFrame() - tl.GetStartFrame()
    assert frames == expected, (row['candidate'], frames, expected)
    assert float(tl.GetSetting('timelineFrameRate')) == 30
    assert tl.GetSetting('timelineResolutionWidth') == '1920'
    assert tl.GetSetting('timelineResolutionHeight') == '1080'
    for item in videos + audios:
        media = item.GetMediaPoolItem()
        assert media and norm(media.GetClipProperty('File Path')) == norm(row['file'])
        assert item.GetStart() == tl.GetStartFrame() and item.GetEnd() == tl.GetEndFrame(), 'Gap or track duration mismatch'
        assert item.GetSourceStartFrame() == row['start_frame'], 'Source IN mismatch'
        # This build reports GetSourceEndFrame inconsistently inclusive/exclusive.
        # Exact source IN plus exact item duration determines the exclusive OUT.
        assert item.GetDuration() == expected, 'Item duration mismatch'
        assert item.GetSourceEndFrame() in (row['end_frame_exclusive'] - 1, row['end_frame_exclusive']), 'Source OUT mismatch'
    return {'candidate': row['candidate'], 'timeline_id': tl.GetUniqueId(), 'name': tl.GetName(), 'frames': frames, 'expected_frames': expected, 'video_items': len(videos), 'audio_items': len(audios), 'source_in': videos[0].GetSourceStartFrame(), 'source_out': videos[0].GetSourceEndFrame(), 'file': row['file'], 'gaps': 0, 'overlaps': 0, 'verified': True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['pilot', 'build', 'verify'])
    args = parser.parse_args()
    plan = json.loads((JOB / 'approved_timeline_plan.json').read_text(encoding='utf-8'))
    pm, project, pool = connect()
    root = pool.GetRootFolder()
    folders = [f for f in root.GetSubFolderList() or [] if f.GetName() == 'sakuyako-2026-09']
    if args.action != 'verify':
        folder = folders[0] if folders else pool.AddSubFolder(root, 'sakuyako-2026-09')
        assert folder and pool.SetCurrentFolder(folder)
        media = {norm(c.GetClipProperty('File Path')): c for c in clips_in(root) if c.GetClipProperty('File Path')}
        missing = list(dict.fromkeys(p['file'] for p in plan if norm(p['file']) not in media))
        if missing:
            assert pool.ImportMedia(missing), 'Import failed'
            time.sleep(1.5)
    media = {norm(c.GetClipProperty('File Path')): c for c in clips_in(root) if c.GetClipProperty('File Path')}
    for row in plan:
        assert norm(row['file']) in media, 'Missing Media Pool source'
        clip = media[norm(row['file'])]
        assert float(clip.GetClipProperty('FPS')) == 30
        assert Path(clip.GetClipProperty('File Path')).is_file()
    existing = {project.GetTimelineByIndex(i).GetName(): project.GetTimelineByIndex(i) for i in range(1, project.GetTimelineCount() + 1)}
    targets = plan[:1] if args.action == 'pilot' else plan
    results = []
    for row in targets:
        connect()
        tl = existing.get(row['name'])
        if not tl:
            assert args.action != 'verify', 'Timeline missing'
            clip = media[norm(row['file'])]
            # Resolve 21.1.0.17 pilot confirms endFrame is exclusive here.
            tl = pool.CreateTimelineFromClips(row['name'], [{'mediaPoolItem': clip, 'startFrame': row['start_frame'], 'endFrame': row['end_frame_exclusive']}])
            assert tl, 'Timeline creation failed'
            time.sleep(1.2)
        results.append(inspect_timeline(tl, row))
        assert pm.SaveProject(), 'Save failed'
        print(json.dumps(results[-1], ensure_ascii=False), flush=True)
    assert len(results) == len(targets)
    if args.action != 'pilot':
        assert project.GetTimelineCount() == len(plan), 'Timeline count mismatch'
    print(json.dumps({'action': args.action, 'verified_count': len(results), 'actual_timeline_count': project.GetTimelineCount(), 'saved': True}, ensure_ascii=False))


if __name__ == '__main__':
    main()
