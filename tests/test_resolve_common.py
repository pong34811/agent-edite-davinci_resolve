import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import resolve_common as rc  # noqa: E402


class FakeTimeline:
    def __init__(self, uid, tc="01:00:00:00"):
        self.uid, self.tc = uid, tc

    def GetUniqueId(self): return self.uid
    def GetCurrentTimecode(self): return self.tc
    def SetCurrentTimecode(self, tc): self.tc = tc; return True


class FakeProject:
    def __init__(self, name, timelines):
        self.name, self.tls, self.current = name, timelines, timelines[0]

    def GetName(self): return self.name
    def GetCurrentTimeline(self): return self.current
    def GetTimelineCount(self): return len(self.tls)
    def GetTimelineByIndex(self, i): return self.tls[i - 1]
    def SetCurrentTimeline(self, tl): self.current = tl; return True


class FakePM:
    def __init__(self, projects):
        self.projects, self.cur = projects, projects[0]

    def GetCurrentProject(self): return self.cur
    def LoadProject(self, name):
        self.cur = next(p for p in self.projects if p.name == name)
        return self.cur


class FakeResolve:
    def __init__(self):
        self.a = FakeTimeline("A")
        self.b = FakeTimeline("B")
        self.p1 = FakeProject("one", [self.a, self.b])
        self.p2 = FakeProject("two", [FakeTimeline("C")])
        self.pm = FakePM([self.p1, self.p2])
        self.page = "edit"

    def GetProjectManager(self): return self.pm
    def GetCurrentPage(self): return self.page
    def OpenPage(self, p): self.page = p; return True


class PreservedStateTests(unittest.TestCase):
    def test_restores_project_timeline_playhead_page(self):
        r = FakeResolve()
        with self.assertRaises(RuntimeError):
            with rc.preserved_state(r):
                r.pm.LoadProject("two")
                r.p1.SetCurrentTimeline(r.b)
                r.a.tc = "02:00:00:00"
                r.page = "color"
                raise RuntimeError("body failed")
        self.assertEqual(r.pm.cur.name, "one")
        self.assertIs(r.p1.current, r.a)
        self.assertEqual(r.a.tc, "01:00:00:00")
        self.assertEqual(r.page, "edit")


class RequireResolveTests(unittest.TestCase):
    def test_exits_when_not_connected(self):
        with mock.patch.object(rc, "connect_resolve", return_value=None):
            with self.assertRaises(SystemExit):
                rc.require_resolve()

    def test_returns_object(self):
        with mock.patch.object(rc, "connect_resolve", return_value="R"):
            self.assertEqual(rc.require_resolve(), "R")


if __name__ == "__main__":
    unittest.main()
