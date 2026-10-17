import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.drt_focus_track import DrtPatchError, patch_drt
from scripts.drt_rebuild_focus_track import main, rebuild_track, validate_ranges
from tests.test_drt_focus_track import _all_dbids, _item_signatures, _read_sequence, drt_pair  # noqa: F401


def _zoom_items(path, name="ZOOM FOCUS"):
    root = _read_sequence(path)
    for w in root.find("VideoTrackVec").findall("Element"):
        t = w.find("Sm2TiTrack")
        if t.findtext("UserDefinedName") == name:
            return [(int(e[0].findtext("Start")), int(e[0].findtext("Duration"))) for e in t.find("Items").findall("Element")]
    return None


def test_create_places_every_range_and_keeps_other_tracks(drt_pair, tmp_path):
    source, template = drt_pair
    out = tmp_path / "out.drt"
    summary = rebuild_track(source, template, out, [[10, 40], [40, 60], [100, 150]], track_name="ZOOM FOCUS", create=True)
    assert _zoom_items(out) == [(10, 30), (40, 20), (100, 50)]
    before = _item_signatures(_read_sequence(source))
    after = _item_signatures(_read_sequence(out))
    assert {k: after[k] for k in before} == before
    ids = _all_dbids(_read_sequence(out))
    assert len(ids) == len(set(ids))
    assert summary["created"] and summary["previous_ranges"] == []


def test_rebuild_replaces_existing_clips(drt_pair, tmp_path):
    source, template = drt_pair
    stage = tmp_path / "stage.drt"
    patch_drt(source, template, stage, 50, 80)
    out = tmp_path / "out.drt"
    summary = rebuild_track(stage, template, out, [[20, 80], [120, 180]], track_name="ZOOM FOCUS")
    assert summary["previous_ranges"] == [[50, 80]]
    assert _zoom_items(out) == [(20, 60), (120, 60)]


def test_missing_track_without_create_fails(drt_pair, tmp_path):
    source, template = drt_pair
    with pytest.raises(DrtPatchError, match="--create"):
        rebuild_track(source, template, tmp_path / "o.drt", [[0, 10]], track_name="ZOOM FOCUS")


def test_refuses_track_with_non_adjustment_items(drt_pair, tmp_path):
    source, template = drt_pair
    with pytest.raises(DrtPatchError, match="non-Adjustment"):
        rebuild_track(source, template, tmp_path / "o.drt", [[0, 10]], track_name="")


def test_dry_run_writes_nothing(drt_pair, tmp_path):
    source, template = drt_pair
    out = tmp_path / "o.drt"
    assert main([str(source), str(template), str(out), "--ranges", "[[0,10]]", "--track-name", "ZOOM FOCUS",
                 "--create", "--dry-run"]) == 0
    assert not out.exists()


@pytest.mark.parametrize("bad", [[], [[5, 5]], [[-1, 4]], [[10, 20], [15, 30]], [[20, 30], [0, 10]], [[0, True]]])
def test_validate_ranges_rejects(bad):
    with pytest.raises(DrtPatchError):
        validate_ranges(bad)


def test_validate_ranges_allows_touching():
    assert validate_ranges([[0, 10], [10, 20]]) == [(0, 10), (10, 20)]
