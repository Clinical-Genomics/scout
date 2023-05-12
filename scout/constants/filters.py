# -*- coding: utf-8 -*-
from .so_terms import SEVERE_SO_TERMS, SEVERE_SO_TERMS_SV

CLINICAL_FILTER_BASE = {
    "variant_type": "clinical",
    "region_annotations": ["exonic", "splicing"],
    "functional_annotations": SEVERE_SO_TERMS,
    "clinsig": [4, 5],
    "clinsig_confident_always_returned": True,
}

CLINICAL_FILTER_BASE_SV = {
    "variant_type": "clinical",
    "region_annotations": ["exonic", "splicing"],
    "functional_annotations": SEVERE_SO_TERMS_SV,
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
    "functional_annotations": SEVERE_SO_TERMS_SV,
    "swegen_freq": "0.02",
}
