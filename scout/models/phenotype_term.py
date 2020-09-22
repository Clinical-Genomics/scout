# -*- coding: utf-8 -*-

# Hpo terms represents data from the hpo web
class HpoTerm(dict):
    """Represents a hpo term

    _id = str, # Same as hpo_id
    hpo_id = str, # Required
    hpo_number = int, # Required
    description = str,
    genes = list, # List with integers that are hgnc_ids
    ancestors = list # list with direct ancestors
    all_ancestors = list # list with all ancestors ancestors in the whole tree
    children = list

    """

    def __init__(
        self,
        hpo_id,
        description,
        genes=None,
        ancestors=None,
        all_ancestors=None,
        children=None,
    ):
        super(HpoTerm, self).__init__()
        self["_id"] = hpo_id
        self["hpo_id"] = hpo_id
        self["hpo_number"] = int(hpo_id.split(":")[-1])
        self["description"] = description
        # These are the direct ancestors
        self["ancestors"] = ancestors or []
        # This all ancestors of all ancestors
        self["all_ancestors"] = all_ancestors or []
        self["children"] = children or []
        self["genes"] = genes or []


# Disease terms represent diseases collected from omim, orphanet and decipher.
# Collected from OMIM
class DiseaseTerm(dict):
    """Represents a disease term

    _id = str, # Same as disease_id
    disease_id = str, # required, like OMIM:600233
    disease_nr = int, # The disease nr
    description = str, # required
    source = str, # required
    genes = list, # List with integers that are hgnc_ids
    inheritance = list, # List of inheritance models connected to the disease
    hpo_terms = list, # List of hpo terms associated with the disease

    """

    def __init__(
        self,
        disease_id,
        disease_nr,
        description,
        source,
        genes=None,
        inheritance=None,
        hpo_terms=None,
    ):
        super(DiseaseTerm, self).__init__()
        self["disease_id"] = disease_id
        self["_id"] = disease_id
        self["disease_nr"] = int(disease_nr)
        self["description"] = description
        self["source"] = source
        self["genes"] = genes or []
        self["inheritance"] = inheritance or []
        self["hpo_terms"] = hpo_terms or []


# phenotype_term is a special object to hold information on case level
# This one might be deprecated when we skip mongoengine
phenotype_term = dict(
    phenotype_id=str,
    feature=str,
    disease_models=list,  # Can be omim_id hpo_id  # list of strings
)
