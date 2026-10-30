"""Offline evidence-report validator; no classification, network or Resolve access.

CLI: py -3.12 scripts/channel_intelligence.py validate REPORT.json
Python: validate_report(report_dict) -> {status, errors, limitations, live_verified}.
Example input contract: see tests/test_channel_intelligence.py:report().
Ranges are half-open, nonnegative frame numbers or seconds; FPS is required
for frame ranges. Source and timeline are independent, with an explicit mapping.
Validation checks report consistency, not truth, sufficiency, rights or freshness
of the underlying evidence. No report is an approval to edit or publish.
"""
import argparse
from datetime import date
from fractions import Fraction
import ipaddress
import json
import math
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlparse


def validate_report(data):
    errors = []
    limitations = ['Offline structural validation only; evidence, permissions, source content and live state are not verified.']

    def error(path, message):
        errors.append(f'{path}: {message}')

    def obj(value, path):
        if not isinstance(value, dict):
            error(path, 'expected object')
            return {}
        return value

    def text(value, path):
        if not isinstance(value, str) or not value.strip():
            error(path, 'nonempty text required')
            return False
        return True

    def day(value, path):
        try:
            if not isinstance(value, str) or len(value) != 10:
                raise ValueError()
            return date.fromisoformat(value)
        except ValueError:
            error(path, 'expected ISO date YYYY-MM-DD')
            return None

    def url(value, path):
        if text(value, path):
            try:
                if any(c.isspace() or unicodedata.category(c) == 'Cc' or c == '\\' for c in value):
                    raise ValueError('invalid URL character')
                if re.search(r'%(?![0-9a-fA-F]{2})', value):
                    raise ValueError('invalid percent escape')
                parsed = urlparse(value)
                valid = (parsed.scheme in ('http', 'https') and bool(parsed.hostname)
                         and parsed.netloc.count('@') <= 1)
                if valid:
                    parsed.port  # Force validation of malformed ports.
                    host = parsed.hostname
                    if ':' in host:
                        ipaddress.IPv6Address(host)
                    else:
                        ascii_host = host.encode('idna').decode('ascii').removesuffix('.')
                        labels = ascii_host.split('.')
                        valid = (len(ascii_host) <= 253 and all(
                            re.fullmatch(r'[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?', label)
                            for label in labels))
            except (ValueError, UnicodeError):
                valid = False
            if not valid:
                error(path, 'expected HTTP(S) URL')

    def finite_number(value):
        if type(value) not in (int, float):
            return False
        try:
            return math.isfinite(value)
        except OverflowError:
            return False

    def array(value, path):
        if not isinstance(value, list):
            error(path, 'expected array')
            return []
        return value

    def interval(value, path):
        value = obj(value, path)
        unit = value.get('unit')
        if unit not in ('frames', 'seconds'):
            error(path + '.unit', 'expected frames or seconds')
        start, end = value.get('start'), value.get('end')
        valid = lambda n: finite_number(n) and n >= 0
        if not valid(start) or not valid(end) or end <= start:
            error(path, 'expected nonnegative start < end')
        elif unit == 'frames' and (type(start) is not int or type(end) is not int):
            error(path, 'frame boundaries must be integers')
        if unit == 'frames':
            try:
                fps = value.get('fps')
                if not isinstance(fps, str) or Fraction(fps) <= 0:
                    raise ValueError()
            except (ValueError, ZeroDivisionError):
                error(path + '.fps', 'expected positive rational string')
        return value

    root = obj(data, '$')
    if type(root.get('version')) is not int or root.get('version') != 1:
        error('$.version', 'expected 1')
    target = obj(root.get('target'), '$.target')
    for key in ('project_id', 'timeline_id', 'revision'):
        text(target.get(key), '$.target.' + key)
    segments = array(root.get('segments'), '$.segments')
    if not segments:
        error('$.segments', 'at least one segment required')
    for i, segment in enumerate(segments):
        p = f'$.segments[{i}]'
        segment = obj(segment, p)
        for key in ('media_id', 'source_path', 'mapping'):
            text(segment.get(key), p + '.' + key)
        clocks = {key: interval(segment.get(key), p + '.' + key) for key in ('source', 'timeline')}
        for kind in ('game', 'channel'):
            q = p + '.' + kind
            identity = obj(segment.get(kind), q)
            status = identity.get('status')
            if status not in ('confirmed', 'candidate', 'unknown', 'conflict'):
                error(q + '.status', 'invalid status')
            if status in ('confirmed', 'candidate'):
                text(identity.get('value'), q + '.value')
            elif identity.get('value') is not None:
                error(q + '.value', 'unknown/conflict must use null')
            evidence = array(identity.get('evidence'), q + '.evidence')
            if status in ('confirmed', 'candidate') and not evidence:
                error(q + '.evidence', 'evidence required')
            if status == 'conflict' and len(evidence) < 2:
                error(q + '.evidence', 'conflict requires at least two observations')
            if status in ('unknown', 'conflict'):
                text(identity.get('reason'), q + '.reason')
            for j, entry in enumerate(evidence):
                ep = f'{q}.evidence[{j}]'
                entry = obj(entry, ep)
                for key in ('modality', 'observation', 'limitations'):
                    text(entry.get(key), ep + '.' + key)
                base = entry.get('timebase')
                at = entry.get('at')
                if not isinstance(base, str) or base not in clocks:
                    error(ep + '.timebase', 'expected source or timeline')
                elif not finite_number(at):
                    error(ep + '.at', 'expected numeric timestamp')
                else:
                    clock = clocks[base]
                    start, end = clock.get('start'), clock.get('end')
                    if clock.get('unit') == 'frames' and type(at) is not int:
                        error(ep + '.at', 'frame timestamp must be an integer')
                    if type(start) in (int, float) and type(end) in (int, float) and not start <= at < end:
                        error(ep + '.at', 'outside declared range')
    research = obj(root.get('research'), '$.research')
    as_of = day(research.get('as_of'), '$.research.as_of')
    status = research.get('status')
    if status not in ('current', 'unavailable'):
        error('$.research.status', 'expected current or unavailable')
    if status == 'unavailable':
        text(research.get('reason'), '$.research.reason')
        limitations.append('Research reported unavailable; older sources are not current.')
    sources = array(research.get('sources'), '$.research.sources')
    if status == 'current' and not sources:
        error('$.research.sources', 'current research requires sources')
    for i, source in enumerate(sources):
        p = f'$.research.sources[{i}]'
        source = obj(source, p)
        url(source.get('url'), p + '.url')
        for key in ('title', 'claim'):
            text(source.get(key), p + '.' + key)
        access = day(source.get('access_date'), p + '.access_date')
        if access and as_of and access > as_of:
            error(p + '.access_date', 'after as-of date')
        if status == 'current' and access and as_of and access != as_of:
            error(p + '.access_date', 'current source must be accessed on as-of date')
    text(research.get('query'), '$.research.query')
    search_date = day(research.get('search_date'), '$.research.search_date')
    if search_date and as_of and search_date > as_of:
        error('$.research.search_date', 'after as-of date')
    if research.get('format') not in ('Shorts', 'long-form'):
        error('$.research.format', 'expected Shorts or long-form')
    comparators = array(research.get('comparators'), '$.research.comparators')
    if len(comparators) < 3:
        text(research.get('shortfall_reason'), '$.research.shortfall_reason')
        limitations.append(f'Only {len(comparators)} comparators reported; relevance is not verified.')
    for i, comparator in enumerate(comparators):
        p = f'$.research.comparators[{i}]'
        comparator = obj(comparator, p)
        url(comparator.get('url'), p + '.url')
        for key in ('title', 'inspected', 'limitations'):
            text(comparator.get(key), p + '.' + key)
        published = day(comparator.get('publication_date'), p + '.publication_date')
        if published and as_of and published > as_of:
            error(p + '.publication_date', 'after as-of date')
    for key in ('analytics', 'transcript'):
        if research.get(key) not in ('available', 'unavailable', 'unknown'):
            error('$.research.' + key, 'expected available, unavailable or unknown')
    permission = obj(research.get('permission'), '$.research.permission')
    for key in ('local_inspection', 'external_transfer', 'analytics'):
        if permission.get(key) not in ('granted', 'not granted', 'unknown'):
            error('$.research.permission.' + key, 'expected granted, not granted or unknown')
    if permission.get('analytics') == 'granted' and research.get('analytics') == 'unknown':
        error('$.research.analytics', 'state availability explicitly when permission is granted')
    if research.get('analytics') == 'available' and permission.get('analytics') != 'granted':
        error('$.research.analytics', 'available analytics requires stated permission')
    return {'status': 'failed' if errors else 'passed', 'errors': errors,
            'limitations': limitations, 'live_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['validate'])
    parser.add_argument('report', help='UTF-8 JSON report path')
    args = parser.parse_args()
    try:
        data = json.loads(Path(args.report).read_text(encoding='utf-8-sig'))
        result = validate_report(data)
    except (OSError, UnicodeError, ValueError) as exc:
        result = {'status': 'failed', 'errors': [str(exc)], 'limitations': [], 'live_verified': False}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
