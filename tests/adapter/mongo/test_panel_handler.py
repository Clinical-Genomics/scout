import pytest
from bson.objectid import ObjectId

from scout.exceptions import IntegrityError


def test_add_panel(adapter, testpanel_obj):
    ## GIVEN a adapter with without panels
    assert adapter.panel_collection.find_one() is None
    ## WHEN inserting a panel
    adapter.add_gene_panel(testpanel_obj)
    ## THEN assert that the panel was loaded
    assert adapter.panel_collection.find_one()


def test_add_same_panel_twice(adapter, testpanel_obj):
    panel_obj = testpanel_obj
    ## GIVEN a adapter without gene panels
    assert adapter.panel_collection.find_one() is None
    ## WHEN inserting a panel twice
    adapter.add_gene_panel(panel_obj)
    ## THEN assert that IntegrityError is raised
    with pytest.raises(IntegrityError):
        adapter.add_gene_panel(panel_obj)


def test_get_panel_by_version(adapter, testpanel_obj):
    panel_obj = testpanel_obj
    adapter.panel_collection.insert_one(panel_obj)
    ## GIVEN a adapter with one gene panel
    assert adapter.panel_collection.find_one()
    ## WHEN getting a panel
    res = adapter.gene_panel(panel_id=panel_obj["panel_name"], version=panel_obj["version"])
    ## THEN assert that the panel was loaded
    assert res["panel_name"] == panel_obj["panel_name"]


def test_get_panel_by_name(adapter, panel_info, testpanel_obj):
    adapter.panel_collection.insert_one(testpanel_obj)
    ## GIVEN a adapter with one gene panel
    assert adapter.panel_collection.find_one()
    ## WHEN getting a panel without version
    res = adapter.gene_panel(panel_id=panel_info["panel_name"])
    ## THEN assert that the panel was loaded
    assert res["panel_name"] == panel_info["panel_name"]


def test_get_non_existing_panel(adapter, testpanel_obj):
    panel_obj = testpanel_obj
    adapter.panel_collection.insert_one(panel_obj)
    ## GIVEN a adapter with one gene panel
    assert adapter.panel_collection.find_one()
    ## WHEN getting a panel
    res = adapter.gene_panel(panel_id="non existing")
    ## THEN assert that the panel was loaded
    assert res is None


def test_get_panel_multiple_versions(adapter, testpanel_obj):
    ## GIVEN an adapter with multiple versions of same gene panel
    testpanel_obj["_id"] = 1
    adapter.panel_collection.insert_one(testpanel_obj)
    testpanel_obj["_id"] = 2
    testpanel_obj["version"] = 2.0
    adapter.panel_collection.insert_one(testpanel_obj)

    res = adapter.gene_panels()
    assert sum(1 for _ in res) == 2
    ## WHEN getting a panel
    res = adapter.gene_panel(panel_id=testpanel_obj["panel_name"])
    ## THEN assert that the last version is fetched
    assert res["version"] == 2.0


def test_reset_pending(adapter, testpanel_obj, gene_obj):
    """Test the function that clears the pending changes from a gene panel"""

    # GIVEN a gene panel
    adapter.panel_collection.insert_one(testpanel_obj)
    # and a gene
    adapter.hgnc_collection.insert_one(gene_obj)

    hgnc_obj = adapter.hgnc_collection.find_one()

    ## WHEN adding a pending action of this gene to a panel
    res = adapter.add_pending(panel_obj=testpanel_obj, hgnc_gene=hgnc_obj, action="add")
    assert len(res["pending"]) == 1

    ## IF reset pending is used to clear pending actions
    ## Then panel should not have any more pending actions
    updated_panel = adapter.reset_pending(res)
    assert updated_panel.get("pending") is None


def test_add_pending(adapter, testpanel_obj, gene_obj):
    adapter.panel_collection.insert_one(testpanel_obj)
    adapter.hgnc_collection.insert_one(gene_obj)
    ## GIVEN a adapter with one gene panel and a gene
    panel_obj = adapter.panel_collection.find_one()
    hgnc_obj = adapter.hgnc_collection.find_one()

    assert panel_obj
    assert hgnc_obj

    ## WHEN adding a pending action
    res = adapter.add_pending(panel_obj=panel_obj, hgnc_gene=hgnc_obj, action="add")
    ## THEN assert that the last version is fetched
    assert len(res["pending"]) == 1


def test_add_pending_wrong_action(adapter, testpanel_obj, gene_obj):
    adapter.panel_collection.insert_one(testpanel_obj)
    adapter.hgnc_collection.insert_one(gene_obj)
    ## GIVEN a adapter with one gene panel and a gene
    panel_obj = adapter.panel_collection.find_one()
    hgnc_obj = adapter.hgnc_collection.find_one()
    assert panel_obj
    assert hgnc_obj

    ## WHEN adding a pending action with invalid action
    with pytest.raises(ValueError):
        ## THEN assert that an error is raised
        adapter.add_pending(panel_obj=panel_obj, hgnc_gene=hgnc_obj, action="hello")


def test_update_panel_panel_name(adapter, testpanel_obj):
    adapter.panel_collection.insert_one(testpanel_obj)
    ## GIVEN a adapter with a gene panel
    panel_obj = adapter.panel_collection.find_one()
    assert panel_obj

    panel_obj["panel_name"]
    new_name = "new name"
    ## WHEN updating the panel name
    panel_obj["panel_name"] = new_name

    res = adapter.update_panel(panel_obj)

    ## THEN assert that the last version is fetched
    assert res["panel_name"] == new_name


def test_update_panel_panel_description(adapter, testpanel_obj):
    adapter.panel_collection.insert_one(testpanel_obj)
    ## GIVEN a adapter with a gene panel
    panel_obj = adapter.panel_collection.find_one()

    assert panel_obj
    assert panel_obj["description"]

    # Update its description
    panel_obj["description"] = "Test description"
    res = adapter.update_panel(panel_obj)

    ## THEN assert that description was updated
    assert res["description"] == "Test description"


def test_apply_pending_delete_gene(adapter, testpanel_obj):
    adapter.panel_collection.insert_one(testpanel_obj)
    ## GIVEN a adapter with a gene panel
    panel_obj = adapter.panel_collection.find_one()

    assert panel_obj

    gene = panel_obj["genes"][0]

    hgnc_id = gene["hgnc_id"]
    hgnc_symbol = gene["symbol"]

    action = {"hgnc_id": hgnc_id, "action": "delete", "symbol": hgnc_symbol, "info": {}}
    ## WHEN adding a action to the panel
    panel_obj["pending"] = [action]
    old_version = panel_obj["version"]

    updated_panel_id = adapter.apply_pending(panel_obj, panel_obj["version"] + 1)
    updated_panel = adapter.panel_collection.find_one({"_id": updated_panel_id})

    # assert that the updated panel has a newer version
    assert updated_panel["version"] != old_version

    ## THEN assert that the new panel does not have the deleted gene
    for gene in updated_panel["genes"]:
        assert gene["hgnc_id"] != hgnc_id


def test_apply_pending_delete_two_genes(adapter, testpanel_obj):
    adapter.panel_collection.insert_one(testpanel_obj)
    ## GIVEN a adapter with a gene panel
    panel_obj = adapter.panel_collection.find_one()

    assert panel_obj

    gene = panel_obj["genes"][0]
    gene2 = panel_obj["genes"][1]

    hgnc_ids = [gene["hgnc_id"], gene2["hgnc_id"]]

    action = {
        "hgnc_id": gene["hgnc_id"],
        "action": "delete",
        "symbol": gene["symbol"],
        "info": {},
    }

    action2 = {
        "hgnc_id": gene2["hgnc_id"],
        "action": "delete",
        "symbol": gene2["symbol"],
        "info": {},
    }

    panel_obj["pending"] = [action, action2]

    updated_panel_id = adapter.apply_pending(panel_obj, panel_obj["version"])
    updated_panel = adapter.panel_collection.find_one({"_id": updated_panel_id})

    for gene in updated_panel["genes"]:
        assert gene["hgnc_id"] not in hgnc_ids


def test_apply_pending_add_gene(adapter, testpanel_obj):
    adapter.panel_collection.insert_one(testpanel_obj)
    ## GIVEN a adapter with a gene panel
    panel_obj = adapter.panel_collection.find_one()

    assert panel_obj

    gene = panel_obj["genes"][0]
    hgnc_id = gene["hgnc_id"]
    hgnc_symbol = gene["symbol"]

    panel_obj["genes"] = []
    adapter.update_panel(panel_obj)

    panel_obj = adapter.panel_collection.find_one()
    assert len(panel_obj["genes"]) == 0

    action = {"hgnc_id": hgnc_id, "action": "add", "symbol": hgnc_symbol, "info": {}}

    panel_obj["pending"] = [action]

    # update panel version to panel_version +1
    updated_panel_id = adapter.apply_pending(panel_obj, panel_obj["version"] + 1)
    updated_panel = adapter.panel_collection.find_one({"_id": updated_panel_id})

    # assert that panel version was updated
    assert updated_panel["version"] == panel_obj["version"] + 1

    assert len(updated_panel["genes"]) == 1


def test_apply_pending_add_two_genes(adapter, testpanel_obj):
    adapter.panel_collection.insert_one(testpanel_obj)
    ## GIVEN a adapter with a gene panel
    panel_obj = adapter.panel_collection.find_one()

    assert panel_obj

    gene = panel_obj["genes"][0]
    gene2 = panel_obj["genes"][1]
    hgnc_ids = [gene["hgnc_id"], gene["hgnc_id"]]
    hgnc_symbols = [gene["symbol"], gene["symbol"]]

    panel_obj["genes"] = []
    adapter.update_panel(panel_obj)

    panel_obj = adapter.panel_collection.find_one()
    assert len(panel_obj["genes"]) == 0

    action1 = {
        "hgnc_id": hgnc_ids[0],
        "action": "add",
        "symbol": hgnc_symbols[0],
        "info": {},
    }

    action2 = {
        "hgnc_id": hgnc_ids[1],
        "action": "add",
        "symbol": hgnc_symbols[1],
        "info": {},
    }

    panel_obj["pending"] = [action1, action2]

    # update panel without changing panel version
    updated_panel_id = adapter.apply_pending(panel_obj, panel_obj["version"])
    updated_panel = adapter.panel_collection.find_one({"_id": updated_panel_id})

    # assert that panel version was NOT updated
    assert updated_panel["version"] == panel_obj["version"]

    assert len(updated_panel["genes"]) == 2
    for gene in updated_panel["genes"]:
        assert gene["hgnc_id"] in hgnc_ids


def test_apply_pending_edit_gene(adapter, testpanel_obj):
    ## GIVEN an adapter with a gene panel
    adapter.panel_collection.insert_one(testpanel_obj)
    panel_obj = adapter.panel_collection.find_one()

    # Given a gene of this panel
    gene = panel_obj["genes"][0]
    hgnc_id = gene["hgnc_id"]
    hgnc_symbol = gene["symbol"]

    # without inheritance models
    assert gene.get("inheritance_models") is None
    assert gene.get("custom_inheritance_models") is None

    # When applying the the pending update to customize inheritance models
    action = {
        "hgnc_id": hgnc_id,
        "action": "edit",
        "symbol": hgnc_symbol,
        "info": {
            "inheritance_models": ["AR"],
            "custom_inheritance_models": ["model_1", "model_2"],
        },
    }
    panel_obj["pending"] = [action]
    updated_panel_id = adapter.apply_pending(panel_obj, panel_obj["version"] + 1)

    # Then the updated panel
    updated_panel = adapter.panel_collection.find_one({"_id": updated_panel_id})

    # should show the right inheritance models
    assert updated_panel["genes"][0]["inheritance_models"] == ["AR"]
    # and the right custom inheritance models
    assert updated_panel["genes"][0]["custom_inheritance_models"] == [
        "model_1",
        "model_2",
    ]


def test_clinical_symbols(case_obj, real_panel_database):
    """test function that returns a set of clinical genes symbols from test case panels"""

    # GIVEN an adapter with genes and a gene panel
    adapter = real_panel_database

    test_panel = adapter.panel_collection.find_one()

    # GIVEN a case analysed with that panel
    case_obj["panels"] = [{"panel_id": test_panel["_id"]}]

    # THEN the clinical_symbols function should return a valid set of clinical genes symbols for the case panel
    clinical_symbols = adapter.clinical_symbols(case_obj)
    assert len(clinical_symbols) > 0


def test_clinical_hgnc_ids(case_obj, real_panel_database):
    """test function that returns a set of clinical genes HGNC IDs from test case panels"""

    # GIVEN an adapter with genes and a gene panel
    adapter = real_panel_database

    test_panel = adapter.panel_collection.find_one()

    # GIVEN a case analysed with that panel
    case_obj["panels"] = [{"panel_id": test_panel["_id"]}]

    # THEN the clinical_hgnc_ids function should return a valid set of hgnc IDs for the case panel
    clinical_hgnc_ids = adapter.clinical_symbols(case_obj)
    assert len(clinical_hgnc_ids) > 0


def test_panel_to_genes(adapter, testpanel_obj):
    """Test function that converts gene panels to list of gene symbols/ids"""

    adapter.panel_collection.insert_one(testpanel_obj)

    # GIVEN a adapter with a gene panel
    panel_obj = adapter.panel_collection.find_one()
    assert panel_obj["genes"]

    # WHEN converting gene panel to list of gene symbols
    object_id = panel_obj["_id"]
    assert isinstance(object_id, ObjectId)

    # THEN return list of gene symbols from correct panel
    gene_symbols = adapter.panel_to_genes(panel_id=panel_obj["_id"])
    assert sorted(gene_symbols) == ["AAA", "BBB"]

    # WHEN converting panel to list of hgnc ids
    gene_symbols = adapter.panel_to_genes(panel_id=panel_obj["_id"], gene_format="hgnc_id")

    # THEN return list of hgnc ids
    assert sorted(gene_symbols) == [100, 222]

    # WHEN converting panel to gene list by panel name
    panel_name = testpanel_obj["panel_name"]
    gene_symbols = adapter.panel_to_genes(panel_name=panel_name)
    assert sorted(gene_symbols) == ["AAA", "BBB"]
