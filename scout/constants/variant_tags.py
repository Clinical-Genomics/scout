from collections import OrderedDict

from .gene_tags import INHERITANCE_PALETTE

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

# Associates an inheritance model with a color, using the same colors categories as scout.constants.gene_tags.INHERITANCE_PALETTE
# The colors of this palette are the same as the MatPlotLib Tableau palette (https://matplotlib.org/3.4.1/gallery/color/named_colors.html)
GENETIC_MODELS_PALETTE = {
    "AR_hom_dn": INHERITANCE_PALETTE["AR"],
    "AR_comp_dn": {"bgcolor": "bg-red", "text_color": "text-white"},
    "AR_hom": {"bgcolor": "bg-orange", "text_color": "text-white"},
    "AR_comp": {"bgcolor": "bg-yellow", "text_color": "text-dark"},
    "AD_dn": INHERITANCE_PALETTE["AD"],
    "AD": {"bgcolor": "bg-cyan", "text_color": "text-dark"},
    "XR_dn": INHERITANCE_PALETTE["XR"],
    "XR": {"bgcolor": "bg-teal", "text_color": "text-white"},
    "XD_dn": INHERITANCE_PALETTE["XD"],
    "XD": {"bgcolor": "bg-gray-400", "text_color": "text-dark"},
}

# Used for filtering variants in blueprints.variants
VARIANT_GENOTYPES = (
    ("", ""),
    ("0/1 or 1/0", "Heterozygous (0/1 or 1/0)"),
    ("1/1", "Homozygous (1/1)"),
    ("0/0", "Homozygous ref (0/0)"),
    ("./.", "Both alleles missing (./.)"),
    ("other", "Other"),
)

VARIANT_CALL = ("Pass", "Filtered", "Not Found", "Not Used")

# Formatting for different filters in the vcf file
VARIANT_FILTERS = {
    "pass": {
        "label": "PASS",
        "description": "Passed filtering",
        "label_class": "success",
    },
    "germline": {
        "label": "GERM",
        "description": "Germline variant",
        "label_class": "warning",
    },
    "germline_risk": {
        "label": "GERM",
        "description": "Germline risk",
        "label_class": "warning",
    },
    "fail_nvaf": {
        "label": "N",
        "description": "Too high VAF in normal sample",
        "label_class": "danger",
    },
    "fail_pvalue": {
        "label": "P",
        "description": "Too low P-value",
        "label_class": "danger",
    },
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
    "fail_no_tvar": {
        "label": "NO",
        "description": "No tumor variant",
        "label_class": "danger",
    },
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
    "fail_strandbias": {
        "label": "SB",
        "description": "Strand bias",
        "label_class": "danger",
    },
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
    "warn_novar": {
        "label": "NO",
        "description": "No tumor variant",
        "label_class": "warning",
    },
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
    "warn_strandbias": {
        "label": "SB",
        "description": "Strand bias",
        "label_class": "warning",
    },
    "warn_low_tvaf": {
        "label": "LO",
        "description": "Low tumor VAF",
        "label_class": "warning",
    },
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
    "high": {"neg": [-float("inf"), -2], "pos": [2, float("inf")]},
}

SPLICEAI_LIMITS = {
    "high recall": 0.2,
    "recommended": 0.5,
    "high precision": 0.8,
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

MANUAL_RANK_OPTIONS = OrderedDict(
    [
        (
            8,
            {
                "label": "KP",
                "name": "Known pathogenic",
                "description": "Known pathogenic, previously known pathogenic in ClinVar, HGMD, literature, etc",
                "label_class": "danger",
            },
        ),
        (
            7,
            {
                "label": "P",
                "name": "Pathogenic",
                "description": (
                    "Pathogenic, novel mutation but overlapping phenotype with known pathogenic, "
                    "no further experimental validation needed"
                ),
                "label_class": "danger",
            },
        ),
        (
            6,
            {
                "label": "NVP",
                "name": "Novel validated pathogenic",
                "description": "Novel validated pathogenic, novel mutation and validated experimentally",
                "label_class": "danger",
            },
        ),
        (
            5,
            {
                "label": "PPP",
                "name": "Pathogenic partial phenotype",
                "description": (
                    "Pathogenic partial phenotype, pathogenic variant explains part of patients phenotype, but "
                    "not all symptoms"
                ),
                "label_class": "danger",
            },
        ),
        (
            4,
            {
                "label": "LP",
                "name": "Likely pathogenic",
                "description": "Likely pathogenic, experimental validation required to prove causality",
                "label_class": "warning",
            },
        ),
        (
            3,
            {
                "label": "PP",
                "name": "Possibly pathogenic",
                "description": "Possibly pathogenic, uncertain significance, but cannot disregard yet",
                "label_class": "primary",
            },
        ),
        (
            2,
            {
                "label": "LB",
                "name": "Likely benign",
                "description": "Likely benign, uncertain significance, but can discard",
                "label_class": "info",
            },
        ),
        (
            1,
            {
                "label": "B",
                "name": "Benign",
                "description": "Benign, does not cause phenotype",
                "label_class": "success",
            },
        ),
        (
            9,
            {
                "label": "VUS",
                "name": "Unknown Significance",
                "description": "Variant of unknown significance",
                "label_class": "default",
            },
        ),
        (
            13,
            {
                "label": "PLP",
                "name": "Pathogenic Low Penetrance",
                "description": "Pathogenic allele with low or reduced penetrance - robust evidence for an intermediate risk increase",
                "label_class": "warning",
            },
        ),
        (
            14,
            {
                "label": "LPLP",
                "name": "Likely Pathogenic Low Penetrance",
                "description": "Likely pathogenic allele with low or reduced penetrance - some evidence for an intermediate risk increase",
                "label_class": "warning",
            },
        ),
        (
            10,
            {
                "label": "RF",
                "name": "Risk Factor",
                "description": "Established risk allele - strong evidence for a small risk increase",
                "label_class": "default",
            },
        ),
        (
            11,
            {
                "label": "LRF",
                "name": "Likely Risk Factor",
                "description": "Likely risk allele - some evidence for a small risk increase",
                "label_class": "default",
            },
        ),
        (
            12,
            {
                "label": "URF",
                "name": "Uncertain Risk Factor",
                "description": "Uncertain risk allele - uncertain evidence for a small risk increase",
                "label_class": "default",
            },
        ),
        (
            0,
            {
                "label": "O",
                "name": "Other",
                "description": "Other, phenotype not related to disease",
                "label_class": "default",
            },
        ),
    ]
)

DISMISS_VARIANT_OPTIONS = {
    2: {
        "label": "Common public",
        "description": "Too common in public databases.",
        "evidence": ["freq"],
    },
    3: {
        "label": "Common local",
        "description": "Too common in local databases.",
        "evidence": ["freq"],
    },
    5: {
        "label": "Irrelevant phenotype",
        "description": "Phenotype not relevant.",
        "evidence": ["OMIM"],
    },
    7: {
        "label": "Inconsistent inheritance pattern",
        "description": "Inheritance pattern not relevant.",
        "evidence": ["OMIM", "GT", "inheritance_model"],
    },
    11: {
        "label": "No plausible compound",
        "description": "No plausible compound - AR disease.",
        "evidence": ["Compounds"],
    },
    13: {
        "label": "Not in disease transcript",
        "description": "Not in transcript relevant to disease.",
        "evidence": ["transcript"],
    },
    17: {
        "label": "Not in RefSeq transcript",
        "description": "Not in a RefSeq transcript - could not be determined relevant.",
        "evidence": ["transcript"],
    },
    19: {
        "label": "Splicing unaffected",
        "description": "Does not appear to affect splicing.",
        "evidence": ["spidex"],
    },
    23: {
        "label": "Inherited from unaffected",
        "description": "Inherited from an unaffected individual.",
        "evidence": ["GT", "pedigree"],
    },
    29: {
        "label": "Technical issues",
        "description": "Technical issues - likely false positive.",
        "evidence": ["GT", "IGV"],
    },
    31: {
        "label": "No protein function",
        "description": "Not likely to alter protein function - eg benign polyQ expansion.",
        "evidence": ["CADD", "conservation"],
    },
    37: {
        "label": "Reputation benign",
        "description": "Reputable source classified benign.",
        "evidence": ["clinvar"],
    },
    41: {
        "label": "Common variation type",
        "description": "Found in a gene with much benign such (e.g. missense) variation.",
        "evidence": ["type"],
    },
    43: {
        "label": "Unstudied variation type",
        "description": "In a gene where mainly other types of variation (e.g. repeat expansion) are established as pathologic.",
        "evidence": ["type"],
    },
}

CANCER_SPECIFIC_VARIANT_DISMISS_OPTIONS = {
    44: {
        "label": "Possible Germline",
        "description": "Variant is possibly a germline event.",
        "evidence": [],
    },
    45: {
        "label": "Low count normal",
        "description": 'Variant has too few reads in normal sample "AD".',
        "evidence": [],
    },
    46: {
        "label": "Low count tumor",
        "description": 'Variant has too few reads in tumor sample. "AD".',
        "evidence": [],
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

VARIANTS_TARGET_FROM_CATEGORY = {
    "sv": "variants.sv_variants",
    "cancer": "variants.cancer_variants",
    "cancer_sv": "variants.cancer_sv_variants",
    "mei": "variants.mei_variants",
    "snv": "variants.variants",
    "str": "variants.str_variants",
    "fusion": "variants.fusion_variants",
}
