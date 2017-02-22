def test_insert_gene(pymongo_adapter):
    ##GIVEN a empty adapter
    assert pymongo_adapter.all_genes().count() == 0
    
    ##WHEN inserting a gene
    gene_obj = {
        'hgnc_id': 1,
        'hgnc_symbol': 'AAA',
        'build': '37'
    }
    obj_id = pymongo_adapter.load_hgnc_gene(gene_obj)
    
    ##THEN assert that the gene is there
    assert pymongo_adapter.all_genes().count() == 1
    ##THEN assert that no genes are in the '38' build
    assert pymongo_adapter.all_genes(build='38').count() == 0

def test_get_gene(pymongo_adapter):
    # pymongo_adapter = real_pymongo_adapter
    ##GIVEN a empty adapter
    assert pymongo_adapter.all_genes().count() == 0
    
    ##WHEN inserting a gene and fetching it
    gene_obj = {
        'hgnc_id': 1,
        'hgnc_symbol': 'AAA',
        'build': '37'
    }
    pymongo_adapter.load_hgnc_gene(gene_obj)
    
    
    ##THEN assert that the correct gene was fetched
    res = pymongo_adapter.hgnc_gene(
            hgnc_id=gene_obj['hgnc_id'], 
            build=gene_obj['build']
        )
    
    assert res['hgnc_id'] == gene_obj['hgnc_id']

    ##THEN assert that there are no genes in the 38 build
    res = pymongo_adapter.hgnc_gene(
            hgnc_id=gene_obj['hgnc_id'], 
            build='38'
        )
    
    assert res == None

def test_get_genes(pymongo_adapter):
    # pymongo_adapter = real_pymongo_adapter
    ##GIVEN a empty adapter
    assert pymongo_adapter.all_genes().count() == 0
    
    ##WHEN inserting two genes and fetching one
    gene_obj = {
        'hgnc_id': 1,
        'hgnc_symbol': 'AAA',
        'build': '37',
        'aliases': ['AAA', 'AAB'],
    }
    pymongo_adapter.load_hgnc_gene(gene_obj)

    gene_obj2 = {
        'hgnc_id': 2,
        'hgnc_symbol': 'AA',
        'build': '37',
        'aliases': ['AA', 'AB'],
    }

    pymongo_adapter.load_hgnc_gene(gene_obj2)
    
    res = pymongo_adapter.hgnc_genes(hgnc_symbol=gene_obj['hgnc_symbol'])
    
    ##THEN assert that the correct gene was fetched
    
    for result in res:
        assert result['hgnc_id'] == gene_obj['hgnc_id']

def test_get_genes_alias(pymongo_adapter):
    # pymongo_adapter = real_pymongo_adapter
    ##GIVEN a empty adapter
    assert pymongo_adapter.all_genes().count() == 0
    
    ##WHEN inserting two genes and fetching one
    gene_obj = {
        'hgnc_id': 1,
        'hgnc_symbol': 'AAA',
        'build': '37',
        'aliases': ['AAA', 'AAB'],
    }
    pymongo_adapter.load_hgnc_gene(gene_obj)

    gene_obj2 = {
        'hgnc_id': 2,
        'hgnc_symbol': 'AA',
        'build': '37',
        'aliases': ['AA', 'AB'],
    }

    pymongo_adapter.load_hgnc_gene(gene_obj2)
    
    res = pymongo_adapter.hgnc_genes(hgnc_symbol='AAB')
    
    ##THEN assert that the correct gene was fetched
    
    for result in res:
        assert result['hgnc_id'] == 1

def test_get_genes_regex(pymongo_adapter):
    # pymongo_adapter = real_pymongo_adapter
    ##GIVEN a empty adapter
    assert pymongo_adapter.all_genes().count() == 0
    
    ##WHEN inserting two genes and fetching one
    gene_obj = {
        'hgnc_id': 1,
        'hgnc_symbol': 'AAA',
        'build': '37',
        'aliases': ['AAA', 'BCD'],
    }
    pymongo_adapter.load_hgnc_gene(gene_obj)

    gene_obj2 = {
        'hgnc_id': 2,
        'hgnc_symbol': 'AA',
        'build': '37',
        'aliases': ['AA', 'AB'],
    }

    pymongo_adapter.load_hgnc_gene(gene_obj2)

    ##THEN assert that the correct gene was fetched    
    res = pymongo_adapter.hgnc_genes(hgnc_symbol='AA', search=True)
    assert res.count() == 2

    ##THEN assert that the correct gene was fetched    
    res = pymongo_adapter.hgnc_genes(hgnc_symbol='AB', search=True)
    assert res.count() == 1

    ##THEN assert that the correct gene was fetched    
    res = pymongo_adapter.hgnc_genes(hgnc_symbol='K', search=True)
    assert res.count() == 0

def test_get_all_genes(pymongo_adapter):
    # pymongo_adapter = real_pymongo_adapter
    ##GIVEN a empty adapter
    assert pymongo_adapter.all_genes().count() == 0
    
    ##WHEN inserting two genes and fetching one
    gene_obj = {
        'hgnc_id': 1,
        'hgnc_symbol': 'AAA',
        'build': '37',
        'aliases': ['AAA', 'AAB'],
    }
    pymongo_adapter.load_hgnc_gene(gene_obj)

    gene_obj2 = {
        'hgnc_id': 2,
        'hgnc_symbol': 'AA',
        'build': '37',
        'aliases': ['AA', 'AB'],
    }

    pymongo_adapter.load_hgnc_gene(gene_obj2)
    
    res = pymongo_adapter.all_genes()
    
    ##THEN assert that the correct number of genes where fetched
    assert res.count() == 2

def test_drop_genes(pymongo_adapter):
    # pymongo_adapter = real_pymongo_adapter
    ##GIVEN a empty adapter
    assert pymongo_adapter.all_genes().count() == 0
    
    ##WHEN inserting two genes and fetching one
    gene_obj = {
        'hgnc_id': 1,
        'hgnc_symbol': 'AAA',
        'build': '37',
        'aliases': ['AAA', 'AAB'],
    }
    pymongo_adapter.load_hgnc_gene(gene_obj)

    gene_obj2 = {
        'hgnc_id': 2,
        'hgnc_symbol': 'AA',
        'build': '37',
        'aliases': ['AA', 'AB'],
    }

    pymongo_adapter.load_hgnc_gene(gene_obj2)
    
    res = pymongo_adapter.all_genes()
    assert res.count() == 2
        
    ##THEN assert that the correct number of genes where fetched
    pymongo_adapter.drop_genes()
    res = pymongo_adapter.all_genes()
    assert res.count() == 0

def test_hgnc_id_to_gene(pymongo_adapter):
    # pymongo_adapter = real_pymongo_adapter
    ##GIVEN a empty adapter
    assert pymongo_adapter.all_genes().count() == 0
    
    ##WHEN inserting two genes and fetching one
    gene_obj = {
        'hgnc_id': 1,
        'hgnc_symbol': 'AAA',
        'build': '37',
        'aliases': ['AAA', 'AAB'],
    }
    pymongo_adapter.load_hgnc_gene(gene_obj)

    gene_obj2 = {
        'hgnc_id': 2,
        'hgnc_symbol': 'AA',
        'build': '37',
        'aliases': ['AA', 'AB'],
    }

    pymongo_adapter.load_hgnc_gene(gene_obj2)
    
    res = pymongo_adapter.all_genes()
    assert res.count() == 2
        
    ##THEN assert that the correct number of genes where fetched
    res = pymongo_adapter.hgncid_to_gene()
    assert gene_obj['hgnc_id'] in res
    assert gene_obj2['hgnc_id'] in res

def test_hgnc_symbol_to_gene(pymongo_adapter):
    # pymongo_adapter = real_pymongo_adapter
    ##GIVEN a empty adapter
    assert pymongo_adapter.all_genes().count() == 0
    
    ##WHEN inserting two genes and fetching one
    gene_obj = {
        'hgnc_id': 1,
        'hgnc_symbol': 'AAA',
        'build': '37',
        'aliases': ['AAA', 'AAB'],
    }
    pymongo_adapter.load_hgnc_gene(gene_obj)

    gene_obj2 = {
        'hgnc_id': 2,
        'hgnc_symbol': 'AA',
        'build': '37',
        'aliases': ['AA', 'AB'],
    }

    pymongo_adapter.load_hgnc_gene(gene_obj2)
    
    res = pymongo_adapter.all_genes()
    assert res.count() == 2
        
    ##THEN assert that the correct number of genes where fetched
    res = pymongo_adapter.hgncsymbol_to_gene()
    assert gene_obj['hgnc_symbol'] in res
    assert gene_obj2['hgnc_symbol'] in res

    