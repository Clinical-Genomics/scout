from scout.parse.omim import (parse_omim_line, parse_genemap2, parse_mim_titles, 
                              parse_mim2gene, get_mim_phenotypes)

GENEMAP_LINES = [
    "# Copyright (c) 1966-2016 Johns Hopkins University. Use of this"\
    " file adheres to the terms specified at https://omim.org/help/agreement.\n",
    "# Generated: 2017-02-02\n",
    "# See end of file for additional documentation on specific fields\n",
    "# Chromosome\tGenomic Position Start\tGenomic Position End\tCyto"\
    " Location\tComputed Cyto Location\tMim Number\tGene Symbols\tGene Name"\
    "\tApproved Symbol\tEntrez Gene ID\tEnsembl Gene ID\tComments\t"\
    "Phenotypes\tMouse Gene Symbol/ID\n",
    "chr1\t1232248\t1235040\t1p36.33\t\t615291\tB3GALT6, SEMDJL1, EDSP2\t"\
    "UDP-Gal:beta-Gal beta-1,3-galactosyltransferase polypeptide 6\tB3GALT"\
    "6\t126792\tENSG00000176022\t\tEhlers-Danlos syndrome, progeroid type,"\
    " 2, 615349 (3), Autosomal recessive; Spondyloepimetaphyseal dysplasia"\
    " with joint laxity, type 1, with or without fractures, 271640 (3),"\
    " Autosomal recessive\tB3galt6 (MGI:2152819)\n",
]

MIM2GENE_LINES = [
    "# Copyright (c) 1966-2016 Johns Hopkins University. Use of this file "\
    "adheres to the terms specified at https://omim.org/help/agreement.\n",
    "# Generated: 2017-02-02\n",
    "# This file provides links between the genes in OMIM and other gene"\
    " identifiers.\n",
    "# THIS IS NOT A TABLE OF GENE-PHENOTYPE RELATIONSHIPS.\n"
    "# MIM Number\tMIM Entry Type (see FAQ 1.3 at https://omim.org/help/faq)\t"\
    "Entrez Gene ID (NCBI)\tApproved Gene Symbol (HGNC)\tEnsembl Gene ID (Ensembl)\n",
    "615291\tgene\t126792\tB3GALT6\tENSG00000176022,ENST00000379198",
    "615349\tphenotype",
    "271640\tphenotype",
]

def test_parse_omim_line():
    ## GIVEN a header and a line
    header = ['a', 'b', 'c']
    line = '1\t2\t3'
    ## WHEN parsing the omim line
    res = parse_omim_line(line, header)
    
    ## THEN assert a dict was built by the header and the line
    assert res['a'] == '1'
    assert res['b'] == '2'
    assert res['c'] == '3'

def test_parse_genemap():
    
    for res in parse_genemap2(GENEMAP_LINES):
        assert res['Chromosome'] == 'chr1'
        assert res['mim_number'] == 615291
        assert res['hgnc_symbol'] == 'B3GALT6'
        assert res['inheritance'] == set(['AR'])
        for phenotype in res['phenotypes']:
            assert phenotype['mim_number']
            assert phenotype['inheritance']

def test_parse_genemap_file(genemap_handle):
    for i,res in enumerate(parse_genemap2(genemap_handle)):
        assert 'mim_number' in res
    
    assert i > 0

def test_parse_mim2gene():
    ## GIVEN some lines from a mim2gene file
    mim2gene_info = parse_mim2gene(MIM2GENE_LINES)
    
    ## WHEN parsing the lines
    first_entry = next(mim2gene_info)
    
    ## ASSERT that they are correctly parsed
    
    # First entry is a gene so it should have a hgnc symbol
    assert first_entry['mim_number'] == 615291
    assert first_entry['entry_type'] == 'gene'
    assert first_entry['hgnc_symbol'] == 'B3GALT6'

def test_parse_mim2gene_file(mim2gene_handle):
    # Just check that the file exists and that some result is given
    for i,res in enumerate(parse_mim2gene(mim2gene_handle)):
        assert 'mim_number' in res
    assert i > 0

def test_get_mim_phenotypes():
    ## GIVEN a small testdata set
    
    # This will return a dictionary with mim number as keys and
    # phenotypes as values
    
    ## WHEN parsing the phenotypes
    phenotypes = get_mim_phenotypes(genemap_lines=GENEMAP_LINES)

    ## THEN assert they where parsed in a correct way
    
    # There was only one line in GENEMAP_LINES that have two phenotypes
    # so we expect that there should be two phenotypes

    assert len(phenotypes) == 2

    term = phenotypes[615349]

    assert term['inheritance'] == set(['AR'])
    assert term['hgnc_symbols'] == set(['B3GALT6'])

def test_get_mim_phenotypes_file(genemap_handle):
    phenotypes = get_mim_phenotypes(genemap_lines=genemap_handle)
    
    for i, mim_nr in enumerate(phenotypes):
        assert phenotypes[mim_nr]['mim_number']

    assert i > 0
        