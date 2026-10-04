"""Offline behavior tests for the native-API video style helper."""
import importlib
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import copy
import subprocess
import zipfile
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
style = importlib.import_module('apply_video_style')
preset_module = importlib.import_module('load_subtitle_preset')


class Clip:
    def __init__(self, uid='gif1', properties=None):
        self.uid = uid
        self.properties = dict(properties or {'ZoomX': 0.391, 'ZoomY': 0.391,
                                              'Pan': 0.0, 'Tilt': 0.0,
                                              'ZoomGang': True, 'AudioVolume': -3.0})
    def GetUniqueId(self):
        return self.uid
    def GetName(self):
        return 'reference.gif'
    def GetProperty(self, key=None):
        return dict(self.properties) if key is None else self.properties.get(key)


    def SetProperty(self, key, value):
        self.properties[key] = value
        return False  # A false native setter can still apply; readback decides.


class ApplyTests(unittest.TestCase):
    def test_dry_run_preserves_every_target(self):
        source = Clip()
        target = Clip('gif2', {'ZoomX': 0.213, 'ZoomY': 0.213, 'Pan': -500.0,
                               'Tilt': 370.0, 'ZoomGang': True})
        before = target.GetProperty()
        result = style.apply_style_batch([source, target], style.capture_style(source),
                                         ['gif2'], apply=False, delay=0)
        self.assertEqual(result['changed_count'], 1)
        self.assertEqual(target.GetProperty(), before)
        self.assertEqual(source.GetProperty('ZoomX'), 0.391)

    def test_apply_reads_back_false_setter_and_repeat_is_noop(self):
        source = Clip()
        target = Clip('gif2', {'ZoomX': 0.213, 'ZoomY': 0.213, 'Pan': -500.0,
                               'Tilt': 370.0, 'ZoomGang': True})
        settings = style.capture_style(source)
        first = style.apply_style_batch([source, target], settings, ['gif2'],
                                        apply=True, delay=0)
        self.assertEqual(first['changed_count'], 1)
        for key, value in settings['properties'].items():
            self.assertEqual(target.GetProperty(key), value)
        second = style.apply_style_batch([source, target], settings, ['gif2'],
                                         apply=True, delay=0)
        self.assertEqual(second['changed_count'], 0)


    def test_failed_second_clip_restores_first_and_failed_clip(self):
        class RejectOnce(Clip):
            rejected = False
            def SetProperty(self, key, value):
                if key == 'Tilt' and value == 0.0 and not self.rejected:
                    self.rejected = True
                    return False
                return super().SetProperty(key, value)
        source = Clip()
        first = Clip('gif2', {'ZoomX': 0.213, 'ZoomY': 0.213, 'Pan': -500.0,
                              'Tilt': 370.0, 'ZoomGang': True})
        second = RejectOnce('gif3', {'ZoomX': 0.213, 'ZoomY': 0.213, 'Pan': -400.0,
                                    'Tilt': 370.0, 'ZoomGang': True})
        old = [first.GetProperty(), second.GetProperty()]
        with self.assertRaisesRegex(RuntimeError, 'readback failed'):
            style.apply_style_batch([first, second], style.capture_style(source),
                                    ['gif2', 'gif3'], apply=True, delay=0)
        self.assertEqual([first.GetProperty(), second.GetProperty()], old)

    def test_unknown_duplicate_missing_targets_and_invalid_style_refused(self):
        clip = Clip()
        settings = style.capture_style(clip)
        for ids in [[], ['gif1', 'gif1'], ['missing']]:
            with self.assertRaises(ValueError):
                style.apply_style_batch([clip], settings, ids, apply=True, delay=0)
        for value in [float('nan'), float('inf'), '0.5']:
            invalid = copy.deepcopy(settings)
            invalid['properties']['ZoomX'] = value
            with self.assertRaises(ValueError):
                style.apply_style_batch([clip], invalid, ['gif1'], apply=True, delay=0)
        invalid = copy.deepcopy(settings)
        invalid['properties']['AudioVolume'] = -10.0
        with self.assertRaises(ValueError):
            style.apply_style_batch([clip], invalid, ['gif1'], apply=True, delay=0)


class GuardTests(unittest.TestCase):
    def test_preservation_allows_target_style_only(self):
        before = {'tracks': [{'items': [{'id': 'gif2', 'start': 10, 'end': 20,
                                          'props': {'Pan': 0.0}}]}]}
        after = copy.deepcopy(before)
        after['tracks'][0]['items'][0]['props']['Pan'] = 200.0
        style.verify_snapshot(before, after, ['gif2'], ['Pan'])
        after['tracks'][0]['items'][0]['end'] = 21
        with self.assertRaises(RuntimeError):
            style.verify_snapshot(before, after, ['gif2'], ['Pan'])

    def test_cli_help_is_available_without_resolve(self):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/apply_video_style.py'), '--help'],
                                capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0)
        self.assertIn('--source-clip-id', result.stdout)
        self.assertIn('--apply', result.stdout)
        self.assertIn('--backup-dir', result.stdout)


class CaptureTests(unittest.TestCase):
    def test_capture_is_native_video_properties_not_audio_or_named_preset(self):
        self.assertIsNotNone(style, 'apply_video_style helper does not exist yet')
        clip = Clip()
        result = style.capture_style(clip)
        self.assertEqual(result['kind'], 'resolve_video_properties')
        self.assertEqual(result['source_clip_id'], 'gif1')
        self.assertEqual(result['properties']['ZoomX'], 0.391)
        self.assertEqual(result['properties']['ZoomGang'], True)
        self.assertNotIn('AudioVolume', result['properties'])
        self.assertEqual(clip.GetProperty('AudioVolume'), -3.0)


class FakeFolder:
    def __init__(self, uid='folder-1'):
        self.uid = uid
    def GetUniqueId(self):
        return self.uid


class FakeMedia:
    def GetClipProperty(self, key):
        return {'File Path': r'C:\media\source.mp4'}.get(key)


class OrchestrationClip(Clip):
    def __init__(self, uid, properties):
        super().__init__(uid, properties)
        self.set_calls = []
        self.media = FakeMedia()
    def SetProperty(self, key, value):
        self.set_calls.append((key, value))
        self.properties[key] = value
        return False  # Resolve can apply a value while returning False.
    def GetStart(self, absolute=False):
        return 100
    def GetEnd(self, absolute=False):
        return 200
    def GetSourceStartFrame(self):
        return 0
    def GetSourceEndFrame(self):
        return 100
    def GetClipEnabled(self):
        return True
    def GetFades(self):
        return {'in': 0, 'out': 0}
    def GetMediaPoolItem(self):
        return self.media


class FakeMediaPool:
    def __init__(self):
        self.folder = FakeFolder()
        self.set_folder_calls = []
    def GetCurrentFolder(self):
        return self.folder
    def SetCurrentFolder(self, folder):
        self.set_folder_calls.append(folder.GetUniqueId())
        self.folder = folder
        return True


class FakeTimeline:
    def __init__(self, clips, uid='timeline-1'):
        self.uid = uid
        self.clips = clips
        self.timecode = '00:00:05:12'
        self.set_timecodes = []
    def GetUniqueId(self):
        return self.uid
    def GetCurrentTimecode(self):
        return self.timecode
    def SetCurrentTimecode(self, value):
        self.set_timecodes.append(value)
        self.timecode = value
        return True
    def GetTrackCount(self, kind):
        return 1 if kind == 'video' else 0
    def GetItemListInTrack(self, kind, index):
        return list(self.clips) if kind == 'video' and index == 1 else []
    def GetStartFrame(self):
        return 0
    def GetEndFrame(self):
        return 200
    def GetSetting(self, key):
        return {
            'timelineFrameRate': '30',
            'timelinePlaybackFrameRate': '30',
            'timelineResolutionWidth': '1920',
            'timelineResolutionHeight': '1080',
        }.get(key)
    def GetTrackName(self, kind, index):
        return f'{kind.title()} {index}'
    def GetIsTrackEnabled(self, kind, index):
        return True
    def GetIsTrackLocked(self, kind, index):
        return False


class FakeProject:
    def __init__(self, timeline, uid='project-1'):
        self.uid = uid
        self.timeline = timeline
        self.pool = FakeMediaPool()
    def GetUniqueId(self):
        return self.uid
    def GetCurrentTimeline(self):
        return self.timeline
    def GetMediaPool(self):
        return self.pool
    def GetName(self):
        return 'Fake project'
    def IsRenderingInProgress(self):
        return False


class FakeManager:
    def __init__(self, project, *, valid_backup=True):
        self.project = project
        self.valid_backup = valid_backup
        self.save_calls = 0
        self.export_calls = []
        self.properties_at_export = None
    def GetCurrentProject(self):
        return self.project
    def SaveProject(self):
        self.save_calls += 1
        return True
    def ExportProject(self, project_name, path, with_clips):
        self.export_calls.append((project_name, path, with_clips))
        target = self.project.timeline.clips[-1]
        self.properties_at_export = target.GetProperty()
        if self.valid_backup:
            with zipfile.ZipFile(path, 'w') as archive:
                archive.writestr('project.xml', '<project/>')
        else:
            Path(path).write_bytes(b'not a DRP archive')
        return True


class FakeResolve:
    def __init__(self, manager):
        self.manager = manager
        self.page = 'edit'
    def GetProjectManager(self):
        return self.manager
    def GetCurrentPage(self):
        return self.page
    def OpenPage(self, page):
        self.page = page
        return True


def make_orchestration_api(*, project_id='project-1', timeline_id='timeline-1', valid_backup=True):
    source = OrchestrationClip('source', {
        'ZoomX': 0.4, 'ZoomY': 0.4, 'Pan': 0.0, 'Tilt': 0.0,
        'ZoomGang': True, 'AudioVolume': -3.0,
    })
    target = OrchestrationClip('target', {
        'ZoomX': 0.2, 'ZoomY': 0.2, 'Pan': 10.0, 'Tilt': -5.0,
        'ZoomGang': True, 'AudioVolume': -6.0,
    })
    timeline = FakeTimeline([source, target], uid=timeline_id)
    project = FakeProject(timeline, uid=project_id)
    manager = FakeManager(project, valid_backup=valid_backup)
    return source, target, timeline, project, manager, FakeResolve(manager)


class MainOrchestrationTests(unittest.TestCase):
    def args(self, backup_dir, *, project_id='project-1', timeline_id='timeline-1', report=None):
        result = [
            '--source-clip-id', 'source', '--target-clip-id', 'target',
            '--project-id', project_id, '--timeline-id', timeline_id,
            '--backup-dir', str(backup_dir), '--apply',
        ]
        if report is not None:
            result += ['--report', str(report)]
        return result

    def run_main(self, resolve, args):
        with mock.patch.object(preset_module, 'connect_resolve', return_value=resolve), \
             mock.patch('time.sleep', return_value=None), \
             contextlib.redirect_stdout(io.StringIO()):
            return style.main(args)

    def test_wrong_project_or_timeline_id_refuses_before_any_write(self):
        cases = (
            ('project-1', 'timeline-1', 'wrong-project', 'timeline-1'),
            ('project-1', 'timeline-1', 'project-1', 'wrong-timeline'),
        )
        for actual_project, actual_timeline, requested_project, requested_timeline in cases:
            with self.subTest(project=requested_project, timeline=requested_timeline), \
                 tempfile.TemporaryDirectory() as temporary:
                source, target, timeline, project, manager, resolve = make_orchestration_api(
                    project_id=actual_project, timeline_id=actual_timeline)
                before = target.GetProperty()
                with self.assertRaisesRegex(ValueError, 'does not match'):
                    self.run_main(resolve, self.args(
                        Path(temporary) / 'backups', project_id=requested_project,
                        timeline_id=requested_timeline))
                self.assertEqual(target.GetProperty(), before)
                self.assertEqual(target.set_calls, [])
                self.assertEqual(manager.save_calls, 0)
                self.assertEqual(manager.export_calls, [])

    def test_invalid_drp_archive_is_rejected_before_any_clip_changes(self):
        with tempfile.TemporaryDirectory() as temporary:
            source, target, timeline, project, manager, resolve = make_orchestration_api(
                valid_backup=False)
            before = target.GetProperty()
            with self.assertRaises(zipfile.BadZipFile):
                self.run_main(resolve, self.args(Path(temporary) / 'backups'))
            self.assertEqual(manager.save_calls, 1)  # Save before export is allowed.
            self.assertEqual(len(manager.export_calls), 1)
            self.assertEqual(target.GetProperty(), before)
            self.assertEqual(target.set_calls, [])

    def test_success_verifies_backup_protected_state_save_and_ui_restoration(self):
        with tempfile.TemporaryDirectory() as temporary:
            source, target, timeline, project, manager, resolve = make_orchestration_api()
            original_target = target.GetProperty()
            original_timecode = timeline.GetCurrentTimecode()
            original_page = resolve.GetCurrentPage()
            original_folder = project.pool.GetCurrentFolder().GetUniqueId()
            report = Path(temporary) / 'result.json'
            self.run_main(resolve, self.args(
                Path(temporary) / 'backups', report=report))

            export_name, backup_path, with_clips = manager.export_calls[0]
            self.assertEqual(export_name, project.GetName())
            self.assertFalse(with_clips)
            self.assertEqual(manager.properties_at_export, original_target)
            with zipfile.ZipFile(backup_path) as archive:
                self.assertIsNone(archive.testzip())
                self.assertIn('project.xml', archive.namelist())
            self.assertNotEqual(target.GetProperty(), original_target)
            self.assertEqual(target.GetProperty('ZoomX'), source.GetProperty('ZoomX'))
            self.assertEqual(target.GetProperty('AudioVolume'), original_target['AudioVolume'])
            self.assertGreaterEqual(manager.save_calls, 3)  # preflight, apply, final restore
            self.assertEqual(timeline.GetCurrentTimecode(), original_timecode)
            self.assertEqual(timeline.set_timecodes, [original_timecode])
            self.assertEqual(resolve.GetCurrentPage(), original_page)
            self.assertEqual(project.pool.GetCurrentFolder().GetUniqueId(), original_folder)
            self.assertEqual(project.pool.set_folder_calls, [original_folder])
            result = json.loads(report.read_text(encoding='utf-8'))
            self.assertTrue(result['saved'])
            self.assertTrue(result['protected_content_verified'])
            self.assertEqual(result['restoration_errors'], [])
            self.assertTrue(Path(result['backup']).is_file())


if __name__ == '__main__':
    unittest.main()
