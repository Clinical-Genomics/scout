import pkg_resources

hgnc_file = pkg_resources.resource_filename('scout', 'resources/hgnc_complete_set.txt.gz')
exac_file = pkg_resources.resource_filename('scout', 'resources/forweb_cleaned_exac_r03_march16_z_data_pLI.txt.gz')
transcripts_file = pkg_resources.resource_filename('scout', 'resources/ensembl_transcripts_37.txt.gz')
hpogenes_file = pkg_resources.resource_filename('scout', 'resources/ALL_SOURCES_ALL_FREQUENCIES_genes_to_phenotype.txt.gz')
