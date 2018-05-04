from scout.parse.ensembl import (parse_ensembl_line, parse_ensembl_transcripts, 
                                 parse_ensembl_transcript_request, parse_transcripts)

from pandas import DataFrame

def test_parse_ensembl_line(transcript_info):
    """Test to parse a line of ensembl transcript"""
    ## GIVEN some transcript information and a header
    header = ['Chromosome/scaffold name', 'Gene stable ID', 'Transcript stable ID', 
              'Transcript start (bp)', 'Transcript end (bp)', 'RefSeq mRNA ID', 
              'RefSeq mRNA predicted ID', 'RefSeq ncRNA ID']
    
    transcript_line = "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}".format(
        transcript_info['chrom'], transcript_info['ens_gene_id'], 
        transcript_info['ens_transcript_id'], transcript_info['start'], transcript_info['end'], 
        transcript_info['refseq_mrna'], transcript_info['refseq_mrna_pred'], 
        transcript_info['refseq_ncrna']
    )
    
    ## WHEN parsing the transcript line
    parsed_transcript = parse_ensembl_line(header=header, line=transcript_line)
    
    ## THEN assert the parsed transcript is as expected
    assert parsed_transcript['chrom'] == transcript_info['chrom']
    assert parsed_transcript['ensembl_gene_id'] == transcript_info['ens_gene_id']
    assert parsed_transcript['ensembl_transcript_id'] == transcript_info['ens_transcript_id']
    assert parsed_transcript['transcript_start'] == transcript_info['start']
    assert parsed_transcript['transcript_end'] == transcript_info['end']
    assert parsed_transcript['refseq_mrna'] == transcript_info['refseq_mrna']
    assert 'refseq_mrna_predicted' not in parsed_transcript
    assert 'refseq_ncrna' not in parsed_transcript
    
def test_parse_ensembl_request(transcript_info):
    """Test to parse a small dataframe line of ensembl transcript"""
    ## GIVEN a small transcript data framse
    
    tx_data = {
        'chromosome_name': transcript_info['chrom'],
        'ensembl_gene_id': [transcript_info['ens_gene_id']],
        'ensembl_transcript_id': [transcript_info['ens_transcript_id']],
        'transcript_start': [transcript_info['start']],
        'transcript_end': [transcript_info['end']],
        'refseq_mrna': [transcript_info['refseq_mrna']],
        'refseq_mrna_predicted': [transcript_info['refseq_mrna_pred']],
        'refseq_ncrna': [transcript_info['refseq_ncrna']],
    }
    df = DataFrame(tx_data)
    
    parsed_transcripts = parse_ensembl_transcript_request(df)
    
    parsed_tx = next(parsed_transcripts)
    
    ## THEN assert the parsed transcript is as expected
    assert parsed_tx['chrom'] == transcript_info['chrom']
    assert parsed_tx['ensembl_gene_id'] == transcript_info['ens_gene_id']
    assert parsed_tx['ensembl_transcript_id'] == transcript_info['ens_transcript_id']
    assert parsed_tx['transcript_start'] == transcript_info['start']
    assert parsed_tx['transcript_end'] == transcript_info['end']
    assert parsed_tx['refseq_mrna'] == transcript_info['refseq_mrna']
    assert parsed_tx['refseq_mrna_predicted'] == transcript_info['refseq_mrna_pred']
    assert parsed_tx['refseq_ncrna'] == transcript_info['refseq_ncrna']


def test_parse_ensembl_transcripts(transcripts_handle):
    """Test to parse all ensembl transcripts"""
    transcripts = parse_ensembl_transcripts(transcripts_handle)
    
    for transcript in transcripts:
        assert transcript['ensembl_transcript_id']
        assert transcript['ensembl_gene_id']


def test_parse_transcripts_file(transcripts_handle):
    """Test to parse all ensembl transcripts"""
    transcripts = parse_transcripts(transcripts_handle)
    
    for transcript_id in transcripts:
        transcript = transcripts[transcript_id]
        assert transcript['ensembl_transcript_id']
        assert transcript['ensembl_gene_id']

def test_parse_transcripts_data_frame(transcripts_df):
    """Test to parse all ensembl transcripts from data frame"""
    ## GIVEN a data frame with transcript information
    transcripts = parse_transcripts(transcripts_df)
    
    ## WHEN parsing the transcripts
    i = 0
    for i,transcript_id in enumerate(transcripts):
        transcript = transcripts[transcript_id]
    ## THEN assert they all got the mandatory ids
        assert transcript['ensembl_transcript_id']
        assert transcript['ensembl_gene_id']
    assert i > 0