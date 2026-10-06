import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('resolve_preflight', ROOT / 'scripts/resolve_preflight.py')
assert spec is not None and spec.loader is not None
pf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pf)


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.catalog = self.tmp / 'catalog'
        self.catalog.mkdir()
        (self.catalog / 'timeline.json').write_text(json.dumps({
            'name': 'timeline',
            'description': 'Timeline operations. Actions: get_items, probe_timeline_structure',
            'parameters': {},
        }), encoding='utf-8')
        server = self.tmp / 'server.py'
        server.write_text('', encoding='utf-8')
        self.mcp = self.tmp / '.mcp.json'
        self.mcp.write_text(json.dumps({'mcpServers': {'davinci-resolve': {
            'command': str(Path(__file__)), 'args': [str(server)]}}}), encoding='utf-8')

    def run_pf(self, need, running=True, api_has=None, mcp=None, catalog=None):
        return pf.evaluate(
            need,
            mcp_config=mcp or self.mcp,
            catalog_dir=catalog or self.catalog,
            resolve_running=lambda: running,
            api_has=api_has,
        )

    def test_tool_in_catalog_uses_mcp(self):
        r = self.run_pf('timeline')
        self.assertEqual(r['verdict'], 'USE_MCP')

    def test_tool_and_action_in_catalog_uses_mcp(self):
        r = self.run_pf('timeline.get_items')
        self.assertEqual(r['verdict'], 'USE_MCP')

    def test_action_missing_from_tool_schema_is_not_mcp(self):
        r = self.run_pf('timeline.set_foo', api_has=lambda name: True)
        self.assertEqual(r['verdict'], 'FALLBACK_SCRIPT')
        self.assertTrue(any('set_foo' in x for x in r['reasons']))

    def test_missing_tool_falls_back_when_api_has_method(self):
        r = self.run_pf('SetStartTimecode', api_has=lambda name: name == 'SetStartTimecode')
        self.assertEqual(r['verdict'], 'FALLBACK_SCRIPT')

    def test_missing_tool_and_no_api_method_is_blocked(self):
        r = self.run_pf('SetNothing', api_has=lambda name: False)
        self.assertEqual(r['verdict'], 'BLOCKED')

    def test_missing_tool_without_api_probe_is_blocked(self):
        # Never recommend writing a script on a guess.
        r = self.run_pf('SetNothing', api_has=None)
        self.assertEqual(r['verdict'], 'BLOCKED')

    def test_resolve_not_running_is_blocked(self):
        r = self.run_pf('timeline', running=False)
        self.assertEqual(r['verdict'], 'BLOCKED')
        self.assertTrue(any('not running' in x.lower() for x in r['reasons']))

    def test_mcp_config_pointing_to_missing_server_is_blocked_for_mcp(self):
        bad = self.tmp / 'bad.json'
        bad.write_text(json.dumps({'mcpServers': {'davinci-resolve': {
            'command': str(self.tmp / 'nope.exe'), 'args': []}}}), encoding='utf-8')
        r = self.run_pf('timeline', mcp=bad, api_has=lambda name: True)
        self.assertEqual(r['verdict'], 'FALLBACK_SCRIPT')
        self.assertTrue(any('server' in x.lower() for x in r['reasons']))

    def test_missing_catalog_dir_does_not_claim_mcp(self):
        r = self.run_pf('timeline', catalog=self.tmp / 'absent', api_has=lambda name: False)
        self.assertEqual(r['verdict'], 'BLOCKED')

    def test_result_is_json_serialisable(self):
        json.dumps(self.run_pf('timeline'))


if __name__ == '__main__':
    unittest.main()
