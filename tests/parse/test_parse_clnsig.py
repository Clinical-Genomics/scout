from scout.parse.variant.clnsig import parse_clnsig

def test_parse_clnsig():
    ## GIVEN some clnsig information
    variant = {
        'info_dict':{
            'CLNACC': "RCV000014440.17|RCV000014441.25|RCV000014442.25|RCV000014443.17|RCV000184011.1|RCV000188658.1",
            'CLNSIG': "5|5|5|5|5|5",
            'CLNREVSTAT': "conf|single|single|single|conf|conf",
            }
    }
    
    ## WHEN parsing the clinical significance
    clnsig_annotations = parse_clnsig(
        acc=variant['info_dict']['CLNACC'], 
        sig=variant['info_dict']['CLNSIG'], 
        revstat=variant['info_dict']['CLNREVSTAT'],
        transcripts=[]
    )
    
    ## THEN assert that they where parsed correct
    assert len(clnsig_annotations) == 6
    
    for entry in clnsig_annotations:
        if entry['accession'] == "RCV000014440.17":
            assert entry['value'] == 5
            assert entry['revstat'] == 'conf'
