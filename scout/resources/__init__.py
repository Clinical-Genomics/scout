import pkg_resources

###### Files ######

# Cytoband
cytoband_hg19_file = "resources/cytoBand_hg19.txt.gz"
cytoband_hg38_file = "resources/cytoBand_hg38.txt.gz"

# Dismissal terms
variant_dismissal_terms = "resources/variant_dismissal_terms.json"
variant_maual_rank_terms = "resources/variant_manual_rank_terms.json"

###### Paths ######

# paths
cytobands_37_path = pkg_resources.resource_filename("scout", cytoband_hg19_file)
cytobands_38_path = pkg_resources.resource_filename("scout", cytoband_hg38_file)

dismissal_terms_path = pkg_resources.resource_filename("scout", variant_dismissal_terms)
maual_rank_terms_path = pkg_resources.resource_filename("scout", variant_maual_rank_terms)

cytoband_files = {
    "37": cytobands_37_path,
    "38": cytobands_38_path,
}

evaluation_terms = {
    "dismissal_terms_path": dismissal_terms_path,
    "manual_rank_path": maual_rank_terms_path,
}
