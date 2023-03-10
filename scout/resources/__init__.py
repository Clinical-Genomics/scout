from contextlib import ExitStack

import importlib_resources

file_manager = ExitStack()

###### Files ######

# Cytoband
cytoband_hg19_file = importlib_resources.files("scout") / "resources/cytoBand_hg19.txt.gz"
cytoband_hg38_file = importlib_resources.files("scout") / "resources/cytoBand_hg38.txt.gz"

###### Paths ######

# Cytoband path
cytobands_37_path = file_manager.enter_context(importlib_resources.as_file(cytoband_hg19_file))
cytobands_38_path = file_manager.enter_context(importlib_resources.as_file(cytoband_hg38_file))

cytoband_files = {
    "37": cytobands_37_path,
    "38": cytobands_38_path,
}
