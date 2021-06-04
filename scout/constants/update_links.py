# A collection of URLs used in Scout update commands

HPO_URL = "https://ci.monarchinitiative.org/view/hpo/job/hpo.annotations/lastSuccessfulBuild/artifact/rare-diseases/util/annotation/{}"
HPO_TERMS_URL = "http://purl.obolibrary.org/obo/hp.obo"
OMIM_DOWNLOADS_URL = "https://data.omim.org/downloads/{}/{}"
OMIM_TO_GENE_URL = "https://omim.org/static/omim/data/mim2gene.txt"
HGNC_COMPLETE_SET = "ftp://ftp.ebi.ac.uk/pub/databases/genenames/new/tsv/hgnc_complete_set.txt"
EXACT_GENE_CONTRAINT = "ftp://ftp.broadinstitute.org/pub/ExAC_release/release0.3/functional_gene_constraint/fordist_cleaned_exac_r03_march16_z_pli_rec_null_data.txt"
EXACT_GENE_CONTRAINT_BUCKET = "https://storage.googleapis.com/gnomad-public/legacy/exacv1_downloads/release0.3.1/manuscript_data/forweb_cleaned_exac_r03_march16_z_data_pLI.txt.gz"
REFSEQ_URL = (
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=nuccore&term={}&idtype=acc"
)
