import unittest
from scripts import verify_review_resume as module


class TimelineProbe:
    def __init__(self):
        self.probes = 0
    def __dir__(self):
        self.probes += 1
        return ['GetName', 'GetUniqueId']
    def GetName(self):
        return 'timeline'
    def GetUniqueId(self):
        return 'id'


class CachedSurfaceTests(unittest.TestCase):
    def test_timeline_capabilities_probed_once_for_repeated_reads(self):
        module._SURFACES.clear()
        t = TimelineProbe()
        self.assertEqual(module.read(t, 'GetName'), 'timeline')
        self.assertEqual(module.read(t, 'GetUniqueId'), 'id')
        self.assertEqual(module.read(t, 'GetName'), 'timeline')
        self.assertEqual(t.probes, 1)


if __name__ == '__main__':
    unittest.main()
