# clinvar Variant sheet
CLINVAR_HEADER = {
    "local_id": "##Local ID",
    "linking_id": "Linking ID",
    "gene_symbol": "Gene symbol",
    "ref_seq": "Reference sequence",
    "hgvs": "HGVS",
    "chromosome": "Chromosome",
    "start": "Start",
    "stop": "Stop",
    "ref": "Reference allele",
    "alt": "Alternate allele",
    "var_type": "Variant type",
    "ncopy": "Copy number",
    "ref_copy": "Reference copy number",
    "outer_start": "Outer start",
    "inner_start": "Inner start",
    "inner_stop": "Inner stop",
    "outer_stop": "Outer stop",
    "variations_ids": "Variation identifiers",
    "condition_id_type": "Condition ID type",  # default = 'HPO'
    "condition_id_value": "Condition ID value",
    "condition_comment": "Condition comment",
    "clinsig": "Clinical significance",
    "clinsig_comment": "Comment on clinical significance",
    "last_evaluated": "Date last evaluated",
    "variant_comment": "Comment on variant",
    "assertion_method": "Assertion method",
    "assertion_method_cit": "Assertion method citation",
    "inheritance_mode": "Mode of inheritance",
    "clinsig_cit": "Clinical significance citations",
    "clinsig_comment": "Comment on clinical significance",
}

# clinvar CaseData sheet
CASEDATA_HEADER = {
    "linking_id": "Linking ID",
    "individual_id": "Individual ID",
    "collection_method": "Collection method",  # default = 'clinical testing'
    "allele_origin": "Allele origin",
    "is_affected": "Affected status",
}
# silence fields in ClinVar CSV output if other fields exist to avoid validation error - the latter are preferred
CLINVAR_SILENCE_IF_EXISTS = {"chromosome": "hgvs", "start": "hgvs", "stop": "hgvs"}

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

# Models of inheritance are defined here:
# https://ftp.ncbi.nlm.nih.gov/pub/GTR/standard_terms/Mode_of_inheritance.txt
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

ASSERTION_METHOD = "ACMG Guidelines, 2015"
ASSERTION_METHOD_CIT = "PMID:25741868"
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
