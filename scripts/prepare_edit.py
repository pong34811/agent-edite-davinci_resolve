"""Prepare cached media intake, a draft plan, Thai lint and contact sheets offline.

MCP-GAP: media_analysis does not orchestrate the repository's offline JSON
contracts and existing caption_lint/contact_sheet helpers. No Resolve control.
Cache identity is resolved path + size + mtime_ns + probe/tool version; use
--refresh if source metadata was preserved after replacing file contents.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat as stat_module
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.caption_lint import lint, parse_srt
from scripts.edit_workflow import file_sha256, load_gate, read_json

MEDIA_EXTENSIONS = {'.mp4', '.mov', '.mkv', '.avi', '.webm', '.m4v', '.mxf',
                    '.wav', '.mp3', '.m4a', '.flac', '.aif', '.aiff', '.ogg', '.ts'}
OWNER = 'prepare_edit_v1'


def _write_json(path, data):
    if path.is_symlink():
        raise ValueError(f'Refusing symlink output: {path}')
    # Exclusive staging prevents unrelated temporary files from being replaced.
    temporary = path.with_name(path.name + '.tmp')
    with temporary.open('x', encoding='utf-8') as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    temporary.replace(path)


def probe_media(path):
    process = subprocess.run(['ffprobe', '-v', 'error', '-show_format', '-show_streams',
                              '-of', 'json', str(path)], capture_output=True,
                             text=True, encoding='utf-8', errors='replace', timeout=60,
                             check=True)
    return json.loads(process.stdout)


def _valid_probe(value):
    return (isinstance(value, dict) and isinstance(value.get('streams'), list)
            and all(isinstance(stream, dict) for stream in value['streams'])
            and any(stream.get('codec_type') in ('audio', 'video') for stream in value['streams']))


def _directory_link(entry):
    # Cloud placeholders are also reparse points; keep those eligible to read.
    tag = getattr(entry.stat(follow_symlinks=False), 'st_reparse_tag', 0)
    return entry.is_symlink() or tag in (
        getattr(stat_module, 'IO_REPARSE_TAG_MOUNT_POINT', 0xA0000003),
        getattr(stat_module, 'IO_REPARSE_TAG_SYMLINK', 0xA000000C))


def _files(root, output):
    """Use scandir for Drive paths; skip links, metadata folders and own output."""
    with os.scandir(root) as entries:
        for entry in sorted(entries, key=lambda item: item.name.casefold()):
            path = Path(entry.path)
            if _directory_link(entry) or path.resolve() == output:
                continue
            if entry.is_dir(follow_symlinks=False):
                if entry.name not in ('.git', '__pycache__'):
                    yield from _files(path, output)
            elif entry.is_file(follow_symlinks=False) and path.suffix.lower() in MEDIA_EXTENSIONS:
                yield path


def _draft_source(row):
    video = next((stream for stream in row.get('probe', {}).get('streams', [])
                  if stream.get('codec_type') == 'video'), {})
    fps = None
    try:
        average, nominal = Fraction(video['avg_frame_rate']), Fraction(video['r_frame_rate'])
        if average == nominal and average > 0:
            fps = str(average)
    except (KeyError, ValueError, ZeroDivisionError, TypeError):
        pass
    count = str(video.get('nb_frames', ''))
    return {'id': row['id'], 'path': row['path'], 'fps': fps,
            'frame_count': int(count) if count.isdecimal() and int(count) > 0 else None}


def _sheets(frames_dir, output):
    from scripts.contact_sheet import build_sheets, load_frames
    frames_dir = Path(frames_dir).resolve(strict=True)
    if frames_dir == output or output in frames_dir.parents or frames_dir in output.parents:
        raise ValueError('Contact sheet input and output must be separate directory trees')
    identities = [(str(path.relative_to(frames_dir)), path.stat().st_size, path.stat().st_mtime_ns)
                  for path in sorted(frames_dir.rglob('*')) if path.is_file()]
    # Analysis JSON may reference absolute frame paths outside frames_dir.
    selected_paths, _ = load_frames(str(frames_dir))
    identities.extend((str(Path(path).resolve()), Path(path).stat().st_size,
                       Path(path).stat().st_mtime_ns) for path in selected_paths)
    key = hashlib.sha256(json.dumps([str(frames_dir), identities,
        file_sha256(Path(__file__).with_name('contact_sheet.py'))]).encode()).hexdigest()[:20]
    folder = output / ('sheets-' + key)
    receipt = folder / 'receipt.json'
    if receipt.is_file():
        saved = read_json(receipt)
        if (not isinstance(saved, dict) or saved.get('status') not in ('prepared', 'unverified')
                or not isinstance(saved.get('frame_count'), int)
                or not isinstance(saved.get('files'), list)
                or (saved['status'] == 'prepared' and not saved['files'])
                or any(not isinstance(row, dict) or not isinstance(row.get('path'), str)
                       or not isinstance(row.get('sha256'), str) for row in saved['files'])):
            raise ValueError('Invalid contact sheet cache receipt; use a fresh output directory')
        if all(Path(row['path']).is_file() and file_sha256(row['path']) == row['sha256']
               for row in saved['files']):
            return saved
        raise ValueError('Cached contact sheet changed; use a fresh output directory')
    sheets, frame_count = build_sheets(str(frames_dir), str(folder))
    result = {'status': 'prepared' if frame_count else 'unverified', 'frame_count': frame_count,
              'limit': 'Sampled stills only; not continuous visual QC',
              'files': [{'path': path, 'sha256': file_sha256(path)} for path, _, _ in sheets]}
    folder.mkdir(parents=True, exist_ok=True)
    _write_json(receipt, result)
    return result


def prepare(root, output, *, probe=None, probe_key=None, srt=None, frames_dir=None, refresh=False):
    root = Path(root).resolve(strict=True)
    requested_output = Path(output)
    if requested_output.is_symlink():
        raise ValueError('Output must not be a symlink')
    output = requested_output.resolve()
    if not root.is_dir() or root == output or output in root.parents:
        raise ValueError('Use a separate output directory, never the source root or its ancestor')
    owner_path = output / '.prepare-edit.json'
    if output.exists() and any(output.iterdir()):
        if not owner_path.is_file() or owner_path.is_symlink():
            raise ValueError('Nonempty output directory is not owned by prepare_edit')
        owner = read_json(owner_path)
        if owner != {'owner': OWNER, 'root': str(root)}:
            raise ValueError('Output directory belongs to a different source or tool')
    for name in ('intake.json', 'edit_decisions.json', 'acceptance_checks.json'):
        if (output / name).is_symlink():
            raise ValueError(f'Refusing symlink output: {name}')
    if probe is None:
        probe = probe_media
    if probe_key is None:
        version = subprocess.run(['ffprobe', '-version'], capture_output=True, text=True,
                                 encoding='utf-8', errors='replace', timeout=15, check=True)
        probe_key = version.stdout.splitlines()[0]
    cache_key = probe_key + ':' + file_sha256(Path(__file__))
    previous = (read_json(output / 'intake.json')
                if not refresh and (output / 'intake.json').is_file() else {'files': []})
    if (not isinstance(previous, dict) or not isinstance(previous.get('files'), list)
            or any(not isinstance(row, dict) or not isinstance(row.get('path'), str)
                   or not isinstance(row.get('fingerprint'), dict)
                   or ('probe' in row and not _valid_probe(row['probe']))
                   for row in previous['files'])):
        raise ValueError('Invalid intake cache; rerun with --refresh')
    cached = {row['path']: row for row in previous.get('files', [])}
    rows, reused = [], 0
    for path in _files(root, output):
        stat = path.stat()
        fingerprint = {'size': stat.st_size, 'mtime_ns': stat.st_mtime_ns, 'probe_key': cache_key}
        old = cached.get(str(path), {})
        row = {'id': hashlib.sha256(os.path.normcase(str(path)).encode('utf-8')).hexdigest()[:20],
               'path': str(path), 'fingerprint': fingerprint}
        if not refresh and old.get('fingerprint') == fingerprint and old.get('probe') and not old.get('error'):
            row['probe'] = old['probe']
            reused += 1
        else:
            try:
                before = (stat.st_size, stat.st_mtime_ns)
                row['probe'] = probe(path)
                after = path.stat()
                if before != (after.st_size, after.st_mtime_ns):
                    raise ValueError('Source changed during probe; retry')
                if not _valid_probe(row['probe']):
                    raise ValueError('Invalid probe data or no audio/video stream found')
            except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
                row.pop('probe', None)
                row['error'] = str(exc)
        rows.append(row)
    report = {'version': 1, 'source_root': str(root), 'files': rows, 'cache_hits': reused,
              'status': 'prepared' if rows and all(not row.get('error') for row in rows) else 'incomplete',
              'live_verified': False,
              'limit': 'Intake only. FPS/frame counts need Resolve confirmation; no story or audio quality verdict'}
    if srt:
        text = Path(srt).read_text(encoding='utf-8-sig')
        cues = list(parse_srt(text))
        rules = load_gate()['caption_rules']
        problems = lint(text, rules['max_thai_characters'], rules['max_duration_seconds'])
        if not cues:
            problems.append(('?', 'No subtitle cues parsed'))
        blocks = re.split(r'\n\s*\n', text.replace('\r\n', '\n').replace('\r', '\n').strip())
        for number, block in enumerate(blocks, 1):
            if block.strip() and (len(list(parse_srt(block))) != 1 or block.count('-->') != 1):
                problems.append((str(number), 'Malformed or unparsed subtitle block'))
        report['caption_lint'] = {'status': 'failed' if problems else 'passed',
            'cue_count': len(cues), 'problems': problems,
            'limit': 'Text lint only; words, speech timing, native placement and readability need review'}
        if problems:
            report['status'] = 'incomplete'
    output.mkdir(parents=True, exist_ok=True)
    if not owner_path.exists():
        _write_json(owner_path, {'owner': OWNER, 'root': str(root)})
    if frames_dir:
        report['contact_sheets'] = _sheets(frames_dir, output)
        if report['contact_sheets']['status'] != 'prepared':
            report['status'] = 'incomplete'
    # Never overwrite the editor's draft or review claims when refreshing intake.
    drafts = {
        'edit_decisions.json': {'version': 1, 'timeline': None,
            'sources': [_draft_source(row) for row in rows if not row.get('error')], 'edits': []},
        'acceptance_checks.json': {'version': 1, 'target': '', 'checks': [
            {'id': check['id'], 'status': 'unverified', 'reviewer': '', 'note': '', 'evidence': []}
            for check in load_gate()['checks']]},
    }
    for name, draft in drafts.items():
        path = output / name
        if not path.exists():
            with path.open('x', encoding='utf-8') as handle:
                json.dump(draft, handle, ensure_ascii=False, indent=2)
                handle.write('\n')
    _write_json(output / 'intake.json', report)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('source_root', type=Path)
    parser.add_argument('--out-dir', required=True, type=Path)
    parser.add_argument('--srt', type=Path)
    parser.add_argument('--frames-dir', type=Path, help='Existing media_analysis clip directory; no extraction')
    parser.add_argument('--refresh', action='store_true', help='Ignore probe cache')
    args = parser.parse_args(argv)
    try:
        report = prepare(args.source_root, args.out_dir, srt=args.srt,
                         frames_dir=args.frames_dir, refresh=args.refresh)
        print(json.dumps({'status': report['status'], 'files': len(report['files']),
                          'cache_hits': report['cache_hits'], 'output': str(args.out_dir.resolve())},
                         ensure_ascii=False, indent=2))
        return 0 if report['status'] == 'prepared' else 1
    except (OSError, ValueError, ImportError, subprocess.SubprocessError) as exc:
        parser.exit(2, f'error: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
