import pkg_resources

###### Files ######

# MatchMaker Exchange json schema, as defined in (defined in https://github.com/ga4gh/mme-apis)
mme_json_schema = 'resources/mme_api.json'

# Cytoband
cytobands_file = 'resources/cytoBand.txt.gz'

###### Paths ######

# MatchMaker Exchange
mme_schema_path = pkg_resources.resource_filename('scout', mme_json_schema)

# Cytoband path
cytobands_path = pkg_resources.resource_filename('scout', cytobands_file)
