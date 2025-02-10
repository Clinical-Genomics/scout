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
    ("Y", "Y-linked"),
    ("MT", "Mitochondrial inheritance"),
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
    "Y": {"bgcolor": "bg-purple", "text_color": "text-white"},
    "MT": {"bgcolor": "bg-purple", "text_color": "text-white"},
    "XD": {"bgcolor": "bg-gray-dark", "text_color": "text-white"},
    "XR": {"bgcolor": "bg-green", "text_color": "text-white"},
    "NA": {"bgcolor": "bg-light", "text_color": "text-dark"},
    "digenic": {"bgcolor": "bg-secondary", "text_color": "text-white"},
    "AEI": {"bgcolor": "bg-light", "text_color": "text-dark"},
    "other": {"bgcolor": "bg-light", "text_color": "text-dark"},
}

INCOMPLETE_PENETRANCE_MAP = {"unknown": None, "None": None, "Complete": False, "Incomplete": True}

MODELS_MAP = {
    "MONOALLELIC, autosomal or pseudoautosomal, NOT imprinted": ["AD"],
    "MONOALLELIC, autosomal or pseudoautosomal, imprinted status unknown": ["AD"],
    "MONOALLELIC, autosomal or pseudoautosomal, maternally imprinted (paternal allele expressed)": [
        "AD"
    ],
    "MONOALLELIC, autosomal or pseudoautosomal, paternally imprinted (maternal allele expressed)": [
        "AD"
    ],
    "BIALLELIC, autosomal or pseudoautosomal": ["AR"],
    "BOTH monoallelic and biallelic, autosomal or pseudoautosomal": ["AD", "AR"],
    "BOTH monoallelic and biallelic (but BIALLELIC mutations cause a more SEVERE disease form), autosomal or pseudoautosomal": [
        "AD",
        "AR",
    ],
    "X-LINKED: hemizygous mutation in males, biallelic mutations in females": ["XR"],
    "X-LINKED: hemizygous mutation in males, monoallelic mutations in females may cause disease (may be less severe, later onset than males)": [
        "XD"
    ],
    "MITOCHONDRIAL": ["MT"],
    "Other": [],
    "Other - please specifiy in evaluation comments": [],
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
        "gnomad.v4.1.constraint_metrics.tsv",
        "gnomad.v4.1.constraint_metrics_reduced.tsv",
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

GNOMAD_CONSTRAINT_FILENAME = "gnomad.v4.1.constraint_metrics.tsv"

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
