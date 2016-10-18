from scout.build import build_panel

def test_build_panel(parsed_panel):
    panel_obj = build_panel(parsed_panel)
    
    assert panel_obj.institute == parsed_panel['institute']