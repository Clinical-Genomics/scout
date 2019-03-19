import logging
import re
from constants import SECONDARY_CRITERIA

LOG = logging.getLogger(__name__)

from scout.constants import (SPIDEX_HUMAN, CLINSIG_MAP)

class QueryHandler(object):

    def build_variant_query(self, query=None, category='snv', variant_type=['clinical']):
        """Build a mongo query across multiple cases.
        Translate query options from a form into a complete mongo query dictionary.

        Beware that unindexed queries against a large variant collection will
        be extremely slow.

        Currently indexed query options:
            hgnc_symbols
            rank_score
            variant_type
            category

        Args:
            query(dict): A query dictionary for the database, from a query form.
            category(str): 'snv', 'sv', 'str' or 'cancer'
            variant_type(str): 'clinical' or 'research'

        Returns:
            mongo_query : A dictionary in the mongo query format.
        """

        query = query or {}
        mongo_variant_query = {}

        LOG.debug("Building a mongo query for %s" % query)

        if query.get('hgnc_symbols'):
            mongo_variant_query['hgnc_symbols'] = {'$in': query['hgnc_symbols']}

        mongo_variant_query['variant_type'] = {'$in': variant_type}

        mongo_variant_query['category'] = category

        rank_score = query.get('rank_score') or 15

        mongo_variant_query['rank_score'] = {'$gte': rank_score}
        LOG.debug("Querying %s" % mongo_variant_query)

        return mongo_variant_query


    def build_query(self, case_id, query=None, variant_ids=None, category='snv'):
        """Build a mongo query

        These are the different query options:
            {
                'genetic_models': list,
                'chrom': str,
                'thousand_genomes_frequency': float,
                'exac_frequency': float,
                'clingen_ngi': int,
                'cadd_score': float,
                'cadd_inclusive": boolean,
                'genetic_models': list(str),
                'hgnc_symbols': list,
                'region_annotations': list,
                'functional_annotations': list,
                'clinsig': list,
                'clinsig_confident_always_returned': boolean,
                'variant_type': str(('research', 'clinical')),
                'chrom': str,
                'start': int,
                'end': int,
                'svtype': list,
                'size': int,
                'size_shorter': boolean,
                'gene_panels': list(str),
                'mvl_tag": boolean,
                'decipher": boolean,
            }

        Arguments:
            case_id(str)
            query(dict): a dictionary of query filters specified by the users
            variant_ids(list(str)): A list of md5 variant ids

        Returns:
            mongo_query : A dictionary in the mongo query format

        """
        query = query or {}
        mongo_query = {}

        ##### Base query params

        # set up the basic query params: case_id, category, type and restrict to list of variants (if var list is provided)
        LOG.debug("Building a mongo query for %s" % case_id)
        mongo_query['case_id'] = case_id

        if variant_ids:
            LOG.debug("Adding variant_ids %s to query" % ', '.join(variant_ids))
            mongo_query['variant_id'] = {'$in': variant_ids}

        LOG.debug("Querying category %s" % category)
        mongo_query['category'] = category

        LOG.debug("Set variant type to %s", mongo_query['variant_type'])
        mongo_query['variant_type'] = query.get('variant_type', 'clinical')

        # Requests to filter based on gene panels, hgnc_symbols or
        # coordinate ranges must always be honored. They are always added to
        # query as top level, implicit '$and'. When both hgnc_symbols and a
        # panel is used, addition of this is delayed until after the rest of
        # the query content is clear.
        gene_query = gene_filter(query, mongo_query)

        if if query.get('chrom'):
            coordinate_filter(query, mongo_query)
        ##### end of base query params

        # A minor, excluding filter criteria will hide variants in general,
        # but can be overridden by an including, major filter criteria
        # such as a Pathogenic ClinSig.
        # If there are no major criteria given, all minor criteria are added as a
        # top level '$and' to the query.
        # If there is only one major criteria given without any minor, it will also be
        # added as a top level '$and'.
        # Otherwise, major criteria are added as a high level '$or' and all minor criteria
        # are joined together with them as a single lower level '$and'.

        # check if any of the secondary criteria was specified in the query:
        secondary_terms = False
        secondary_filter = None
        for term in SECONDARY_CRITERIA:
            if query.get(term):
                secondary_terms = True

        if secondary_terms:
            secondary_filter = secondary_query(query, mongo_query)

        # clinsig is a primary criterion in the query (the only one for now)
        if query.get('clinsig'):
            clinsig_filter = clinsig_query(query, mongo_query)

            if query.get('clinsig_confident_always_returned') == True and secondary_terms:
                if gene_query:
                    mongo_query['$and'] = [
                        {'$or': gene_query},
                        {
                            '$or': [
                                {'$and': secondary_filter}, {'clinsig': clinsig_filter}
                            ]
                        }
                    ]
                else:
                    mongo_query['$or'] = [ {'$and': secondary_filter},
                                          {'clinsig': clinsig_filter} ]

            elif secondary_terms:

                if gene_query:
                    mongo_query['$and'] = [
                        {'$or': gene_query},
                        {
                            '$or': [
                                {'$and': secondary_filter}, {'clinsig' : clinsig_filter}
                            ]
                        }
                    ]
                else:
                    mongo_query['$or'] = [ {'$and': secondary_filter},
                                           {'clinsig' : clinsig_filter} ]

            else: # only clinsig parameter, no other secondary filters
                mongo_query['clnsig'] = clnsig_query

        elif secondary_terms: # Only secondary parameters available
            if gene_query:
                mongo_query['$and'] = [ {'$or': gene_query},
                                        {'$and': secondary_filter} ]
            else:
                mongo_query['$and'] = secondary_filter

        elif gene_query:

            mongo_query['$and'] = [{ '$or': gene_query }]



    def clinsig_query(self, query, mongo_query):
        """ Add clinsig filter values to the mongo query object

            Args:
                query(dict): a dictionary of query filters specified by the users
                mongo_query(dict): the query that is going to be submitted to the database

            Returns:
                clinsig_query(dict): a dictionary with clinsig key-values

        """
        LOG.info('Clinsig is a query parameter')
        rank = []
        str_rank = []
        trusted_revision_level = ['mult', 'single', 'exp', 'guideline']
        clinsig_query = {}

        for item in query['clinsig']:
            rank.append(int(item))
            # search for human readable clinsig values in newer cases
            rank.append(CLINSIG_MAP[int(item)])
            str_rank.append(CLINSIG_MAP[int(item)])

        if query.get('clinsig_confident_always_returned') == True:
            clinsig_query = {
                        '$elemMatch': {
                            '$or' : [
                                {
                                    '$and' : [
                                         {'value' : { '$in': rank }},
                                         {'revstat': { '$in': trusted_revision_level }}
                                    ]
                                },
                                {
                                    '$and': [
                                        {'value' : re.compile('|'.join(str_rank))},
                                        {'revstat' : re.compile('|'.join(trusted_revision_level))}
                                    ]
                                }
                            ]
                        }
                     }
        else:
            LOG.debug("add CLINSIG filter for rank: %s" %', '.join(str(query['clinsig'])))

            clnsig_query = {
                    '$elemMatch': {
                            '$or' : [
                                { 'value' : { '$in': rank }},
                                { 'value' : re.compile('|'.join(str_rank)) }
                            ]
                    }
                }

        return clinsig_query



    def coordinate_filter(self, query, mongo_query):
        """ Adds genomic coordinated-related filters to the query object

        Args:
            query(dict): a dictionary of query filters specified by the users
            mongo_query(dict): the query that is going to be submitted to the database

        Returns:
            mongo_query(dict): returned object contains coordinate filters

        """
        LOG.info('Adding genomic coordinates to the query')
        chromosome = query['chrom']
        mongo_query['chromosome'] = chromosome

        if (query.get('start') and query.get('end')):
            mongo_query['position'] = {'$lte': int(query['end'])}
            mongo_query['end'] = {'$gte': int(query['start'])}

        return mongo_query



    def gene_filter(self, query, mongo_query):
        """ Adds gene-related filters to the query object

        Args:
            query(dict): a dictionary of query filters specified by the users
            mongo_query(dict): the query that is going to be submitted to the database

        Returns:
            mongo_query(dict): returned object contains gene and panel-related filters

        """
        LOG.info('Adding panel and genes-related parameters to the query')

        gene_query = []

        if query.get('hgnc_symbols') and query.get('gene_panels'):
            gene_query.append({'hgnc_symbols': {'$in': query['hgnc_symbols']}})
            gene_query.append({'panels': {'$in': query['gene_panels']}})
            mongo_query['$or']=gene_query
        else:
            if query.get('hgnc_symbols'):
                hgnc_symbols = query['hgnc_symbols']
                mongo_query['hgnc_symbols'] = {'$in': hgnc_symbols}
                logger.debug("Adding hgnc_symbols: %s to query" %
                             ', '.join(hgnc_symbols))

            if query.get('gene_panels'):
                gene_panels = query['gene_panels']
                mongo_query['panels'] = {'$in': gene_panels}

        return gene_query


    def secondary_query(self, query, mongo_query, secondary_filter=None):
        """Creates a secondary query object based on secondary parameters specified by user

            Args:
                query(dict): a dictionary of query filters specified by the users
                mongo_query(dict): the query that is going to be submitted to the database

            Returns:
                mongo_query_minor(list): a dictionary with secondary query parameters

        """
        LOG.info('Creating a query object with secondary parameters')

        mongo_query_minor = []

        gnomad = query.get('gnomad_frequency')
        if gnomad is not None:
            # -1 means to exclude all variants that exists in gnomad
            if gnomad == '-1':
                mongo_query['gnomad_frequency'] = {'$exists': False}
            else:
                # Replace comma with dot
                mongo_query_minor.append(
                    {
                        '$or': [
                            {
                                'gnomad_frequency': {'$lt': float(gnomad)}
                            },
                            {
                                'gnomad_frequency': {'$exists': False}
                            }
                        ]
                    }
                )
            logger.debug("Adding gnomad_frequency to query")

        local_obs = query.get('local_obs')
        if  local_obs is not None:
            mongo_query_minor.append({
                '$or': [
                    {'local_obs_old': None},
                    {'local_obs_old': {'$lt': local_obs + 1}},
                ]
            })

        if query.get('clingen_ngi') is not None:
            mongo_query_minor.append({
                '$or': [
                    {'clingen_ngi': {'$exists': False}},
                    {'clingen_ngi': {'$lt': query['clingen_ngi'] + 1}},
                ]
            })

        if query.get('swegen') is not None:
            mongo_query_minor.append({
                '$or': [
                    {'swegen': {'$exists': False}},
                    {'swegen': {'$lt': query['swegen'] + 1}},
                ]
            })

        if query.get('spidex_human'):
            # construct spidex query. Build the or part starting with empty SPIDEX values
            spidex_human = query['spidex_human']

            spidex_query_or_part = []
            if ( 'not_reported' in spidex_human):
                spidex_query_or_part.append({'spidex': {'$exists': False}})

            for spidex_level in SPIDEX_HUMAN:
                if ( spidex_level in spidex_human ):
                    spidex_query_or_part.append({'$or': [
                                {'$and': [{'spidex': {'$gt': SPIDEX_HUMAN[spidex_level]['neg'][0]}},
                                          {'spidex': {'$lt': SPIDEX_HUMAN[spidex_level]['neg'][1]}}]},
                                {'$and': [{'spidex': {'$gt': SPIDEX_HUMAN[spidex_level]['pos'][0]}},
                                          {'spidex': {'$lt': SPIDEX_HUMAN[spidex_level]['pos'][1]}} ]} ]})

            mongo_query_minor.append({'$or': spidex_query_or_part })

        if query.get('cadd_score') is not None:
            cadd = query['cadd_score']
            cadd_query = {'cadd_score': {'$gt': float(cadd)}}
            logger.debug("Adding cadd_score: %s to query", cadd)

            if query.get('cadd_inclusive') is True:
                cadd_query = {
                    '$or': [
                        cadd_query,
                        {'cadd_score': {'$exists': False}}
                        ]}
                logger.debug("Adding cadd inclusive to query")

            mongo_query_minor.append(cadd_query)

        if query.get('genetic_models'):
            models = query['genetic_models']
            mongo_query_minor.append({'genetic_models': {'$in': models}})

            logger.debug("Adding genetic_models: %s to query" %
                         ', '.join(models))

        if query.get('functional_annotations'):
            functional = query['functional_annotations']
            mongo_query_minor.append({'genes.functional_annotation': {'$in': functional}})

            logger.debug("Adding functional_annotations %s to query" %
                         ', '.join(functional))

        if query.get('region_annotations'):
            region = query['region_annotations']
            mongo_query_minor.append({'genes.region_annotation': {'$in': region}})

            logger.debug("Adding region_annotations %s to query" %
                         ', '.join(region))

        if query.get('size'):
            size = query['size']
            size_query = {'length': {'$gt': int(size)}}
            logger.debug("Adding length: %s to query" % size)

            if query.get('size_shorter'):
                size_query = {
                    '$or': [
                        {'length': {'$lt': int(size)}},
                        {'length': {'$exists': False}}
                    ]}
                logger.debug("Adding size less than, undef inclusive to query.")

            mongo_query_minor.append(size_query)

        if query.get('svtype'):
            svtype = query['svtype']
            mongo_query_minor.append({'sub_category': {'$in': svtype}})
            logger.debug("Adding SV_type %s to query" %
                         ', '.join(svtype))

        if query.get('decipher'):
            mongo_query['decipher'] = {'$exists': True}
            logger.debug("Adding decipher to query")

        if query.get('depth'):
            logger.debug("add depth filter")
            mongo_query_minor.append({
                'tumor.read_depth': {
                    '$gt': query.get('depth'),
                }
            })

        if query.get('alt_count'):
            logger.debug("add min alt count filter")
            mongo_query_minor.append({
                'tumor.alt_depth': {
                    '$gt': query.get('alt_count'),
                }
            })

        if query.get('control_frequency'):
            logger.debug("add minimum control frequency filter")
            mongo_query_minor.append({
                'normal.alt_freq': {
                    '$lt': float(query.get('control_frequency')),
                }
            })

        if query.get('mvl_tag'):
            logger.debug("add managed variant list filter")
            mongo_query_minor.append({
                'mvl_tag': {
                    '$exists': True,
                }
            })

        return mongo_query_minor
