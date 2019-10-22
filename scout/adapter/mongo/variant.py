# -*- coding: utf-8 -*-
# stdlib modules
import logging
import re
import pathlib
import tempfile

from datetime import datetime
from pprint import pprint as pp

# Third party modules
import pymongo

from cyvcf2 import VCF
from intervaltree import IntervalTree

# Local modules
from scout.parse.variant.rank_score import parse_rank_score

from scout.parse.variant import parse_variant
from scout.build import build_variant

from scout.utils.coordinates import is_par

from pymongo.errors import (DuplicateKeyError, BulkWriteError)
from scout.exceptions import IntegrityError

from .variant_loader import VariantLoader

LOG = logging.getLogger(__name__)


class VariantHandler(VariantLoader):

    """Methods to handle variants in the mongo adapter"""

    def variants(self, case_id, query=None, variant_ids=None, category='snv',
                 nr_of_variants=10, skip=0, sort_key='variant_rank'):
        """Returns variants specified in question for a specific case.

        If skip not equal to 0 skip the first n variants.

        Arguments:
            case_id(str): A string that represents the case
            query(dict): A dictionary with querys for the database
            variant_ids(List[str])
            category(str): 'sv', 'str', 'snv' or 'cancer'
            nr_of_variants(int): if -1 return all variants
            skip(int): How many variants to skip
            sort_key: ['variant_rank', 'rank_score', 'position']

        Yields:
            result(Iterable[Variant])
        """
        LOG.debug("Fetching variants from {0}".format(case_id))

        if variant_ids:
            nr_of_variants = len(variant_ids)

        elif nr_of_variants == -1:
            nr_of_variants = 0 # This will return all variants

        else:
            nr_of_variants = skip + nr_of_variants

        mongo_query = self.build_query(case_id, query=query,
                                       variant_ids=variant_ids,
                                       category=category)
        sorting = []
        if sort_key == 'variant_rank':
            sorting = [('variant_rank', pymongo.ASCENDING)]
        if sort_key == 'rank_score':
            sorting = [('rank_score', pymongo.DESCENDING)]
        if sort_key == 'position':
            sorting = [('position', pymongo.ASCENDING)]

        result = self.variant_collection.find(
            mongo_query,
            skip=skip,
            limit=nr_of_variants
        ).sort(sorting)

        return result

    def sanger_variants(self, institute_id=None, case_id=None):
        """Return all variants with sanger information

        Args:
            institute_id(str)
            case_id(str)

        Returns:
            res(pymongo.Cursor): A Cursor with all variants with sanger activity
        """
        query = {'validation': {'$exists': True}}
        if institute_id:
            query['institute_id'] = institute_id
        if case_id:
            query['case_id'] = case_id

        return self.variant_collection.find(query)

    def variant(self, document_id=None, case_id=None, simple_id=None):
        """Returns the specified variant.
        
        Creates a query to the database based on the values of the parameters. 

        Arguments:
            document_id : A md5 key that represents the variant or "variant_id"
            case_id (str): case id (will search with "variant_id")
            simple_id (str): a variant simple_id (example: 1_161184089_G_GTA)

        Returns:
            variant_object(Variant): A odm variant object
        """
        query = {}
        if case_id and document_id:
            # search for a variant in a case by variant_id
            query['case_id'] = case_id
            query['variant_id'] = document_id
        elif case_id and simple_id:
            # search for a variant in a case by its simple_id
            query['case_id'] = case_id
            query['simple_id'] = simple_id
        else:
            # search with a unique id
            query['_id'] = document_id

        variant_obj = self.variant_collection.find_one(query)
        if not variant_obj:
            return None
        
        chrom = variant_obj['chromosome']
        if chrom in ['X', 'Y']:
            ## TODO add the build here
            variant_obj['is_par'] = is_par(chrom, variant_obj['position'])
        return variant_obj

    def gene_variants(self, query=None, category='snv', variant_type=['clinical'], 
                      institute_id=None, nr_of_variants=50, skip=0):
        """Return all variants seen in a given gene.

        If skip not equal to 0 skip the first n variants.

        Arguments:
            query(dict): A dictionary with querys for the database, including
            variant_type: 'clinical', 'research'
            category(str): 'sv', 'str', 'snv' or 'cancer'
            institute_id: institute ID (required for similarity query)
            nr_of_variants(int): if -1 return all variants
            skip(int): How many variants to skip

        Query can contain:
            phenotype_terms,
            phenotype_groups,
            similar_case,
            cohorts
        """
        mongo_variant_query = self.build_variant_query(query=query,
                                   institute_id=institute_id,
                                   category=category, variant_type=variant_type)

        sorting = [('rank_score', pymongo.DESCENDING)]

        if nr_of_variants == -1:
            nr_of_variants = 0 # This will return all variants
        else:
            nr_of_variants = skip + nr_of_variants

        result = self.variant_collection.find(
            mongo_variant_query
            ).sort(sorting).skip(skip).limit(nr_of_variants)

        return result

    def verified(self, institute_id):
        """Return all verified variants for a given institute

        Args:
            institute_id(str): institute id

        Returns:
            res(list): a list with validated variants
        """
        query = {
            'verb' : 'validate',
            'institute' : institute_id,
        }
        res = []
        validate_events = self.event_collection.find(query)
        for validated in list(validate_events):
            case_id = validated['case']
            var_obj = self.variant(case_id=case_id, document_id=validated['variant_id'])
            case_obj = self.case(case_id=case_id)
            if not case_obj or not var_obj:
                continue # Take into account that stuff might have been removed from database
            var_obj['case_obj'] = {
                'display_name' : case_obj['display_name'],
                'individuals' : case_obj['individuals']
            }
            res.append(var_obj)

        return res

    def get_causatives(self, institute_id, case_id=None):
        """Return all causative variants for an institute

            Args:
                institute_id(str)
                case_id(str)

            Yields:
                str: variant document id
        """

        causatives = []

        if case_id:

            case_obj = self.case_collection.find_one(
                    {"_id": case_id}
                )
            causatives = [causative for causative in case_obj['causatives']]

        elif institute_id:

            query = self.case_collection.aggregate([
                {'$match': {'collaborators': institute_id, 'causatives': {'$exists': True}}},
                {'$unwind': '$causatives'},
                {'$group': {'_id': '$causatives'}}
            ])
            causatives = [item['_id'] for item in query]

        return causatives

    def check_causatives(self, case_obj=None, institute_obj=None, limit_genes=None):
        """Check if there are any variants that are previously marked causative

            Loop through all variants that are marked 'causative' for an
            institute and check if any of the variants are present in the
            current case.

            Args:
                case_obj (dict): A Case object
                institute_obj (dict): check across the whole institute
                limit_genes (list): list of gene hgnc_ids to limit the search to

            Returns:
                causatives(iterable(Variant))
        """
        institute_id = case_obj['owner'] if case_obj else institute_obj['_id']
        var_causative_events = self.event_collection.find({
            'institute' : institute_id,
            'verb':'mark_causative',
            'category' : 'variant'
        })
        positional_variant_ids = set()
        for var_event in var_causative_events:
            if case_obj and var_event['case'] == case_obj['_id']:
                # exclude causatives from the same case
                continue
            other_case = self.case(var_event['case'])
            if other_case is None:
                # Other variant belongs to a case that doesn't exist any more
                continue
            other_link = var_event['link']
            # link contains other variant ID
            other_causative_id = other_link.split('/')[-1]

            if other_causative_id in other_case.get('causatives',[]):
                positional_variant_ids.add(var_event['variant_id'])

        if len(positional_variant_ids) == 0:
            return []
        filters = {'variant_id': {'$in': list(positional_variant_ids)}}
        if case_obj:
            filters['case_id'] = case_obj['_id']
        else:
            filters['institute'] = institute_obj['_id']
        if limit_genes:
            filters['genes.hgnc_id'] = {'$in':limit_genes}
        return self.variant_collection.find(filters)

    def other_causatives(self, case_obj, variant_obj):
        """Find the same variant marked causative in other cases.

        Checks all other cases if there are any variants on the same position that are marked 
        causative.
        
        Args:
            case_obj(dict)
            variant_obj(dict)

        Yields:
            other_causative(dict) = {
                                        '_id' : variant_id,
                                        'case_id' : other_case['_id'],
                                        'case_display_name' : other_case['display_name']
                                    }
        """
        # variant id without "*_[variant_type]"
        variant_prefix = variant_obj['simple_id']
        clinical_variant = ''.join([variant_prefix, '_clinical'])
        research_variant = ''.join([variant_prefix, '_research'])

        var_causative_events = self.event_collection.find({
            'verb':'mark_causative',
            'subject' : {'$in' : [clinical_variant, research_variant] },
            'category' : 'variant'
        })
        
        # This is to keep track that we do not return the same variant multiple times
        returned = set()

        for var_event in var_causative_events:
            if var_event['case'] == case_obj['_id']:
                # This is the variant the search started from, do not collect it
                continue
            other_case = self.case(var_event['case'])
            if other_case is None:
                # Other variant belongs to a case that doesn't exist any more
                continue
            if variant_obj['institute'] not in other_case.get('collaborators'):
                # User doesn't have access to this case/variant
                continue

            other_case_causatives = other_case.get('causatives', [])
            other_link = var_event['link']
            # link contains other variant ID
            other_causative_id = other_link.split('/')[-1]

            # if variant is still causative for that case:
            if other_causative_id not in other_case_causatives:
                continue

            other_causative = {
                '_id' : other_causative_id,
                'case_id' : other_case['_id'],
                'case_display_name' : other_case['display_name']
            }
            
            if other_causative in returned:
                continue

            returned.add(other_causative)

            yield other_causative


    def delete_variants(self, case_id, variant_type, category=None):
        """Delete variants of one type for a case

            This is used when a case is reanalyzed

            Args:
                case_id(str): The case id
                variant_type(str): 'research' or 'clinical'
                category(str): 'snv', 'sv' or 'cancer'
        """
        category = category or ''
        LOG.info("Deleting old {0} {1} variants for case {2}".format(
                    variant_type, category, case_id))
        query = {'case_id': case_id, 'variant_type': variant_type}
        if category:
            query['category'] = category
        result = self.variant_collection.delete_many(query)
        LOG.info("{0} variants deleted".format(result.deleted_count))

    def overlapping(self, variant_obj):
        """Return overlapping variants.

        Look at the genes that a variant overlaps to.
        Then return all variants that overlap these genes.

        If variant_obj is sv it will return the overlapping snvs and oposite
        There is a problem when SVs are huge since there are to many overlapping variants.

        Args:
            variant_obj(dict)

        Returns:
            variants(iterable(dict))
        """
        #This is the category of the variants that we want to collect
        category = 'snv' if variant_obj['category'] == 'sv' else 'sv'

        query = {
            '$and': [
                {'case_id': variant_obj['case_id']},
                {'category': category},
                {'hgnc_ids' : { '$in' : variant_obj['hgnc_ids']}}
            ]
        }

        sort_key = [('rank_score', pymongo.DESCENDING)]
        # We collect the 30 most severe overlapping variants
        variants = self.variant_collection.find(query).sort(sort_key).limit(30)

        return variants

    def evaluated_variants(self, case_id):
        """Returns variants that has been evaluated

        Return all variants, snvs/indels and svs from case case_id
        which have a entry for 'acmg_classification', 'manual_rank', 'dismiss_variant'
        or if they are commented.

        Args:
            case_id(str)

        Returns:
            variants(iterable(Variant))
        """
        # Get all variants that have been evaluated in some way for a case
        query = {
            '$and': [
                {'case_id': case_id},
                {
                    '$or': [
                        {'acmg_classification': {'$exists': True}},
                        {'manual_rank': {'$exists': True}},
                        {'dismiss_variant': {'$exists': True}},
                    ]
                }
            ],
        }

        # Collect the result in a dictionary
        variants = {}
        for var in self.variant_collection.find(query):
            variants[var['variant_id']] = self.add_gene_info(var)

        # Collect all variant comments from the case
        event_query = {
            '$and': [
                {'case': case_id},
                {'category': 'variant'},
                {'verb': 'comment'},
            ]
        }

        # Get all variantids for commented variants
        comment_variants = {event['variant_id'] for event in self.event_collection.find(event_query)}

        # Get the variant objects for commented variants, if they exist
        for var_id in comment_variants:
            # Skip if we already added the variant
            if var_id in variants:
                continue
            # Get the variant with variant_id (not _id!)
            variant_obj = self.variant(var_id, case_id=case_id)

            # There could be cases with comments that refers to non existing variants
            # if a case has been reanalysed
            if not variant_obj:
                continue

            variant_obj['is_commented'] = True
            variants[var_id] = variant_obj

        # Return a list with the variant objects
        return variants.values()


    def get_region_vcf(self, case_obj, chrom=None, start=None, end=None,
                       gene_obj=None, variant_type='clinical', category='snv',
                       rank_threshold=None):
        """Produce a reduced vcf with variants from the specified coordinates
           This is used for the alignment viewer.

        Args:
            case_obj(dict): A case from the scout database
            variant_type(str): 'clinical' or 'research'. Default: 'clinical'
            category(str): 'snv' or 'sv'. Default: 'snv'
            rank_threshold(float): Only load variants above this score. Default: 5
            chrom(str): Load variants from a certain chromosome
            start(int): Specify the start position
            end(int): Specify the end position
            gene_obj(dict): A gene object from the database

        Returns:
            file_name(str): Path to the temporary file
        """
        rank_threshold = rank_threshold or -100

        variant_file = None
        if variant_type == 'clinical':
            if category == 'snv':
                variant_file = case_obj['vcf_files'].get('vcf_snv')
            elif category == 'sv':
                variant_file = case_obj['vcf_files'].get('vcf_sv')
            elif category == 'str':
                variant_file = case_obj['vcf_files'].get('vcf_str')
        elif variant_type == 'research':
            if category == 'snv':
                variant_file = case_obj['vcf_files'].get('vcf_snv_research')
            elif category == 'sv':
                variant_file = case_obj['vcf_files'].get('vcf_sv_research')

        if not variant_file:
            raise SyntaxError("Vcf file does not seem to exist")

        vcf_obj = VCF(variant_file)
        region = ""

        if gene_obj:
            chrom = gene_obj['chromosome']
            start = gene_obj['start']
            end = gene_obj['end']

        if chrom:
            if (start and end):
                region = "{0}:{1}-{2}".format(chrom, start, end)
            else:
                region = "{0}".format(chrom)

        else:
            rank_threshold = rank_threshold or 5

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
            file_name = str(pathlib.Path(temp.name))
            for header_line in vcf_obj.raw_header.split('\n'):
                if len(header_line) > 3:
                    temp.write(header_line + '\n')
            for variant in vcf_obj(region):
                temp.write(str(variant))

        return file_name


    def sample_variants(self, variants, sample_name, category = 'snv'):
        """Given a list of variants get variant objects found in a specific patient

        Args:
            variants(list): a list of variant ids
            sample_name(str): a sample display name
            category(str): 'snv', 'sv' ..

        Returns:
            result(iterable(Variant))
        """
        LOG.info('Retrieving variants for subject : {0}'.format(sample_name))
        has_allele = re.compile('1|2') # a non wild-type allele is called at least once in this sample

        query = {
            '$and': [
                {'_id' : { '$in' : variants}},
                {'category' : category},
                {'samples': {
                    '$elemMatch': { 'display_name' : sample_name, 'genotype_call': { '$regex' : has_allele } }
                }}
            ]
        }

        result = self.variant_collection.find(query)
        return result
