
def test_build_query(adapter):
    case_id = 'cust000'
    
    # GIVEN a empty database
    
    # WHEN building a query
    query = adapter.build_query(case_id)
    
    # THEN the query should be on the right format
    assert query['case_id'] == case_id
    assert query['category'] == 'snv'
    assert query['variant_type'] == 'clinical'

def test_build_gnomad_query(adapter):
    case_id = 'cust000'
    freq = 0.01
    query = {'gnomad_frequency': freq}
    
    mongo_query = adapter.build_query(case_id, query=query)
    
    assert mongo_query['case_id'] == case_id
    assert mongo_query['category'] == 'snv'
    assert mongo_query['variant_type'] == 'clinical'    
    assert mongo_query['$and'] == [
        {
            '$or':[
                {'gnomad_frequency': {'$lt': freq}},
                {'gnomad_frequency': {'$exists': False}}
            ]
        }
    ]

def test_build_non_existing_gnomad(adapter):
    case_id = 'cust000'
    freq = '-1'
    query = {'gnomad_frequency': freq}
    
    mongo_query = adapter.build_query(case_id, query=query)
    
    assert mongo_query['gnomad_frequency'] == {'$exists': False}

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
    cadd_inclusive = True
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

def test_build_gnomad_and_cadd(adapter):
    case_id = 'cust000'
    freq = 0.01
    cadd = 10.0
    query = {'gnomad_frequency': freq, 'cadd_score': cadd}
    
    mongo_query = adapter.build_query(case_id, query=query)
    
    assert mongo_query['$and'] == [
        {
            '$or':[
                {'gnomad_frequency': {'$lt': freq}},
                {'gnomad_frequency': {'$exists': False}}
            ]
        },
        {
            'cadd_score': {'$gt': cadd}
        }
    ]

def test_build_clinsig(adapter):
    case_id = 'cust000'
    clinsig_items = [ 3, 4, 5 ]
    query = {'clinsig': clinsig_items}
    
    mongo_query = adapter.build_query(case_id, query=query)

    assert mongo_query['clnsig.value'] == {
            '$in': clinsig_items
            }

def test_build_clinsig_filter(adapter):
    case_id = 'cust000'
    clinsig_items = [ 4, 5 ]
    region_annotation = ['exonic', 'splicing']
    
    query = {'region_annotations': region_annotation, 
                 'clinsig': clinsig_items }
    
    mongo_query = adapter.build_query(case_id, query=query)
    
    assert mongo_query['$and'] == [
        { 'genes.region_annotation':
              {'$in': region_annotation }
          },
        { 'clnsig.value':
              { '$in': clinsig_items }
          } 
        ]

def test_build_clinsig_always(adapter):
    case_id = 'cust000'
    clinsig_confident_always_returned = True
    clinsig_items = [ 4, 5 ]
    region_annotation = ['exonic', 'splicing']
    freq=0.01
    
    query = {'region_annotations': region_annotation, 
             'clinsig': clinsig_items,
             'clinsig_confident_always_returned': clinsig_confident_always_returned,
             'gnomad_frequency': freq
             }

    mongo_query = adapter.build_query(case_id, query=query)

    assert mongo_query['$or'] == [
        { '$and': 
          [ {
              '$or':[
                {'gnomad_frequency': {'$lt': freq}},
                {'gnomad_frequency': {'$exists': False}}
            ]
         },
            {'genes.region_annotation':
               {'$in': region_annotation }
          },
             ]},
        { 'clnsig':
              {
                '$elemMatch': { 'value':
                                    { '$in' : clinsig_items },
                                'revstat':
                                    { '$in' : ['mult', 
                                               'single', 
                                               'exp', 
                                               'guideline'] 
                                      }
                                }
                }
          }
        ]

def test_build_spidex_not_reported(adapter):
    case_id = 'cust000'
    spidex_human = ['not_reported']

    query = { 'spidex_human': spidex_human }
    
    mongo_query = adapter.build_query(case_id, query=query)
    
    assert mongo_query['$and'] == [{'$or': [{'spidex': {'$exists': False}}] }] 

def test_build_spidex_high(adapter):
    case_id = 'cust000'
    spidex_human = ['high']

    query = { 'spidex_human': spidex_human }
    
    mongo_query = adapter.build_query(case_id, query=query)
    
    assert mongo_query['$and'] == [{'$or': [{'$or': [
                    {'$and': [
                            {'spidex': {'$gt': -2}}, {'spidex': {'$lt': -float('inf')}}]}, 
                    {'$and': [
                            {'spidex': {'$gt': 2}}, {'spidex': {'$lt': float('inf')}}]}
                    ]}]}]

def test_build_clinsig_always_only(adapter):
    case_id = 'cust000'
    clinsig_confident_always_returned = True
    clinsig_items = [ 4, 5 ]

    query = {'clinsig': clinsig_items,
             'clinsig_confident_always_returned': clinsig_confident_always_returned
             }

    mongo_query = adapter.build_query(case_id, query=query)

    assert mongo_query['clnsig'] == {
        '$elemMatch': { 'value':
                            { '$in' : clinsig_items },
                        'revstat':
                            { '$in' : ['mult', 
                                       'single', 
                                       'exp', 
                                       'guideline'] 
                              }
                        }
        }

def test_build_chrom(adapter):
    case_id = 'cust000'
    chrom = '1'
    query = {'chrom': chrom}

    mongo_query = adapter.build_query(case_id, query=query)

    assert mongo_query['chromosome'] == chrom


def test_build_ngi_sv(adapter):
    case_id = 'cust000'
    count = 1
    query = {'clingen_ngi': count}
    
    mongo_query = adapter.build_query(case_id, query=query)
    assert  mongo_query['$and'] == [
        {
            '$or':[
                {'clingen_ngi': {'$exists': False}},
                {'clingen_ngi': {'$lt': query['clingen_ngi'] + 1}}
            ]
        }
    ]

def test_build_range(adapter):
    case_id = 'cust000'
    chrom = '1'
    start = 10
    end = 11
    query = {'chrom': chrom, 'start': start, 'end': end}

    mongo_query = adapter.build_query(case_id, query=query)

    assert mongo_query['chromosome'] == chrom
    assert mongo_query['position'] == {'$lte': end}
    assert mongo_query['end'] == {'$gte': start}

def test_get_overlapping_variant(populated_database, parsed_case):
    """Add a couple of overlapping variants"""
    
    ## GIVEN a database with some basic information but no variants
    
    case_id = parsed_case['case_id']

    assert populated_database.variants(case_id, category='snv').count() == 0
    
    assert populated_database.variants(case_id, category='sv').count() == 0

    ## WHEN inserting a couple of variants
    
    institute_id = parsed_case['owner']
    institute_obj = populated_database.institute(institute_id)
    snv_one = dict(
        _id='first',
        document_id='first',
        variant_id='first',
        display_name='first',
        simple_id='first',
        variant_type='clinical',
        category='snv',
        sub_category='snv',
        case_id=case_id,
        chromosome='1',
        position=235824342,
        end=235824342,
        length=1,
        reference='A',
        alternative='T',
        rank_score=10,
        variant_rank=1,
        institute=institute_obj,
        hgnc_symbols=['LYST'],
        hgnc_ids=[1968]
    )
    populated_database.load_variant(snv_one)

    snv_two = dict(
        _id='second',
        document_id='second',
        variant_id='second',
        display_name='second',
        simple_id='second',
        variant_type='clinical',
        category='snv',
        sub_category='snv',
        case_id=case_id,
        chromosome='1',
        position=235824350,
        end=235824350,
        length=1,
        reference='G',
        alternative='T',
        rank_score=9,
        variant_rank=2,
        institute=institute_obj,
        hgnc_symbols=['LYST'],
        hgnc_ids=[1968]
    )
    
    populated_database.load_variant(snv_two)

    sv_one = dict(
        _id='first_sv',
        document_id='first_sv',
        variant_id='first_sv',
        display_name='first_sv',
        simple_id='first_sv',
        variant_type='clinical',
        category='sv',
        sub_category='ins',
        case_id=case_id,
        chromosome='1',
        position=235824350,
        end=235824355,
        length=5,
        reference='A',
        alternative='ATTTTTT',
        rank_score=10,
        variant_rank=1,
        institute=institute_obj,
        hgnc_symbols=['LYST'],
        hgnc_ids=[1968]
    )
    populated_database.load_variant(sv_one)
    ## THEN make sure that the variants where inserted
    result = populated_database.variants(case_id, category='snv')
    # Thow snvs where loaded
    assert result.count() == 2

    #One SV was added
    result = populated_database.variants(case_id, category='sv')
    assert result.count() == 1
        
    #Try to match only snv_one
    query = {'chrom': '1', 'start': 235824342, 'end':235824342}
    result = populated_database.variants(case_id, category='snv', query=query)
    assert result.count() == 1

    #Try to match both snvs
    query = {'chrom': '1', 'start': 235824341, 'end':235824352}
    result = populated_database.variants(case_id, category='snv', query=query)
    assert result.count() == 2

    #Try interval larger than sv
    query = {'chrom': '1', 'start': 235824342, 'end':235824360}
    result = populated_database.variants(case_id, category='sv', query=query)
    assert result.count() == 1

    #Try interval lower overlap sv
    query = {'chrom': '1', 'start': 235824332, 'end':235824352}
    result = populated_database.variants(case_id, category='sv', query=query)
    assert result.count() == 1

    #Try interval outside sv
    query = {'chrom': '1', 'start': 5, 'end':7}
    result = populated_database.variants(case_id, category='sv', query=query)
    assert result.count() == 0

    #Try minimal interval sv
    query = {'chrom': '1', 'start': 235824352, 'end':235824352}
    result = populated_database.variants(case_id, category='sv', query=query)
    assert result.count() == 1

    # test function
    result = populated_database.overlapping(snv_one)
    index = 0
    for variant in result:
        index += 1
    assert index == 1

    # test function
    result = populated_database.overlapping(snv_two)
    index = 0
    for variant in result:
        index += 1
    assert index == 1

    # test function
    result = populated_database.overlapping(sv_one)
    index = 0
    for variant in result:
        index += 1
    assert index == 2
