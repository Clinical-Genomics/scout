from scout.build.variant.clnsig import build_clnsig

def test_build_clnsig():
    clnsig_info = {
        'value': 5,
        'accession': 'some_accession',
        'revstat': 'arevstat'
    }
    
    clsnig_obj = build_clnsig(clnsig_info)
    
    assert isinstance(clsnig_obj, dict)