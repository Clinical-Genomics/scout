CONSEQUENCE = (
    "deleterious",
    "deleterious_low_confidence",
    "probably_damaging",
    "possibly_damaging",
    "tolerated",
    "tolerated_low_confidence",
    "benign",
    "unknown",
)

CONSERVATION = {
    "gerp": {"conserved_min": 2, "conserved_max": 10},
    "phast": {"conserved_min": 0.8, "conserved_max": 100},
    "phylop": {"conserved_min": 2.5, "conserved_max": 100},
}

FEATURE_TYPES = (
    "exonic",
    "splicing",
    "ncRNA_exonic",
    "intronic",
    "ncRNA",
    "upstream",
    "5UTR",
    "3UTR",
    "downstream",
    "TFBS",
    "regulatory_region",
    "genomic_feature",
    "intergenic_variant",
)

# constants relating to evaluation terms
EVALUATION_TERM_CATEGORIES = ("dismissal_term", "manual_rank")

SV_TYPES = ("ins", "del", "dup", "cnv", "inv", "bnd")

GENETIC_MODELS = (
    ("AR_hom", "Autosomal Recessive Homozygote"),
    ("AR_hom_dn", "Autosomal Recessive Homozygote De Novo"),
    ("AR_comp", "Autosomal Recessive Compound"),
    ("AR_comp_dn", "Autosomal Recessive Compound De Novo"),
    ("AD", "Autosomal Dominant"),
    ("AD_dn", "Autosomal Dominant De Novo"),
    ("XR", "X Linked Recessive"),
    ("XR_dn", "X Linked Recessive De Novo"),
    ("XD", "X Linked Dominant"),
    ("XD_dn", "X Linked Dominant De Novo"),
)


VARIANT_CALL = ("Pass", "Filtered", "Not Found", "Not Used")

# Describe conversion between numerical SPIDEX values and human readable.
# Abs is not tractable in mongo query.
SPIDEX_HUMAN = {
    "low": {"neg": [-1, 0], "pos": [0, 1]},
    "medium": {"neg": [-2, -1], "pos": [1, 2]},
    "high": {"neg": [-2, -float("inf")], "pos": [2, float("inf")]},
}

SPIDEX_LEVELS = ("not_reported", "low", "medium", "high")

CANCER_TIER_OPTIONS = {
    "1A": {
        "label": "Tier IA",
        "description": "Strong Clinical Significance. Biomarkers in FDA or guidlines that "
        "predict response, resistance to therapy, diagnosis or prognosis "
        "to specific tumor type.",
        "label_class": "danger",
    },
    "1B": {
        "label": "Tier IB",
        "description": "Potential Clinical Significance Biomarkers in well-powered, concenus "
        "affirmed studies that predict response, resistance to therapy, "
        "diagnostic or prognostic significance to specific tumor type.",
        "label_class": "danger",
    },
    "2C": {
        "label": "Tier IIC",
        "description": "Biomarkers in FDA or guidlines that "
        "predict response, resistance to therapy,"
        "to a different tumor type; are diagnostic or prognostic for "
        "multiple small studies; or serve as study inclusion criteria.",
        "label_class": "warning",
    },
    "2D": {
        "label": "Tier IID",
        "description": "Biomarkers that show plausible therapeutic significance based on "
        "preclinical studies, may assist diagnosis or prognosis based on "
        "small reports.",
        "label_class": "warning",
    },
    "3": {
        "label": "Tier III",
        "description": "Variant of Unknown Clinical Significance-"
        "Not observed in the population, nor in tumor databases."
        "No convincing published evidence of cancer association.",
        "label_class": "primary",
    },
    "4": {
        "label": "Tier IV",
        "description": "Observed at high frequency in the population. No published evidence.",
        "label_class": "default",
    },
}

MOSAICISM_OPTIONS = {
    1: {
        "label": "Suspected in parent",
        "description": "Variant is suspected to be mosaic in a parent sample.",
        "evidence": ["allele_count"],
    },
    2: {
        "label": "Suspected in affected",
        "description": "Variant is suspected to be mosaic in a affected sample.",
        "evidence": ["allele_count"],
    },
    3: {
        "label": "Confirmed in parent",
        "description": "Variant is confirmed to be mosaic in a parent sample.",
        "evidence": ["allele_count"],
    },
    4: {
        "label": "Confirmed in affected",
        "description": "Variant is confirmed to be mosaic in a affected sample.",
        "evidence": ["allele_count"],
    },
    5: {
        "label": "Not evident in parental reads",
        "description": "Variant was inspected for mosaicism, but not seen in reads from parental samples.",
        "evidence": ["allele_count"],
    },
}
