import pytest


@pytest.fixture
def exon_info(request):
    exon = dict(
        chrom="1",
        ens_gene_id="ENSG00000176022",
        ens_exon_id="ENSE00001480062",
        ens_transcript_id="ENST00000379198",
        start=1167629,
        end=1170421,
        utr_5_start=1167629,
        utr_5_end=1167658,
        utr_3_start=1168649,
        utr_3_end=1170421,
        strand=1,
        exon_rank=1,
    )

    return exon


@pytest.fixture
def genemap_lines():
    """Returns some lines in genemap2 format, including header"""
    lines = [
        "# Copyright (c) 1966-2016 Johns Hopkins University. Use of this"
        " file adheres to the terms specified at https://omim.org/help/agreement.\n",
        "# Generated: 2017-02-02\n",
        "# See end of file for additional documentation on specific fields\n",
        "# Chromosome\tGenomic Position Start\tGenomic Position End\tCyto"
        " Location\tComputed Cyto Location\tMIM Number\tGene Symbols\tGene Name"
        "\tApproved Symbol\tEntrez Gene ID\tEnsembl Gene ID\tComments\t"
        "Phenotypes\tMouse Gene Symbol/ID\n",
        "chr1\t1232248\t1235040\t1p36.33\t\t615291\tB3GALT6, SEMDJL1, EDSP2\t"
        "UDP-Gal:beta-Gal beta-1,3-galactosyltransferase polypeptide 6\tB3GALT"
        "6\t126792\tENSG00000176022\t\tEhlers-Danlos syndrome, progeroid type,"
        " 2, 615349 (3), Autosomal recessive; Spondyloepimetaphyseal dysplasia"
        " with joint laxity, type 1, with or without fractures, 271640 (3),"
        " Autosomal recessive\tB3galt6 (MGI:2152819)\n",
    ]
    return lines


@pytest.fixture
def mim2gene_lines():
    """Returns some lines in mim2gene format, including header"""
    lines = [
        "# Copyright (c) 1966-2016 Johns Hopkins University. Use of this file "
        "adheres to the terms specified at https://omim.org/help/agreement.\n",
        "# Generated: 2017-02-02\n",
        "# This file provides links between the genes in OMIM and other gene"
        " identifiers.\n",
        "# THIS IS NOT A TABLE OF GENE-PHENOTYPE RELATIONSHIPS.\n"
        "# MIM Number\tMIM Entry Type (see FAQ 1.3 at https://omim.org/help/faq)\t"
        "Entrez Gene ID (NCBI)\tApproved Gene Symbol (HGNC)\tEnsembl Gene ID (Ensembl)\n",
        "615291\tgene\t126792\tB3GALT6\tENSG00000176022,ENST00000379198",
        "615349\tphenotype",
        "271640\tphenotype",
    ]

    return lines
