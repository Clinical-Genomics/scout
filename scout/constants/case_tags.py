ANALYSIS_TYPES = ('wgs', 'wes', 'mixed', 'unknown')

SEX_MAP = {1: 'male', 2: 'female', 'other': 'unknown', 0: 'unknown', 
          '1': 'male', '2': 'female', '0': 'unknown'}
REV_SEX_MAP = {'male':'1', 'female': '2', 'unknown': '0'}

PHENOTYPE_MAP = {1: 'unaffected', 2: 'affected', 0: 'unknown', -9: 'unknown'}
REV_PHENOTYPE_MAP = {value: key for key, value in PHENOTYPE_MAP.items()}


CASE_STATUSES = ("prioritized", "inactive", "active", "solved", "archived")

VERBS_MAP = {
    "assign": "was assigned to",
    "unassign": "was unassigned from",
    "status": "updated the status for",
    "comment": "commented on",
    "synopsis": "updated synopsis for",
    "pin": "pinned variant",
    "unpin": "removed pinned variant",
    "sanger": "ordered sanger sequencing for",
    "cancel_sanger": "cancelled sanger order for",
    "archive": "archived",
    "open_research": "opened research mode for",
    "mark_causative": "marked causative for",
    "unmark_causative": "unmarked causative for",
    "manual_rank": "updated manual rank for",
    "add_phenotype": "added HPO term for",
    "remove_phenotype": "removed HPO term for",
    "add_case": "added case",
    "update_case": "updated case",
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
}

VERBS = list(VERBS_MAP.keys())
