import logging

from scout.models import (Variant, DoesNotExist)

logger = logging.getLogger(__name__)

class VariantHandler(object):
    """Methods to handle variants in the mongo adapter"""
    
    def variants(self, case_id, query=None, variant_ids=None, 
                 nr_of_variants=10, skip=0):
        """Returns variants specified in question for a specific case.
            
        If skip ≠ 0 skip the first n variants.

        Arguments:
            case_id(str): A string that represents the case
            query(dict): A dictionary with querys for the database

        Yields:
            Variant objects
        """
        if variant_ids:
            nr_of_variants = len(variant_ids)
        else:
            nr_of_variants = skip + nr_of_variants

        mongo_query = build_query(case_id, query, variant_ids)
        
        result = Variant.objects(__raw__=mongo_query).order_by('variant_rank')
                    .skip(skip)
                    .limit(nr_of_variants)
        
        for variant in result:
            yield variant

    def variant(self, document_id):
        """Returns the specified variant.

           Arguments:
               document_id : A md5 key that represents the variant

           Returns:
               variant_object: A odm variant object
        """
        try:
            return Variant.objects.get(document_id=document_id)
        except DoesNotExist:
            return None
    
    def next_variant(self, document_id):
        """Returns the next variant from the rank order.
      
          Arguments:
              document_id : A md5 key that represents the variant
          
          Returns:
              variant_object: A odm variant object
        """
        previous_variant = Variant.objects.get(document_id=document_id)
        logger.info("Fetching next variant for {0}".format(
            previous_variant.display_name))

        rank = previous_variant.variant_rank or 0
        case_id = previous_variant.case_id
        variant_type = previous_variant.variant_type
        try:
            return Variant.objects.get(__raw__=({'$and':[
                                          {'case_id': case_id},
                                          {'variant_type': variant_type},
                                          {'variant_rank': rank+1}
                                          ]
                                        }
                                      )
                                    )   
        except DoesNotExist:
            return None

    def previous_variant(self, document_id):
        """Returns the previus variant from the rank order

            Arguments:
                document_id : A md5 key that represents the variant

            Returns:
                variant_object: A odm variant object
        """
        previous_variant = Variant.objects.get(document_id=document_id)
        logger.info("Fetching previous variant for {0}".format(
            previous_variant.display_name))
        rank = previous_variant.variant_rank or 0
        case_id = previous_variant.case_id
        variant_type = previous_variant.variant_type
        try:
            return Variant.objects.get(__raw__=({'$and':[
                                          {'case_id': case_id},
                                          {'variant_type': variant_type},
                                          {'variant_rank': rank - 1}
                                          ]
                                        }
                                      )
                                    )
        except DoesNotExist:
            return None
