import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def report():
    return {
        'version': 1,
        'target': {'project_id': 'p', 'timeline_id': 't', 'revision': 'r1'},
        'segments': [{
            'media_id': 'm', 'source_path': 'clip.mov',
            'source': {'start': 0, 'end': 100, 'unit': 'frames', 'fps': '25'},
            'timeline': {'start': 200, 'end': 400, 'unit': 'frames', 'fps': '50'},
            'mapping': 'Observed placement; no speed assumption',
            'game': {'status': 'candidate', 'value': 'Game A', 'evidence': [{'at': 25, 'timebase': 'source', 'modality': 'visual', 'observation': 'HUD resembles A', 'limitations': 'one sample'}]},
            'channel': {'status': 'unknown', 'value': None, 'evidence': [], 'reason': 'Not inspected'},
        }],
        'research': {
            'as_of': '2026-10-27', 'status': 'unavailable', 'reason': 'offline',
            'sources': [{'url': 'https://example.org/guide', 'title': 'Guide', 'access_date': '2026-10-20', 'claim': 'Prior guidance'}],
            'query': 'game shorts', 'search_date': '2026-10-27',
            'comparators': [], 'shortfall_reason': 'offline', 'format': 'Shorts',
            'analytics': 'unknown', 'transcript': 'unavailable',
            'permission': {'local_inspection': 'not granted', 'external_transfer': 'not granted', 'analytics': 'not granted'},
        },
    }


def test_uncertain_report_is_valid_but_not_live_verified():
    from scripts.channel_intelligence import validate_report
    result = validate_report(report())
    assert result['status'] == 'passed'
    assert result['live_verified'] is False
    assert result['limitations']


@pytest.mark.parametrize('mutation', [
    lambda r: r['segments'][0]['game'].update(status='confirmed', evidence=[]),
    lambda r: r['segments'][0]['game'].update(status='unknown', value='Game A'),
    lambda r: r['segments'][0]['game'].update(status='conflict', evidence=[]),
    lambda r: r['segments'][0]['source'].update(fps='0'),
    lambda r: r['segments'][0]['timeline'].update(end=100),
    lambda r: r['segments'][0].update(mapping=''),
    lambda r: r['research'].update(shortfall_reason=''),
    lambda r: r['research'].update(status='current'),
    lambda r: r['research']['permission'].update(analytics='granted'),
    lambda r: r['research'].update(as_of='not-a-date'),
])
def test_malformed_or_unsupported_claims_fail(mutation):
    from scripts.channel_intelligence import validate_report
    data = report()
    mutation(data)
    assert validate_report(data)['status'] == 'failed'


@pytest.mark.parametrize('field,value', [
    ('timebase', []),
    ('url', 'http://[bad'),
    ('url', 'http://:80'),
    ('url', 'https://exa mple.org'),
    ('url', 'https://example.org\\evil'),
    ('url', 'https://.'),
    ('url', 'https://%zz'),
    ('url', 'https://example.org/%zz'),
    ('url', 'https://example.org/path%'),
    ('url', 'https://example.org/?q=%2'),
    ('url', 'https://example.org/#%xz'),
    ('url', 'https://user@@example.org/'),
    ('url', 'https://user@other@example.org/'),
    ('url', 'https://example.org/pa\nth'),
    ('url', 'https://example.org/pa\x00th'),
    ('url', 'https://foo..example'),
    ('start', 10**400),
    ('at', 10**400),
    ('at', 25.5),
])
@pytest.mark.parametrize('interface', ['api', 'cli'])
def test_invalid_values_return_structured_failure(field, value, interface, tmp_path):
    from scripts.channel_intelligence import validate_report
    data = report()
    if field == 'url':
        data['research']['sources'][0]['url'] = value
    elif field == 'start':
        data['segments'][0]['source']['start'] = value
    else:
        data['segments'][0]['game']['evidence'][0][field] = value
    if interface == 'api':
        result = validate_report(data)
    else:
        path = tmp_path / 'invalid.json'
        path.write_text(json.dumps(data), encoding='utf-8')
        run = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'channel_intelligence.py'),
                              'validate', str(path)], capture_output=True, text=True)
        assert run.returncode == 1
        result = json.loads(run.stdout)
    assert result['status'] == 'failed'
    assert result['errors']


@pytest.mark.parametrize('url', ['https://例え.テスト/path', 'http://127.0.0.1:8080/',
                                 'https://[2001:db8::1]/', 'https://example.org./',
                                 'https://user%40name@example.org/a%20b?q=%2f#%AB',
                                 'https://example.org/path@name'])
def test_valid_international_and_ip_hosts_are_accepted(url):
    from scripts.channel_intelligence import validate_report
    data = report()
    data['research']['sources'][0]['url'] = url
    assert validate_report(data)['status'] == 'passed'


def test_multiple_segments_and_conflict_are_preserved():
    from scripts.channel_intelligence import validate_report
    data = report()
    second = copy.deepcopy(data['segments'][0])
    second['game'] = {'status': 'conflict', 'value': None, 'reason': 'contradictory observations',
                      'evidence': [second['game']['evidence'][0], {'at': 50, 'timebase': 'source', 'modality': 'visual', 'observation': 'HUD resembles B', 'limitations': 'one sample'}]}
    data['segments'].append(second)
    assert validate_report(data)['status'] == 'passed'


def test_cli_reads_json_and_reports_invalid_json(tmp_path):
    script = ROOT / 'scripts' / 'channel_intelligence.py'
    path = tmp_path / 'input.json'
    path.write_text(json.dumps(report()), encoding='utf-8')
    run = subprocess.run([sys.executable, str(script), 'validate', str(path)], capture_output=True, text=True)
    assert run.returncode == 0
    assert json.loads(run.stdout)['status'] == 'passed'
    path.write_text('{', encoding='utf-8')
    run = subprocess.run([sys.executable, str(script), 'validate', str(path)], capture_output=True, text=True)
    assert run.returncode != 0
    assert json.loads(run.stdout)['status'] == 'failed'
