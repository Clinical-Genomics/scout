# -*- coding: utf-8 -*-

"""
scout.models.phenomodel
~~~~~~~~~~~~~~~~~~
Define a document to describe a phenomodel dictionary

Phenomodels are stored in phenomodel collection
"""
from bson import ObjectId
from datetime import datetime

phenomodel = dict(
    _id=ObjectId,
    institute=str,  # institute["_id"]
    name=str,  # name of phenotype model, example: Epilepsy
    description=str,  # phenomodel description
    subpanels=list,  # list of subpanel dictionaries
    created=datetime,
    updated=datetime,
)

# A subpanel dictionary
subpanel = dict(
    _id=dict(  # id is md5 string
        title=str,  # Subpanel title
        subtitle=str,  # Subpanel subtitle
        created=datetime,
        updated=datetime,
        checkboxes=list,  # a list of checkboxes dictionaries
    )
)

# A checkbox dictionary
checkbox = dict(
    term_id=dict(  # term_id is an HPO term (HP:0002133) or an OMIM term(OMIM:117100)
        description=str,  # HPO term description of OMIM term description ir custom description
        name=str,  # an HPO term (HP:0002133) or an OMIM term(OMIM:117100)
        checkbox_type=str,  # hpo or omim
        children=list,  # present only id checkbox_type=hpo. A list of checkbox dictionaries representing eventual nested HPO terms and their children.
    )
)
