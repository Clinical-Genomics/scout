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

def test_add_pending(panel_database):
    adapter = panel_database
    panel_obj = adapter.panel_collection.find_one()
    hgnc_obj = adapter.hgnc_collection.find_one()
    ## GIVEN an adapter with a gene panel
    res = adapter.gene_panels()
    assert res.count() == 1
    ## WHEN adding a pending action
    res = adapter.add_pending(
        panel_obj=panel_obj,
        hgnc_gene=hgnc_obj,
        action='add'
    )
    ## THEN assert that the last version is fetched
    assert len(res['pending']) == 1

def test_add_pending_wrong_action(panel_database):
    adapter = panel_database
    panel_obj = adapter.panel_collection.find_one()
    hgnc_obj = adapter.hgnc_collection.find_one()
    ## GIVEN an adapter with a gene panel
    res = adapter.gene_panels()
    assert res.count() == 1
    ## WHEN adding a pending action with invalid action
    with pytest.raises(ValueError):
    ## THEN assert that an error is raised
        res = adapter.add_pending(
            panel_obj=panel_obj,
            hgnc_gene=hgnc_obj,
            action='hello'
        )

def test_update_panel_panel_name(panel_database):
    adapter = panel_database
    panel_obj = adapter.panel_collection.find_one()
    old_name = panel_obj['panel_name']
    new_name = 'new name'
    ## GIVEN an adapter with a gene panel
    res = adapter.gene_panels()
    assert res.count() == 1
    ## WHEN updating the panel name
    panel_obj['panel_name'] = new_name

    res = adapter.update_panel(panel_obj)

    ## THEN assert that the last version is fetched
    assert res['panel_name'] == new_name

def test_apply_pending_delete_gene(panel_database):
    ## GIVEN an adapter with a gene panel
    adapter = panel_database
    panel_obj = adapter.panel_collection.find_one()

    gene = panel_obj['genes'][0]
    hgnc_id = gene['hgnc_id']
    hgnc_symbol = gene['symbol']

    action = {
        'hgnc_id': hgnc_id,
        'action': 'delete',
        'symbol': hgnc_symbol,
        'info': {}
    }
    ## WHEN adding a action to the panel
    panel_obj['pending'] = [action]
    old_version = panel_obj['version']

    updated_panel_id = adapter.apply_pending(panel_obj, panel_obj['version']+1)
    updated_panel = adapter.panel_collection.find_one( {'_id' : updated_panel_id} )

    # assert that the updated panel has a newer version
    assert updated_panel['version'] != old_version

    ## THEN assert that the new panel does not have the deleted gene
    for gene in updated_panel['genes']:
        assert gene['hgnc_id'] != hgnc_id

def test_apply_pending_delete_two_genes(real_panel_database):
    adapter = real_panel_database
    panel_obj = adapter.panel_collection.find_one()

    gene = panel_obj['genes'][0]
    gene2 = panel_obj['genes'][1]

    hgnc_ids = [gene['hgnc_id'], gene2['hgnc_id']]

    action = {
        'hgnc_id': gene['hgnc_id'],
        'action': 'delete',
        'symbol': gene['symbol'],
        'info': {}
    }

    action2 = {
        'hgnc_id': gene2['hgnc_id'],
        'action': 'delete',
        'symbol': gene2['symbol'],
        'info': {}
    }

    panel_obj['pending'] = [action, action2]

    updated_panel_id = adapter.apply_pending(panel_obj, panel_obj['version'])
    updated_panel = adapter.panel_collection.find_one( {'_id' : updated_panel_id} )

    for gene in updated_panel['genes']:
        assert gene['hgnc_id'] not in hgnc_ids

def test_apply_pending_add_gene(real_panel_database):
    adapter = real_panel_database
    panel_obj = adapter.panel_collection.find_one()

    gene = panel_obj['genes'][0]
    hgnc_id = gene['hgnc_id']
    hgnc_symbol = gene['symbol']

    panel_obj['genes'] = []
    adapter.update_panel(panel_obj)

    panel_obj = adapter.panel_collection.find_one()
    assert len(panel_obj['genes']) == 0

    action = {
        'hgnc_id': hgnc_id,
        'action': 'add',
        'symbol': hgnc_symbol,
        'info': {}
    }

    panel_obj['pending'] = [action]

    # update panel version to panel_version +1
    updated_panel_id = adapter.apply_pending(panel_obj, panel_obj['version']+1)
    updated_panel = adapter.panel_collection.find_one( {'_id' : updated_panel_id} )

    #assert that panel version was updated
    assert updated_panel['version'] == panel_obj['version'] + 1

    assert len(updated_panel['genes']) == 1

def test_apply_pending_add_two_genes(real_panel_database):
    adapter = real_panel_database
    panel_obj = adapter.panel_collection.find_one()

    gene = panel_obj['genes'][0]
    gene2 = panel_obj['genes'][1]
    hgnc_ids = [gene['hgnc_id'], gene['hgnc_id']]
    hgnc_symbols = [gene['symbol'], gene['symbol']]

    panel_obj['genes'] = []
    adapter.update_panel(panel_obj)

    panel_obj = adapter.panel_collection.find_one()
    assert len(panel_obj['genes']) == 0

    action1 = {
        'hgnc_id': hgnc_ids[0],
        'action': 'add',
        'symbol': hgnc_symbols[0],
        'info': {}
    }

    action2 = {
        'hgnc_id': hgnc_ids[1],
        'action': 'add',
        'symbol': hgnc_symbols[1],
        'info': {}
    }

    panel_obj['pending'] = [action1, action2]

    # update panel without changing panel version
    updated_panel_id = adapter.apply_pending(panel_obj, panel_obj['version'])
    updated_panel = adapter.panel_collection.find_one( {'_id' : updated_panel_id} )

    #assert that panel version was NOT updated
    assert updated_panel['version'] == panel_obj['version']

    assert len(updated_panel['genes']) == 2
    for gene in updated_panel['genes']:
        assert gene['hgnc_id'] in hgnc_ids
