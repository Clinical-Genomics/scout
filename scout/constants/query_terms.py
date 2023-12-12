# -*- coding: utf-8 -*-

# These terms are used by the function that creates a variant query dictionary in adapters

# Always respected. Always added as top level,
# with implicit '$and'
FUNDAMENTAL_CRITERIA = [
    "case_id",
    "variant_ids",
    "category",
    "variant_type",
    "hgnc_symbols",
    "repids",
    "gene_panels",
    "chrom",
    "start",
    "end",
    "variant_ids",
    "hide_dismissed",
    "show_unaffected",
]

# If there is only one primary criterion given without any secondary, it will also be
# added as a top level '$and'.
# Otherwise, primary criteria are added as a high level '$or' and all secondary criteria
# are joined together with them as a single lower level '$and'.
PRIMARY_CRITERIA = ["clinsig"]

# Secondary, excluding filter criteria will hide variants in general,
# but can be overridden by an including, major filter criteria
# such as a Pathogenic ClinSig.
SECONDARY_CRITERIA = [
    "gnomad_frequency",
    "local_obs",
    "local_obs_freq",
    "clingen_ngi",
    "swegen",
    "swegen_freq",
    "spidex_human",
    "cadd_score",
    "revel",
    "genetic_models",
    "genotypes",
    "functional_annotations",
    "region_annotations",
    "size",
    "svtype",
    "decipher",
    "depth",
    "alt_count",
    "somatic_score",
    "control_frequency",
    "mvl_tag",
    "clinvar_tag",
    "cosmic_tag",
    "tumor_frequency",
    "fusion_score",
    "ffpm",
    "junction_reads",
    "split_reads",
    "fusion_caller",
]
