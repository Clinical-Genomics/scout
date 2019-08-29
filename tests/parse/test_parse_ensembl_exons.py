from pprint import pprint as pp

from scout.parse.ensembl import (parse_ensembl_exons, parse_ensembl_exon_request)

from pandas import DataFrame

def test_parse_ensembl_request(exon_info):
    """Test to parse a small dataframe line of ensembl transcript"""
    ## GIVEN a small transcript data framse
    
    exon_data = {
        'chromosome_name': exon_info['chrom'],
        'ensembl_gene_id': [exon_info['ens_gene_id']],
        'ensembl_transcript_id': [exon_info['ens_transcript_id']],
        'ensembl_exon_id': [exon_info['ens_exon_id']],
        'exon_chrom_start': [exon_info['start']],
        'exon_chrom_end': [exon_info['end']],
        '5_utr_start': [exon_info['utr_5_start']],
        '5_utr_end': [exon_info['utr_5_end']],
        '3_utr_start': [exon_info['utr_3_start']],
        '3_utr_end': [exon_info['utr_3_end']],
        'strand': [exon_info['strand']],
        'rank': [exon_info['exon_rank']],
    }
    df = DataFrame(exon_data)
    
    parsed_exons = parse_ensembl_exon_request(df)
    
    parsed_exon = next(parsed_exons)
    
    ## THEN assert the parsed transcript is as expected
    assert parsed_exon['chrom'] == exon_info['chrom']
    assert parsed_exon['gene'] == exon_info['ens_gene_id']
    assert parsed_exon['transcript'] == exon_info['ens_transcript_id']

def test_parse_ensembl_transcripts(exons_handle):
    """Test to parse all ensembl exons"""
    ## GIVEN an iterable with exon lines
    ## WHEN parsing the exons in that file
    exons = parse_ensembl_exons(exons_handle)

    ## THEN assert that these exons have some keys
    for exon in exons:
        assert exon['ens_exon_id']
        assert exon['transcript']
        assert exon['gene']


def test_parse_exons_data_frame(exons_df):
    """Test to parse all ensembl exons from data frame"""
    ## GIVEN a data frame with exon information
    exons = parse_ensembl_exon_request(exons_df)

    ## WHEN parsing the exons
    i = 0
    for i,exon_info in enumerate(exons):
        ## THEN assert they all got the mandatory ids
        assert exon_info['ens_exon_id']
        assert exon_info['transcript']
        assert exon_info['gene']
    assert i > 0