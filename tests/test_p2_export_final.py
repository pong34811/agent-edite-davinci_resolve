import pytest

from scripts.p2_export_final import assert_unique_out_names, cover_path_for, plan_jobs, safe, select_jobs

VDO = "G:/x/vdo"


def test_cover_name_matches_timeline():
    assert cover_path_for("แพ้เกม! ปราสาทแตก-Becastled-vdo_9x16", VDO).endswith(
        "แพ้เกม! ปราสาทแตก-Becastled-vdo_9x16.jpg")


def test_150s_variant_replaces_original_and_keeps_original_filename():
    jobs = plan_jobs(["A-vdo", "A-vdo_150s", "B-vdo"], prefer_variant=True)
    assert [(j["timeline"], j["out_name"]) for j in jobs] == [("A-vdo_150s", "A-vdo"), ("B-vdo", "B-vdo")]


def test_vertical_150s_maps_back_to_9x16_name():
    jobs = plan_jobs(["A-vdo_9x16", "A-vdo_9x16_150s"], prefer_variant=True)
    assert [(j["timeline"], j["out_name"], j["vertical"]) for j in jobs] == [("A-vdo_9x16_150s", "A-vdo_9x16", True)]


def test_vertical_flag_and_skip_archived():
    jobs = plan_jobs(["X-vdo_9x16", "Y-vdo", "old archived-vdo"], prefer_variant=True)
    assert [(j["out_name"], j["vertical"]) for j in jobs] == [("X-vdo_9x16", True), ("Y-vdo", False)]


def test_safe_strips_windows_illegal_chars_but_keeps_thai_and_bang():
    assert safe('แพ้เกม! a:b*c?') == "แพ้เกม! abc"


def test_select_jobs_keeps_only_timelines_with_a_cover():
    names = ["A-vdo", "A-vdo_9x16", "Draft copy", "B-vdo_150s", "B-vdo"]
    covers = {"A-vdo.jpg", "A-vdo_9x16.jpg", "B-vdo.jpg", "Thumbs.db"}
    sel, missing = select_jobs(names, covers)
    assert [j["out_name"] for j in sel] == ["A-vdo", "A-vdo_9x16", "B-vdo"]
    assert [j["timeline"] for j in sel][-1] == "B-vdo_150s"
    assert missing == ["Draft copy"]


def test_assert_unique_out_names_across_projects():
    a = [{"out_name": "X"}, {"out_name": "Y"}]
    b = [{"out_name": "Z"}]
    assert_unique_out_names({"p1": a, "p2": b})
    with pytest.raises(ValueError, match="X"):
        assert_unique_out_names({"p1": a, "p2": [{"out_name": "X"}]})

