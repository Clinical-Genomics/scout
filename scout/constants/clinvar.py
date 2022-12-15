CLINVAR_API_URL = "https://submit.ncbi.nlm.nih.gov/api/v1/submissions/"
PRECLINVAR_URL = "https://preclinvar.scilifelab.se"

ASSERTION_METHOD = "ACMG Guidelines, 2015"
ASSERTION_METHOD_CIT = "PMID:25741868"
NOT_PROVIDED = "not provided"

# Header used to create the Variant .CSV file for the manual ClinVar submission
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
    "breakpoint1": "Breakpoint 1",
    "breakpoint2": "Breakpoint 2",
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
    "inheritance_mode": "Mode of inheritance",
    "clinsig_cit": "Clinical significance citations",
    "clinsig_comment": "Comment on clinical significance",
    "drug_response": "Drug response condition",
    "funct_conseq": "Functional consequence",
    "funct_conseq_comment": "Comment on functional consequence",
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
CLNSIG_TERMS = [
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
    NOT_PROVIDED,
]

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
    "Autosomal dominant inheritance with maternal imprinting",
    "Autosomal dominant inheritance with paternal imprinting",
    "Autosomal unknown",
    "Codominant",
    "Genetic anticipation",
    "Mitochondrial inheritance",
    "Multifactorial inheritance",
    "Oligogenic inheritance",
    "Other",
    "Semidominant inheritance",
    "Somatic mutation",
    "Sporadic",
    "Unknown mechanism",
    "Sex-limited autosomal dominant",
    "X-linked inheritance",
    "X-linked dominant inheritance",
    "X-linked recessive inheritance",
    "Y-linked inheritance",
]

CLINVAR_SV_TYPES = [
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

AFFECTED_STATUS = ["yes", "no", "unknown", NOT_PROVIDED, "not applicable"]

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
    NOT_PROVIDED,
]

# Available databases used to describe phenotypes (Key/Description)
PHENO_DBS = {
    "HPO": "HPO",
    "MedGen": "MedGen",
    "MeSH": "MeSH",
    "MONDO": "MONDO",
    "OMIM": "OMIM",
    "Orphanet": "Orphanet",
    "UMLS": "UMLS",
}
