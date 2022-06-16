ANALYSIS_TYPES = ("wgs", "wes", "mixed", "unknown", "panel", "panel-umi", "external")

CUSTOM_CASE_REPORTS = [
    "multiqc",
    "cnv_report",
    "coverage_qc_report",
    "gene_fusion_report",
    "gene_fusion_report_research",
]

CASE_REPORT_CASE_FEATURES = [
    "display_name",
    "created_at",
    "updated_at",
    "status",
    "madeline_info",
    "synopsis",
    "phenotype_terms",
    "diagnosis_phenotypes",
    "panels",
]

CASE_REPORT_CASE_IND_FEATURES = [
    "display_name",
    "sex",
    "confirmed_sex",
    "phenotype",
    "phenotype_human",
    "analysis_type",
    "predicted_ancestry",
    "confirmed_parent",
]

CASE_REPORT_VARIANT_TYPES = {
    "causatives_detailed": "causatives",
    "partial_causatives_detailed": "partial_causatives",
    "suspects_detailed": "suspects",
    "classified_detailed": "acmg_classification",
    "tagged_detailed": "manual_rank",
    "tier_detailed": "cancer_tier",
    "dismissed_detailed": "dismiss_variant",
    "commented_detailed": "is_commented",
}

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
    "mark_causative": "marked causative for",
    "update_diagnosis": "updated diagnosis for",
    "rerun": "requested rerun of",
    "status": "updated the status for",
    "comment": "commented on",
    "comment_update": "updated a comment for",
    "pin": "pinned variant",
    "assign": "was assigned to",
    "unassign": "was unassigned from",
    "synopsis": "updated synopsis for",
    "unpin": "removed pinned variant",
    "sanger": "ordered sanger sequencing for",
    "cancel_sanger": "cancelled sanger order for",
    "archive": "archived",
    "open_research": "opened research mode for",
    "reset_research": "canceled research mode request for",
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
    "rerun_monitor": "requested rerun monitoring for",
    "rerun_unmonitor": "disabled rerun monitoring for",
    "validate": "marked validation status for",
    "add_cohort": "updated cohort for",
    "remove_cohort": "removed cohort for",
    "acmg": "updated ACMG classification for",
    "dismiss_variant": "dismissed variant for",
    "reset_dismiss_variant": "reset dismissed variant status for",
    "reset_dismiss_all_variants": "reset all dismissed variants for",
    "mosaic_tags": "updated mosaic tags for",
    "update_default_panels": "updated default panels for",
    "update_clinical_filter_hpo": "updated clinical filter HPO status for",
    "mme_add": "exported to Matchmaker patient",
    "mme_remove": "removed from Matchmaker patient",
    "filter_stash": "stored a filter for",
    "filter_audit": "marked case audited with filter",
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
    "case": {"label": "Case or Individual Name", "prefix": "case:", "placeholder": "example:18201"},
    "exact_pheno": {
        "label": "HPO Terms",
        "prefix": "exact_pheno:",
        "placeholder": "example:HP:0001166,HP:0001250,...",
    },
    "exact_dia": {
        "label": "OMIM Terms",
        "prefix": "exact_dia:",
        "placeholder": "example:OMIM:616538,OMIM:607681,...",
    },
    "synopsis": {
        "label": "Search Synopsis",
        "prefix": "synopsis:",
        "placeholder": "example:epilepsy",
    },
    "panel": {"label": "Gene Panel", "prefix": "panel:", "placeholder": "example:NMD"},
    "status": {"label": "Case Status", "prefix": "status:", "placeholder": "example:active"},
    "track": {"label": "Analysis Track", "prefix": "track:", "placeholder": "rare or cancer"},
    "pheno_group": {
        "label": "Phenotype Group",
        "prefix": "pheno_group:",
        "placeholder": "example:HP:0001166",
    },
    "cohort": {"label": "Patient Cohort", "prefix": "cohort:", "placeholder": "example:pedhep"},
    "similar_case": {
        "label": "Similar Case",
        "prefix": "similar_case:",
        "placeholder": "example:18201",
    },
    "similar_pheno": {
        "label": "Similar Phenotype",
        "prefix": "similar_pheno:",
        "placeholder": "example:HP:0001166,HP:0001250,..",
    },
    "pinned": {"label": "Pinned Gene", "prefix": "pinned:", "placeholder": "example:POT1"},
    "causative": {"label": "Causative Gene", "prefix": "causative:", "placeholder": "example:POT1"},
    "user": {
        "label": "Assigned User",
        "prefix": "user:",
        "placeholder": "example:John Doe",
    },
}


EVENTS_MAP = {
    "mark_causative": f"Marked nof event_type causative",
    "update_diagnosis": f"Updated nof event_type diagnosis",
    "rerun": f"Requested rerun nof event_type",
    "status": f"Updated the status of nof event_type",
    "comment": f"Commented on nof event_type",
    "comment_update": f"Updated comment on nof event_type",
    "pin": f"Pinned nof event_type",
    "assign": f"Assigned nof event_type",
    "unassign": f"Unassigned nof event_type",
    "synopsis": f"Updated synopsis on nof event_type",
    "unpin": f"Removed pinned nof event_type",
    "sanger": f"Ordered Sanger sequencing ",
    "cancel_sanger": f"Cancelled Sanger order",
    "archive": f"Archived nof event_type",
    "open_research": f"Opened research mode",
    "reset_research": f"Canceled research mode",
    "unmark_causative": f"Unmarked nof event_type causative",
    "mark_partial_causative": f"Marked nof event_type partial causative",
    "unmark_partial_causative": f"Unmarked nof event_type partial causative",
    "manual_rank": f"Updated nof event_type manual rank",
    "cancer_tier": f"Updated nof event_type cancer tier",
    "add_phenotype": f"Added nof event_type HPO term",
    "remove_phenotype": f"Removed nof event_type HPO term",
    "remove_variants": f"Removed nof event_type",
    "add_case": f"Added nof event_type",
    "update_case": f"Updated nof event_type",
    "update_individual": f"Updated nof individuals",
    "check_case": f"Marked nof event_type",
    "share": f"Shared case",
    "unshare": f"Revoked access",
    "rerun_monitor": f"Requested rerun monitoring",
    "rerun_unmonitor": f"Disabled rerun monitoring",
    "validate": f"Marked validation status",
    "add_cohort": f"Updated cohort",
    "remove_cohort": f"Removed cohort",
    "acmg": f"Updated nof event_type ACMG classification",
    "dismiss_variant": f"Dismissed nof event_type",
    "reset_dismiss_variant": f"Reset dismissed nof event_type",
    "reset_dismiss_all_variants": f"Reset all dismissed variants",
    "mosaic_tags": f"Updated mosaic tags",
    "update_default_panels": f"Updated nof default panels",
    "update_clinical_filter_hpo": f"Updated clinical filter HPO status",
    "mme_add": f"Exported to Matchmaker",
    "mme_remove": f"Removed nof from Matchmaker",
    "filter_stash": f"Stored filter",
    "filter_audit": f"Marked case audited with filter",
    "update_sample": f"Updated sample data",
    "update_case_group_ids": f"Updated case group IDs",
}
