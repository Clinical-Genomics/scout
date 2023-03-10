import importlib_resources

###### Paths ######

# Cytoband path
cytobands_37_path = importlib_resources.files("scout") / "resources/cytoBand_hg19.txt.gz"
cytobands_38_path = importlib_resources.files("scout") / "resources/cytoBand_hg38.txt.gz"

cytoband_files = {
    "37": cytobands_37_path,
    "38": cytobands_38_path,
}
