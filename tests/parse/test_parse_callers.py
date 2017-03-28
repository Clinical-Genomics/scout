from scout.parse.variant.callers import parse_callers

def test_parse_callers():
    # GIVEN information that gatk and freebayes have passed
    variant = {
        'info_dict':{
            'set': ['gatk-freebayes']
        }
    }
    
    # WHEN parsing the information
    callers = parse_callers(variant)
    
    #THEN the correct callers should be passed
    assert callers['gatk'] == 'Pass'
    assert callers['freebayes'] == 'Pass'
    assert callers['samtools'] == None

def test_parse_callers_only_one():
    # GIVEN information about the variant callers
    variant = {
        'info_dict':{
            'set': ['gatk']
        }
    }
    
    # WHEN parsing the information
    callers = parse_callers(variant)
    
    #THEN the correct callers should be passed
    assert callers['gatk'] == 'Pass'
    assert callers['freebayes'] == None
    assert callers['samtools'] == None

def test_parse_callers_complex():
    # GIVEN information about the variant callers
    variant = {
        'info_dict':{
            'set': ['gatk-filterInsamtools-freebayes']
        }
    }
    
    # WHEN parsing the information
    callers = parse_callers(variant)
    
    #THEN the correct output should be returned
    assert callers['gatk'] == 'Pass'
    assert callers['freebayes'] == 'Pass'
    assert callers['samtools'] == 'Filtered'

def test_parse_callers_intersection():
    # GIVEN information that all callers agree on Pass
    variant = {
        'info_dict':{
            'set': ['Intersection']
        }
    }
    
    # WHEN parsing the information
    callers = parse_callers(variant)
    
    #THEN all callers should be passed
    assert callers['gatk'] == 'Pass'
    assert callers['freebayes'] == 'Pass'
    assert callers['samtools'] == 'Pass'

def test_parse_callers_filtered_all():
    # GIVEN information that all callers agree on filtered
    variant = {
        'info_dict':{
            'set': ['FilteredInAll']
        }
    }
    
    # WHEN parsing the information
    callers = parse_callers(variant)
    
    #THEN all callers should be filtered
    assert callers['gatk'] == 'Filtered'
    assert callers['freebayes'] == 'Filtered'
    assert callers['samtools'] == 'Filtered'
