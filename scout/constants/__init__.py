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
    CASE_REPORT_VARIANT_TYPES,
    CASE_SEARCH_TERMS,
    CASE_STATUSES,
    CASE_TAGS,
    CUSTOM_CASE_REPORTS,
    PHENOTYPE_MAP,
    REV_PHENOTYPE_MAP,
    REV_SEX_MAP,
    SAMPLE_SOURCE,
    SEX_MAP,
    VERBS_ICONS_MAP,
    VERBS_MAP,
)
from .clinvar import (
    AFFECTED_STATUS,
    ALLELE_OF_ORIGIN,
    ASSERTION_METHOD,
    ASSERTION_METHOD_CIT,
    CLINVAR_ASSERTION_METHOD_CIT_DB_OPTIONS,
    CLINVAR_INHERITANCE_MODELS,
    CLINVAR_SV_TYPES,
    COLLECTION_METHOD,
    CONDITION_PREFIX,
    GERMLINE_CLASSIF_TERMS,
)
from .clnsig import CLINSIG_MAP, REV_CLINSIG_MAP, TRUSTED_REVSTAT_LEVEL
from .disease_parsing import (
    DISEASE_INHERITANCE_TERMS,
    ENTRY_PATTERN,
    INHERITANCE_TERMS_MAPPER,
    MIMNR_PATTERN,
    OMIM_STATUS_MAP,
)
from .file_types import FILE_TYPE_MAP
from .filters import (
    CLINICAL_FILTER_BASE,
    CLINICAL_FILTER_BASE_CANCER,
    CLINICAL_FILTER_BASE_MEI,
    CLINICAL_FILTER_BASE_SV,
)
from .gene_tags import (
    GENE_CONSTRAINT_LABELS,
    GENE_PANELS_INHERITANCE_MODELS,
    GNOMAD_CONSTRAINT_FILENAME,
    INCOMPLETE_PENETRANCE_MAP,
    INHERITANCE_PALETTE,
    MODELS_MAP,
    PANEL_GENE_INFO_MODELS,
    PANEL_GENE_INFO_TRANSCRIPTS,
    PANELAPP_CONFIDENCE_EXCLUDE,
    UPDATE_GENES_RESOURCES,
    VALID_MODELS,
)
from .igv_tracks import CASE_SPECIFIC_TRACKS, HUMAN_REFERENCE, IGV_TRACKS, USER_DEFAULT_TRACKS
from .indexes import ID_PROJECTION, INDEXES
from .phenotype import (
    COHORT_TAGS,
    HPO_URL,
    HPOTERMS_URL,
    ORPHA_URLS,
    PHENOTYPE_GROUPS,
    UPDATE_DISEASES_RESOURCES,
)
from .query_terms import FUNDAMENTAL_CRITERIA, PRIMARY_CRITERIA, SECONDARY_CRITERIA
from .so_terms import SEVERE_SO_TERMS, SEVERE_SO_TERMS_SV, SO_TERM_KEYS, SO_TERMS
from .variant_tags import (
    CANCER_SPECIFIC_VARIANT_DISMISS_OPTIONS,
    CANCER_TIER_OPTIONS,
    CONSEQUENCE,
    CONSERVATION,
    DISMISS_VARIANT_OPTIONS,
    FEATURE_TYPES,
    GENETIC_MODELS,
    GENETIC_MODELS_PALETTE,
    MANUAL_RANK_OPTIONS,
    MOSAICISM_OPTIONS,
    SPIDEX_HUMAN,
    SPIDEX_LEVELS,
    SV_TYPES,
    VARIANT_CALL,
    VARIANT_FILTERS,
    VARIANT_GENOTYPES,
    VARIANTS_TARGET_FROM_CATEGORY,
)
from .variants_export import (
    CANCER_EXPORT_HEADER,
    EXPORT_HEADER,
    EXPORTED_VARIANTS_LIMIT,
    MITODEL_HEADER,
    MT_COV_STATS_HEADER,
    MT_EXPORT_HEADER,
    VCF_HEADER,
    VERIFIED_VARIANTS_HEADER,
)

DATE_DAY_FORMATTER = "%Y-%m-%d"

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
            [
                Interval(60001, 2699521, "par1"),
                Interval(154931044, 155260561, "par2"),
                Interval(88456972, 92375509, "xtr"),
            ],
        ),
        "Y": IntervalTree(
            [
                Interval(10001, 2649521, "par1"),
                Interval(59034050, 59363567, "par2"),
                Interval(2917959, 6102616, "xtr"),
            ]
        ),
    },
    "38": {
        "X": IntervalTree(
            [
                Interval(10001, 2781480, "par1"),
                Interval(155701383, 156030896, "par2"),
                Interval(89201883, 93120510, "xtr"),
            ]
        ),
        "Y": IntervalTree(
            [
                Interval(10001, 2781480, "par1"),
                Interval(56887903, 57217416, "par2"),
                Interval(3049918, 6234575, "xtr"),
            ]
        ),
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
        {"id": "tnscope", "name": "TNScope"},
        {"id": "tnscope_umi", "name": "TNscope_UMI"},
        {"id": "vardict", "name": "VarDict"},
    ],
    "cancer_sv": [
        {"id": "gatk", "name": "GATK"},
        {"id": "manta", "name": "Manta"},
        {"id": "dellysv", "name": "DellySV"},
        {"id": "cnvkit", "name": "CNVkit"},
        {"id": "ascat", "name": "ASCAT"},
        {"id": "dellycnv", "name": "DellyCNV"},
        {"id": "tiddit", "name": "TIDDIT"},
    ],
    "mei": [{"id": "retroseq", "name": "RetroSeq"}],
    "sv": [
        {"id": "gatk", "name": "GATK"},
        {"id": "cnvnator", "name": "CNVnator"},
        {"id": "cnvpytor", "name": "CNVpytor"},
        {"id": "delly", "name": "Delly"},
        {"id": "sniffles", "name": "Sniffles"},
        {"id": "tiddit", "name": "TIDDIT"},
        {"id": "manta", "name": "Manta"},
    ],
    "str": [{"id": "expansionhunter", "name": "ExpansionHunter"}],
    "fusion": [
        {"id": "arriba", "name": "Arriba"},
        {"id": "starfusion", "name": "STARfusion"},
        {"id": "fusioncatcher", "name": "FusionCatcher"},
    ],
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
