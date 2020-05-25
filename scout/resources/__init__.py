import pkg_resources


###### Files ######

# Cytoband

cytobands_file = "resources/cytoBand.txt.gz"
cytoband_hg19_file = "resources/cytoBand_hg19.txt.gz"
cytoband_hg38_file = "resources/cytoBand_hg38.txt.gz"

###### Paths ######

# Cytoband path

cytobands_path = pkg_resources.resource_filename("scout", cytobands_file)
cytobands_37_path = pkg_resources.resource_filename("scout", cytoband_hg19_file)
cytobands_38_path = pkg_resources.resource_filename("scout", cytoband_hg38_file)

cytoband_files = [
    {"build": "37", "path": cytobands_37_path},
    {"build": "38", "path": cytobands_38_path},
]
