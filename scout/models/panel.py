# -*- coding: utf-8 -*-
from datetime import datetime

panel_gene = dict(
    hgnc_id=int,  # required
    symbol=str,
    disease_associated_transcripts=list,  # list of strings that represent refseq transcripts
    reduced_penetrance=bool,
    mosaicism=bool,
    database_entry_version=str,
    inheritance_models=list,
    custom_inheritance_models=list,
    comment=str,  # panel context gene comment
)


## gene panel should be indexed on genes.hgnc_id
gene_panel = dict(
    panel_name=str,  # required
    institute=str,  # institute_id
    version=float,  # required
    date=datetime,  # required
    display_name=str,  # default is panel_name
    genes=list,  # list of panel genes, sorted on panel_gene['symbol']
    maintainer=list,  # list of user ids with write access
)
