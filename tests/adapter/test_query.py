
def test_build_query(adapter):
    case_id = 'cust000'
    
    query = adapter.build_query(case_id)
    
    assert query['case_id'] == case_id
    assert query['category'] == 'snv'
    assert query['variant_type'] == 'clinical'

def test_build_thousand_g_query(adapter):
    case_id = 'cust000'
    freq = 0.01
    query = {'thousand_genomes_frequency': freq}
    
    mongo_query = adapter.build_query(case_id, query=query)
    
    assert mongo_query['case_id'] == case_id
    assert mongo_query['category'] == 'snv'
    assert mongo_query['variant_type'] == 'clinical'    
    assert mongo_query['$and'] == [
        {
            '$or':[
                {'thousand_genomes_frequency': {'$lt': freq}},
                {'thousand_genomes_frequency': {'$exists': False}}
            ]
        }
    ]

def test_build_non_existing_thousand_g(adapter):
    case_id = 'cust000'
    freq = '-1'
    query = {'thousand_genomes_frequency': freq}
    
    mongo_query = adapter.build_query(case_id, query=query)
    
    assert mongo_query['thousand_genomes_frequency'] == {'$exists': False}

def test_build_cadd_exclusive(adapter):
    case_id = 'cust000'
    cadd = 10.0
    cadd_inclusive = False
    query = {'cadd_score': cadd, 'cadd_inclusive': cadd_inclusive}

    mongo_query = adapter.build_query(case_id, query=query)

    assert mongo_query['$and'] == [
        {
            'cadd_score': {'$gt': cadd}
        }
    ]

def test_build_cadd_inclusive(adapter):
    case_id = 'cust000'
    cadd = 10.0
    cadd_inclusive = 'yes'
    query = {'cadd_score': cadd, 'cadd_inclusive': cadd_inclusive}

    mongo_query = adapter.build_query(case_id, query=query)

    assert mongo_query['$and'] == [
        {
            '$or':[
                {'cadd_score': {'$gt': cadd}},
                {'cadd_score': {'$exists': False}}
            ]
        }
    ]

def test_build_thousand_g_and_cadd(adapter):
    case_id = 'cust000'
    freq = 0.01
    cadd = 10.0
    query = {'thousand_genomes_frequency': freq, 'cadd_score': cadd}
    
    mongo_query = adapter.build_query(case_id, query=query)
    
    assert mongo_query['$and'] == [
        {
            '$or':[
                {'thousand_genomes_frequency': {'$lt': freq}},
                {'thousand_genomes_frequency': {'$exists': False}}
            ]
        },
        {
            'cadd_score': {'$gt': cadd}
        }
    ]

def test_build_chrom(adapter):
    case_id = 'cust000'
    chrom = '1'
    query = {'chrom': chrom}

    mongo_query = adapter.build_query(case_id, query=query)

    assert mongo_query['chromosome'] == chrom

def test_build_range(adapter):
    case_id = 'cust000'
    chrom = '1'
    start = 10
    end = 11
    query = {'chrom': chrom, 'start': start, 'end': end}

    mongo_query = adapter.build_query(case_id, query=query)

    assert mongo_query['chromosome'] == chrom
    assert mongo_query['position'] == {'$lt': end}
    assert mongo_query['end'] == {'$gt': start}


