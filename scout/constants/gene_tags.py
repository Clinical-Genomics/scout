# These inheritance models are distinct from the official OMIM models of inheritance for variants
# which are specified by GENETIC_MODELS (in variant_tags.py).
# The following models are used while describing inheritance of genes in gene panels
# It's a custom-compiled list of values
GENE_PANELS_INHERITANCE_MODELS = (
    ("AD", "AD - Autosomal Dominant"),
    ("AR", "AR - Autosomal recessive"),
    ("XL", "XL - X Linked"),
    ("XD", "XD - X Linked Dominant"),
    ("XR", "XR - X Linked Recessive"),
    ("NA", "NA - not available"),
    ("AD (imprinting)", "AD (imprinting) - Autosomal Dominant (imprinting)"),
    ("digenic", "digenic - Digenic"),
    ("AEI", "AEI - Allelic expression imbalance"),
    ("other", "other - Other"),
)

# Associates an inheritance model with a color, for displaying inheritance on Variant page
INHERITANCE_PALETTE = {
    "AD": {"bgcolor": "bg-blue", "text_color": "text-white"},
    "AD (imprinting)": {"bgcolor": "bg-cyan", "text_color": "text-dark"},
    "AR": {"bgcolor": "bg-pink", "text_color": "text-white"},
    "XL": {"bgcolor": "bg-purple", "text_color": "text-white"},
    "XD": {"bgcolor": "bg-gray-dark", "text_color": "text-white"},
    "XR": {"bgcolor": "bg-green", "text_color": "text-white"},
    "NA": {"bgcolor": "bg-light", "text_color": "text-dark"},
    "digenic": {"bgcolor": "bg-secondary", "text_color": "text-white"},
    "AEI": {"bgcolor": "bg-light", "text_color": "text-dark"},
    "other": {"bgcolor": "bg-light", "text_color": "text-dark"},
}

VALID_MODELS = ("AR", "AD", "MT", "XD", "XR", "X", "Y")

INCOMPLETE_PENETRANCE_MAP = {"unknown": None, "Complete": None, "Incomplete": True}

MODELS_MAP = {
    "monoallelic_not_imprinted": ["AD"],
    "monoallelic_maternally_imprinted": ["AD"],
    "monoallelic_paternally_imprinted": ["AD"],
    "monoallelic": ["AD"],
    "biallelic": ["AR"],
    "monoallelic_and_biallelic": ["AD", "AR"],
    "monoallelic_and_more_severe_biallelic": ["AD", "AR"],
    "xlinked_biallelic": ["XR"],
    "xlinked_monoallelic": ["XD"],
    "mitochondrial": ["MT"],
    "unknown": [],
}

PANEL_GENE_INFO_TRANSCRIPTS = [
    "disease_associated_transcripts",
    "disease_associated_transcript",
    "transcripts",
]

PANEL_GENE_INFO_MODELS = [
    "genetic_disease_models",
    "genetic_disease_model",
    "inheritance_models",
    "genetic_inheritance_models",
]

# Values can be the real resource or the Scout demo one
UPDATE_GENES_RESOURCES = {
    "mim2genes": ["mim2genes.txt", "mim2gene_reduced.txt"],
    "genemap2": ["genemap2.txt", "genemap2_reduced.txt"],
    "hpo_genes": ["genes_to_phenotype.txt", "genes_to_phenotype_reduced.txt"],
    "hgnc_lines": ["hgnc.txt", "hgnc_reduced_set.txt"],
    "exac_lines": [
        "gnomad.v4.0.constraint_metrics.tsv",
        "gnomad.v4.0.constraint_metrics_reduced.tsv",
    ],
    "ensembl_genes_37": ["ensembl_genes_37.txt", "ensembl_genes_37_reduced.txt"],
    "ensembl_genes_38": ["ensembl_genes_38.txt", "ensembl_genes_38_reduced.txt"],
    "ensembl_transcripts_37": [
        "ensembl_transcripts_37.txt",
        "ensembl_transcripts_37_reduced.txt",
    ],
    "ensembl_transcripts_38": [
        "ensembl_transcripts_38.txt",
        "ensembl_transcripts_38_reduced.txt",
    ],
}

PANELAPP_CONFIDENCE_EXCLUDE = {
    "green": ["ModerateEvidence", "LowEvidence"],
    "amber": ["LowEvidence"],
    "red": [],
}

GNOMAD_CONSTRAINT_FILENAME = "gnomad.v4.0.constraint_metrics.tsv"

GENE_CONSTRAINT_LABELS = {
    "pli_score": "lof.pLI",
    "constraint_lof_oe": "lof.oe",
    "constraint_lof_oe_ci_lower": "lof.oe_ci.lower",
    "constraint_lof_oe_ci_upper": "lof.oe_ci.upper",
    "constraint_lof_z": "lof.z_score",
    "constraint_mis_oe": "mis.oe",
    "constraint_mis_oe_ci_lower": "mis.oe_ci.lower",
    "constraint_mis_oe_ci_upper": "mis.oe_ci.upper",
    "constraint_mis_z": "mis.z_score",
}
