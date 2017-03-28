# -*- coding: utf-8 -*-

# Hpo terms represents data from the hpo web
hpo_term = dict(
    _id = str, # Same as hpo_id
   hpo_id = str, # Required
   description = str,
   genes = list, # List with integers that are hgnc_ids 
)

# Disease terms represent diseases collected from omim, orphanet and decipher.
# Collected from OMIM
disease_term = dict(
    _id = str, # Same as disease_id
    disease_id = str, # required, like OMIM:600233
    disase_nr = int, # The disease nr
    description = str, # required
    source = str, # required
    genes = list, # List with integers that are hgnc_ids 
)

# phenotype_term is a special object to hold information on case level
# This one might be deprecated when we skip mongoengine
phenotype_term = dict(
    phenotype_id = str, # Can be omim_id hpo_id
    feature = str, 
    disease_models = list, # list of strings
)

