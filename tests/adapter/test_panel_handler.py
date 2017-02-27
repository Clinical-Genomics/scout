import pytest

from scout.exceptions import IntegrityError

def test_add_panel(gene_database, panel_obj):
    adapter = gene_database
    ## GIVEN a adapter with genes but no panels
    assert adapter.all_genes().count() > 0
    assert adapter.gene_panels().count() == 0
    ## WHEN inserting a panel
    adapter.add_gene_panel(panel_obj)
    ## THEN assert that the panel was loaded
    assert adapter.panel_collection.find().count() == 1

def test_add_same_panel_twice(gene_database, panel_obj):
    adapter = gene_database
    ## GIVEN a adapter with genes but no panels
    assert adapter.gene_panels().count() == 0
    ## WHEN inserting a panel twice
    adapter.add_gene_panel(panel_obj)
    ## THEN assert that IntegrityError is raised
    with pytest.raises(IntegrityError):
        adapter.add_gene_panel(panel_obj)


def test_get_panel_by_version(panel_database, panel_info):
    adapter = panel_database
    ## GIVEN a adapter with one gene panel
    res = adapter.gene_panels()
    assert res.count() == 1
    ## WHEN getting a panel
    res = adapter.gene_panel(
        panel_id=panel_info['panel_name'],
        version=float(panel_info['version']))
    ## THEN assert that the panel was loaded
    assert res['panel_name'] == panel_info['panel_name']

def test_get_panel_by_name(panel_database, panel_info):
    adapter = panel_database
    ## GIVEN a adapter with one gene panel
    res = adapter.gene_panels()
    assert res.count() == 1
    ## WHEN getting a panel
    res = adapter.gene_panel(panel_id=panel_info['panel_name'])
    ## THEN assert that the panel was loaded
    assert res['panel_name'] == panel_info['panel_name']

def test_get_non_existing_panel(panel_database, panel_info):
    adapter = panel_database
    ## GIVEN a adapter with one gene panel
    res = adapter.gene_panels()
    assert res.count() == 1
    ## WHEN getting a panel
    res = adapter.gene_panel(panel_id='non existing')
    ## THEN assert that the panel was loaded
    assert res is None

def test_get_panel_multiple_versions(panel_database, panel_obj):
    adapter = panel_database
    panel_obj['version'] = 2.0
    adapter.add_gene_panel(panel_obj)
    ## GIVEN a adapter with two gene panel
    res = adapter.gene_panels()
    assert res.count() == 2
    ## WHEN getting a panel
    res = adapter.gene_panel(panel_id=panel_obj['panel_name'])
    ## THEN assert that the last version is fetched
    assert res['version'] == 2.0
    