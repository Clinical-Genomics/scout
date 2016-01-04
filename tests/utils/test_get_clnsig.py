from scout.ext.backend.utils import get_clnsig

def test_get_clnsig():
    variant = {
        'info_dict':{
            'SnpSift_CLNACC': [
                "RCV000014440.17|RCV000014441.25|RCV000014442.25|RCV000014443.17|RCV000184011.1|RCV000188658.1" 
                ],
            'SnpSift_CLNSIG': [
                "5|5|5|5|5|5" 
                ],
            
            }
    }
    clnsig_annotations = get_clnsig(variant)
    assert len(clnsig_annotations) == 6
