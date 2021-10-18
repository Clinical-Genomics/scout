# -*- coding: utf-8 -*-
import re

from intervaltree import Interval, IntervalTree

from scout.parse.cytoband import parse_cytoband
from scout.resources import cytoband_files
from scout.utils.handle import get_file_handle

from .acmg import ACMG_COMPLETE_MAP, ACMG_CRITERIA, ACMG_MAP, ACMG_OPTIONS, REV_ACMG_MAP
from .case_tags import (
    ANALYSIS_TYPES,
    CANCER_PHENOTYPE_MAP,
    CASE_REPORT_CASE_FEATURES,
    CASE_REPORT_CASE_IND_FEATURES,
    CASE_REPORT_VARIANT_TYPES,
    CASE_SEARCH_TERMS,
    CASE_STATUSES,
    CUSTOM_CASE_REPORTS,
    PHENOTYPE_MAP,
    REV_PHENOTYPE_MAP,
    REV_SEX_MAP,
    SAMPLE_SOURCE,
    SEX_MAP,
    VERBS_MAP,
)
from .clinvar import CASEDATA_HEADER, CLINVAR_HEADER, CLINVAR_INHERITANCE_MODELS
from .clnsig import CLINSIG_MAP, REV_CLINSIG_MAP, TRUSTED_REVSTAT_LEVEL
from .file_types import FILE_TYPE_MAP
from .filters import CLINICAL_FILTER_BASE, CLINICAL_FILTER_BASE_CANCER, CLINICAL_FILTER_BASE_SV
from .gene_tags import (
    GENE_CUSTOM_INHERITANCE_MODELS,
    INCOMPLETE_PENETRANCE_MAP,
    MODELS_MAP,
    PANEL_GENE_INFO_MODELS,
    PANEL_GENE_INFO_TRANSCRIPTS,
    UPDATE_GENES_RESOURCES,
    VALID_MODELS,
)
from .igv_tracks import CASE_SPECIFIC_TRACKS, HUMAN_REFERENCE, IGV_TRACKS, USER_DEFAULT_TRACKS
from .indexes import INDEXES
from .phenotype import COHORT_TAGS, PHENOTYPE_GROUPS, UPDATE_DISEASES_RESOURCES
from .query_terms import FUNDAMENTAL_CRITERIA, PRIMARY_CRITERIA, SECONDARY_CRITERIA
from .so_terms import SEVERE_SO_TERMS, SO_TERM_KEYS, SO_TERMS
from .variant_tags import (
    CANCER_SPECIFIC_VARIANT_DISMISS_OPTIONS,
    CANCER_TIER_OPTIONS,
    CONSEQUENCE,
    CONSERVATION,
    DISMISS_VARIANT_OPTIONS,
    FEATURE_TYPES,
    GENETIC_MODELS,
    MANUAL_RANK_OPTIONS,
    MOSAICISM_OPTIONS,
    SPIDEX_HUMAN,
    SPIDEX_LEVELS,
    SV_TYPES,
    VARIANT_CALL,
    VARIANT_FILTERS,
    VARIANT_REPORT_VARIANT_FEATURES,
)
from .variants_export import (
    EXPORT_HEADER,
    MT_COV_STATS_HEADER,
    MT_EXPORT_HEADER,
    VCF_HEADER,
    VERIFIED_VARIANTS_HEADER,
)

cytobands_37_handle = get_file_handle(cytoband_files.get("37"))
cytobands_38_handle = get_file_handle(cytoband_files.get("38"))

COLLECTIONS = [
    "hgnc_gene",
    "user",
    "institute",
    "event",
    "case",
    "case_group",
    "gene_panel",
    "hpo_term",
    "disease_term",
    "variant",
    "acmg",
]

BUILDS = ["37", "38", "GRCh38"]

CYTOBANDS_37 = parse_cytoband(cytobands_37_handle)
CYTOBANDS_38 = parse_cytoband(cytobands_38_handle)

AUTOSOMES = [str(nr) for nr in range(1, 23)]
CHROMOSOMES = AUTOSOMES + [
    "X",
    "Y",
    "MT",
]  # Chromosomes of build 37 would be default. I don't dare to change this yet since it's used all over the place. It needs major refactoring
CHROMOSOMES_38 = AUTOSOMES + ["X", "Y", "M"]

# Maps chromosomes to integers
CHROMOSOME_INTEGERS = {chrom: i + 1 for i, chrom in enumerate(CHROMOSOMES)}


PAR_COORDINATES = {
    "37": {
        "X": IntervalTree(
            [Interval(60001, 2699521, "par1"), Interval(154931044, 155260561, "par2")]
        ),
        "Y": IntervalTree([Interval(10001, 2649521, "par1"), Interval(59034050, 59363567, "par2")]),
    },
    "38": {
        "X": IntervalTree(
            [Interval(10001, 2781480, "par1"), Interval(155701383, 156030896, "par2")]
        ),
        "Y": IntervalTree([Interval(10001, 2781480, "par1"), Interval(56887903, 57217416, "par2")]),
    },
}

CALLERS = {
    "snv": [
        {"id": "gatk", "name": "GATK"},
        {"id": "freebayes", "name": "Freebayes"},
        {"id": "samtools", "name": "SAMtools"},
        {"id": "bcftools", "name": "Bcftools"},
        {"id": "deepvariant", "name": "DeepVariant"},
    ],
    "cancer": [
        {"id": "mutect", "name": "MuTect"},
        {"id": "pindel", "name": "Pindel"},
        {"id": "gatk", "name": "GATK"},
        {"id": "freebayes", "name": "Freebayes"},
    ],
    "cancer_sv": [
        {"id": "manta", "name": "Manta"},
        {"id": "gatk", "name": "GATK"},
    ],
    "sv": [
        {"id": "gatk", "name": "GATK"},
        {"id": "cnvnator", "name": "CNVnator"},
        {"id": "delly", "name": "Delly"},
        {"id": "tiddit", "name": "TIDDIT"},
        {"id": "manta", "name": "Manta"},
    ],
    "str": [{"id": "expansionhunter", "name": "ExpansionHunter"}],
}

BND_ALT_PATTERN = re.compile(r".*[\],\[](.*?):(.*?)[\],\[]")
CHR_PATTERN = re.compile(r"(chr)?(.*)", re.IGNORECASE)

AMINO_ACID_RESIDUE_3_TO_1 = {
    "Ala": "A",
    "Arg": "R",
    "Asn": "N",
    "Asp": "D",
    "Asx": "B",
    "Cys": "C",
    "Glu": "E",
    "Gln": "Q",
    "Glx": "Z",
    "Gly": "G",
    "His": "H",
    "Ile": "I",
    "Leu": "L",
    "Lys": "K",
    "Met": "M",
    "Phe": "F",
    "Pro": "P",
    "Ser": "S",
    "Thr": "T",
    "Trp": "W",
    "Tyr": "Y",
    "Val": "V",
    "Ter": "*",
    "del": "del",
}
