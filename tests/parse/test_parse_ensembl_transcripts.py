from scout.parse.ensembl import (parse_ensembl_line, parse_ensembl_transcripts)

def test_parse_ensembl_line(transcripts_handle):
    """Test to parse a line of ensembl transcript"""
    header = next(transcripts_handle).split('\t')
    first_gene = next(transcripts_handle)
    gene_info = parse_ensembl_line(header=header, line=first_gene)
    
    assert gene_info['ensembl_gene_id'] == first_gene.split('\t')[0]


def test_parse_ensembl_transcripts(transcripts_handle):
    """Test to parse all ensembl transcripts"""
    transcripts = parse_ensembl_transcripts(transcripts_handle)
    
    for transcript in transcripts:
        assert transcript['ensembl_transcript_id']