"""load_subtitle_preset_auto: several --timeline values share one Resolve restart."""
from scripts.load_subtitle_preset_auto import build_parser


def test_timeline_repeats_into_a_list():
    a = build_parser().parse_args(["--timeline", "A_9x16", "--timeline", "B_9x16", "--preset", "Mitr-short-001"])
    assert a.timeline == ["A_9x16", "B_9x16"]
    assert a.preset == "Mitr-short-001" and not a.apply


def test_single_timeline_still_works():
    a = build_parser().parse_args(["--timeline", "Timeline 1_9x16", "--preset", "Mitr-short-001", "--apply"])
    assert a.timeline == ["Timeline 1_9x16"] and a.apply
