from scripts import emoji_pop_overlay as m


def test_scale_expression_is_even_and_overshoots():
    e = m.scale_expr(360)
    assert e.startswith("max(2,trunc(360*") and "1.15" in e and e.endswith("/2)*2)")


def test_filter_graph_places_centre_and_fades_before_end():
    g = m.filter_graph(1920, 1080, 60, 2.0, 384, 302, 360)
    assert "s=1920x1080:r=60:d=2.0" in g
    assert "fade=t=out:st=1.75:d=0.25:alpha=1" in g
    assert "x='384-overlay_w/2':y='302-overlay_h/2'" in g
    assert g.endswith("format=yuva444p10le[v]")
