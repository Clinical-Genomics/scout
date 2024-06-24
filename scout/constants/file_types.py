# Collect general information about the file types used in Scout
# Load priority determines load order, with lowest value loaded first.

FILE_TYPE_MAP = {
    "vcf_cancer": {
        "category": "cancer",
        "variant_type": "clinical",
        "load_priority": 10,
    },
    "vcf_cancer_research": {
        "category": "cancer",
        "variant_type": "research",
        "load_priority": 110,
    },
    "vcf_cancer_sv": {
        "category": "cancer_sv",
        "variant_type": "clinical",
        "load_priority": 20,
    },
    "vcf_cancer_sv_research": {
        "category": "cancer_sv",
        "variant_type": "research",
        "load_priority": 120,
    },
    "vcf_fusion": {
        "category": "fusion",
        "variant_type": "clinical",
        "load_priority": 70,
    },
    "vcf_fusion_research": {
        "category": "fusion",
        "variant_type": "research",
        "load_priority": 170,
    },
    "vcf_mei": {
        "category": "mei",
        "variant_type": "clinical",
        "load_priority": 60,
    },
    "vcf_mei_research": {
        "category": "mei",
        "variant_type": "research",
        "load_priority": 160,
    },
    "vcf_snv": {
        "category": "snv",
        "variant_type": "clinical",
        "load_priority": 35,
    },
    "vcf_snv_mt": {
        "category": "snv",
        "variant_type": "clinical",
        "load_priority": 30,
    },
    "vcf_snv_research": {
        "category": "snv",
        "variant_type": "research",
        "load_priority": 135,
    },
    "vcf_snv_research_mt": {
        "category": "snv",
        "variant_type": "research",
        "load_priority": 130,
    },
    "vcf_sv": {
        "category": "sv",
        "variant_type": "clinical",
        "load_priority": 45,
    },
    "vcf_sv_mt": {
        "category": "sv",
        "variant_type": "clinical",
        "load_priority": 40,
    },
    "vcf_sv_research": {
        "category": "sv",
        "variant_type": "research",
        "load_priority": 145,
    },
    "vcf_sv_research_mt": {
        "category": "sv",
        "variant_type": "research",
        "load_priority": 140,
    },
    "vcf_str": {
        "category": "str",
        "variant_type": "clinical",
        "load_priority": 50,
    },
}

OMICS_FILE_TYPE_MAP = {
    "fraser": {
        "format": "tsv",
        "analysis_type": "wts",
        "category": "outlier",
        "sub_category": "splicing",
        "variant_type": "clinical",
    },
    "outrider": {
        "format": "tsv",
        "analysis_type": "wts",
        "category": "outlier",
        "sub_category": "expression",
        "variant_type": "clinical",
    },
    "fraser_research": {
        "format": "tsv",
        "analysis_type": "wts",
        "category": "outlier",
        "sub_category": "splicing",
        "variant_type": "research",
    },
    "outrider_research": {
        "format": "tsv",
        "analysis_type": "wts",
        "category": "outlier",
        "sub_category": "expression",
        "variant_type": "research",
    },
}
