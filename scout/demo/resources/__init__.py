import importlib_resources

BASE_PATH = importlib_resources.files("scout")

###### Paths ######

# Gene paths
reduced_resources_path = BASE_PATH / "demo/resources"
hgnc_reduced_path = BASE_PATH / "demo/resources/hgnc_reduced_set.txt"
exac_reduced_path = (
    BASE_PATH / "demo/resources/forweb_cleaned_exac_r03_march16_z_data_pLI_reduced.txt"
)
transcripts37_reduced_path = BASE_PATH / "demo/resources/ensembl_transcripts_37_reduced.txt"
transcripts38_reduced_path = BASE_PATH / "demo/resources/ensembl_transcripts_38_reduced.txt"
genes37_reduced_path = BASE_PATH / "demo/resources/ensembl_genes_37_reduced.txt"
genes38_reduced_path = BASE_PATH / "demo/resources/ensembl_genes_38_reduced.txt"
exons37_reduced_path = BASE_PATH / "demo/resources/ensembl_exons_37_reduced.txt"
exons38_reduced_path = BASE_PATH / "demo/resources/ensembl_exons_38_reduced.txt"

# OMIM paths
mim2gene_reduced_path = BASE_PATH / "demo/resources/mim2gene_reduced.txt"
genemap2_reduced_path = BASE_PATH / "demo/resources/genemap2_reduced.txt"

# HPO paths
hpoterms_reduced_path = BASE_PATH / "demo/resources/reduced.hpo.obo"
genes_to_phenotype_reduced_path = BASE_PATH / "demo/resources/genes_to_phenotype_reduced.txt"
phenotype_to_genes_reduced_path = BASE_PATH / "demo/resources/phenotype_to_genes_reduced.txt"
hpo_terms_def_path = BASE_PATH / "demo/resources/hpo_terms.csv"


# Additional paths
madeline_path = BASE_PATH / "demo/madeline.xml"

demo_files = {
    "exac_path": exac_reduced_path,
    "genemap2_path": genemap2_reduced_path,
    "mim2gene_path": mim2gene_reduced_path,
    "genes37_path": genes37_reduced_path,
    "genes38_path": genes38_reduced_path,
    "hgnc_path": hgnc_reduced_path,
    "hpo_to_genes_path": phenotype_to_genes_reduced_path,
    "hpogenes_path": genes_to_phenotype_reduced_path,
    "hpoterms_path": hpoterms_reduced_path,
    "madeline_path": madeline_path,
    "transcripts37_path": transcripts37_reduced_path,
    "transcripts38_path": transcripts38_reduced_path,
    "panel_path": transcripts38_reduced_path,
}
