"""Offline test of the bin reuse/dedupe import in scripts.apply_enrichment_d22.pool_clips (no Resolve)."""
import pytest

from scripts.apply_enrichment_d22 import pool_clips


class Clip:
    def __init__(self, path):
        self.path = path

    def GetClipProperty(self, name):
        return {name: self.path}


class Folder:
    def __init__(self, clips):
        self.clips = clips

    def GetClipList(self):
        return self.clips


class MediaPool:
    def __init__(self, short=False):
        self.calls, self.short = [], short

    def ImportMedia(self, paths):
        self.calls.append(list(paths))
        return [Clip(p) for p in paths][: len(paths) - 1 if self.short else None]


def test_reuses_bin_clips_and_imports_each_new_path_once():
    old = Clip(r"G:\Lib\BGM\Song.mp3")
    mp = MediaPool()
    paths = [r"g:\lib\bgm\song.mp3", r"G:\Lib\SFX\pop.wav", r"G:\Lib\SFX\pop.wav", r"G:\Lib\GIF\a.gif"]
    pool = pool_clips(mp, Folder([old]), paths)
    assert mp.calls == [[r"G:\Lib\SFX\pop.wav", r"G:\Lib\GIF\a.gif"]]
    assert pool[paths[0]] is old
    assert pool[paths[1]] is pool[paths[2]]


def test_no_import_when_everything_is_in_the_bin():
    mp = MediaPool()
    pool_clips(mp, Folder([Clip(r"C:\a.wav")]), [r"C:\a.wav"])
    assert mp.calls == []


def test_short_import_stops():
    with pytest.raises(RuntimeError, match="import returned 1 of 2"):
        pool_clips(MediaPool(short=True), Folder([]), [r"C:\a.wav", r"C:\b.wav"])
