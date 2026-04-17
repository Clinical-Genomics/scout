from copy import deepcopy

import pytest


@pytest.fixture
def parsed_gene():
    gene_info = {
        "hgnc_id": 1,
        "hgnc_symbol": "AAA",
        "ensembl_id": "ENSG1",
        "chromosome": "1",
        "start": 10,
        "end": 100,
        "build": "37",
    }
    return gene_info
