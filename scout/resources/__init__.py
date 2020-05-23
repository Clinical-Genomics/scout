import pkg_resources


###### Files ######

# Cytoband

cytobands_file = "resources/cytoBand.txt.gz"
cytoband_hg19_file = "resources/cytoBand_hg19.txt"
cytoband_hg38_file = "resources/cytoBand_hg38.txt"

###### Paths ######

# Cytoband path

cytobands_path = pkg_resources.resource_filename("scout", cytobands_file)

cytoband_files = [
    {"build": "37", "path": pkg_resources.resource_filename("scout", cytoband_hg19_file),},
    {"build": "38", "path": pkg_resources.resource_filename("scout", cytoband_hg38_file),},
]
