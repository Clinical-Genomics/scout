from scout.build.genes.transcript import build_transcript

def test_build_simplest_transcript():
    ## GIVEN some transcript information
    transcript_info = {
        'transcript': 'ENST1',
        'hgnc_id': 1,
        'chrom': '1',
        'start': 10,
        'end': 100,
    }
    
    ## WHEN building the transcript
    
    transcript_obj = build_transcript(transcript_info)
    
    assert transcript_obj['transcript_id'] == transcript_info['transcript']
    assert transcript_obj['hgnc_id'] == transcript_info['hgnc_id']