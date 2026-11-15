from scripts.set_dialogue_leveler import apply_to_items, leveler_props, mismatches


class FakeItem:
    """Mimics 21.1.0.17: enabling the leveler also flips BackgroundReduction on and OutputGain to +2."""

    def __init__(self, sticky=None):
        self.p = {"AudioVolume": 0.0, "AudioDialogueLevelerEnabled": False,
                  "AudioDialogueLevelerBackgroundReduction": False, "AudioDialogueLevelerOutputGain": 0.0}
        self.sticky = sticky or {}

    def GetName(self):
        return "a1.mp4"

    def SetProperty(self, k, v):
        if k in self.sticky:
            return True  # Resolve says yes but keeps its own value
        self.p[k] = v
        if k == "AudioDialogueLevelerEnabled" and v:
            self.p["AudioDialogueLevelerBackgroundReduction"] = True
            self.p["AudioDialogueLevelerOutputGain"] = 2.0
        return True

    def GetProperty(self, k):
        return self.sticky.get(k, self.p.get(k))


def test_on_sets_side_effect_keys_explicitly():
    props = leveler_props(True)
    assert props["AudioDialogueLevelerBackgroundReduction"] is False
    assert props["AudioDialogueLevelerOutputGain"] == 0.0
    assert "AudioVolume" not in props


def test_off_only_disables():
    assert leveler_props(False) == {"AudioDialogueLevelerEnabled": False}
    assert leveler_props(False, -3)["AudioVolume"] == -3.0


def test_apply_overrides_enable_side_effects():
    it = FakeItem()
    assert apply_to_items([it], leveler_props(True), settle=0) == []
    assert it.p["AudioDialogueLevelerBackgroundReduction"] is False
    assert it.p["AudioDialogueLevelerOutputGain"] == 0.0


def test_readback_mismatch_is_reported():
    it = FakeItem(sticky={"AudioVolume": 0.0})
    errs = apply_to_items([it], leveler_props(True, 6.0), settle=0)
    assert any("AudioVolume" in e for e in errs)
    assert mismatches(it, {"AudioDialogueLevelerEnabled": True}) == []
