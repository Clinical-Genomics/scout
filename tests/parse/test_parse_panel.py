import datetime
from scout.parse.panel import (parse_gene_panel, parse_genes, parse_gene)
from scout.utils.handle import get_file_handle

def test_parse_minimal_gene():
    ## GIVEN minimal gene line and header
    header = ["hgnc_id"]
    gene_line = ["10"]
    ## WHEN parsing the genes
    gene = parse_gene(gene_line, header)
    ## THEN assert that the gene is correctly parsed
    
    assert gene['hgnc_id'] == 10

def test_parse_gene():
    ## GIVEN gene line and header
    header = [
        "hgnc_id", 
        "hgnc_symbol",
        "disease_associated_transcripts",
        "reduced_penetrance",
        "genetic_disease_models",
        "mosaicism",
        "database_entry_version"
    ]
    hgnc_id = '10'
    hgnc_symbol = 'hello'
    transcripts = 'a,b,c'
    penetrance = 'YES'
    models = 'AR,AD'
    mosaicism = ''
    version = ''
    
    gene_line = [
        hgnc_id, 
        hgnc_symbol, 
        transcripts, 
        penetrance, 
        models,
        mosaicism,
        version
    ]
    ## WHEN parsing the genes
    gene = parse_gene(gene_line, header)
    ## THEN assert that the gene is correctly parsed
    assert gene['hgnc_id'] == int(hgnc_id)
    assert gene['hgnc_symbol'] == hgnc_symbol.upper()
    assert gene['transcripts'] == transcripts.split(',')
    assert gene['inheritance_models'] == models.split(',')
    assert gene['reduced_penetrance'] == True if penetrance else False
    assert gene['mosaicism'] == False
    assert gene['database_entry_version'] == version

def test_parse_panel_lines():
    ## GIVEN a iterable with panel lines
    panel_lines = [
        "##panel_id=panel1",
        "##institute=cust000",
        "##version=1.0",
        "##date=2016-12-09",
        "##display_name=Test panel",
        "#hgnc_id\thgnc_symbol\tdisease_associated_transcripts\treduced_penet"\
        "rance\tgenetic_disease_models\tmosaicism\tdatabase_entry_version\tor"\
        "iginal_hgnc",
        "7481\tMT-TF\t\t\t\t\t\tMT-TF\n"
    ]
    nr_genes = len([line for line in panel_lines if not line.startswith('#')])
    
    ## WHEN parsing the panel of genes
    genes = parse_genes(panel_lines)
    
    ## THEN assert that all genes from the file have been parsed
    assert len(genes) == nr_genes
    
    ## THEN assert that some genes exists in the panel
    for gene in genes:
        assert gene['hgnc_symbol']
        assert gene['hgnc_id']

def test_parse_panel_doublette():
    ## GIVEN a iterable with panel lines where one gene occurs twice
    panel_lines = [
        "#hgnc_id\thgnc_symbol\tdisease_associated_transcripts\treduced_penet"\
        "rance\tgenetic_disease_models\tmosaicism\tdatabase_entry_version\tor"\
        "iginal_hgnc",
        "7481\tMT-TF\t\t\t\t\t\tMT-TF\n"
        "7481\tMT-TF\t\t\t\t\t\tMT-TF\n"
    ]    
    ## WHEN parsing the panel of genes
    genes = parse_genes(panel_lines)
    
    ## THEN that the gene is only occuring once
    assert len(genes) == 1
    

def test_parse_panel_genes(panel_1_file):
    # GIVEN a gene panel file
    nr_genes = 0
    with open(panel_1_file, 'r') as f:
        for line in f:
            if not line.startswith('#'):
                nr_genes += 1

    # WHEN parsing the panel of genes
    f = get_file_handle(panel_1_file)
    genes = parse_genes(f)

    # THEN assert that all genes from the file have been parsed
    assert len(genes) == nr_genes

    # THEN assert that some genes exists in the panek
    for gene in genes:
        assert gene['hgnc_symbol']
        assert gene['hgnc_id']

def test_get_full_list_panel(panel_info):
    panel_1_file = panel_info['file']
    nr_genes = 0
    with open(panel_1_file, 'r') as f:
        for line in f:
            if not line.startswith('#'):
                nr_genes += 1

    panel = parse_gene_panel(panel_info)

    assert panel['panel_name'] == panel_info['panel_name']
    assert len(panel['genes']) == nr_genes
    assert panel['date'] == panel_info['date']
    assert panel['institute'] == panel_info['institute']
