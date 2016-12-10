import datetime
from scout.parse.panel import (parse_gene_panel, parse_genes)
from scout.utils.handle import get_file_handle

def test_parse_panel_genes(panel_1_file):
    # GIVEN a gene panel file
    nr_genes = 0
    f = get_file_handle(panel_1_file)
    for line in f:
        if not line.startswith('#'):
            nr_genes += 1
    
    # WHEN parsing the panel of genes
    genes = parse_genes(panel_1_file)
    
    # THEN assert that all genes from the file have been parsed
    assert len(genes) == nr_genes
    
    # THEN assert that some genes exists in the panek
    for gene in genes:
        assert gene['hgnc_symbol']
        assert gene['hgnc_id']

def test_get_full_list_panel(panel_info):
    panel_1_file = panel_info['file']
    nr_genes = 0
    f = get_file_handle(panel_1_file)
    for line in f:
        if not line.startswith('#'):
            nr_genes += 1
    
    panel = parse_gene_panel(panel_info)

    assert panel['id'] == panel_info['name']
    assert len(panel['genes']) == nr_genes
    assert panel['date'] == datetime.date.today()
    assert panel['institute'] == panel_info['institute']
