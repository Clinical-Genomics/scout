from scout.parse.omim import (parse_omim_line, parse_genemap2)

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
    genemap_lines = [
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
        " Autosomal recessive\tB3galt6 (MGI:2152819)\n"
    ]
    for res in parse_genemap2(genemap_lines):
        assert res['Chromosome'] == 'chr1'
        assert res['mim_number'] == 615291
        assert res['hgnc_symbol'] == 'B3GALT6'
        assert res['inheritance'] == set(['AR'])
        for phenotype in res['phenotypes']:
            assert phenotype['mim_number']
            assert phenotype['inheritance']
            
