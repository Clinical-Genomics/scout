#!/usr/bin/env python
# encoding: utf-8
"""
get_genotype.py

Parse all genotype information and build mongo engine objects.

Created by Måns Magnusson on 2014-11-10.
Copyright (c) 2014 __MoonsoInc__. All rights reserved.

"""

import logging

from scout.models import GTCall

logger = logging.getLogger(__name__)


def get_genotype(variant, individual_id, display_name):
    """Get the genotype information in the proper format and return
         ODM specified gt call.
      
         Args:
             variant (dict): A dictionary with the information about a variant
             individual_id (str): A string that represents the individual id
             display_name (str): A string that represents the individual id
      
         Returns:
             mongo_gt_call : A mongo engine object with the gt-call information
      
    """
    # Initiate a mongo engine gt call object
    mongo_gt_call = GTCall(sample_id=individual_id,
                          display_name=display_name)
    
    # Fill the onbject with the relevant information:
    mongo_gt_call['genotype_call'] = variant['genotypes'][individual_id].genotype

    mongo_gt_call['read_depth'] = variant['genotypes'][individual_id].depth_of_coverage

    mongo_gt_call['allele_depths'] = [variant['genotypes'][individual_id].ref_depth,
                                        variant['genotypes'][individual_id].alt_depth]

    mongo_gt_call['genotype_quality'] = variant['genotypes'][individual_id].genotype_quality

    return mongo_gt_call
