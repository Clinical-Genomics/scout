from  scout.build import build_individual

def test_build_individual():
    individual = {
        'ind_id': '1',
        'father': '2',
        'mother': '3',
        'display_name': '1-1',
        'sex': '1',
        'phenotype': 2,
        'bam_file': 'a.bam',
        'capture_kits': ['Agilent']
        
    }
    ind_obj = build_individual(individual)
    
    assert ind_obj.individual_id == individual['ind_id']
    assert ind_obj.display_name == individual['display_name']
    assert ind_obj.capture_kits == individual['capture_kits']