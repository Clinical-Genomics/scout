# -*- coding: utf-8 -*-
from datetime import datetime

# A panel can
panel_gene = dict(
    hgnc_id = int, # required
    symbol = str,

    disease_associated_transcripts = list, # list of strings that represent refseq transcripts
    reduced_penetrance = bool,
    mosaicism = bool,
    database_entry_version = str,
    inheritance_models = list,
)

# A panel can hold STR objects
panel_str = dict(
    hgnc_id = int,
    hgnc_symbol = str,
    repid = str,
    ru = str,
    normal_max = int,
    pathologic_min = int,
    disease = str
)

# a panel can hold region obbjects
panel_region = dict(
    region_id = str,
    chromosome = str,
    start = int,
    end = int
)

## gene panel should be indexed on genes.hgnc_id
gene_panel = dict(
    panel_name = str, # required
    institute = str, # institute_id
    version = float, # required
    date = datetime, # required
    category = str, # required; gene_symbol, STR or region: default gene_symbol.
    display_name = str, # default is panel_name
    genes = list, # list of panel genes, sorted on panel_gene['symbol']
)
