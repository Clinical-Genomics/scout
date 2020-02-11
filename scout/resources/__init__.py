import pkg_resources


###### Files ######

# Cytoband

cytobands_file = "resources/cytoBand.txt.gz"

###### Paths ######

# Cytoband path

cytobands_path = pkg_resources.resource_filename("scout", cytobands_file)
