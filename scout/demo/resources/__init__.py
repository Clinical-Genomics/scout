from contextlib import ExitStack

import importlib_resources

file_manager = ExitStack()

###### Files ######

# Gene sources:
resources_folder = importlib_resources.files("scout") / "demo/resources"
hgnc_file = importlib_resources.files("scout") / "demo/resources/hgnc_reduced_set.txt"
exac_file = (
    importlib_resources.files("scout")
    / "demo/resources/forweb_cleaned_exac_r03_march16_z_data_pLI_reduced.txt"
)
transcripts37_file = (
    importlib_resources.files("scout") / "demo/resources/ensembl_transcripts_37_reduced.txt"
)
genes37_file = importlib_resources.files("scout") / "demo/resources/ensembl_genes_37_reduced.txt"
exons37_file = importlib_resources.files("scout") / "demo/resources/ensembl_exons_37_reduced.txt"
transcripts38_file = (
    importlib_resources.files("scout") / "demo/resources/ensembl_transcripts_38_reduced.txt"
)
genes38_file = importlib_resources.files("scout") / "demo/resources/ensembl_genes_38_reduced.txt"
exons38_file = importlib_resources.files("scout") / "demo/resources/ensembl_exons_38_reduced.txt"

# OMIM resources:
mim2gene_file = importlib_resources.files("scout") / "demo/resources/mim2gene_reduced.txt"
genemap2_file = importlib_resources.files("scout") / "demo/resources/genemap2_reduced.txt"

# Hpo resources
genes_to_phenotype_to_diseases_file = (
    importlib_resources.files("scout") / "demo/resources/genes_to_phenotype_reduced.txt"
)
hpoterms_file = importlib_resources.files("scout") / "demo/resources/reduced.hpo.obo"
hpo_phenotype_to_genes_to_diseases_file = (
    importlib_resources.files("scout") / "demo/resources/phenotype_to_genes_reduced.txt"
)

hpo_terms_def_file = importlib_resources.files("scout") / "demo/resources/hpo_terms.csv"

# Additional resources
madeline_file = importlib_resources.files("scout") / "demo/madeline.xml"

###### Paths ######

# Gene paths
reduced_resources_path = file_manager.enter_context(importlib_resources.as_file(resources_folder))
hgnc_reduced_path = file_manager.enter_context(importlib_resources.as_file(hgnc_file))
exac_reduced_path = file_manager.enter_context(importlib_resources.as_file(exac_file))
transcripts37_reduced_path = file_manager.enter_context(
    importlib_resources.as_file(transcripts37_file)
)
transcripts38_reduced_path = file_manager.enter_context(
    importlib_resources.as_file(transcripts38_file)
)
genes37_reduced_path = file_manager.enter_context(importlib_resources.as_file(genes37_file))
genes38_reduced_path = file_manager.enter_context(importlib_resources.as_file(genes38_file))
exons37_reduced_path = file_manager.enter_context(importlib_resources.as_file(exons37_file))
exons38_reduced_path = file_manager.enter_context(importlib_resources.as_file(exons38_file))

# OMIM paths
mim2gene_reduced_path = file_manager.enter_context(importlib_resources.as_file(mim2gene_file))
genemap2_reduced_path = file_manager.enter_context(importlib_resources.as_file(genemap2_file))

# HPO paths
hpoterms_reduced_path = file_manager.enter_context(importlib_resources.as_file(hpoterms_file))
genes_to_phenotype_reduced_path = file_manager.enter_context(
    importlib_resources.as_file(genes_to_phenotype_to_diseases_file)
)
phenotype_to_genes_reduced_path = file_manager.enter_context(
    importlib_resources.as_file(hpo_phenotype_to_genes_to_diseases_file)
)
hpo_terms_def_path = file_manager.enter_context(importlib_resources.as_file(hpo_terms_def_file))


# Additional paths
madeline_path = file_manager.enter_context(importlib_resources.as_file(madeline_file))

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
