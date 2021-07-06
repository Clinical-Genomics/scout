# These inheritance models are distinct from the official OMIM models of inheritance for variants
# which are specified by GENETIC_MODELS (in variant_tags.py).
# The following models are used while describing inheritance of genes in gene panels
# It's a custom-compiled list of values
GENE_CUSTOM_INHERITANCE_MODELS = (
    ("AD", "Autosomal Dominant"),
    ("AR", "Autosomal recessive"),
    ("XL", "X Linked"),
    ("XD", "X Linked Dominant"),
    ("XR", "X Linked Recessive"),
    ("NA", "not available"),
    ("AD (imprinting)", "Autosomal Dominant (imprinting)"),
    ("digenic", "Digenic"),
    ("AEI", "Allelic expression imbalance"),
    ("other", "Other"),
)

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
        "fordist_cleaned_exac_r03_march16_z_pli_rec_null_data.txt",
        "forweb_cleaned_exac_r03_march16_z_data_pLI_reduced.txt",
    ],
    "ensembl_genes_37": ["ensembl_genes_37.txt", "ensembl_genes_37_reduced.txt"],
    "ensembl_genes_38": ["ensembl_genes_38.txt", "ensembl_genes_38_reduced.txt"],
    "ensembl_transcripts_37": ["ensembl_transcripts_37.txt", "ensembl_transcripts_37_reduced.txt"],
    "ensembl_transcripts_38": ["ensembl_transcripts_38.txt", "ensembl_transcripts_38_reduced.txt"],
}
