import pytest


@pytest.fixture
def parsed_exon():
    exon = dict(
        chrom="1",
        hgnc_id=234,
        exon_id="1-1167629-1170421",
        transcript="ENST00000379198",
        ens_exon_id="ENSE00001480062",
        start=1167629,
        end=1170421,
        strand=1,
        rank=1,
    )

    return exon


@pytest.fixture
def test_gene():
    gene = {
        # This is the hgnc id, required:
        "hgnc_id": 1,
        # The primary symbol, required
        "hgnc_symbol": "test",
        "ensembl_id": "ensembl1",  # required
        "ensembl_gene_id": "ensembl1",  # required
        "build": "37",  # '37' or '38', defaults to '37', required
        "chromosome": 1,  # required
        "start": 10,  # required
        "end": 100,  # required
        "description": "A gene",  # Gene description
        "aliases": ["test"],  # Gene symbol aliases, includes hgnc_symbol, str
        "entrez_id": 1,
        "omim_id": 1,
        "pli_score": 1.0,
        "primary_transcripts": ["NM1"],  # List of refseq transcripts (str)
        "ucsc_id": "1",
        "uniprot_ids": ["1"],  # List of str
        "vega_id": "1",
    }
    return gene


@pytest.fixture
def test_disease_id():
    disease_id = "OMIM:615349"
    return disease_id


@pytest.fixture
def test_disease():
    disease_info = {
        "description": "EHLERS-DANLOS SYNDROME, PROGEROID TYPE, 2",
        "hgnc_symbols": {"B3GALT6"},
        "hgnc_ids": {17978},
        "hpo_terms": {"HP:0008807", "HP:0010575"},
        "inheritance": {"AR"},
    }
    return disease_info


@pytest.fixture
def test_hpo_info():
    hpo_info = {
        "hpo_id": "HP:0000878",
        "description": "11 pairs of ribs",
        "genes": [1, 2],
    }
    return hpo_info
