from scout.build import build_panel

def test_build_panel(gene_database, parsed_panel):
    panel_obj = build_panel(parsed_panel, gene_database)

    assert panel_obj.institute == parsed_panel['institute']
    assert len(parsed_panel['genes']) == len(panel_obj.gene_objects)