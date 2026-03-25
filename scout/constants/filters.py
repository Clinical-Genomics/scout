# -*- coding: utf-8 -*-
from .so_terms import SEVERE_SO_TERMS

SIGNIFICANT_METHBAT_COMPARE = ["HypoMethylated", "HyperMethylated", "HypoASM", "HyperASM"]
SIGNIFICANT_METHBAT_SUMMARY = ["AlleleSpecificMethylation"]
SIGNIFICANT_METHBAT_CPG_LABEL = "imprint"

CLINICAL_FILTER_BASE = {
    "variant_type": "clinical",
    "region_annotations": ["exonic", "splicing"],
    "functional_annotations": SEVERE_SO_TERMS,
    "clinsig": [4, 5],
    "clinvar_trusted_revstat": True,
    "prioritise_clinvar": True,
}

CLINICAL_FILTER_BASE_SV = {
    "variant_type": "clinical",
    "region_annotations": ["exonic", "splicing"],
    "functional_annotations": SEVERE_SO_TERMS,
    "local_obs": 30,
    "clingen_ngi": 10,
    "swegen": 10,
}

CLINICAL_FILTER_BASE_CANCER = {
    "variant_type": "clinical",
    "region_annotations": ["exonic", "splicing"],
    "functional_annotations": SEVERE_SO_TERMS,
}

CLINICAL_FILTER_BASE_MEI = {
    "variant_type": "clinical",
    "region_annotations": ["exonic", "splicing"],
    "functional_annotations": SEVERE_SO_TERMS,
    "swegen_freq": "0.02",
}

CLINICAL_FILTER_BASE_OUTLIER = {
    "variant_type": "clinical",
    "delta_psi": 0.1,
    "padjust": 0.05,
    "p_adjust_gene": 0.1,
}

CLINICAL_FILTER_BASE_OUTLIER_METHYLATION = {
    "variant_type": "clinical",
    "svtype": "methylation",
    "methbat_significance": SIGNIFICANT_METHBAT_COMPARE
    + SIGNIFICANT_METHBAT_SUMMARY
    + [SIGNIFICANT_METHBAT_CPG_LABEL],
    "category_pop_freq": 0.02,
}
