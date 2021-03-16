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
