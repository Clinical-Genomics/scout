# -*- coding: utf-8 -*-

# These are the valid SO terms with corresponfing severity rank
SO_TERMS = {
    'transcript_ablation': {'rank':1, 'region':'exonic'},
    'splice_donor_variant': {'rank':2, 'region':'splicing'},
    'splice_acceptor_variant': {'rank':3, 'region':'splicing'},
    'stop_gained': {'rank':4, 'region':'exonic'},
    'frameshift_variant': {'rank':5, 'region':'exonic'},
    'stop_lost': {'rank':6, 'region':'exonic'},
    'start_lost': {'rank': 7, 'region': 'exonic'},
    'initiator_codon_variant': {'rank':8, 'region':'exonic'},
    'inframe_insertion': {'rank':9, 'region':'exonic'},
    'inframe_deletion': {'rank':10, 'region':'exonic'},
    'missense_variant': {'rank':11, 'region':'exonic'},
    'protein_altering_variant': {'rank':12, 'region':'exonic'},
    'transcript_amplification': {'rank':13, 'region':'exonic'},
    'splice_region_variant': {'rank':14, 'region':'splicing'},
    'incomplete_terminal_codon_variant': {'rank':15, 'region':'exonic'},
    'synonymous_variant': {'rank':16, 'region':'exonic'},
    'stop_retained_variant': {'rank':17, 'region':'exonic'},
    'coding_sequence_variant': {'rank':18, 'region':'exonic'},
    'mature_miRNA_variant': {'rank':19, 'region':'ncRNA_exonic'},
    '5_prime_UTR_variant': {'rank':20, 'region':'5UTR'},
    '3_prime_UTR_variant': {'rank':21, 'region':'3UTR'},
    'non_coding_transcript_exon_variant': {'rank':22, 'region':'ncRNA_exonic'},
    'non_coding_exon_variant': {'rank':23, 'region':'ncRNA_exonic'},
    'non_coding_transcript_variant': {'rank':24, 'region':'ncRNA_exonic'},
    'nc_transcript_variant': {'rank':25, 'region':'ncRNA_exonic'},
    'intron_variant': {'rank':26, 'region':'intronic'},
    'NMD_transcript_variant': {'rank':27, 'region':'ncRNA'},
    'upstream_gene_variant': {'rank':28, 'region':'upstream'},
    'downstream_gene_variant': {'rank':29, 'region':'downstream'},
    'TFBS_ablation': {'rank':30, 'region':'TFBS'},
    'TFBS_amplification': {'rank':31, 'region':'TFBS'},
    'TF_binding_site_variant': {'rank':32, 'region':'TFBS'},
    'regulatory_region_ablation': {'rank':33, 'region':'regulatory_region'},
    'regulatory_region_amplification': {'rank':34, 'region':'regulatory_region'},
    'regulatory_region_variant': {'rank':35, 'region':'regulatory_region'},
    'feature_elongation': {'rank':36, 'region':'genomic_feature'},
    'feature_truncation': {'rank':37, 'region':'genomic_feature'},
    'intergenic_variant': {'rank':38, 'region':'intergenic_variant'}
}

SO_TERM_KEYS = list(SO_TERMS.keys())


CONSEQUENCE = (
    'deleterious',
    'deleterious_low_confidence',
    'probably_damaging',
    'possibly_damaging',
    'tolerated',
    'tolerated_low_confidence',
    'benign',
    'unknown'
)

CONSERVATION = ('NotConserved', 'Conserved')

SEVERE_SO_TERMS = (
    'transcript_ablation',
    'splice_donor_variant',
    'splice_acceptor_variant',
    'stop_gained',
    'frameshift_variant',
    'stop_lost',
    'start_lost',
    'initiator_codon_variant',
    'inframe_insertion',
    'inframe_deletion',
    'missense_variant',
    'protein_altering_variant',
    'transcript_amplification',
    'splice_region_variant',
    'incomplete_terminal_codon_variant',
    'synonymous_variant',
    'stop_retained_variant',
)

FEATURE_TYPES = (
  'exonic',
  'splicing',
  'ncRNA_exonic',
  'intronic',
  'ncRNA',
  'upstream',
  '5UTR',
  '3UTR',
  'downstream',
  'TFBS',
  'regulatory_region',
  'genomic_feature',
  'intergenic_variant'
)

GENETIC_MODELS = (
  ('AR_hom', 'Autosomal Recessive Homozygote'),
  ('AR_hom_dn', 'Autosomal Recessive Homozygote De Novo'),
  ('AR_comp', 'Autosomal Recessive Compound'),
  ('AR_comp_dn', 'Autosomal Recessive Compound De Novo'),
  ('AD', 'Autosomal Dominant'),
  ('AD_dn', 'Autosomal Dominant De Novo'),
  ('XR', 'X Linked Recessive'),
  ('XR_dn', 'X Linked Recessive De Novo'),
  ('XD', 'X Linked Dominant'),
  ('XD_dn', 'X Linked Dominant De Novo'),
)

ACMG_TERMS = (
  'pathegenic',
  'likely pathegenic',
  'uncertain significance',
  'likely benign',
  'benign'
)

VARIANT_CALL = (
    'Pass',
    'Filtered',
    'Not Found',
    'Not Used',
)

ANALYSIS_TYPES = ('wgs', 'wes', 'mixed', 'unknown')

SEX_MAP = {1: 'male', 2: 'female', 'other': 'unknown'}
REV_SEX_MAP = {value: key for key, value in SEX_MAP.items()}

PHENOTYPE_MAP = {1: 'unaffected', 2: 'affected', 0: 'unknown', -9: 'unknown'}
REV_PHENOTYPE_MAP = {value: key for key, value in PHENOTYPE_MAP.items()}

CLINSIG_MAP = {
    0: 'Uncertain significance',
    1: 'not provided',
    2: 'Benign',
    3: 'Likely benign',
    4: 'Likely pathogenic',
    5: 'Pathogenic',
    6: 'drug response',
    7: 'histocompatibility',
    255: 'other'
}
