import logging

logger = logging.getLogger(__name__)

def build_query(case_id, query=None, variant_ids=None):
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
    logger.info("Building a mongo query for {0}".format(case_id))
    # We will allways use the case id when we query the database
    mongo_query['case_id'] = case_id
    logger.debug("Setting case_id to {0}".format(case_id))
    mongo_query['variant_type'] = 'clinical'
    logger.debug("Setting variant type to 'clinical' as default")
    any_query = False
    mongo_query['$and'] = []
    if query:
    # We need to check if there is any query specified in the input query
        mongo_query['variant_type'] = query.get('variant_type', 'clinical')
        logger.debug("Updating variant type to {0}".format(
            mongo_query['variant_type']))

        if query.get('thousand_genomes_frequency'):
            thousandg_freq = query.get('thousand_genomes_frequency')
            if thousandg_freq == '-1':
                mongo_query['$and'].append({
                    'thousand_genomes_frequency': {'$exists': False}
                })
            else:
                try:
                    mongo_query['$and'].append({
                        '$or': [
                            {'thousand_genomes_frequency':
                                {'$lt': float(query['thousand_genomes_frequency'])}},
                            {'thousand_genomes_frequency': {'$exists': False}}
                        ]
                    })
                    logger.debug("Adding thousand_genomes_frequency to query")
                    any_query = True
                except TypeError:
                    pass

        if query.get('exac_frequency'):
            try:
                mongo_query['$and'].append({
                    '$or': [
                        {'exac_frequency':
                            {'$lt': float(query['exac_frequency'])}},
                        {'exac_frequency': {'$exists': False}}
                    ]
                })
                logger.debug("Adding exac_frequency to query")
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
            logger.debug("Adding genetic_models={0} to query".format(
                ', '.join(query['genetic_models'])))
            any_query = True

        if query.get('hgnc_symbols'):
            mongo_query['$and'].append(
                {'hgnc_symbols':{
                    '$in': query['hgnc_symbols']
                    }
                }
            )
            logger.debug("Adding hgnc_symbols={0} to query".format(
                ', '.join(query['hgnc_symbols'])))
            any_query = True

        if query.get('gene_lists'):
            mongo_query['$and'].append(
                {'gene_lists':{
                    '$in': query['gene_lists']
                    }
                }
            )
            logger.debug("Adding gene_lists={0} to query".format(
                ', '.join(query['gene_lists'])))
            any_query = True

        if query.get('functional_annotations'):
            mongo_query['$and'].append(
                {'genes.functional_annotation':{
                    '$in': query['functional_annotations']
                    }
                }
            )
            logger.debug("Adding functional_annotations={0} to query".format(
                ', '.join(query['functional_annotations'])))
            any_query = True

        if query.get('region_annotations'):
            mongo_query['$and'].append(
                {'genes.region_annotation':{
                    '$in': query['region_annotations']
                    }
                }
            )
            logger.debug("Adding region_annotations={0} to query".format(
                ', '.join(query['region_annotations'])))
            any_query = True

    if variant_ids:
        mongo_query['$and'].append(
            {'variant_id':{
                '$in': variant_ids
                }
            }
        )
        logger.debug("Adding variant_ids={0} to query".format(
            ', '.join(variant_ids)))
        any_query = True

    if not any_query:
        del mongo_query['$and']

    return mongo_query
