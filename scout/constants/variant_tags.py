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

SPLICEAI_LIMITS = {
    "high recall": 0.2,
    "recommended": 0.5,
    "high precision": 0.8,
}

SPIDEX_LEVELS = ("not_reported", "low", "medium", "high")

EVALUATION_TERM_CATEGORIES = ("dismissal_term", "manual_rank", "cancer_tier", "mosaicism_option")
