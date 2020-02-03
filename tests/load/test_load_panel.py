from pprint import pprint as pp
from scout.load.panel import load_panel


def test_load_panel(gene_database, panel_info):
    # GIVEN an database with genes but no panels
    adapter = gene_database
    assert sum(1 for i in adapter.gene_panels()) == 0

    # WHEN loading a gene panel
    load_panel(
        panel_path=panel_info["file"],
        adapter=adapter,
        institute=panel_info["institute"],
        panel_id=panel_info["panel_name"],
        panel_type=panel_info["type"],
        version=panel_info["version"],
        display_name=panel_info["full_name"],
    )

    # THEN make sure that the panel is loaded

    assert adapter.gene_panel(panel_id=panel_info["panel_name"])
