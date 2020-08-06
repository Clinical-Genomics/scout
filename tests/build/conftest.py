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
def test_transcript():
     transcript ={
         'chrom': '1',
         'transcript_start': 1167629,
         'transcript_end': 1170421,
         'mrna': {'NM_080605'},
         'mrna_predicted': set(),
         'nc_rna': set(),
         'ensembl_gene_id': 'ENSG00000176022',
         'ensembl_transcript_id': 'ENST00000379198',
         'hgnc_id': 17978,
         'primary_transcripts': {'NM_080605'}
     }
     return transcript
