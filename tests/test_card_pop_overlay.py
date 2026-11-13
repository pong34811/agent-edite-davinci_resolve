from PIL import Image

from scripts import card_pop_overlay as m


def test_pop_scale_overshoots_then_settles():
    assert m.pop_scale(-0.01) == 0.0
    assert abs(m.pop_scale(0.10) - 1.15) < 1e-9
    assert abs(m.pop_scale(0.15) - 1.075) < 1e-9
    assert m.pop_scale(0.5) == 1.0


def test_fade_alpha_only_in_last_fade_window():
    assert m.fade_alpha(1.0, 2.0, 0.25) == 1.0
    assert abs(m.fade_alpha(1.875, 2.0, 0.25) - 0.5) < 1e-9
    assert m.fade_alpha(2.0, 2.0, 0.25) == 0.0


def test_card_box_keeps_aspect_and_centre():
    left, top, w, h = m.card_box(813, 1185, 1560, 470, 860, 1.0)
    assert h == 860 and w == round(813 * 860 / 1185)
    assert abs(left + w / 2 - 1560) <= 1 and abs(top + h / 2 - 470) <= 1


def test_frame_stagger_and_stacking(tmp_path):
    red = Image.new("RGBA", (100, 200), (255, 0, 0, 255))
    blue = Image.new("RGBA", (100, 200), (0, 0, 255, 255))
    cards = [(red, {"cx": 100, "cy": 150, "h": 200}), (blue, {"cx": 140, "cy": 150, "h": 200})]
    early = m.frame(cards, 0.05, 2.0, 0.2, 0.25, 320, 300)
    assert early.getpixel((140, 150))[2] == 0  # second card not started yet
    late = m.frame(cards, 1.0, 2.0, 0.2, 0.25, 320, 300)
    assert late.getpixel((140, 150))[:3] == (0, 0, 255)  # later card stacks on top
    r, g, b, _ = late.getpixel((70, 150))  # first card, lightly darkened by the second card's shadow
    assert r > 200 and g == 0 and b == 0
    assert late.getpixel((5, 5))[3] == 0  # transparent outside the cards
