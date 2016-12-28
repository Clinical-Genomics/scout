import logging

logger = logging.getLogger(__name__)

class QueryHandler(object):

    def build_query(self, case_id, query=None, variant_ids=None, category='snv'):
        """Build a mongo query

        These are the different query options:
            {
                'genetic_models': list,
                'thousand_genomes_frequency': float,
                'exac_frequency': float,
                'cadd_score': float,
                'genetic_models': list(str),
                'hgnc_symbols': list,
                'region_annotations': list,
                'functional_annotations': list,
                'variant_type': str(('research', 'clinical')),
                'chrom': str,
                'start': int,
                'end': int
            }

        Arguments:
            case_id(str)
            query(dict): A dictionary with querys for the database
            variant_ids(list(str)): A list of md5 variant ids

        Returns:
            mongo_query : A dictionary in the mongo query format

        """
        query = query or {}
        mongo_query = {}
        logger.info("Building a mongo query for %s" % case_id)
        mongo_query['case_id'] = case_id
        logger.debug("Querying category %s" % category)
        mongo_query['category'] = category

        # We need to check if there is any query specified in the input query
        mongo_query['variant_type'] = query.get('variant_type', 'clinical')
        logger.debug("Set variant type to %s" % mongo_query['variant_type'])

        mongo_query['$and'] = []

        if query.get('chrom'):
            chromosome = query['chrom']
            mongo_query['chromosome'] = chromosome
            #Only check coordinates if there is a chromosome
            if (query.get('start') and query.get('end')):
                mongo_query['position'] = {'$lte': int(query['end'])}

                mongo_query['end'] = {'$gte': int(query['start'])}


        if query.get('thousand_genomes_frequency'):
            thousandg = query.get('thousand_genomes_frequency')
            if thousandg == '-1':
                mongo_query['thousand_genomes_frequency'] = {'$exists': False}

            else:
                mongo_query['$and'].append(
                    {
                        '$or': [
                            {'thousand_genomes_frequency':
                                {'$lt': float(thousandg)}},
                            {'thousand_genomes_frequency': {'$exists': False}}
                        ]
                    })
            logger.debug("Adding thousand_genomes_frequency to query")

        if query.get('exac_frequency'):
            exac = query['exac_frequency']
            if exac == '-1':
                mongo_query['thousand_genomes_frequency'] = {'$exists': False}
            else:
                mongo_query['$and'].append(
                    {
                        '$or': [
                            {'exac_frequency':
                                {'$lt': float(exac)}},
                            {'exac_frequency': {'$exists': False}}
                        ]
                    })

        if query.get('cadd_score'):
            cadd = query['cadd_score']
            cadd_query = {'cadd_score': {'$gt': float(cadd)}}
            logger.debug("Adding cadd_score: %s to query" % cadd)

            if query.get('cadd_inclusive') == 'yes':
                cadd_query = {
                    '$or': [
                        cadd_query,
                        {'cadd_score': {'$exists': False}}
                    ]}
                logger.debug("Adding cadd inclusive to query")

            mongo_query['$and'].append(cadd_query)

        if query.get('genetic_models'):
            models = query['genetic_models']
            mongo_query['genetic_models'] = {'$in': models}

            logger.debug("Adding genetic_models: %s to query" %
                         ', '.join(models))

        if query.get('hgnc_symbols'):
            hgnc_symbols = query['hgnc_symbols']
            mongo_query['hgnc_symbols'] = {'$in': hgnc_symbols}

            logger.debug("Adding hgnc_symbols: %s to query" %
                         ', '.join(hgnc_symbols))

        if query.get('functional_annotations'):
            functional = query['functional_annotations']
            mongo_query['genes.functional_annotation'] = {'$in': functional}

            logger.debug("Adding functional_annotations %s to query" %
                         ', '.join(functional))

        if query.get('region_annotations'):
            region = query['region_annotations']
            mongo_query['genes.region_annotation'] = {'$in': region}

            logger.debug("Adding region_annotations %s to query" %
                         ', '.join(region))

        if query.get('clinsig'):
            rank = query['clinsig']
            logger.debug("add CLINSIG filter for rank: %s", rank)
            mongo_query['clnsig'] = rank

        if variant_ids:
            mongo_query['variant_id'] = {'$in': variant_ids}

            logger.debug("Adding variant_ids %s to query" %
                ', '.join(variant_ids))

        if not mongo_query['$and']:
            del mongo_query['$and']

        return mongo_query
