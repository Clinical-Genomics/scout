from scout.build.transcript import build_transcript

def test_build_simplest_transcript():
    ## GIVEN some transcript information
    transcript_info = {
        'transcript_id': 'ENST1',
        'hgnc_id': 1
    }
    
    ## WHEN building the transcript
    
    transcript_obj = build_transcript(transcript_info)
    
    assert transcript_obj['transcript_id'] == transcript_info['transcript_id']
    assert transcript_obj['hgnc_id'] == transcript_info['hgnc_id']