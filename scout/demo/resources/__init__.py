from importlib_resources import files

from scout.demo import madeline_path

BASE_PATH = "scout.demo.resources"

###### Paths ######

# Gene paths
reduced_resources_path = str(files(BASE_PATH))
hgnc_reduced_path = str(files(BASE_PATH).joinpath("hgnc_reduced_set.txt"))
exac_reduced_path = str(
    files(BASE_PATH).joinpath("forweb_cleaned_exac_r03_march16_z_data_pLI_reduced.txt")
)
transcripts37_reduced_path = str(files(BASE_PATH).joinpath("ensembl_transcripts_37_reduced.txt"))
transcripts38_reduced_path = str(files(BASE_PATH).joinpath("ensembl_transcripts_38_reduced.txt"))
genes37_reduced_path = str(files(BASE_PATH).joinpath("ensembl_genes_37_reduced.txt"))
genes38_reduced_path = str(files(BASE_PATH).joinpath("ensembl_genes_38_reduced.txt"))
exons37_reduced_path = str(files(BASE_PATH).joinpath("ensembl_exons_37_reduced.txt"))
exons38_reduced_path = str(files(BASE_PATH).joinpath("ensembl_exons_38_reduced.txt"))

# OMIM paths
mim2gene_reduced_path = str(files(BASE_PATH).joinpath("mim2gene_reduced.txt"))
genemap2_reduced_path = str(files(BASE_PATH).joinpath("genemap2_reduced.txt"))

# HPO paths
hpoterms_reduced_path = str(files(BASE_PATH).joinpath("reduced.hpo.obo"))
hpo_phenotype_annotation_reduced_path = str(files(BASE_PATH).joinpath("reduced.phenotype.hpoa"))
genes_to_phenotype_reduced_path = str(files(BASE_PATH).joinpath("genes_to_phenotype_reduced.txt"))
phenotype_to_genes_reduced_path = str(files(BASE_PATH).joinpath("phenotype_to_genes_reduced.txt"))
hpo_terms_def_path = str(files(BASE_PATH).joinpath("hpo_terms.csv"))

demo_files = {
    "exac_path": exac_reduced_path,
    "genemap2_path": genemap2_reduced_path,
    "mim2gene_path": mim2gene_reduced_path,
    "genes37_path": genes37_reduced_path,
    "genes38_path": genes38_reduced_path,
    "hgnc_path": hgnc_reduced_path,
    "hpo_to_genes_path": phenotype_to_genes_reduced_path,
    "hpogenes_path": genes_to_phenotype_reduced_path,
    "hpo_phenotype_annotation_path": hpo_phenotype_annotation_reduced_path,
    "hpoterms_path": hpoterms_reduced_path,
    "madeline_path": madeline_path,
    "transcripts37_path": transcripts37_reduced_path,
    "transcripts38_path": transcripts38_reduced_path,
    "panel_path": transcripts38_reduced_path,
}
