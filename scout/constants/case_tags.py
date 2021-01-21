ANALYSIS_TYPES = ("wgs", "wes", "mixed", "unknown", "panel", "external")

SEX_MAP = {
    1: "male",
    2: "female",
    "other": "unknown",
    0: "unknown",
    "1": "male",
    "2": "female",
    "0": "unknown",
}
REV_SEX_MAP = {"male": "1", "female": "2", "unknown": "0"}

PHENOTYPE_MAP = {1: "unaffected", 2: "affected", 0: "unknown", -9: "unknown"}
CANCER_PHENOTYPE_MAP = {1: "normal", 2: "tumor", 0: "unknown", -9: "unknown"}
REV_PHENOTYPE_MAP = {value: key for key, value in PHENOTYPE_MAP.items()}

CASE_STATUSES = ("prioritized", "inactive", "active", "solved", "archived")

VERBS_MAP = {
    "assign": "was assigned to",
    "unassign": "was unassigned from",
    "status": "updated the status for",
    "comment": "commented on",
    "comment_update": "updated a comment for",
    "synopsis": "updated synopsis for",
    "pin": "pinned variant",
    "unpin": "removed pinned variant",
    "sanger": "ordered sanger sequencing for",
    "cancel_sanger": "cancelled sanger order for",
    "archive": "archived",
    "open_research": "opened research mode for",
    "mark_causative": "marked causative for",
    "unmark_causative": "unmarked causative for",
    "mark_partial_causative": "mark partial causative for",
    "unmark_partial_causative": "unmarked partial causative for",
    "manual_rank": "updated manual rank for",
    "cancer_tier": "updated cancer tier for",
    "add_phenotype": "added HPO term for",
    "remove_phenotype": "removed HPO term for",
    "remove_variants": "removed variants for",
    "add_case": "added case",
    "update_case": "updated case",
    "update_individual": "updated individuals for",
    "check_case": "marked case as",
    "share": "shared case with",
    "unshare": "revoked access for",
    "rerun": "requested rerun of",
    "validate": "marked validation status for",
    "update_diagnosis": "updated diagnosis for",
    "add_cohort": "updated cohort for",
    "remove_cohort": "removed cohort for",
    "acmg": "updated ACMG classification for",
    "dismiss_variant": "Dismissed variant for",
    "mosaic_tags": "Updated mosaic tags for",
    "update_default_panels": "updated default panels for",
    "update_clinical_filter_hpo": "updated clinical filter HPO status for",
    "mme_add": "Exported to MatchMaker patient",
    "mme_remove": "Removed from MatchMaker patient",
    "filter_stash": "stored a filter for",
    "update_sample": "updated sample data for",
    "update_case_group_ids": "updated case group ids for",
}

# Tissue types for rare disease samples and controls

SOURCES = [
    "blood",
    "bone marrow",
    "buccal swab",
    "cell line",
    "cell-free DNA",
    "cytology (FFPE)",
    "cytology (not fixed/fresh)",
    "muscle",
    "nail",
    "saliva",
    "skin",
    "tissue (FFPE)",
    "tissue (fresh frozen)",
    "CVB",
    "AC",
    "other fetal tissue",
    "other",
    "unknown",
]

SAMPLE_SOURCE = dict((i, el) for i, el in enumerate(SOURCES))

CASE_SEARCH_TERMS = {
    "case": {"label": "Case or individual name", "prefix": "case:"},
    "exact_pheno": {
        "label": "HPO term",
        "prefix": "exact_pheno:",
    },
    "synopsis": {
        "label": "Search synopsis",
        "prefix": "synopsis:",
    },
    "panel": {"label": "Gene panel", "prefix": "panel:"},
    "status": {"label": "Case status", "prefix": "status:"},
    "pheno_group": {
        "label": "Phenotype group",
        "prefix": "pheno_group:",
    },
    "cohort": {"label": "Patient cohort", "prefix": "cohort:"},
    "Similar case": {
        "label": "Similar case",
        "prefix": "similar_case:",
    },
    "similar_pheno": {
        "label": "Similar phenotype",
        "prefix": "similar_pheno:",
    },
    "pinned": {"label": "Pinned gene", "prefix": "pinned:"},
    "causative": {"label": "Causative gene", "prefix": "causative:"},
    "user": {"label": "Assigned user", "prefix": "user:"},
}
