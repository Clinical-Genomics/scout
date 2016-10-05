from scout.parse.transcript import create_ensembl_to_refseq

def test_ensembl_to_refseq():
    variant = {
        'info_dict':{'Ensembl_transcript_to_refseq_transcript': [
                "SIVA1:ENST00000329967>NM_006427|ENST00000556431", 
                "AKT1:ENST00000349310>NM_001014432/XM_005267402"]
            }
    }
    conversion = create_ensembl_to_refseq(variant)
    assert conversion['ENST00000329967'] == ["NM_006427"]
    assert 'ENST00000556431' not in conversion
    assert conversion['ENST00000349310'] == ['NM_001014432','XM_005267402']