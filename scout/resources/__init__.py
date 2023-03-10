import importlib_resources

###### Paths ######

BASE_PATH = importlib_resources.files("scout")

# Cytoband path
cytobands_37_path = str(BASE_PATH / "resources/cytoBand_hg19.txt.gz")
cytobands_38_path = str(BASE_PATH / "resources/cytoBand_hg38.txt.gz")

cytoband_files = {
    "37": cytobands_37_path,
    "38": cytobands_38_path,
}
