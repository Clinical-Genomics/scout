from scout.parse.variant.clnsig import parse_clnsig

def test_parse_clnsig():
    variant = {
        'info_dict':{
            'CLNACC': [
                "RCV000014440.17|RCV000014441.25|RCV000014442.25|RCV000014443.17|RCV000184011.1|RCV000188658.1" 
                ],
            'CLNSIG': [
                "5|5|5|5|5|5" 
                ],
            'CLNREVSTAT': [
                "conf|single|single|single|conf|conf" 
                ],
            }
    }
    clnsig_annotations = parse_clnsig(variant)
    assert len(clnsig_annotations) == 6
