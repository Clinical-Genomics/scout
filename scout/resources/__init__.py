import pkg_resources

hgnc_file = 'resources/hgnc_complete_set.txt.gz'
exac_file = 'resources/forweb_cleaned_exac_r03_march16_z_data_pLI.txt.gz'
transcripts37_file = 'resources/ensembl_transcripts_37.txt.gz'
transcripts38_file = 'resources/ensembl_transcripts_38.txt.gz'

hpogenes_file = 'resources/ALL_SOURCES_ALL_FREQUENCIES_genes_to_phenotype.txt.gz'
hpoterms_file = 'resources/ALL_SOURCES_ALL_FREQUENCIES_phenotype_to_genes.txt.gz'
hpodisease_file = 'resources/diseases_to_genes.txt.gz'

hgnc_path = pkg_resources.resource_filename('scout', hgnc_file)
exac_path = pkg_resources.resource_filename('scout', exac_file)
transcripts37_path = pkg_resources.resource_filename('scout', transcripts37_file)
transcripts38_path = pkg_resources.resource_filename('scout', transcripts38_file)

hpogenes_path = pkg_resources.resource_filename('scout', hpogenes_file)
hpoterms_path = pkg_resources.resource_filename('scout', hpoterms_file)
hpodisease_path = pkg_resources.resource_filename('scout', hpodisease_file)
