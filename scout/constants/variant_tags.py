VARIANT_REPORT_VARIANT_FEATURES = [
    "_id",
    "variant_id",
    "display_name",
    "sanger_ordered",
    "validation",
    "phenotypes",
    "chromosome",
    "position",
    "end",
    "end_chrom",
    "cytoband_start",
    "cytoband_end",
    "reference",
    "alternative",
    "dbsnp_id",
    "panels",
    "samples",
    "frequency",
    "dbsnp_id",
    "thousandg_link",
    "thousand_genomes_frequency",
    "max_thousand_genomes_frequency",
    "max_exac_frequency",
    "exac_frequency",
    "gnomad_frequency" "variant_rank",
    "rank_score",
    "manual_rank",
    "cancer_tier",
    "cadd_score",
    "genetic_models",
    "acmg_classification",
    "genes",
    "comments",
    "category",
    "dismiss_variant",
    "variant_rank",
    "str_repid",
    "str_display_ru",
    "str_ru",
    "str_status",
]

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

# Formatting for different filters in the vcf file
VARIANT_FILTERS = {
    "pass": {"label": "PASS", "description": "Passed filtering", "label_class": "success"},
    "germline": {"label": "GERM", "description": "Germline variant", "label_class": "warning"},
    "germline_risk": {"label": "GERM", "description": "Germline risk", "label_class": "warning"},
    "fail_nvaf": {
        "label": "N",
        "description": "Too high VAF in normal sample",
        "label_class": "danger",
    },
    "fail_pvalue": {"label": "P", "description": "Too low P-value", "label_class": "danger"},
    "fail_homopolymer_indel": {
        "label": "HP",
        "Variant in homopolymer region": "Passed filtering",
        "label_class": "danger",
    },
    "fail_longdel": {
        "label": "LD",
        "description": "Long DEL from vardict",
        "label_class": "danger",
    },
    "fail_no_tvar": {"label": "NO", "description": "No tumor variant", "label_class": "danger"},
    "fail_pon_freebayes": {
        "label": "PON",
        "description": "Variant in panel of normals",
        "label_class": "danger",
    },
    "fail_pon_tnscope": {
        "label": "PON",
        "description": "Variant in panel of normals",
        "label_class": "danger",
    },
    "fail_pon_vardict": {
        "label": "PON",
        "description": "Variant in panel of normals",
        "label_class": "danger",
    },
    "fail_strandbias": {"label": "SB", "description": "Strand bias", "label_class": "danger"},
    "warn_homopolymer_indel": {
        "label": "HP",
        "Variant in homopolymer region": "Passed filtering",
        "label_class": "warning",
    },
    "warn_low_tcov": {
        "label": "COV",
        "description": "Low tumor coverage",
        "label_class": "warning",
    },
    "warn_novar": {"label": "NO", "description": "No tumor variant", "label_class": "warning"},
    "warn_pon_freebayes": {
        "label": "PON",
        "description": "Passed filtering",
        "label_class": "warning",
    },
    "warn_pon_tnscope": {
        "label": "PON",
        "description": "Passed filtering",
        "label_class": "warning",
    },
    "warn_pon_vardict": {
        "label": "PON",
        "description": "Passed filtering",
        "label_class": "warning",
    },
    "warn_strandbias": {"label": "SB", "description": "Strand bias", "label_class": "warning"},
    "warn_low_tvaf": {"label": "LO", "description": "Low tumor VAF", "label_class": "warning"},
    "warn_verylow_tvaf": {
        "label": "XLO",
        "description": "Very low tumor WAF",
        "label_class": "warning",
    },
}

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
