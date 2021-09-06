"""Fixtures for cases"""
import datetime

import pytest


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
        ],
    }
    return panel_info


@pytest.fixture
def dummy_case():
    """Return a simple case"""
    case_info = {
        "case_id": "1",
        "owner": "cust000",
        "individuals": [
            {"analysis_type": "wgs", "sex": 1, "phenotype": 2, "individual_id": "ind1"}
        ],
        "status": "inactive",
    }
    return case_info
