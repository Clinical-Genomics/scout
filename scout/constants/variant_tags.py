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

# Describe conversion between numerical SPIDEX values and human readable.
# Abs is not tractable in mongo query.
SPIDEX_HUMAN = {
    'low': { 'neg': [-1,0], 'pos': [0, 1]},
    'medium': { 'neg': [-2,-1], 'pos': [1,2]},
    'high': { 'neg': [-2,-float('inf')], 'pos': [2,float('inf')]}
}

SPIDEX_LEVELS = (
    'not_reported',
    'low',
    'medium',
    'high'
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

DISMISS_VARIANT_OPTIONS = {
    2: {
        'label': 'Common public',
        'description': 'Too common in public databases.',
        'evidence': ['freq']
        },
    3: {
        'label': 'Common local',
        'description': 'Too common in local databases.',
        'evidence': ['freq']
        },
    5: {
        'label': 'Irrelevant phenotype',
        'description': 'Phenotype not relevant.',
        'evidence': ['OMIM']
        },
    7: {
        'label': 'Inconsistent inheritance pattern',
        'description': 'Inheritance pattern not relevant.',
        'evidence': ['OMIM', 'GT', 'inheritance_model']
        },
    11: {
        'label': 'No plausible compound',
        'description': 'No plausible compound - AR disease.',
        'evidence': ['Compounds']
        },
    13: {
        'label': 'Not in disease transcript',
        'description': 'Not in transcript relevant to disease.',
        'evidence': ['transcript']
        },
    17: {
        'label': 'Not in RefSeq transcript',
        'description':
            'Not in a RefSeq transcript - could not be determined relevant.',
        'evidence': ['transcript']
        },
    19: {
        'label': 'Splicing unaffected',
        'description': 'Does not appear to affect splicing.',
        'evidence': ['spidex']
        },
    23: {
        'label': 'Inherited from unaffected',
        'description': 'Inherited from an unaffected individual.',
        'evidence': ['GT', 'pedigree']
        },
    29: {
        'label': 'Technical issues',
        'description': 'Technical issues - likely false positive.',
        'evidence': ['GT', 'pileup']
        },
    31: {
        'label': 'No protein function',
        'description': 
        'Not likely to alter protein function - eg benign polyQ expansion.',
        'evidence': ['CADD', 'conservation']
        },
    37: {
        'label': 'Reputation benign',
        'description': 'Reputable source classified benign.',
        'evidence': ['clinvar']
        },
    41: {
        'label': 'Common variation type',
        'description': 
        'Found in a gene with much benign such (e.g. missense) variation.',
        'evidence': ['type']
        },
    43: {
        'label': 'Unstudied variation type',
        'description': 
        'In a gene where mainly other types of variation (e.g. repeat expansion) are established as pathologic.',
        'evidence': ['type']
        }
}

MOSAICISM_OPTIONS = {
    1: {
        'label': 'Suspected in parent',
        'description': 'Variant is suspected to be mosaic in a parent sample.',
        'evidence': ['allele_count']
        },
    2: {
        'label': 'Suspected in affected',
        'description': 'Variant is suspected to be mosaic in a affected sample.',
        'evidence': ['allele_count']
        },
    3: {
        'label': 'Confirmed in parent',
        'description': 'Variant is confirmed to be mosaic in a parent sample.',
        'evidence': ['allele_count']
        },
    4: {
        'label': 'Confirmed in affected',
        'description': 'Variant is confirmed to be mosaic in a affected sample.',
        'evidence': ['allele_count']
        },
}
