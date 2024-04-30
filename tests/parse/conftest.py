import pytest

"""Fixtures for coordinates"""


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
    csq_header = """Allele|Consequence|IMPACT|SYMBOL|Gene|Feature_type|Feature|BIOTYqPE|EXON|INTRON|HGVSc|HGVSp|cDNA_position|CDS_position|Protein_position|Amino_acids|Codons|Existing_variation|DISTANCE|STRAND|FLAGS|SYMBOL_SOURCE|HGNC_ID|CANONICAL|TSL|APPRIS|CCDS|ENSP|SWISSPROT|TREMBL|UNIPARC|UNIPROT_ISOFORM|REFSEQ_MATCH|SOURCE|REFSEQ_OFFSET|GIVEN_REF|USED_REF|BAM_EDIT|SIFT|PolyPhen|DOMAINS|HGVS_OFFSET|MOTIF_NAME|MOTIF_POS|HIGH_INF_POS|MOTIF_SCORE_CHANGE|TRANSCRIPTION_FACTORS|LoFtool|GERP++_NR|GERP++_RS|REVEL_rankscore|phastCons100way_vertebrate|phyloP100way_vertebrate|MES-NCSS_downstream_acceptor|MES-NCSS_downstream_donor|MES-NCSS_upstream_acceptor|MES-NCSS_upstream_donor|MES-SWA_acceptor_alt|MES-SWA_acceptor_diff|MES-SWA_acceptor_ref|MES-SWA_acceptor_ref_comp|MES-SWA_donor_alt|MES-SWA_donor_diff|MES-SWA_donor_ref|MES-SWA_donor_ref_comp|MaxEntScan_alt|MaxEntScan_diff|MaxEntScan_ref|ExACpLI|SpliceAI_pred_DP_AG|SpliceAI_pred_DP_AL|SpliceAI_pred_DP_DG|SpliceAI_pred_DP_DL|SpliceAI_pred_DS_AG|SpliceAI_pred_DS_AL|SpliceAI_pred_DS_DG|SpliceAI_pred_DS_DL|SpliceAI_pred_SYMBOL|genomic_superdups_frac_match|CLINVAR|CLINVAR_CLNSIG|CLINVAR_CLNVID|CLINVAR_CLNREVSTAT"""

    return csq_header


@pytest.fixture
def vep_103_csq():
    """Returns the CSQ entry of a VEP-annotated variant - Has the same fields as vep_csq_header"""
    # Note that this has both MANE_SELECT and MANE_PLUS_CLINCAL set for testing purposes, but that
    # will never happen in real CSQ entries
    csq_entry = """G|intron_variant|MODIFIER|LMBRD1|ENSG00000168216|Transcript|ENST00000370577|protein_coding||1/15|ENST00000370577.3:c.69+397T>C|||||||||-1||HGNC|23038|YES|||CCDS4969.1|ENSP00000359609|LMBD1_HUMAN||UPI000003ED25|||Ensembl||A|A|||||||||||0.919||||||11.477|8.884||6.354|-2.006|1.389|-0.617|-0.617|5.299|-2.973|2.494|2.325||||0.00|-37|18|-2|3|0.00|0.00|0.06|0.17|LMBRD1|||||,G|intron_variant&NMD_transcript_variant|MODIFIER|LMBRD1|ENSG00000168216|Transcript|ENST00000472827|nonsense_mediated_decay||1/15|ENST00000472827.1:c.69+397T>C|||||||||-1||HGNC|23038|||||ENSP00000433385|LMBD1_HUMAN||UPI0000458A4E|||Ensembl||A|A|||||||||||0.919||||||11.477|8.884||6.354|-2.006|1.389|-0.617|-0.617|5.299|-2.973|2.494|2.325||||0.00|-37|18|-2|3|0.00|0.00|0.06|0.17|LMBRD1|||||,G|5_prime_UTR_variant|MODIFIER|LMBRD1|55788|Transcript|NM_001363722.2|protein_coding|1/16||NM_001363722.2:c.-273T>C||51|||||||-1||EntrezGene|23038|||||NP_001350651.1|||||rseq_mrna_match|RefSeq||A|A|||||||||||0.919||||||11.477|9.216|||-2.006|1.389|-0.617|-0.617|5.299|-2.973|2.494|2.325||||0.00|-37|18|-2|3|0.00|0.00|0.06|0.17|LMBRD1|||||,G|splice_region_variant&5_prime_UTR_variant|LOW|LMBRD1|55788|Transcript|NM_001367271.1|protein_coding|1/16||NM_001367271.1:c.-153T>C||194|||||||-1||EntrezGene|23038|||||NP_001354200.1|||||rseq_mrna_match|RefSeq||A|A|||||||||||0.919||||||11.477|2.325|||-2.006|1.389|-0.617|-0.617|5.299|-2.973|2.494|2.325|5.299|-2.973|2.325|0.00|-37|18|-2|3|0.00|0.00|0.06|0.17|LMBRD1|||||,G|splice_donor_variant|HIGH|LMBRD1|55788|Transcript|NM_001367272.1|protein_coding||1/15|NM_001367272.1:c.-151+2T>C|||||||||-1||EntrezGene|23038|||||NP_001354201.1|||||rseq_mrna_match|RefSeq||A|A|||||||||||0.919||||||11.477|8.884||2.494|-2.006|1.389|-0.617|-0.617|5.299|-2.973|2.494|2.325|-5.260|7.754|2.494|0.00|-37|18|-2|3|0.00|0.00|0.06|0.17|LMBRD1|||||,G|intron_variant|MODIFIER|LMBRD1|55788|Transcript|NM_018368.4|protein_coding||1/15|NM_018368.4:c.69+397T>C|||||||||-1||EntrezGene|23038|YES||||NP_060838.3|||||rseq_mrna_match|RefSeq||A|A|||||||||||0.919||||||11.477|8.884||6.354|-2.006|1.389|-0.617|-0.617|5.299|-2.973|2.494|2.325||||0.00|-37|18|-2|3|0.00|0.00|0.06|0.17|LMBRD1|||||;"""

    return csq_entry


@pytest.fixture
def vep_107_csq_header():
    # VEP 107
    csq_header = """Allele|Consequence|IMPACT|SYMBOL|Gene|Feature_type|Feature|BIOTYPE|EXON|INTRON|HGVSc|HGVSp|cDNA_position|CDS_position|Protein_position|Amino_acids|Codons|Existing_variation|DISTANCE|STRAND|FLAGS|SYMBOL_SOURCE|HGNC_ID|REFSEQ_MATCH|SOURCE|REFSEQ_OFFSET|GIVEN_REF|USED_REF|BAM_EDIT|GENE_PHENO|SIFT|PolyPhen|miRNA|HGVS_OFFSET|AF|AFR_AF|AMR_AF|EAS_AF|EUR_AF|SAS_AF|CLIN_SIG|SOMATIC|PHENO|MOTIF_NAME|MOTIF_POS|HIGH_INF_POS|MOTIF_SCORE_CHANGE|TRANSCRIPTION_FACTORS|SpliceAI_pred_DP_AG|SpliceAI_pred_DP_AL|SpliceAI_pred_DP_DG|SpliceAI_pred_DP_DL|SpliceAI_pred_DS_AG|SpliceAI_pred_DS_AL|SpliceAI_pred_DS_DG|SpliceAI_pred_DS_DL|SpliceAI_pred_SYMBOL|CADD_PHRED|CADD_RAW|1000Gp3_AC|1000Gp3_AF|1000Gp3_AFR_AC|1000Gp3_AFR_AF|1000Gp3_AMR_AC|1000Gp3_AMR_AF|1000Gp3_EAS_AC|1000Gp3_EAS_AF|1000Gp3_EUR_AC|1000Gp3_EUR_AF|1000Gp3_SAS_AC|1000Gp3_SAS_AF|ALSPAC_AC|ALSPAC_AF|AltaiNeandertal|Ancestral_allele|CADD_phred|CADD_raw|CADD_raw_rankscore|DANN_rankscore|DANN_score|Denisova|ESP6500_AA_AC|ESP6500_AA_AF|ESP6500_EA_AC|ESP6500_EA_AF|Eigen-PC-phred|Eigen-PC-raw|Eigen-PC-raw_rankscore|Eigen-phred|Eigen-raw|Eigen_coding_or_noncoding|Ensembl_geneid|Ensembl_proteinid|Ensembl_transcriptid|ExAC_AC|ExAC_AF|ExAC_AFR_AC|ExAC_AFR_AF|ExAC_AMR_AC|ExAC_AMR_AF|ExAC_Adj_AC|ExAC_Adj_AF|ExAC_EAS_AC|ExAC_EAS_AF|ExAC_FIN_AC|ExAC_FIN_AF|ExAC_NFE_AC|ExAC_NFE_AF|ExAC_SAS_AC|ExAC_SAS_AF|ExAC_nonTCGA_AC|ExAC_nonTCGA_AF|ExAC_nonTCGA_AFR_AC|ExAC_nonTCGA_AFR_AF|ExAC_nonTCGA_AMR_AC|ExAC_nonTCGA_AMR_AF|ExAC_nonTCGA_Adj_AC|ExAC_nonTCGA_Adj_AF|ExAC_nonTCGA_EAS_AC|ExAC_nonTCGA_EAS_AF|ExAC_nonTCGA_FIN_AC|ExAC_nonTCGA_FIN_AF|ExAC_nonTCGA_NFE_AC|ExAC_nonTCGA_NFE_AF|ExAC_nonTCGA_SAS_AC|ExAC_nonTCGA_SAS_AF|ExAC_nonpsych_AC|ExAC_nonpsych_AF|ExAC_nonpsych_AFR_AC|ExAC_nonpsych_AFR_AF|ExAC_nonpsych_AMR_AC|ExAC_nonpsych_AMR_AF|ExAC_nonpsych_Adj_AC|ExAC_nonpsych_Adj_AF|ExAC_nonpsych_EAS_AC|ExAC_nonpsych_EAS_AF|ExAC_nonpsych_FIN_AC|ExAC_nonpsych_FIN_AF|ExAC_nonpsych_NFE_AC|ExAC_nonpsych_NFE_AF|ExAC_nonpsych_SAS_AC|ExAC_nonpsych_SAS_AF|FATHMM_converted_rankscore|FATHMM_pred|FATHMM_score|GERP++_NR|GERP++_RS|GERP++_RS_rankscore|GM12878_confidence_value|GM12878_fitCons_score|GM12878_fitCons_score_rankscore|GTEx_V6p_gene|GTEx_V6p_tissue|GenoCanyon_score|GenoCanyon_score_rankscore|H1-hESC_confidence_value|H1-hESC_fitCons_score|H1-hESC_fitCons_score_rankscore|HUVEC_confidence_value|HUVEC_fitCons_score|HUVEC_fitCons_score_rankscore|Interpro_domain|LRT_Omega|LRT_converted_rankscore|LRT_pred|LRT_score|M-CAP_pred|M-CAP_rankscore|M-CAP_score|MetaLR_pred|MetaLR_rankscore|MetaLR_score|MetaSVM_pred|MetaSVM_rankscore|MetaSVM_score|MutPred_AAchange|MutPred_Top5features|MutPred_protID|MutPred_rankscore|MutPred_score|MutationAssessor_UniprotID|MutationAssessor_pred|MutationAssessor_score|MutationAssessor_score_rankscore|MutationAssessor_variant|MutationTaster_AAE|MutationTaster_converted_rankscore|MutationTaster_model|MutationTaster_pred|MutationTaster_score|PROVEAN_converted_rankscore|PROVEAN_pred|PROVEAN_score|Polyphen2_HDIV_pred|Polyphen2_HDIV_rankscore|Polyphen2_HDIV_score|Polyphen2_HVAR_pred|Polyphen2_HVAR_rankscore|Polyphen2_HVAR_score|REVEL_rankscore|REVEL_score|Reliability_index|SIFT_converted_rankscore|SIFT_pred|SIFT_score|SiPhy_29way_logOdds|SiPhy_29way_logOdds_rankscore|SiPhy_29way_pi|TWINSUK_AC|TWINSUK_AF|Transcript_id_VEST3|Transcript_var_VEST3|Uniprot_aapos_Polyphen2|Uniprot_acc_Polyphen2|Uniprot_id_Polyphen2|VEST3_rankscore|VEST3_score|aaalt|aapos|aaref|alt|cds_strand|chr|clinvar_clnsig|clinvar_golden_stars|clinvar_rs|clinvar_trait|codon_degeneracy|codonpos|fathmm-MKL_coding_group|fathmm-MKL_coding_pred|fathmm-MKL_coding_rankscore|fathmm-MKL_coding_score|genename|gnomAD_exomes_AC|gnomAD_exomes_AF|gnomAD_exomes_AFR_AC|gnomAD_exomes_AFR_AF|gnomAD_exomes_AFR_AN|gnomAD_exomes_AMR_AC|gnomAD_exomes_AMR_AF|gnomAD_exomes_AMR_AN|gnomAD_exomes_AN|gnomAD_exomes_ASJ_AC|gnomAD_exomes_ASJ_AF|gnomAD_exomes_ASJ_AN|gnomAD_exomes_EAS_AC|gnomAD_exomes_EAS_AF|gnomAD_exomes_EAS_AN|gnomAD_exomes_FIN_AC|gnomAD_exomes_FIN_AF|gnomAD_exomes_FIN_AN|gnomAD_exomes_NFE_AC|gnomAD_exomes_NFE_AF|gnomAD_exomes_NFE_AN|gnomAD_exomes_OTH_AC|gnomAD_exomes_OTH_AF|gnomAD_exomes_OTH_AN|gnomAD_exomes_SAS_AC|gnomAD_exomes_SAS_AF|gnomAD_exomes_SAS_AN|gnomAD_genomes_AC|gnomAD_genomes_AF|gnomAD_genomes_AFR_AC|gnomAD_genomes_AFR_AF|gnomAD_genomes_AFR_AN|gnomAD_genomes_AMR_AC|gnomAD_genomes_AMR_AF|gnomAD_genomes_AMR_AN|gnomAD_genomes_AN|gnomAD_genomes_ASJ_AC|gnomAD_genomes_ASJ_AF|gnomAD_genomes_ASJ_AN|gnomAD_genomes_EAS_AC|gnomAD_genomes_EAS_AF|gnomAD_genomes_EAS_AN|gnomAD_genomes_FIN_AC|gnomAD_genomes_FIN_AF|gnomAD_genomes_FIN_AN|gnomAD_genomes_NFE_AC|gnomAD_genomes_NFE_AF|gnomAD_genomes_NFE_AN|gnomAD_genomes_OTH_AC|gnomAD_genomes_OTH_AF|gnomAD_genomes_OTH_AN|hg18_chr|hg18_pos(1-based)|hg19_chr|hg19_pos(1-based)|integrated_confidence_value|integrated_fitCons_score|integrated_fitCons_score_rankscore|phastCons100way_vertebrate|phastCons100way_vertebrate_rankscore|phastCons20way_mammalian|phastCons20way_mammalian_rankscore|phyloP100way_vertebrate|phyloP100way_vertebrate_rankscore|phyloP20way_mammalian|phyloP20way_mammalian_rankscore|pos(1-based)|ref|refcodon|rs_dbSNP150|gnomADg|gnomADg_AF_POPMAX|gnomADg_AF"""

    return csq_header


@pytest.fixture
def vep_107_csq():
    csq_entry = """TA|intron_variant|MODIFIER|CPNE4|ENSG00000196353|Transcript|ENST00000429747|protein_coding||1/15|ENST00000429747.1:c.-2+56179_-2+56180dup|||||||rs1354150623||-1||HGNC|2317||Ensembl|||||||||||||||||||||||||||||||||0.768|-0.189993||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||3:131697231-131697243|7.69231e-02|5.47945e-02,TA|intron_variant|MODIFIER|CPNE4|ENSG00000196353|Transcript|ENST00000502818|protein_coding||2/16|ENST00000502818.1:c.53+59169_53+59170dup|||||||rs1354150623||-1||HGNC|2317||Ensembl|||||||||||||||||||||||||||||||||0.768|-0.189993||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||3:131697231-131697243|7.69231e-02|5.47945e-02,TA|intron_variant|MODIFIER|CPNE4|ENSG00000196353|Transcript|ENST00000505957|protein_coding||2/3|ENST00000505957.1:c.-2+56179_-2+56180dup|||||||rs1354150623||-1|cds_end_NF|HGNC|2317||Ensembl|||||||||||||||||||||||||||||||||0.768|-0.189993||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||3:131697231-131697243|7.69231e-02|5.47945e-02,TA|intron_variant|MODIFIER|CPNE4|ENSG00000196353|Transcript|ENST00000511604|protein_coding||4/18|ENST00000511604.1:c.-2+56179_-2+56180dup|||||||rs1354150623||-1||HGNC|2317||Ensembl|||||||||||||||||||||||||||||||||0.768|-0.189993||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||3:131697231-131697243|7.69231e-02|5.47945e-02,TA|intron_variant|MODIFIER|CPNE4|ENSG00000196353|Transcript|ENST00000512055|protein_coding||5/19|ENST00000512055.1:c.-2+56179_-2+56180dup|||||||rs1354150623||-1||HGNC|2317||Ensembl|||||||||||||||||||||||||||||||||0.768|-0.189993||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||3:131697231-131697243|7.69231e-02|5.47945e-02,TA|intron_variant|MODIFIER|CPNE4|ENSG00000196353|Transcript|ENST00000512332|protein_coding||2/16|ENST00000512332.1:c.53+59169_53+59170dup|||||||rs1354150623||-1||HGNC|2317||Ensembl|||||||||||||||||||||||||||||||||0.768|-0.189993||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||3:131697231-131697243|7.69231e-02|5.47945e-02,TA|intron_variant|MODIFIER|CPNE4|ENSG00000196353|Transcript|ENST00000514999|protein_coding||1/2|ENST00000514999.1:c.-2+39067_-2+39068dup|||||||rs1354150623||-1|cds_end_NF|HGNC|2317||Ensembl|||||||||||||||||||||||||||||||||0.768|-0.189993||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||3:131697231-131697243|7.69231e-02|5.47945e-02,TA|intron_variant|MODIFIER|CPNE4|131034|Transcript|NM_001289112.2|protein_coding||1/15|NM_001289112.2:c.53+59169_53+59170dup|||||||rs1354150623||-1||EntrezGene|2317||RefSeq|||||||||||||||||||||||||||||||||0.768|-0.189993||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||3:131697231-131697243|7.69231e-02|5.47945e-02,TA|intron_variant|MODIFIER|CPNE4|131034|Transcript|NM_130808.3|protein_coding||1/15|NM_130808.3:c.-2+56179_-2+56180dup|||||||rs1354150623||-1||EntrezGene|2317||RefSeq|||||||||||||||||||||||||||||||||0.768|-0.189993||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||3:131697231-131697243|7.69231e-02|5.47945e-02,TA|intron_variant|MODIFIER|CPNE4|131034|Transcript|NM_153429.2|protein_coding||2/16|NM_153429.2:c.53+59169_53+59170dup|||||||rs1354150623||-1||EntrezGene|2317||RefSeq|||||||||||||||||||||||||||||||||0.768|-0.189993||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||3:131697231-131697243|7.69231e-02|5.47945e-02,TA|regulatory_region_variant|MODIFIER|||RegulatoryFeature|ENSR00001975847|open_chromatin_region||||||||||rs1354150623||||||||||||||||||||||||||||||||||||||||0.768|-0.189993||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||3:131697231-131697243|7.69231e-02|5.47945e-02"""

    return csq_entry
