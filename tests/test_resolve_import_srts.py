"""Offline tests (fake Resolve objects) for scripts/resolve_import_srts.py."""
import json
import os

import pytest

from scripts import resolve_import_srts as mod

TL_ID = "tl-1"


class FakeItem:
    def __init__(self, start, end, name):
        self._s, self._e, self._n = start, end, name

    def GetStart(self):
        return self._s

    def GetEnd(self):
        return self._e

    def GetName(self):
        return self._n


class FakeTimeline:
    def __init__(self, uid=TL_ID, sub_tracks=0, add_ok=True):
        self.uid = uid
        self.sub = sub_tracks
        self.add_ok = add_ok
        self.deleted = []
        self.delete_ok = True
        self.video = {1: [FakeItem(0, 3300, "v.mp4")]}
        self.audio = {1: [FakeItem(0, 3300, "v.mp4")]}

    def GetUniqueId(self):
        return self.uid

    def GetTrackCount(self, kind):
        return {"subtitle": self.sub, "video": len(self.video), "audio": len(self.audio)}[kind]

    def AddTrack(self, kind):
        if not self.add_ok:
            return False
        self.sub += 1
        return True

    def DeleteTrack(self, kind, idx):
        self.deleted.append((kind, idx))
        if self.delete_ok:
            self.sub -= 1
            return True
        return False

    def GetItemListInTrack(self, kind, idx):
        return {"video": self.video, "audio": self.audio}.get(kind, {}).get(idx, [])


class FakeClip:
    def __init__(self, path):
        self.path = path

    def GetClipProperty(self, key):
        return self.path


class FakeFolder:
    def __init__(self, name="Master", clips=None):
        self.name = name
        self.clips = clips if clips is not None else []

    def GetName(self):
        return self.name

    def GetClipList(self):
        return list(self.clips)

    def GetSubFolderList(self):
        return []


class FakeMediaPool:
    def __init__(self, append_result=True, import_ok=True):
        self.root = FakeFolder()
        self.append_result = append_result
        self.import_ok = import_ok
        self.appended = []
        self.deleted_clips = 0

    def GetRootFolder(self):
        return self.root

    def GetCurrentFolder(self):
        return self.root

    def DeleteClips(self, clips):
        self.deleted_clips += len(clips)
        self.root.clips = [c for c in self.root.clips if c not in clips]
        return True

    def ImportMedia(self, paths):
        return [FakeClip(paths[0])] if self.import_ok else []

    def AppendToTimeline(self, payload):
        self.appended.append(payload)
        return [object()] if self.append_result else []


class FakeProject:
    def __init__(self, tl, mp):
        self.tl, self.mp = tl, mp
        self.cur = tl

    def GetName(self):
        return "proj"

    def GetTimelineCount(self):
        return 1

    def GetTimelineByIndex(self, i):
        return self.tl

    def GetCurrentTimeline(self):
        return self.cur

    def SetCurrentTimeline(self, t):
        self.cur = t
        return True

    def GetMediaPool(self):
        return self.mp


class FakePM:
    def __init__(self, proj):
        self.proj = proj
        self.saves = 0

    def GetCurrentProject(self):
        return self.proj

    def SaveProject(self):
        self.saves += 1
        return True


class FakeResolve:
    def __init__(self, pm, page="edit"):
        self.pm, self.page = pm, page

    def GetProjectManager(self):
        return self.pm

    def GetCurrentPage(self):
        return self.page


@pytest.fixture
def env(tmp_path, monkeypatch):
    (tmp_path / "srt").mkdir()
    (tmp_path / "backup").mkdir()
    (tmp_path / "backup" / "b.drp").write_bytes(b"drp-bytes")
    (tmp_path / "jobs.json").write_text(
        json.dumps([{"job": 1, "timeline_id": TL_ID, "fps": 60}]), encoding="utf-8")
    monkeypatch.setattr(mod, "W", str(tmp_path))
    monkeypatch.setattr(mod, "BACKUP", str(tmp_path / "backup" / "b.drp"))
    monkeypatch.setattr(mod, "SPACING", 0)
    monkeypatch.setattr(mod.time, "sleep", lambda s: None)

    def build(tl=None, mp=None):
        tl = tl or FakeTimeline()
        mp = mp or FakeMediaPool()
        pm = FakePM(FakeProject(tl, mp))
        res = FakeResolve(pm)
        monkeypatch.setattr(mod, "resolve", res, raising=False)
        return tl, mp, pm, res

    build.path = tmp_path
    return build


def _results(env):
    return json.loads((env.path / "import-results.json").read_text(encoding="utf-8"))["1"]


def test_import_happy_path_records_added_track(env):
    tl, mp, pm, _ = env()
    rec = mod.do_import(1)
    assert rec["status"] == "imported (unverified)"
    assert rec["added_subtitle_track_index"] == 1
    assert mp.appended == [[{"mediaPoolItem": mp.appended[0][0]["mediaPoolItem"]}]]
    assert pm.saves == 1


def test_import_aborts_without_backup(env):
    tl, mp, pm, _ = env()
    os.remove(mod.BACKUP)
    rec = mod.do_import(1)
    assert rec["status"].startswith("ABORT: backup")
    assert tl.sub == 0 and mp.appended == [] and pm.saves == 0


def test_import_aborts_with_empty_backup(env):
    tl, mp, pm, _ = env()
    open(mod.BACKUP, "wb").close()
    rec = mod.do_import(1)
    assert rec["status"].startswith("ABORT: backup")
    assert tl.sub == 0


def test_addtrack_false_aborts_no_import_or_append(env):
    tl, mp, pm, _ = env(tl=FakeTimeline(add_ok=False))
    imported = []
    orig = mp.ImportMedia
    mp.ImportMedia = lambda p: imported.append(p) or orig(p)
    rec = mod.do_import(1)
    assert rec["status"].startswith("ABORT: AddTrack")
    assert rec["AddTrack"] is False
    assert imported == [] and mp.appended == [] and pm.saves == 0
    assert "added_subtitle_track_index" not in rec


def test_empty_append_marks_failed_not_imported(env):
    tl, mp, pm, _ = env(mp=FakeMediaPool(append_result=False))
    rec = mod.do_import(1)
    assert rec["status"].startswith("FAILED: AppendToTimeline")
    assert "imported" not in rec["status"]
    assert rec["Append_returned"] == 0
    assert pm.saves == 0
    assert _results(env)["status"].startswith("FAILED")


def test_import_empty_importmedia_is_failed(env):
    tl, mp, pm, _ = env(mp=FakeMediaPool(import_ok=False))
    rec = mod.do_import(1)
    assert rec["status"].startswith("FAILED: ImportMedia")
    assert mp.appended == []


def test_rollback_deletes_only_added_track(env):
    tl, mp, pm, _ = env()
    mod.do_import(1)
    rec = mod.do_rollback(1)
    assert tl.deleted == [("subtitle", 1)]
    assert rec["rolled_back"] is True and rec["subtitle_tracks_now"] == 0
    # Second rollback has no record any more and must delete nothing.
    rec2 = mod.do_rollback(1)
    assert rec2["rolled_back"] is False and tl.deleted == [("subtitle", 1)]


def test_rollback_refuses_preexisting_subtitle_track(env):
    tl, mp, pm, _ = env(tl=FakeTimeline(sub_tracks=2))
    rec = mod.do_import(1)  # aborts: already has tracks
    assert rec["status"].startswith("ABORT: timeline already has")
    rec = mod.do_rollback(1)
    assert rec["rolled_back"] is False
    assert tl.deleted == [] and tl.sub == 2


def test_rollback_refuses_when_track_count_changed(env):
    tl, mp, pm, _ = env()
    mod.do_import(1)
    tl.sub = 2  # a foreign subtitle track appeared since the import
    rec = mod.do_rollback(1)
    assert rec["status"].startswith("ABORT: subtitle track count 2")
    assert tl.deleted == [] and tl.sub == 2


def test_rollback_without_import_record_deletes_nothing(env):
    tl, mp, pm, _ = env(tl=FakeTimeline(sub_tracks=1))
    rec = mod.do_rollback(1)
    assert rec["rolled_back"] is False and tl.deleted == []


def test_rollback_timeline_none_guarded(env):
    tl, mp, pm, _ = env()
    mod.do_import(1)
    (env.path / "jobs.json").write_text(
        json.dumps([{"job": 1, "timeline_id": "gone", "fps": 60}]), encoding="utf-8")
    rec = mod.do_rollback(1)
    assert rec["status"] == "ABORT: timeline not found"
    assert tl.deleted == []


def test_rollback_reads_back_failed_delete(env):
    tl, mp, pm, _ = env()
    mod.do_import(1)
    tl.delete_ok = False  # DeleteTrack returns False and count stays 1
    rec = mod.do_rollback(1)
    assert rec["rolled_back"] is False
    assert rec["status"].startswith("FAILED: subtitle track count 1")


def test_rollback_deletes_stale_pool_items_with_readback(env):
    tl, mp, pm, _ = env()
    mod.do_import(1)
    srt = os.path.join(mod.W, "srt", "job1.srt")
    mp.root.clips = [FakeClip(srt), FakeClip("other.srt")]
    rec = mod.do_rollback(1)
    assert rec["rolled_back"] is True and rec["stale_pool_items_left"] == 0
    assert [c.path for c in mp.root.clips] == ["other.srt"]


def test_merge_is_atomic_on_failure(env, monkeypatch):
    env()
    mod._merge(1, {"a": 1})
    p = env.path / "import-results.json"
    before = p.read_text(encoding="utf-8")

    def boom(*a, **k):
        raise RuntimeError("disk full")

    monkeypatch.setattr(mod.json, "dump", boom)
    with pytest.raises(RuntimeError):
        mod._merge(1, {"b": 2})
    assert p.read_text(encoding="utf-8") == before
    assert not (env.path / "import-results.json.tmp").exists()


def test_merge_updates_and_keeps_other_jobs(env):
    env()
    mod._merge(1, {"a": 1})
    mod._merge(2, {"z": 9})
    mod._merge(1, {"b": 2})
    data = json.loads((env.path / "import-results.json").read_text(encoding="utf-8"))
    assert data == {"1": {"a": 1, "b": 2}, "2": {"z": 9}}
    assert not (env.path / "import-results.json.tmp").exists()


def test_parse_srt_finds_timing_line_by_regex(tmp_path):
    p = tmp_path / "x.srt"
    thai = "สวัสดี"
    bom = chr(0xFEFF)
    blocks = [
        [bom + "1", "00:00:01,500 --> 00:00:02,250", thai],
        ["garbage block without timing"],
        ["00:00:03,000 --> 00:00:04,000", thai, "second line"],
    ]
    crlf = chr(13) + chr(10)
    p.write_bytes((crlf * 2).join(crlf.join(b) for b in blocks).encode("utf-8"))
    cues = mod._parse_srt(str(p))
    assert len(cues) == 2
    assert cues[0] == {"start_s": 1.5, "end_s": 2.25, "text": thai}
    assert cues[1]["start_s"] == 3.0
    assert cues[1]["text"] == thai + chr(10) + "second line"


def test_snapshot_and_diff_against_baseline(env):
    tl, mp, pm, res = env()
    snap = mod.snapshot_state(res)
    assert snap["page"] == "edit" and snap["cur_tl_id"] == TL_ID and snap["folder"] == "Master"
    assert snap["tls"][TL_ID]["video1"] == [[0, 3300, "v.mp4"]]
    # Baseline (JSON round trip) with subtitle count 0: only subtitle change is allowed.
    base = json.loads(json.dumps(snap))
    base["tls"][TL_ID]["sub"] = 0
    snap["tls"][TL_ID]["sub"] = 1
    assert mod.diff_snapshot(base, snap) == []
    # Changes to video items, page, folder or active timeline are reported.
    tl.video[1][0]._e = 3299
    snap2 = mod.snapshot_state(res)
    snap2["page"] = "deliver"
    snap2["folder"] = "Other"
    diffs = mod.diff_snapshot(base, snap2)
    assert any("video1" in d for d in diffs)
    assert any(d.startswith("page") for d in diffs)
    assert any(d.startswith("folder") for d in diffs)


def test_do_snapshot_writes_files_and_diff(env):
    tl, mp, pm, res = env()
    base = mod.snapshot_state(res)
    (env.path / "baseline.json").write_text(json.dumps(base), encoding="utf-8")
    mod.do_import(1)
    rec = mod.do_snapshot()
    assert rec["matches_baseline"] is True
    assert rec["subtitle_tracks_per_timeline"] == {TL_ID: 1}
    assert (env.path / "post-state.json").exists()
    tl.audio[1][0]._s = 5
    assert mod.do_snapshot()["matches_baseline"] is False
