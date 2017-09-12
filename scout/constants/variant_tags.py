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


VARIANT_CALL = (
    'Pass',
    'Filtered',
    'Not Found',
    'Not Used',
)

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
