"""Offline contracts catch bad source ranges, false QC passes and stale intake."""
import copy
import json
import shutil
import subprocess
import sys
import wave
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def decision():
    return {
        'version': 1,
        'timeline': {'name': 'Review', 'width': 1920, 'height': 1080,
                     'fps': '60000/1001', 'start_frame': 86400},
        'sources': [{'id': 'camera', 'path': 'camera.mp4', 'fps': '30000/1001',
                     'frame_count': 300}],
        'edits': [{'id': 'beat1', 'source_id': 'camera', 'in_frame': 10,
                   'out_frame': 40, 'record_frame': 86400,
                   'track_kind': 'video', 'track_index': 1,
                   'story_beat': 'setup', 'reason': 'Keep the complete question',
                   'evidence': ['contact-sheet.jpg'], 'confidence': 'high'}],
    }


def test_source_and_record_frames_use_their_own_rates():
    from scripts.edit_workflow import validate_decisions
    result = validate_decisions(decision())
    assert result['status'] == 'passed'
    assert result['placements'][0]['record_end_frame'] == 86460
    assert result['live_verified'] is False


@pytest.mark.parametrize('change', [
    {'out_frame': 301}, {'in_frame': -1}, {'out_frame': 10},
    {'source_id': 'missing'}, {'record_frame': 86399},
    {'reason': ''}, {'evidence': []}, {'track_kind': 'subtitle'},
    {'in_frame': True}, {'speed': 1.1},
])
def test_invalid_or_unsupported_edits_cannot_pass(change):
    from scripts.edit_workflow import validate_decisions
    data = decision()
    data['edits'][0].update(change)
    assert validate_decisions(data)['status'] == 'failed'


def test_duplicate_ids_paths_and_same_track_overlap_are_rejected():
    from scripts.edit_workflow import validate_decisions
    data = decision()
    duplicate = copy.deepcopy(data['edits'][0])
    duplicate['id'] = 'beat2'
    duplicate['record_frame'] += 1
    data['edits'].append(duplicate)
    assert validate_decisions(data)['status'] == 'failed'
    data = decision()
    data['sources'].append({**data['sources'][0], 'id': 'alias'})
    assert validate_decisions(data)['status'] == 'failed'


@pytest.mark.parametrize('fps', ['0/0', 'NaN', '-24', '0', True])
def test_bad_frame_rates_are_errors_instead_of_silent_24fps_fallback(fps):
    from scripts.edit_workflow import validate_decisions
    data = decision()
    data['timeline']['fps'] = fps
    assert validate_decisions(data)['status'] == 'failed'


def test_draft_is_not_an_approved_cut():
    from scripts.edit_workflow import validate_decisions
    data = decision()
    data['edits'] = []
    assert validate_decisions(data)['status'] == 'failed'


def test_acceptance_needs_every_check_and_real_matching_evidence(tmp_path):
    from scripts.edit_workflow import evaluate_acceptance, file_sha256, load_gate
    proof = tmp_path / 'proof.json'
    proof.write_text('measured evidence', encoding='utf-8')
    evidence = {'path': 'proof.json', 'sha256': file_sha256(proof)}
    checks = {'version': 1, 'target': 'project/timeline-id/render-v1', 'checks': [
        {'id': check['id'], 'status': 'passed', 'reviewer': 'editor',
         'note': 'Reviewed this target', 'evidence': [evidence]}
        for check in load_gate()['checks']
    ]}
    assert evaluate_acceptance(checks, tmp_path)['status'] == 'passed'
    proof.write_text('changed after review', encoding='utf-8')
    assert evaluate_acceptance(checks, tmp_path)['status'] == 'failed'
    checks['checks'] = []
    assert evaluate_acceptance(checks, tmp_path)['status'] == 'unverified'


def test_unknown_duplicate_and_empty_evidence_cannot_pass_gate(tmp_path):
    from scripts.edit_workflow import evaluate_acceptance
    for rows in ([{'id': 'invented', 'status': 'passed'}],
                 [{'id': 'story', 'status': 'passed', 'evidence': []}],
                 [{'id': 'story', 'status': 'unverified'}] * 2):
        result = evaluate_acceptance({'version': 1, 'target': 'id', 'checks': rows}, tmp_path)
        assert result['status'] == 'failed'


def test_cli_invalid_json_has_error_exit_without_traceback(tmp_path):
    bad = tmp_path / 'bad.json'
    bad.write_text('{', encoding='utf-8')
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/edit_workflow.py'),
                             'validate', str(bad)], capture_output=True, text=True)
    assert result.returncode == 2
    assert 'Traceback' not in result.stderr


def test_prepare_reuses_probe_but_invalidates_changed_files_and_keeps_plan(tmp_path):
    from scripts.prepare_edit import prepare
    sources = tmp_path / 'source'
    sources.mkdir()
    media = sources / 'กล้อง.mp4'
    media.write_bytes(b'first')
    output = sources / 'review'
    calls = []

    def probe(path):
        calls.append(path)
        return {'streams': [{'codec_type': 'video', 'avg_frame_rate': '30/1',
                             'r_frame_rate': '30/1', 'nb_frames': '300'}],
                'format': {'duration': '10'}}

    first = prepare(sources, output, probe=probe, probe_key='test-v1')
    assert first['status'] == 'prepared'
    assert len(calls) == 1
    draft = json.loads((output / 'edit_decisions.json').read_text(encoding='utf-8'))
    assert draft['timeline'] is None  # No assumed aspect ratio or FPS.
    assert draft['sources'][0]['frame_count'] == 300
    (output / 'edit_decisions.json').write_text('user-owned plan', encoding='utf-8')
    prepare(sources, output, probe=probe, probe_key='test-v1')
    assert len(calls) == 1
    assert (output / 'edit_decisions.json').read_text(encoding='utf-8') == 'user-owned plan'
    media.write_bytes(b'changed media')
    prepare(sources, output, probe=probe, probe_key='test-v1')
    assert len(calls) == 2
    prepare(sources, output, probe=probe, probe_key='test-v2')
    assert len(calls) == 3
    assert media.read_bytes() == b'changed media'


def test_prepare_refuses_source_output_collision_and_unowned_folder(tmp_path):
    from scripts.prepare_edit import prepare
    with pytest.raises(ValueError):
        prepare(tmp_path, tmp_path, probe=lambda p: {}, probe_key='test')
    output = tmp_path / 'review'
    output.mkdir()
    (output / 'important.txt').write_text('keep')
    with pytest.raises(ValueError):
        prepare(tmp_path, output, probe=lambda p: {}, probe_key='test')
    assert (output / 'important.txt').read_text() == 'keep'


def test_failed_probe_is_incomplete_and_retried_not_cached(tmp_path):
    from scripts.prepare_edit import prepare
    media = tmp_path / 'source'
    media.mkdir()
    (media / 'bad.mp4').write_bytes(b'bad')
    def fail(path):
        raise RuntimeError('probe failed')
    result = prepare(media, tmp_path / 'output', probe=fail, probe_key='test')
    assert result['status'] == 'incomplete'
    assert result['files'][0]['error']
    result = prepare(media, tmp_path / 'output', probe=lambda p: {'streams': [
        {'codec_type': 'audio'}]}, probe_key='test')
    assert result['status'] == 'prepared'


def test_prepare_uses_existing_caption_lint_and_requires_cues(tmp_path):
    from scripts.prepare_edit import prepare
    media = tmp_path / 'source'
    media.mkdir()
    (media / 'audio.wav').write_bytes(b'input')
    srt = tmp_path / 'captions.srt'
    srt.write_text('1\n00:00:00,000 --> 00:00:02,000\nสวัสดี\n', encoding='utf-8')
    result = prepare(media, tmp_path / 'output', srt=srt,
                     probe=lambda p: {'streams': [{'codec_type': 'audio'}]}, probe_key='test')
    assert result['caption_lint']['status'] == 'failed'
    srt.write_text('not a subtitle', encoding='utf-8')
    result = prepare(media, tmp_path / 'output', srt=srt,
                     probe=lambda p: {'streams': [{'codec_type': 'audio'}]}, probe_key='test')
    assert result['caption_lint']['status'] == 'failed'


@pytest.mark.parametrize('data', [
    {'version': True, 'target': 'id', 'checks': []},
    {'version': 1, 'target': 'id', 'checks': [{'id': [], 'status': 'passed'}]},
])
def test_malformed_acceptance_returns_failure_instead_of_crash(data, tmp_path):
    from scripts.edit_workflow import evaluate_acceptance
    assert evaluate_acceptance(data, tmp_path)['status'] == 'failed'


@pytest.mark.skipif(not shutil.which('ffprobe'), reason='ffprobe not installed')
def test_real_prepare_cli_probes_synthetic_audio_and_reuses_cache(tmp_path):
    source = tmp_path / 'media'
    source.mkdir()
    with wave.open(str(source / 'synthetic.wav'), 'wb') as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(8000)
        audio.writeframes(b'\x00\x00' * 8000)
    output = tmp_path / 'review'
    cmd = [sys.executable, str(ROOT / 'scripts/prepare_edit.py'),
           str(source), '--out-dir', str(output)]
    first = subprocess.run(cmd, capture_output=True, text=True)
    assert first.returncode == 0, first.stderr
    manifest = json.loads((output / 'intake.json').read_text(encoding='utf-8'))
    assert manifest['files'][0]['probe']['streams'][0]['sample_rate'] == '8000'
    second = subprocess.run(cmd, capture_output=True, text=True)
    assert second.returncode == 0, second.stderr
    assert json.loads(second.stdout)['cache_hits'] == 1
    invalid_draft = subprocess.run([sys.executable, str(ROOT / 'scripts/edit_workflow.py'),
        'validate', str(output / 'edit_decisions.json')], capture_output=True, text=True)
    assert invalid_draft.returncode == 1


def test_corrupt_cache_is_controlled_error_and_refresh_can_recover(tmp_path):
    from scripts.prepare_edit import prepare
    source = tmp_path / 'media'
    source.mkdir()
    (source / 'test.wav').write_bytes(b'source')
    output = tmp_path / 'out'
    probe = lambda path: {'streams': [{'codec_type': 'audio'}]}
    prepare(source, output, probe=probe, probe_key='v1')
    for bad in ([], {'files': [{}]}, {'files': [None]}):
        (output / 'intake.json').write_text(json.dumps(bad), encoding='utf-8')
        with pytest.raises(ValueError, match='cache'):
            prepare(source, output, probe=probe, probe_key='v1')
        assert prepare(source, output, probe=probe, probe_key='v1', refresh=True)['status'] == 'prepared'


@pytest.mark.parametrize('streams', [None, [None], [], 'video'])
def test_nested_bad_probe_is_never_a_prepared_cache(streams, tmp_path):
    from scripts.prepare_edit import prepare
    source = tmp_path / 'media'
    source.mkdir()
    (source / 'test.wav').write_bytes(b'source')
    output = tmp_path / 'out'
    good_probe = lambda p: {'streams': [{'codec_type': 'audio'}]}
    prepare(source, output, probe=good_probe, probe_key='v1')
    cached = json.loads((output / 'intake.json').read_text(encoding='utf-8'))
    cached['files'][0]['probe'] = {'streams': streams}
    (output / 'intake.json').write_text(json.dumps(cached), encoding='utf-8')
    with pytest.raises(ValueError, match='cache'):
        prepare(source, output, probe=good_probe, probe_key='v1')
    result = prepare(source, output, probe=lambda p: {'streams': streams},
                     probe_key='v1', refresh=True)
    assert result['status'] == 'incomplete'


def test_cloud_reparse_points_remain_eligible_but_junctions_do_not():
    from types import SimpleNamespace
    from scripts.prepare_edit import _directory_link
    def entry(tag):
        return SimpleNamespace(is_symlink=lambda: False,
            stat=lambda **kwargs: SimpleNamespace(st_reparse_tag=tag, st_file_attributes=1024))
    assert _directory_link(entry(0xA0000003))  # IO_REPARSE_TAG_MOUNT_POINT
    assert not _directory_link(entry(0x9000001A))  # IO_REPARSE_TAG_CLOUD


def test_partially_broken_srt_is_not_a_lint_pass(tmp_path):
    from scripts.prepare_edit import prepare
    source = tmp_path / 'media'
    source.mkdir()
    (source / 'test.wav').write_bytes(b'source')
    srt = tmp_path / 'captions.srt'
    srt.write_text('1\n00:00:00,000 --> 00:00:01,000\nดี\n\n'
                   '2\n00:bad --> 00:00:02,000\nเสีย\n', encoding='utf-8')
    result = prepare(source, tmp_path / 'out', srt=srt,
        probe=lambda p: {'streams': [{'codec_type': 'audio'}]}, probe_key='v1')
    assert result['caption_lint']['status'] == 'failed'


def test_contact_sheet_cache_tracks_external_frames_and_validates_receipt(tmp_path):
    from PIL import Image
    from scripts.prepare_edit import prepare
    source = tmp_path / 'media'
    source.mkdir()
    (source / 'test.wav').write_bytes(b'source')
    frames = tmp_path / 'analysis'
    frames.mkdir()
    external = tmp_path / 'external.png'
    Image.new('RGB', (80, 40), 'red').save(external)
    (frames / 'visual.json').write_text(json.dumps({'frame_paths': [str(external)]}), encoding='utf-8')
    output = tmp_path / 'out'
    kwargs = {'frames_dir': frames, 'probe': lambda p: {'streams': [{'codec_type': 'audio'}]}, 'probe_key': 'v1'}
    first = prepare(source, output, **kwargs)['contact_sheets']
    assert prepare(source, output, **kwargs)['contact_sheets']['files'] == first['files']
    Image.new('RGB', (100, 60), 'blue').save(external)
    second = prepare(source, output, **kwargs)['contact_sheets']
    assert second['files'][0]['path'] != first['files'][0]['path']
    receipt = Path(second['files'][0]['path']).parent / 'receipt.json'
    receipt.write_text('[]', encoding='utf-8')
    with pytest.raises(ValueError, match='receipt'):
        prepare(source, output, **kwargs)


@pytest.mark.skipif(sys.platform != 'win32', reason='Windows junction behavior')
def test_intake_does_not_follow_windows_directory_junction(tmp_path):
    from scripts.prepare_edit import prepare
    source = tmp_path / 'source'
    source.mkdir()
    (source / 'own.wav').write_bytes(b'own')
    outside = tmp_path / 'other'
    outside.mkdir()
    (outside / 'outside.wav').write_bytes(b'outside')
    link = source / 'junction'
    created = subprocess.run(['cmd', '/c', 'mklink', '/J', str(link), str(outside)],
                             capture_output=True, text=True)
    assert created.returncode == 0, created.stderr
    try:
        result = prepare(source, tmp_path / 'out',
            probe=lambda p: {'streams': [{'codec_type': 'audio'}]}, probe_key='v1')
        assert len(result['files']) == 1
        assert result['files'][0]['path'].endswith('own.wav')
    finally:
        link.rmdir()  # Removes only this junction, never its target.
