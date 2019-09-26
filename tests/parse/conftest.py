import pytest

@pytest.fixture
def exon_info(request):
    exon = dict(
        chrom = '1',
        ens_gene_id = 'ENSG00000176022',
        ens_exon_id = 'ENSE00001480062',
        ens_transcript_id = 'ENST00000379198',
        start = 1167629,
        end = 1170421,
        utr_5_start=1167629,
        utr_5_end=1167658,
        utr_3_start=1168649,
        utr_3_end=1170421,
        strand=1,
        exon_rank=1,
    )

    return exon
