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
                'end': int,
                'gene_panels': list(str),
            }

        Arguments:
            case_id(str)
            query(dict): A dictionary with querys for the database
            variant_ids(list(str)): A list of md5 variant ids

        Returns:
            mongo_query : A dictionary in the mongo query format

        """
        return self.mongoengine_adapter.build_query(
            case_id=case_id, 
            query=query, 
            variant_ids=variant_ids, 
            category=category
        )
