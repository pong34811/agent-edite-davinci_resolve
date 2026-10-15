"""Validate offline edit plans and reconcile evidence against the house gate.

MCP-GAP: media_analysis/timeline/render do not consume this repository's JSON
contracts. This helper is offline only; no Resolve API, imports or edits.
The shipped schema uses a small explicit JSON Schema subset checked below.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from fractions import Fraction
from pathlib import Path

CONTRACTS = Path(__file__).resolve().parents[1] / 'docs/contracts'


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def load_gate():
    return read_json(CONTRACTS / 'acceptance-gate.json')


def _shape(value, schema, location='$'):
    """Validate only the keywords used by the shipped, trusted plan schema."""
    types = {'object': dict, 'array': list, 'string': str, 'integer': int}
    expected = types[schema['type']]
    if not isinstance(value, expected) or (expected is int and isinstance(value, bool)):
        return [f'{location}: expected {schema["type"]}']
    errors = []
    if 'enum' in schema and value not in schema['enum']:
        errors.append(f'{location}: unsupported value')
    if isinstance(value, dict):
        properties = schema.get('properties', {})
        for key in schema.get('required', []):
            if key not in value:
                errors.append(f'{location}.{key}: required')
        if schema.get('additionalProperties') is False:
            errors.extend(f'{location}.{key}: unsupported field' for key in value.keys() - properties.keys())
        for key in value.keys() & properties.keys():
            errors.extend(_shape(value[key], properties[key], f'{location}.{key}'))
    elif isinstance(value, list):
        if len(value) < schema.get('minItems', 0):
            errors.append(f'{location}: too few items')
        for index, item in enumerate(value):
            errors.extend(_shape(item, schema['items'], f'{location}[{index}]'))
    elif isinstance(value, str):
        if len(value.strip()) < schema.get('minLength', 0):
            errors.append(f'{location}: empty text')
        if 'pattern' in schema and not re.fullmatch(schema['pattern'], value):
            errors.append(f'{location}: invalid format (use an integer or rational FPS string)')
    elif 'minimum' in schema and value < schema['minimum']:
        errors.append(f'{location}: below minimum')
    return errors


def validate_decisions(data, base_dir=Path('.')):
    errors = _shape(data, read_json(CONTRACTS / 'edit-decisions.schema.json'))
    placements = []
    result = {'status': 'failed', 'errors': errors, 'placements': placements,
              'live_verified': False,
              'limit': 'Plan validation only; no media, meaning, sync, native cues or live conform verified'}
    if errors:
        return result
    timeline = data['timeline']
    sources, paths = {}, set()
    try:
        timeline_fps = Fraction(timeline['fps'])
        if timeline_fps <= 0:
            raise ValueError('timeline FPS must be positive')
        for source in data['sources']:
            fps = Fraction(source['fps'])
            if fps <= 0:
                raise ValueError(f'{source["id"]}: source FPS must be positive')
            canonical = os.path.normcase(str((Path(base_dir) / source['path']).resolve()))
            if source['id'] in sources or canonical in paths:
                errors.append(f'{source["id"]}: duplicate source ID or path')
            sources[source['id']] = source
            paths.add(canonical)
    except (ValueError, ZeroDivisionError, OSError) as exc:
        errors.append(str(exc))
        return result
    ids, tracks = set(), {}
    for edit in data['edits']:
        ident = edit['id']
        if ident in ids:
            errors.append(f'{ident}: duplicate edit ID')
        ids.add(ident)
        source = sources.get(edit['source_id'])
        if source is None:
            errors.append(f'{ident}: unknown source')
            continue
        start, end, record = edit['in_frame'], edit['out_frame'], edit['record_frame']
        if not 0 <= start < end <= source['frame_count']:
            errors.append(f'{ident}: source range outside [0, frame_count)')
            continue
        if record < timeline['start_frame']:
            errors.append(f'{ident}: before visible timeline start')
        length = Fraction(end - start) * timeline_fps / Fraction(source['fps'])
        # Round half up once; never round either FPS to a nominal integer.
        duration = (2 * length.numerator + length.denominator) // (2 * length.denominator)
        if duration < 1:
            errors.append(f'{ident}: duration rounds to zero record frames')
        key = (edit['track_kind'], edit['track_index'])
        tracks.setdefault(key, []).append((record, record + duration, ident))
        placements.append({'id': ident, 'record_start_frame': record,
                           'record_end_frame': record + duration})
    for intervals in tracks.values():
        furthest_end = -1
        for start, end, ident in sorted(intervals):
            if start < furthest_end:
                errors.append(f'{ident}: overlaps another edit on the same track')
            furthest_end = max(furthest_end, end)
    result['status'] = 'failed' if errors else 'passed'
    return result


def evaluate_acceptance(data, base_dir):
    gate = load_gate()
    errors, rows = [], []
    if not isinstance(data, dict) or type(data.get('version')) is not int or data['version'] != 1 or not isinstance(data.get('target'), str) or not data['target'].strip() or not isinstance(data.get('checks'), list):
        return {'status': 'failed', 'errors': ['Expected version 1, target and checks list'], 'checks': []}
    allowed = {check['id'] for check in gate['checks']}
    supplied = {}
    for check in data['checks']:
        if not isinstance(check, dict) or not isinstance(check.get('id'), str) or check['id'] not in allowed:
            errors.append('Unknown or invalid check ID')
            continue
        ident = check['id']
        if ident in supplied:
            errors.append(f'{ident}: duplicate check')
        supplied[ident] = check
    for requirement in gate['checks']:
        ident = requirement['id']
        check = supplied.get(ident, {'status': 'unverified'})
        status = check.get('status')
        issues = []
        if status not in ('passed', 'failed', 'unverified'):
            issues.append('invalid status')
        if status == 'passed':
            for field in ('reviewer', 'note'):
                if not isinstance(check.get(field), str) or not check[field].strip():
                    issues.append(f'{field} required for a passed check')
            evidence = check.get('evidence')
            if not isinstance(evidence, list) or not evidence:
                issues.append('nonempty evidence list required')
            else:
                for entry in evidence:
                    try:
                        if not isinstance(entry, dict) or not isinstance(entry.get('path'), str) or not entry['path'].strip():
                            raise ValueError('invalid evidence path')
                        path = Path(base_dir) / entry['path']
                        if not path.is_file() or path.stat().st_size == 0:
                            raise ValueError('evidence missing or empty')
                        if entry.get('sha256') != file_sha256(path):
                            raise ValueError('evidence hash missing or changed')
                    except (ValueError, OSError) as exc:
                        issues.append(str(exc))
        if issues:
            errors.extend(f'{ident}: {issue}' for issue in issues)
            status = 'failed'
        rows.append({'id': ident, 'lane': requirement['lane'], 'status': status})
    status = ('failed' if errors or any(row['status'] == 'failed' for row in rows)
              else 'unverified' if any(row['status'] != 'passed' for row in rows) else 'passed')
    return {'version': 1, 'target': data['target'], 'status': status,
            'checks': rows, 'errors': errors,
            'limit': 'Reconciles reviewer claims and evidence hashes; does not judge evidence content or current Resolve state'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('action', choices=['validate', 'accept', 'hash'])
    parser.add_argument('input', type=Path)
    parser.add_argument('--out', type=Path, help='New report file; never overwrite')
    args = parser.parse_args(argv)
    try:
        if args.action == 'hash':
            report = {'path': str(args.input.resolve()), 'sha256': file_sha256(args.input)}
        else:
            data = read_json(args.input)
            report = (validate_decisions(data, args.input.resolve().parent) if args.action == 'validate'
                      else evaluate_acceptance(data, args.input.resolve().parent))
        payload = json.dumps(report, ensure_ascii=False, indent=2)
        if args.out:
            with args.out.open('x', encoding='utf-8') as handle:
                handle.write(payload + '\n')
        print(payload)
        return 0 if report.get('status', 'passed') == 'passed' else 1
    except (OSError, ValueError) as exc:
        parser.exit(2, f'error: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
