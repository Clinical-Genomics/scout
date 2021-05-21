"""Fixtures for cases"""
import datetime

import pytest


@pytest.fixture
def hpo_term(gene_list):
    """A test HPO term"""
    term = {
        "_id": "HP:0001250",
        "hpo_id": "HP:0001250",
        "description": "Seizure",
        "genes": gene_list,
    }
    return term


@pytest.fixture
def gene_list():
    """A list of HGNC ids"""
    gene_list = [26113, 9479, 10889, 18040, 10258, 1968]
    return gene_list


@pytest.fixture
def panel():
    """Return a simple panel"""
    panel_info = {
        "panel_name": "panel1",
        "display_name": "test panel",
        "institute": "cust000",
        "version": 1.0,
        "date": datetime.datetime.now(),
        "genes": [
            {"hgnc_id": 234, "symbol": "ADK"},
            {"hgnc_id": 7481, "symbol": "MT-TF"},
            {"hgnc_id": 1968, "symbol": "LYST"},
        ],
    }
    return panel_info


@pytest.fixture
def test_case(panel):
    """Return a simple case"""
    case_info = {
        "case_id": "1",
        "genome_build": 37,
        "owner": "cust000",
        "individuals": [
            {"analysis_type": "wgs", "sex": 1, "phenotype": 2, "individual_id": "ind1"}
        ],
        "status": "inactive",
        "panels": [panel],
    }
    return case_info
