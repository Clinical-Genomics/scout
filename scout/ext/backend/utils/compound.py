#!/usr/bin/env python
# encoding: utf-8
"""
get_compounds.py

Get the compounds of a variant.

Created by Måns Magnusson on 2014-11-10.
Copyright (c) 2014 __MoonsoInc__. All rights reserved.

"""

import logging

from scout.models import Compound
from . import generate_md5_key

logger = logging.getLogger(__name__)

def get_compounds(variant, case, variant_type):
    """Get a list with mongoengine compounds for this variant.
    
        Arguments:
            variant(dict): A Variant dictionary
            case(Case): A case object
            variant_type(str): 'research' or 'clinical'

        Returns:
            compounds(list(Compound)): A list of mongo engine compound objects
    """
    # We need the case to construct the correct id
    case_id = case.case_id
    case_name = case.display_name
    compounds = []
    logger.debug("Checking compounds for case {0} in variant {1}".format(
        case_id, variant['variant_id']))
    
    for compound in variant['compound_variants'].get(case_name, []):
        compound_name = compound['variant_id']
        # The compound id have to match the document id
        compound_id = generate_md5_key(compound_name.split('_') +
                                   [variant_type] +
                                   case_id.split('_'))
        try:
            compound_score = float(compound['compound_score'])
        except TypeError:
            compound_score = 0.0
        
        mongo_compound = Compound(
                            variant=compound_id,
                            display_name=compound_name,
                            combined_score=compound_score
                        )
        
        compounds.append(mongo_compound)
    
    return compounds

