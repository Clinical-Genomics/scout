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


@pytest.fixture
def vep_csq_header():
    """Returns the CSQ description from the header of a VEP-annotated VCF file - Has the same fields as vep_csq"""
    csq_header = """Allele|Consequence|IMPACT|SYMBOL|Gene|Feature_type|Feature|BIOTYPE|EXON|INTRON|HGVSc|HGVSp|cDNA_position|CDS_position|Protein_position|Amino_acids|Codons|Existing_variation|DISTANCE|STRAND|FLAGS|VARIANT_CLASS|SYMBOL_SOURCE|HGNC_ID|CANONICAL|MANE_SELECT|MANE_PLUS_CLINICAL|TSL|APPRIS|CCDS|ENSP|SWISSPROT|TREMBL|UNIPARC|UNIPROT_ISOFORM|REFSEQ_MATCH|SOURCE|REFSEQ_OFFSET|GIVEN_REF|USED_REF|BAM_EDIT|GENE_PHENO|SIFT|PolyPhen|DOMAINS|miRNA|HGVS_OFFSET|AF|AFR_AF|AMR_AF|EAS_AF|EUR_AF|SAS_AF|AA_AF|EA_AF|gnomAD_AF|gnomAD_AFR_AF|gnomAD_AMR_AF|gnomAD_ASJ_AF|gnomAD_EAS_AF|gnomAD_FIN_AF|gnomAD_NFE_AF|gnomAD_OTH_AF|gnomAD_SAS_AF|MAX_AF|MAX_AF_POPS|CLIN_SIG|SOMATIC|PHENO|PUBMED|MOTIF_NAME|MOTIF_POS|HIGH_INF_POS|MOTIF_SCORE_CHANGE|TRANSCRIPTION_FACTORS|CADD_PHRED|CADD_RAW|LoFtool|MES-NCSS_downstream_acceptor|MES-NCSS_downstream_donor|MES-NCSS_upstream_acceptor|MES-NCSS_upstream_donor|MES-SWA_acceptor_alt|MES-SWA_acceptor_diff|MES-SWA_acceptor_ref|MES-SWA_acceptor_ref_comp|MES-SWA_donor_alt|MES-SWA_donor_diff|MES-SWA_donor_ref|MES-SWA_donor_ref_comp|MaxEntScan_alt|MaxEntScan_diff|MaxEntScan_ref|gnomAD_mt_AF_hom|gnomAD_mt_AF_het|phyloP100way|phastCons"""

    return csq_header


@pytest.fixture
def vep_csq():
    """Returns the CSQ entry of a VEP-annotated variant - Has the same fields as vep_csq_header"""
    # Note that this has both MANE_SELECT and MANE_PLUS_CLINCAL set for testing purposes, but that
    # will never happen in real CSQ entries
    csq_entry = """C|synonymous_variant|LOW|SCN5A|6331|Transcript|NM_000335.5|protein_coding|17/28||NM_000335.5:c.3183A>G|NP_000326.2:p.Glu1061%3D|3392|3183|1061|E|gaA/gaG|rs7430407&CS1510231&COSV61125864||-1||SNV|EntrezGene|HGNC:10593|YES|NM_000335.5|NM_001099404.2||||NP_000326.2||||||RefSeq||T|T||||||||0.9242|0.8661|0.9164|0.997|0.9085|0.9438|0.8889|0.883|0.9139|0.8876|0.9444|0.8688|0.9993|0.9275|0.8895|0.9041|0.9398|0.9993|gnomAD_EAS|likely_benign&benign|0&0&1|1&1&1|25741868&24033266&27182706&26401487&25401102&20004937||||||1.179|-0.072561|0.000413|5.050|8.066|9.991|10.355|-11.882|-0.089|-11.970|-11.970|-1.050|2.025|0.976|0.976||||0.2|0.0123|-1.08899998664856|0.0209999997168779"""

    return csq_entry


@pytest.fixture
def vep_103_csq_header():
    """Returns the CSQ description from the header of a VEP-annotated VCF file - Has the same fields as vep_csq"""
    csq_header = """Consequence annotations from Ensembl VEP. Format: Allele|Consequence|IMPACT|SYMBOL|Gene|Feature_type|Feature|BIOTYqPE|EXON|INTRON|HGVSc|HGVSp|cDNA_position|CDS_position|Protein_position|Amino_acids|Codons|Existing_variation|DISTANCE|STRAND|FLAGS|SYMBOL_SOURCE|HGNC_ID|CANONICAL|TSL|APPRIS|CCDS|ENSP|SWISSPROT|TREMBL|UNIPARC|UNIPROT_ISOFORM|REFSEQ_MATCH|SOURCE|REFSEQ_OFFSET|GIVEN_REF|USED_REF|BAM_EDIT|SIFT|PolyPhen|DOMAINS|HGVS_OFFSET|MOTIF_NAME|MOTIF_POS|HIGH_INF_POS|MOTIF_SCORE_CHANGE|TRANSCRIPTION_FACTORS|LoFtool|GERP++_NR|GERP++_RS|REVEL_rankscore|phastCons100way_vertebrate|phyloP100way_vertebrate|MES-NCSS_downstream_acceptor|MES-NCSS_downstream_donor|MES-NCSS_upstream_acceptor|MES-NCSS_upstream_donor|MES-SWA_acceptor_alt|MES-SWA_acceptor_diff|MES-SWA_acceptor_ref|MES-SWA_acceptor_ref_comp|MES-SWA_donor_alt|MES-SWA_donor_diff|MES-SWA_donor_ref|MES-SWA_donor_ref_comp|MaxEntScan_alt|MaxEntScan_diff|MaxEntScan_ref|ExACpLI|SpliceAI_pred_DP_AG|SpliceAI_pred_DP_AL|SpliceAI_pred_DP_DG|SpliceAI_pred_DP_DL|SpliceAI_pred_DS_AG|SpliceAI_pred_DS_AL|SpliceAI_pred_DS_DG|SpliceAI_pred_DS_DL|SpliceAI_pred_SYMBOL|genomic_superdups_frac_match|CLINVAR|CLINVAR_CLNSIG|CLINVAR_CLNVID|CLINVAR_CLNREVSTAT"""

    return csq_header


@pytest.fixture
def vep_103_csq():
    """Returns the CSQ entry of a VEP-annotated variant - Has the same fields as vep_csq_header"""
    # Note that this has both MANE_SELECT and MANE_PLUS_CLINCAL set for testing purposes, but that
    # will never happen in real CSQ entries
    csq_entry = """G|intron_variant|MODIFIER|LMBRD1|ENSG00000168216|Transcript|ENST00000370577|protein_coding||1/15|ENST00000370577.3:c.69+397T>C|||||||||-1||HGNC|23038|YES|||CCDS4969.1|ENSP00000359609|LMBD1_HUMAN||UPI000003ED25|||Ensembl||A|A|||||||||||0.919||||||11.477|8.884||6.354|-2.006|1.389|-0.617|-0.617|5.299|-2.973|2.494|2.325||||0.00|-37|18|-2|3|0.00|0.00|0.06|0.17|LMBRD1|||||,G|intron_variant&NMD_transcript_variant|MODIFIER|LMBRD1|ENSG00000168216|Transcript|ENST00000472827|nonsense_mediated_decay||1/15|ENST00000472827.1:c.69+397T>C|||||||||-1||HGNC|23038|||||ENSP00000433385|LMBD1_HUMAN||UPI0000458A4E|||Ensembl||A|A|||||||||||0.919||||||11.477|8.884||6.354|-2.006|1.389|-0.617|-0.617|5.299|-2.973|2.494|2.325||||0.00|-37|18|-2|3|0.00|0.00|0.06|0.17|LMBRD1|||||,G|5_prime_UTR_variant|MODIFIER|LMBRD1|55788|Transcript|NM_001363722.2|protein_coding|1/16||NM_001363722.2:c.-273T>C||51|||||||-1||EntrezGene|23038|||||NP_001350651.1|||||rseq_mrna_match|RefSeq||A|A|||||||||||0.919||||||11.477|9.216|||-2.006|1.389|-0.617|-0.617|5.299|-2.973|2.494|2.325||||0.00|-37|18|-2|3|0.00|0.00|0.06|0.17|LMBRD1|||||,G|splice_region_variant&5_prime_UTR_variant|LOW|LMBRD1|55788|Transcript|NM_001367271.1|protein_coding|1/16||NM_001367271.1:c.-153T>C||194|||||||-1||EntrezGene|23038|||||NP_001354200.1|||||rseq_mrna_match|RefSeq||A|A|||||||||||0.919||||||11.477|2.325|||-2.006|1.389|-0.617|-0.617|5.299|-2.973|2.494|2.325|5.299|-2.973|2.325|0.00|-37|18|-2|3|0.00|0.00|0.06|0.17|LMBRD1|||||,G|splice_donor_variant|HIGH|LMBRD1|55788|Transcript|NM_001367272.1|protein_coding||1/15|NM_001367272.1:c.-151+2T>C|||||||||-1||EntrezGene|23038|||||NP_001354201.1|||||rseq_mrna_match|RefSeq||A|A|||||||||||0.919||||||11.477|8.884||2.494|-2.006|1.389|-0.617|-0.617|5.299|-2.973|2.494|2.325|-5.260|7.754|2.494|0.00|-37|18|-2|3|0.00|0.00|0.06|0.17|LMBRD1|||||,G|intron_variant|MODIFIER|LMBRD1|55788|Transcript|NM_018368.4|protein_coding||1/15|NM_018368.4:c.69+397T>C|||||||||-1||EntrezGene|23038|YES||||NP_060838.3|||||rseq_mrna_match|RefSeq||A|A|||||||||||0.919||||||11.477|8.884||6.354|-2.006|1.389|-0.617|-0.617|5.299|-2.973|2.494|2.325||||0.00|-37|18|-2|3|0.00|0.00|0.06|0.17|LMBRD1|||||;"""

    return csq_entry
