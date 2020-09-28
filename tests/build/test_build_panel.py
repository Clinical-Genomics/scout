import pytest

from scout.exceptions import IntegrityError
from scout.build.panel import build_panel, build_gene
from datetime import datetime


def test_build_panel_gene(adapter, test_gene):
    adapter.load_hgnc_gene(test_gene)
    ## GIVEN some gene info
    gene_info = {"hgnc_id": test_gene["hgnc_id"], "inheritance_models": ["AR", "AD"]}

    ## WHEN building a gene obj
    gene_obj = build_gene(gene_info, adapter)

    ## THEN assert that the object is correct

    assert gene_obj["hgnc_id"] == 1
    assert gene_obj["symbol"] == test_gene["hgnc_symbol"]
    assert gene_obj["ar"] is True
    assert gene_obj["ad"] is True
    assert "mt" not in gene_obj


def test_build_panel(institute_database, test_gene):
    ## GIVEN a adapter with a gene and a institute
    adapter = institute_database
    adapter.load_hgnc_gene(test_gene)

    # panel_id and display_name contain leading and trailing whitespaces to test that the spaces are removed
    panel_info = {
        "panel_id": " panel1",
        "institute": "cust000",
        "date": datetime.now(),
        "display_name": "first panel ",
        "description": "first panel description",
        "genes": [{"hgnc_id": 1}],
        "version": 1.0,
    }
    ## WHEN building a gene panel
    panel_obj = build_panel(panel_info, adapter)

    ## THEN assert that the panel was given the right attributes and that the leading and trailing spaces were removed
    assert panel_obj["institute"] == panel_info["institute"]
    assert panel_obj["panel_name"] == "panel1"
    assert panel_obj["display_name"] == "first panel"
    assert len(panel_info["genes"]) == len(panel_obj["genes"])


def test_build_panel_no_id(institute_database, test_gene):
    ## GIVEN a adapter with a gene and a institute
    adapter = institute_database
    adapter.load_hgnc_gene(test_gene)

    ## WHEN building a gene panel without panel_name
    panel_info = {
        "institute": "cust000",
        "date": datetime.now(),
        "display_name": "first panel",
        "genes": [{"hgnc_id": 1}],
        "version": 1.0,
    }
    ## THEN assert a KeyError was raised
    with pytest.raises(KeyError):
        panel_obj = build_panel(panel_info, adapter)


def test_build_panel_no_institute(institute_database, test_gene):
    ## GIVEN a adapter with a gene and a institute
    adapter = institute_database
    adapter.load_hgnc_gene(test_gene)

    ## WHEN building a gene panel without institute
    panel_info = {
        "panel_name": "panel1",
        "date": datetime.now(),
        "display_name": "first panel",
        "genes": [{"hgnc_id": 1}],
        "version": 1.0,
    }
    ## THEN assert a KeyError was raised
    with pytest.raises(KeyError):
        panel_obj = build_panel(panel_info, adapter)


def test_build_panel_no_date(institute_database, test_gene):
    ## GIVEN a adapter with a gene and a institute
    adapter = institute_database
    adapter.load_hgnc_gene(test_gene)

    ## WHEN building a gene panel without date
    panel_info = {
        "panel_name": "panel1",
        "institute": "cust000",
        "display_name": "first panel",
        "genes": [{"hgnc_id": 1}],
        "version": 1.0,
    }
    ## THEN assert a KeyError was raised
    with pytest.raises(KeyError):
        panel_obj = build_panel(panel_info, adapter)


def test_build_panel_non_existing_insitute(institute_database, test_gene):
    ## GIVEN a adapter with a gene and a institute
    adapter = institute_database
    adapter.load_hgnc_gene(test_gene)
    assert adapter.institute("cust001") is None

    ## WHEN building a gene panel with wrong institute
    panel_info = {
        "panel_name": "panel1",
        "institute": "cust0001",
        "date": datetime.now(),
        "display_name": "first panel",
        "genes": [{"hgnc_id": 1}],
        "version": 1.0,
    }
    ## THEN assert that an IntegrityError is raised
    with pytest.raises(IntegrityError):
        panel_obj = build_panel(panel_info, adapter)


def test_build_panel_non_existing_gene(institute_database, institute_obj):
    """Test creating a panel by proving one gene that is not in database"""

    ### GIVEN a adapter with an institute and no genes
    adapter = institute_database
    assert adapter.hgnc_collection.find_one() is None

    ## WHEN building a gene panel with wrong institute
    panel_info = {
        "panel_name": "panel1",
        "institute": institute_obj["_id"],
        "date": datetime.now(),
        "display_name": "first panel",
        "genes": [{"hgnc_id": 1}],
        "version": 1.0,
    }

    ## THEN assert that an IntegrityError is raised
    with pytest.raises(IntegrityError):
        panel_obj = build_panel(panel_info, adapter)
