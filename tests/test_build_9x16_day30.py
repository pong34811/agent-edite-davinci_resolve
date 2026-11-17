from scripts.build_9x16_day30 import layouts, merge, ORIG_NAME, TARGET_NAME, FPS


def test_merge_ranges():
    assert merge([(545, 803), (1217, 1601)]) == [(545, 803), (1217, 1601)]
    assert merge([(10, 50), (40, 100)]) == [(10, 100)]
    assert merge([(10, 20), (30, 40)]) == [(10, 20), (30, 40)]
    assert merge([]) == []


def test_layouts_structure():
    lay = layouts()
    assert "V1" in lay and "V3" in lay and "FULL" in lay
    for k in ("V1", "V3", "FULL"):
        assert lay[k]["ZoomX"] == lay[k]["ZoomY"]
        assert lay[k]["ZoomX"] > 1.0
        assert "Pan" in lay[k]
        assert "Tilt" in lay[k]


def test_timeline_names():
    assert ORIG_NAME == "Timeline 1"
    assert TARGET_NAME == "Timeline 1_9x16"
    assert FPS == 60
