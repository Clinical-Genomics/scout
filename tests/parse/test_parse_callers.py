from scout.parse.callers import parse_callers

def test_parse_callers():
    variant = {
        'info_dict':{
            'set': ['gatk-freebayes']
        }
    }
    
    callers = parse_callers(variant)
    
    assert callers['gatk'] == 'Pass'
    assert callers['freebayes'] == 'Pass'
    assert callers['samtools'] == None

def test_parse_callers_only_one():
    variant = {
        'info_dict':{
            'set': ['gatk']
        }
    }
    
    callers = parse_callers(variant)
    
    assert callers['gatk'] == 'Pass'
    assert callers['freebayes'] == None
    assert callers['samtools'] == None

def test_parse_callers_complex():
    variant = {
        'info_dict':{
            'set': ['gatk-filterInsamtools-freebayes']
        }
    }
    
    callers = parse_callers(variant)
    
    assert callers['gatk'] == 'Pass'
    assert callers['freebayes'] == 'Pass'
    assert callers['samtools'] == 'Filtered'

def test_parse_callers_intersection():
    variant = {
        'info_dict':{
            'set': ['Intersection']
        }
    }
    
    callers = parse_callers(variant)
    
    assert callers['gatk'] == 'Pass'
    assert callers['freebayes'] == 'Pass'
    assert callers['samtools'] == 'Pass'

def test_parse_callers_filtered_all():
    variant = {
        'info_dict':{
            'set': ['FilteredInAll']
        }
    }
    
    callers = parse_callers(variant)
    
    assert callers['gatk'] == 'Filtered'
    assert callers['freebayes'] == 'Filtered'
    assert callers['samtools'] == 'Filtered'
