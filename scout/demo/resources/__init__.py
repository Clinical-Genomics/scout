import pkg_resources

###### Files ######

# Gene sources:
resources_folder = "demo/resources"
hgnc_file = "demo/resources/hgnc_reduced_set.txt"
exac_file = "demo/resources/forweb_cleaned_exac_r03_march16_z_data_pLI_reduced.txt"
transcripts37_file = "demo/resources/ensembl_transcripts_37_reduced.txt"
genes37_file = "demo/resources/ensembl_genes_37_reduced.txt"
exons37_file = "demo/resources/ensembl_exons_37_reduced.txt"
transcripts38_file = "demo/resources/ensembl_transcripts_38_reduced.txt"
genes38_file = "demo/resources/ensembl_genes_38_reduced.txt"
exons38_file = "demo/resources/ensembl_exons_38_reduced.txt"

# OMIM resources:
mim2gene_file = "demo/resources/mim2gene_reduced.txt"
genemap2_file = "demo/resources/genemap2_reduced.txt"

# Hpo resources
genes_to_phenotype_to_diseases_file = "demo/resources/genes_to_phenotype_reduced.txt"
hpoterms_file = "demo/resources/reduced.hpo.obo"
hpo_phenotype_to_genes_to_diseases_file = "demo/resources/phenotype_to_genes_reduced.txt"

hpo_terms_def_file = "demo/resources/hpo_terms.csv"

# Additional resources
madeline_file = "demo/madeline.xml"

###### Paths ######

# Gene paths
reduced_resources_path = pkg_resources.resource_filename("scout", resources_folder)
hgnc_reduced_path = pkg_resources.resource_filename("scout", hgnc_file)
exac_reduced_path = pkg_resources.resource_filename("scout", exac_file)
transcripts37_reduced_path = pkg_resources.resource_filename("scout", transcripts37_file)
transcripts38_reduced_path = pkg_resources.resource_filename("scout", transcripts38_file)
genes37_reduced_path = pkg_resources.resource_filename("scout", genes37_file)
genes38_reduced_path = pkg_resources.resource_filename("scout", genes38_file)
exons37_reduced_path = pkg_resources.resource_filename("scout", exons37_file)
exons38_reduced_path = pkg_resources.resource_filename("scout", exons38_file)

# OMIM paths
mim2gene_reduced_path = pkg_resources.resource_filename("scout", mim2gene_file)
genemap2_reduced_path = pkg_resources.resource_filename("scout", genemap2_file)

# HPO paths
hpoterms_reduced_path = pkg_resources.resource_filename("scout", hpoterms_file)
genes_to_phenotype_reduced_path = pkg_resources.resource_filename(
    "scout", genes_to_phenotype_to_diseases_file
)
phenotype_to_genes_reduced_path = pkg_resources.resource_filename(
    "scout", hpo_phenotype_to_genes_to_diseases_file
)
hpo_terms_def_path = pkg_resources.resource_filename("scout", hpo_terms_def_file)


# Additional paths
madeline_path = pkg_resources.resource_filename("scout", madeline_file)

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
