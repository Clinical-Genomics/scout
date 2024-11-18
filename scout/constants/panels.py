EXPORT_PANEL_FIELDS = [
    ("#hgnc_id", "hgnc_id"),
    ("symbol", "symbol"),
    ("disease_associated_transcripts", "disease_associated_transcripts"),
    ("reduced_penetrance", "reduced_penetrance"),
    ("mosaicism", "mosaicism"),
    ("database_entry_version", "database_entry_version"),
    ("inheritance_models", "inheritance_models"),
    ("custom_inheritance_models", "custom_inheritance_models"),
    ("comment", "comment"),
]

PANELAPP_CONFIDENCE_EXCLUDE = {
    "green": ["1", "2"],
    "amber": ["1"],
    "red": [],
}

PRESELECTED_PANELAPP_PANEL_TYPE_SLUGS = [
    "cancer-germline-100k",
    "clingen-curated-genes",
    "gms-cancer-germline-virtual",
    "gms-rare-disease",
    "gms-rare-disease-virtual",
    "gms-signed-off",
    "rare-disease-100k",
]
