import datetime
from scout.parse.panel import (parse_gene_panel, parse_genes)

def test_parse_panel_genes(panel_1_file):
    nr_genes = 0
    with open(panel_1_file, 'r') as f:
        for line in f:
            if not line.startswith('#'):
                nr_genes += 1
    
    genes = parse_genes(panel_1_file)
    
    assert len(genes) == nr_genes
    
    for gene in genes:
        assert gene['hgnc_symbol']
        if gene['hgnc_symbol'] == 'COQ2':
            assert gene['disease_associated_transcripts'] == ['NM_015697']
        if gene['hgnc_symbol'] == 'APPL1':
            assert gene['reduced_penetrance'] == True
            
    

def test_get_full_list_panel(panel_info):
    panel_1_file = panel_info['file']
    nr_genes = 0
    with open(panel_1_file, 'r') as f:
        for line in f:
            if not line.startswith('#'):
                nr_genes += 1
    
    panel = parse_gene_panel(panel_info)

    assert panel['id'] == panel_info['name']
    assert len(panel['genes']) == nr_genes
    assert panel['date'] == datetime.date.today()
    assert panel['institute'] == panel_info['institute']
