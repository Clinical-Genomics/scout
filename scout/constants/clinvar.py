ASSERTION_METHOD = "ACMG Guidelines, 2015"
ASSERTION_METHOD_CIT = "PMID:25741868"

# Header used to create the Variant .CSV file for the manual ClinVar submission
VARIANT_FIELDS = {
    "local_id": {"csv_header": "##Local ID", "required": True, "type": str},
    "linking_id": {"csv_header": "Linking ID", "required": True, "type": str},
    "gene_symbols": {"csv_header": "Gene symbol", "required": False, "type": str},
    "ref_seq": {"csv_header": "Reference sequence", "required": False, "type": str},
    "hgvs": {"csv_header": "HGVS", "required": False, "type": str},
    "chromosome": {
        "csv_header": "Chromosome",
        "required": False,
        "type": str,
    },
    "start": {"csv_header": "Start", "required": False, "type": int},
    "stop": {"csv_header": "Stop", "required": False, "type": int},
    "ref": {"csv_header": "Reference allele", "required": False, "type": str},
    "alt": {"csv_header": "Alternate allele", "required": False, "type": str},
    "var_type": {"csv_header": "Variant type", "required": False, "type": str},
    "copy_number": {"csv_header": "Copy number", "required": False, "type": int},
    "ref_copy_number": {"csv_header": "Reference copy number", "required": False, "type": int},
    "bp_1": {"csv_header": "Breakpoint 1", "required": False, "type": int},
    "bp_2": {"csv_header": "Breakpoint 2", "required": False, "type": int},
    "outer_start": {"csv_header": "Outer start", "required": False, "type": int},
    "inner_start": {"csv_header": "Inner start", "required": False, "type": int},
    "inner_stop": {"csv_header": "Inner stop", "required": False, "type": int},
    "outer_stop": {"csv_header": "Outer stop", "required": False, "type": int},
    "dbsnp_id": {"csv_header": "Variation identifiers", "required": False, "type": str},
    "condition_id_type": {
        "csv_header": "Condition ID type",
        "required": True,
        "type": str,
    },
    "condition_id_value": {
        "csv_header": "Condition ID value",
        "required": True,
        "type": str,
    },
    "variant_condition_comment": {
        "csv_header": "Condition comment",
        "required": False,
        "type": str,
    },
    "clinsig": {"csv_header": "Clinical significance", "required": True, "type": str},
    "clinsig_comment": {
        "csv_header": "Comment on clinical significance",
        "required": False,
        "type": str,
    },
    "clinsig_cit": {
        "csv_header": "Clinical significance citations",
        "required": False,
        "type": str,
    },
    "last_evaluated": {"csv_header": "Date last evaluated", "required": False, "type": str},
    "variant_comment": {"csv_header": "Comment on variant", "required": False, "type": str},
    "assertion_method": {"csv_header": "Assertion method", "required": True, "type": str},
    "assertion_method_cit": {
        "csv_header": "Assertion method citation",
        "required": True,
        "type": str,
    },
    "inheritance_mode": {
        "csv_header": "Mode of inheritance",
        "required": False,
        "type": str,
    },
    "drug_response": {
        "csv_header": "Drug response condition",
        "required": False,  # required if clinsig == 'drug response'
        "type": str,
    },
    "funct_conseq": {"csv_header": "Functional consequence", "required": False, "type": str},
    "funct_conseq_comment": {
        "csv_header": "Comment on functional consequence",
        "required": False,
        "type": str,
    },
}

# Header used to create the CaseData .CSV file for the manual ClinVar submission
CASEDATA_HEADER = {
    "linking_id": "Linking ID",
    "individual_id": "Individual ID",
    "collection_method": "Collection method",  # default = 'clinical testing'
    "allele_origin": "Allele origin",
    "is_affected": "Affected status",
    "sv_analysis_method": "Structural variant method/analysis type",
    "clin_features": "Clinical features",
    "tissue": "Tissue",
    "sex": "Sex",
    "age": "Age",
    "ethnicity": "Population Group/Ethnicity",
    "fam_history": "Family history",
    "is_proband": "Proband",
    "is_secondary_finding": "Secondary finding",
    "is_mosaic": "Mosaicism",
    "zygosity": "Zygosity",
    "co_occurr_gene": "Co-occurrences, same gene",
    "co_occurr_other": "Co-occurrence, other genes",
    "platform_type": "Platform type",
    "platform_name": "Platform name",
    "method": "Method",
    "method_purpose": "Method purpose",
    "method_cit": "Method citations",
    "testing_lab": "Testing laboratory",
    "reported_at": "Date variant was reported to submitter",
}

####################################################################
# The following items are defined in the ClinVar API specifications:
# https://www.ncbi.nlm.nih.gov/clinvar/docs/api_http/
####################################################################
CLNSIG_TERMS = {
    "Pathogenic",
    "Likely pathogenic",
    "Uncertain significance",
    "Likely benign",
    "Benign",
    "Pathogenic, low penetrance",
    "Uncertain risk allele",
    "Likely pathogenic, low penetrance",
    "Established risk allele",
    "Likely risk allele",
    "affects",
    "association",
    "drug response",
    "confers sensitivity",
    "protective",
    "other",
    "not provided",
}

REVSTAT_TERMS = {
    "conflicting_interpretations",
    "multiple_submitters",
    "no_conflicts",
    "single_submitter",
    "criteria_provided",
    "no_assertion_criteria_provided",
    "no_assertion_provided",
    "practice_guideline",
    "reviewed_by_expert_panel",
}

CLINVAR_INHERITANCE_MODELS = [
    "Autosomal dominant inheritance",
    "Autosomal recessive inheritance",
    "Mitochondrial inheritance",
    "Somatic mutation",
    "Genetic anticipation",
    "Sporadic",
    "Sex-limited autosomal dominant",
    "X-linked recessive inheritance",
    "X-linked dominant inheritance",
    "Y-linked inheritance",
    "Other",
    "X-linked inheritance",
    "Codominant",
    "Semidominant inheritance",
    "Autosomal unknown",
    "Autosomal dominant inheritance with maternal imprinting",
    "Autosomal dominant inheritance with paternal imprinting",
    "Multifactorial inheritance",
    "Unknown mechanism",
    "Oligogenic inheritance",
]

SV_TYPES = [
    "Insertion",
    "Deletion",
    "Duplication",
    "Tandem duplication",
    "copy number loss",
    "copy number gain",
    "Inversion",
    "Translocation",
    "Complex",
]

AFFECTED_STATUS = ["yes", "no", "unknown", "not provided", "not applicable"]

ALLELE_OF_ORIGIN = [
    "germline",
    "somatic",
    "de novo",
    "unknown",
    "inherited",
    "maternal",
    "paternal",
    "biparental",
    "not applicable",
]

COLLECTION_METHOD = [
    "curation",
    "literature only",
    "reference population",
    "provider interpretation",
    "phenotyping only",
    "case-control",
    "clinical testing",
    "in vitro",
    "in vivo",
    "research",
    "not provided",
]
