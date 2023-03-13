from importlib_resources import files

BASE_PATH = "scout.resources"

###### Paths ######

# Cytoband path
cytobands_37_path = str(files(BASE_PATH).joinpath("cytoBand_hg19.txt.gz"))
cytobands_38_path = str(files(BASE_PATH).joinpath("cytoBand_hg38.txt.gz"))

cytoband_files = {
    "37": cytobands_37_path,
    "38": cytobands_38_path,
}
