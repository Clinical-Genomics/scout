import pkg_resources


###### Files ######

# Gene sources:
hgnc_file = 'resources/hgnc_complete_set.txt.gz'
exac_file = 'resources/forweb_cleaned_exac_r03_march16_z_data_pLI.txt.gz'
transcripts37_file = 'resources/ensembl_transcripts_37.txt.gz'
transcripts38_file = 'resources/ensembl_transcripts_38.txt.gz'

# Cytoband

cytobands_file = 'resources/cytoBand.txt.gz'

###### Paths ######

# Gene paths
hgnc_path = pkg_resources.resource_filename('scout', hgnc_file)
exac_path = pkg_resources.resource_filename('scout', exac_file)
transcripts37_path = pkg_resources.resource_filename('scout', transcripts37_file)
transcripts38_path = pkg_resources.resource_filename('scout', transcripts38_file)


# Cytoband path

cytobands_path = pkg_resources.resource_filename('scout', cytobands_file)
