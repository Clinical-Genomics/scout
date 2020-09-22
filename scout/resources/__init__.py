import pkg_resources


###### Files ######

# Cytoband
cytoband_hg19_file = "resources/cytoBand_hg19.txt.gz"
cytoband_hg38_file = "resources/cytoBand_hg38.txt.gz"

###### Paths ######

# Cytoband path
cytobands_37_path = pkg_resources.resource_filename("scout", cytoband_hg19_file)
cytobands_38_path = pkg_resources.resource_filename("scout", cytoband_hg38_file)

cytoband_files = {
    "37": cytobands_37_path,
    "38": cytobands_38_path,
}
