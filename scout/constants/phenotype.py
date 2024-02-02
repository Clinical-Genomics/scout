HPO_URL = "http://purl.obolibrary.org/obo/hp/hpoa/{}"
HPOTERMS_URL = (
    "https://raw.githubusercontent.com/obophenotype/human-phenotype-ontology/master/hp.obo"
)

ORPHA_URLS = {
    "orpha_to_hpo": "https://www.orphadata.com/data/xml/en_product4.xml",
    "orpha_to_genes": "https://www.orphadata.com/data/xml/en_product6.xml",
    "orpha_inheritance": "https://www.orphadata.com/data/xml/en_product9_ages.xml",
}

PHENOTYPE_GROUPS = {
    "HP:0001298": {"name": "Encephalopathy", "abbr": "ENC"},
    "HP:0012759": {"name": "Neurodevelopmental abnormality", "abbr": "NDEV"},
    "HP:0001250": {"name": "Seizures", "abbr": "EP"},
    "HP:0100022": {"name": "Abnormality of movement", "abbr": "MOVE"},
    "HP:0000707": {"name": "Neurology, other", "abbr": "NEUR"},
    "HP:0003011": {"name": "Abnormality of the musculature", "abbr": "MUSC"},
    "HP:0001638": {"name": "Cardiomyopathy", "abbr": "CARD"},
    "HP:0001507": {"name": "Growth abnormality", "abbr": "GROW"},
    "HP:0001392": {"name": "Abnormality of the liver", "abbr": "LIV"},
    "HP:0011458": {"name": "Abdominal symptom", "abbr": "GI"},
    "HP:0012373": {"name": "Abnormal eye physiology", "abbr": "EYE"},
    "HP:0000077": {"name": "Abnormality of the kidney", "abbr": "KIDN"},
    "HP:0000951": {"name": "Abnormality of the skin", "abbr": "SKIN"},
    "HP:0001939": {"name": "Abnormality of metabolism/homeostasis", "abbr": "METAB"},
    "HP:0000118": {"name": "As yet undefined/to be added", "abbr": "UND"},
    "HP:0002011": {"name": "Abnormal CNS morphology", "abbr": "MRI"},
}

COHORT_TAGS = ["endo", "mito", "ketogenic diet", "pedhep", "other"]

# Downloaded resources can be real downloaded files or demo files (located in scout/scout/demo/resources)
UPDATE_DISEASES_RESOURCES = {
    "genemap_lines": ["genemap2.txt", "genemap2_reduced.txt"],
    "hpo_gene_lines": ["phenotype_to_genes.txt", "phenotype_to_genes_reduced.txt"],
    "hpo_annotation_lines": ["phenotype.hpoa", "reduced.phenotype.hpoa"],
    "orpha_to_genes_lines": [
        "orphadata_en_product6.xml",
        "orphadata_en_product6_reduced.xml",
    ],
    "orpha_to_hpo_lines": [
        "orphadata_en_product4.xml",
        "orphadata_en_product4_reduced.xml",
    ],
    "orpha_inheritance_lines": [
        "en_product9_ages.xml",
        "en_product9_ages_reduced.xml",
    ],
}
