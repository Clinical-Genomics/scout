# -*- coding: utf-8 -*-
from .so_terms import SEVERE_SO_TERMS

CLINICAL_FILTER = {
    "variant_type": "clinical",
    "region_annotations": ["exonic", "splicing"],
    "functional_annotations": SEVERE_SO_TERMS,
    "clinsig": [4, 5],
    "clinsig_confident_always_returned": True,
}

CLINICAL_FILTER_SV = {
    "variant_type": "clinical",
    "region_annotations": ["exonic", "splicing"],
    "functional_annotations": SEVERE_SO_TERMS,
    "clingen_ngi": 10,
    "swegen": 10,
}

CLINICAL_FILTER_CANCER = {
    "variant_type": "clinical",
    "region_annotations": ["exonic", "splicing"],
    "functional_annotations": SEVERE_SO_TERMS,
}
