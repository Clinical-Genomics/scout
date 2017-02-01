from scout.build.panel import build_panel, build_gene

def test_build_gene():
    ## GIVEN some gene info
    gene_info = {
        'hgnc_id': 1,
        'inheritance_models': ['AR','AD']
    }
    
    ## WHEN building a gene obj
    gene_obj = build_gene(gene_info)
    
    ## THEN assert that the object is correct
    
    assert gene_obj.hgnc_id == 1
    assert gene_obj.ar == True
    assert gene_obj.ad == True
    assert not gene_obj.mt
    

def test_build_panel(parsed_panel):
    panel_obj = build_panel(parsed_panel)

    assert panel_obj.institute == parsed_panel['institute']
    assert len(parsed_panel['genes']) == len(panel_obj.genes)