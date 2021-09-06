"""Fixtures for coordinates"""

import pytest


class CyvcfVariant:
    """Mock a cyvcf variant

    Default is to return a variant with three individuals high genotype
    quality.
    """

    def __init__(
        self,
    ):
        self._chrom = "1"
        self._position = 80000
        self._reference = "A"
        self._alternative = "C"
        self._end = None
        self.var_type = "snv"
        self.INFO = {}

    @property
    def gt_quals(self):
        """Get the genotype qualities"""
        return [60, 60, 60]

    @property
    def gt_types(self):
        """Get the genotypes"""
        return [1, 1, 0]

    @property
    def CHROM(self):
        """Get the chrom"""
        return self._chrom

    @CHROM.setter
    def CHROM(self, value):
        """Set the chromosome"""
        self._chrom = value

    @property
    def POS(self):
        """Get the pos"""
        return self._position

    @POS.setter
    def POS(self, value):
        """Set the pos"""
        self._position = value

    @property
    def REF(self):
        """Get the reference"""
        return self._reference

    @REF.setter
    def REF(self, value):
        """Set the reference"""
        self._reference = value

    @property
    def ALT(self):
        """Get the alternative"""
        return [self._alternative]

    @ALT.setter
    def ALT(self, value):
        """Set the alternative"""
        self._alternative = value

    @property
    def end(self):
        """Get the end"""
        return self._end or self._position

    @end.setter
    def end(self, value):
        """Set the end"""
        self._end = value

    def __repr__(self):
        return (
            f"CyvcfVariant:CHROM:{self._chrom},REF:{self._reference},ALT:{self._alternative},POS:"
            f"{self._position},end:{self._end},INFO:{self.INFO}"
        )


@pytest.fixture
def mock_variant():
    """Return a mocked cyvcf2 variant"""
    return CyvcfVariant()


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
        "# This file provides links between the genes in OMIM and other gene" " identifiers.\n",
        "# THIS IS NOT A TABLE OF GENE-PHENOTYPE RELATIONSHIPS.\n"
        "# MIM Number\tMIM Entry Type (see FAQ 1.3 at https://omim.org/help/faq)\t"
        "Entrez Gene ID (NCBI)\tApproved Gene Symbol (HGNC)\tEnsembl Gene ID (Ensembl)\n",
        "615291\tgene\t126792\tB3GALT6\tENSG00000176022,ENST00000379198",
        "615349\tphenotype",
        "271640\tphenotype",
    ]

    return lines
