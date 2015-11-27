import logging

logger = logging.getLogger(__name__)

def build_query(self, case_id, query=None, variant_ids=None):
    """Build a mongo query
    
    query looks like:
        {
            'genetic_models': list,
            'thousand_genomes_frequency': float,
            'exac_frequency': float,
            'functional_annotations': list,
            'hgnc_symbols': list,
            'region_annotations': list
        }

    Arguments:
        case_id(str)
        query(dict): A dictionary with querys for the database
        variant_ids(list(str)): A list of md5 variant ids
    
    Returns:
        mongo_query : A dictionary in the mongo query format

    """
    mongo_query = {}
    # We will allways use the case id when we query the database
    mongo_query['case_id'] = case_id
    mongo_query['variant_type'] = query.get('variant_type', 'clinical')
    if query:
    # We need to check if there is any query specified in the input query
        any_query = False
        mongo_query['$and'] = []

    if query.get('thousand_genomes_frequency'):
        try:
            mongo_query['$and'].append(
                {'thousand_genomes_frequency':{
                    '$lt': float(query['thousand_genomes_frequency'])
                    }
                }
            )
            any_query = True
        except TypeError:
            pass

    if query.get('exac_frequency'):
        try:
            mongo_query['$and'].append(
                {'exac_frequency':{
                    '$lt': float(query['exac_frequency'])
                    }
                }
            )
            any_query = True
        except TypeError:
            pass

    if query.get('genetic_models'):
        mongo_query['$and'].append(
            {'genetic_models':{
                '$in': query['genetic_models']
                }
            }
        )
        any_query = True

    if query.get('hgnc_symbols'):
        mongo_query['$and'].append(
            {'hgnc_symbols':{
                '$in': query['hgnc_symbols']
                }
            }
        )
        any_query = True

    if query.get('gene_lists'):
        mongo_query['$and'].append(
            {'gene_lists':{
                '$in': query['gene_lists']
                }
            }
        )
        any_query = True

    if query.get('functional_annotations'):
        mongo_query['$and'].append(
            {'genes.functional_annotation':{
                '$in': query['functional_annotations']
                }
            }
        )
        any_query = True

    if query.get('region_annotations'):
        mongo_query['$and'].append(
            {'genes.region_annotation':{
                '$in': query['region_annotations']
                }
            }
        )
        any_query = True

    if variant_ids:
        mongo_query['$and'].append(
            {'variant_id':{
                '$in': variant_ids
                }
            }
        )
        any_query = True


    if not any_query:
        del mongo_query['$and']

    return mongo_query