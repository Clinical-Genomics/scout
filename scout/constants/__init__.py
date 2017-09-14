# -*- coding: utf-8 -*-
from collections import OrderedDict

from intervaltree import (IntervalTree, Interval)

from scout.parse.cytoband import parse_cytoband
from scout.resources import cytobands_path
from scout.utils.handle import get_file_handle

cytobands_handle = get_file_handle(cytobands_path)

CYTOBANDS = parse_cytoband(cytobands_handle)

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

SV_TYPES = (
    'ins',
    'del',
    'dup',
    'cnv',
    'inv',
    'bnd'
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

ACMG_MAP = {
    4: 'pathogenic',
    3: 'likely_pathogenic',
    2: 'likely_benign',
    1: 'benign',
    0: 'uncertain_significance'
}
REV_ACMG_MAP = {value: key for key, value in ACMG_MAP.items()}
ACMG_SHORT_MAP = {value: ''.join([word[0].upper() for word in value.split('_')]) for value in
                  ACMG_MAP.values()}

VARIANT_CALL = (
    'Pass',
    'Filtered',
    'Not Found',
    'Not Used',
)

ANALYSIS_TYPES = ('wgs', 'wes', 'mixed', 'unknown')

SEX_MAP = {1: 'male', 2: 'female', 'other': 'unknown', 0: 'unknown'}
REV_SEX_MAP = {value: key for key, value in SEX_MAP.items() if key != 'other'}

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
REV_CLINSIG_MAP = {
    'uncertain_significance': 0,
    'not_provided': 1,
    'benign': 2,
    'likely_benign': 3,
    'likely_pathogenic': 4,
    'pathogenic': 5,
    'drug_response': 6,
    'histocompatibility': 7,
    'other': 255
}

CASE_STATUSES = ("prioritized", "inactive", "active", "solved", "archived")

PHENOTYPE_GROUPS = {
    'HP:0001298': {
        'name': 'Encephalopathy',
        'abbr': 'ENC'
    },
    'HP:0012759': {
        'name': 'Neurodevelopmental abnormality',
        'abbr': 'NDEV'
    },
    'HP:0001250': {
        'name': 'Seizures',
        'abbr': 'EP'
    },
    'HP:0100022': {
        'name': 'Abnormality of movement',
        'abbr': 'MOVE'
    },
    'HP:0000707': {
        'name': 'Neurology, other',
        'abbr': 'NEUR'
    },
    'HP:0003011': {
        'name': 'Abnormality of the musculature',
        'abbr': 'MUSC'
    },
    'HP:0001638': {
        'name': 'Cardiomyopathy',
        'abbr': 'CARD'
    },
    'HP:0001507': {
        'name': 'Growth abnormality',
        'abbr': 'GROW'
    },
    'HP:0001392': {
        'name': 'Abnormality of the liver',
        'abbr': 'LIV'
    },
    'HP:0011458': {
        'name': 'Abdominal symptom',
        'abbr': 'GI'
    },
    'HP:0012373': {
        'name': 'Abnormal eye physiology',
        'abbr': 'EYE'
    },
    'HP:0000077': {
        'name': 'Abnormality of the kidney',
        'abbr': 'KIDN'
    },
    'HP:0000951': {
        'name': 'Abnormality of the skin',
        'abbr': 'SKIN'
    },
    'HP:0001939': {
        'name': 'Abnormality of metabolism/homeostasis',
        'abbr': 'METAB'
    },
    'HP:0000118': {
        'name': 'As yet undefined/to be added',
        'abbr': 'UND'
    },
    'HP:0002011': {
        'name': 'Abnormal CNS morphology',
        'abbr': 'MRI'
    }
}

COHORT_TAGS = [
    'endo',
    'mito',
    'ketogenic diet',
    'pedhep',
    'other',
]

PAR_COORDINATES = {
    '37': {
        'X': IntervalTree([Interval(60001, 2699521, 'par1'),
                           Interval(154931044, 155260561, 'par2')]),
        'Y': IntervalTree([Interval(10001, 2649521, 'par1'),
                           Interval(59034050, 59363567, 'par2')])
    },
    '38': {
        'X': IntervalTree([Interval(10001, 2781480, 'par1'),
                           Interval(155701383, 156030896, 'par2')]),
        'Y': IntervalTree([Interval(10001, 2781480, 'par1'),
                           Interval(56887903, 57217416, 'par2')])
    },
}

MANUAL_RANK_OPTIONS = {
    8: {
        'label': 'known pathogenic',
        'description': 'Previously known pathogenic in Clinvar Hgmd literature etc',
    },
    7: {
        'label': 'pathogenic',
        'description': ("Novel mutation but overlapping phenotype with known pathogenic, "
                        "no further experimental validation needed"),
    },
    6: {
        'label': 'novel validated pathogenic',
        'description': 'Novel mutation and validated experimentally',
    },
    5: {
        'label': 'pathogenic partial phenotype',
        'description': ("Pathogenic variant explains part of patients phenotype, but "
                        "not all symptoms"),
    },
    4: {
        'label': 'likely pathogenic',
        'description': 'Experimental validation required to prove causality',
    },
    3: {
        'label': 'possibly pathogenic',
        'description': 'Uncertain significance, but cannot disregard yet',
    },
    2: {
        'label': 'likely benign',
        'description': 'Uncertain significance, but can discard',
    },
    1: {
        'label': 'benign',
        'description': 'Does not cause phenotype',
    },
    0: {
        'label': 'other',
        'description': 'Phenotype not related to disease',
    },
}

ACMG_COMPLETE_MAP = OrderedDict(
    pathogenic=dict(code='pathogenic', short='P', label='Pathogenic', color='danger'),
    likely_pathogenic=dict(code='likely_pathogenic', short='LP', label='Likely Pathogenic',
                           color='warning'),
    uncertain_significance=dict(code='uncertain_significance', short='VUS',
                                label='Uncertain Significance', color='primary'),
    likely_benign=dict(code='likely_benign', short='LB', label='Likely Benign', color='info'),
    benign=dict(code='benign', short='B', label='Benign', color='success'),
)
ACMG_OPTIONS = ACMG_COMPLETE_MAP.values()
