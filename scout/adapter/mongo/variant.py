# -*- coding: utf-8 -*-
import logging
import re

import pymongo

from pymongo.errors import DuplicateKeyError
from scout.exceptions import IntegrityError

logger = logging.getLogger(__name__)


class VariantHandler(object):

    """Methods to handle variants in the mongo adapter"""

    def add_gene_info(self, variant_obj, gene_panels=None):
        """Add extra information about genes from gene panels"""
        gene_panels = gene_panels or []

        # We need to check if there are any additional information in the gene panels

        # extra_info will hold information from gene panels
        extra_info = {}
        for panel_obj in gene_panels:
            for gene_info in panel_obj['genes']:
                hgnc_id = gene_info['hgnc_id']
                if hgnc_id in extra_info:
                    extra_info[hgnc_id].append(gene_info)
                else:
                    extra_info[hgnc_id] = [gene_info]

        # Loop over the genes in the variant object to add information
        # from hgnc_genes and panel genes
        for variant_gene in variant_obj['genes']:
            hgnc_id = variant_gene['hgnc_id']
            # Get the hgnc_gene
            hgnc_gene = self.hgnc_gene(hgnc_id)

            # Create a dictionary with transcripts information
            transcripts_dict = {}
            if hgnc_gene:
                # Add transcript information from the hgnc gene
                for transcript in hgnc_gene.get('transcripts',[]):
                    tx_id = transcript['ensembl_transcript_id']
                    transcripts_dict[tx_id] = transcript

                # Add the transcripts to the gene object
                hgnc_gene['transcripts_dict'] = transcripts_dict

                if hgnc_gene.get('incomplete_penetrance'):
                    variant_gene['omim_penetrance'] = True

            # Get the panel specific information for the gene
            panel_info = extra_info.get(hgnc_id, [])

            # Manually annotated disease associated transcripts
            disease_associated = set()
            manual_penetrance = False
            mosaicism = False
            manual_inheritance = set()

            # We need to loop since there can be information from multiple
            # panels
            for gene_info in panel_info:
                # Check if there are manually annotated disease transcripts
                if gene_info.get('disease_associated_transcripts'):
                    for tx in gene_info['disease_associated_transcripts']:
                        # We remove the version of transcript at this stage
                        tx = re.sub(r'\.[0-9]', '', tx)
                        disease_associated.add(tx)
                if gene_info.get('reduced_penetrance'):
                    manual_penetrance = True

                if gene_info.get('mosaicism'):
                    mosaicism = True
                if gene_info.get('ar'):
                    manual_inheritance.add('AR')
                if gene_info.get('ad'):
                    manual_inheritance.add('AD')
                if gene_info.get('mt'):
                    manual_inheritance.add('MT')
                if gene_info.get('xr'):
                    manual_inheritance.add('XR')
                if gene_info.get('xd'):
                    manual_inheritance.add('XD')
                if gene_info.get('y'):
                    manual_inheritance.add('Y')

            variant_gene['disease_associated_transcripts'] = list(disease_associated)
            variant_gene['manual_penetrance'] = manual_penetrance
            variant_gene['mosaicism'] = mosaicism
            variant_gene['manual_inheritance'] = list(manual_inheritance)

            # Now add the information from hgnc and panels
            # to the transcripts on the variant

            # First loop over the variants transcripts
            for transcript in variant_gene.get('transcripts', []):
                tx_id = transcript['transcript_id']
                if tx_id in transcripts_dict:
                    hgnc_transcript = transcripts_dict[tx_id]
                    # If the transcript has a ref seq identifier we add that
                    # to the variants transcript
                    if 'refseq_ids' in hgnc_transcript:
                        refseq_ids = hgnc_transcript['refseq_ids']
                        transcript['refseq_ids'] = refseq_ids

                        # Check if any of the refseq ids are disease associated
                        for refseq_id in refseq_ids:
                            if refseq_id in disease_associated:
                                transcript['is_disease_associated'] = True

                    if hgnc_transcript.get('is_primary'):
                        transcript['is_primary'] = True

            variant_gene['common'] = hgnc_gene

            # Add the associated disease terms
            variant_gene['disease_terms'] = self.disease_terms(hgnc_id)

        return variant_obj

    def variants(self, case_id, query=None, variant_ids=None,
                 category='snv', nr_of_variants=10, skip=0,
                 sort_key='variant_rank'):
        """Returns variants specified in question for a specific case.

        If skip not equal to 0 skip the first n variants.

        Arguments:
            case_id(str): A string that represents the case
            query(dict): A dictionary with querys for the database
            variant_ids(List[str])
            category(str): 'sv' or 'snv'
            nr_of_variants(int): if -1 return all variants
            skip(int): How many variants to skip
            sort_key: 'variant_rank' or 'rank_score'

        Yields:
            result(Iterable[Variant])
        """
        logger.info("Fetching variants from {0}".format(case_id))

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

        result = self.variant_collection.find(
                        mongo_query,
                        skip=skip,
                        limit=nr_of_variants).sort(sorting)

        return result

    def variant(self, document_id, gene_panels=None):
        """Returns the specified variant.

           Arguments:
               document_id : A md5 key that represents the variant
               gene_panels(List[GenePanel])

           Returns:
               variant_object(Variant): A odm variant object
        """
        variant_obj = self.variant_collection.find_one({'_id': document_id})
        if variant_obj:
            variant_obj = self.add_gene_info(variant_obj, gene_panels)
        return variant_obj

    def get_causatives(self, institute_id):
        """Return all causative variants for an institute

            Args:
                institute_id(str)

            Yields:
                str: variant document id
        """
        for case in self.cases(collaborator=institute_id, has_causatives=True):
            for variant_id in case.get('causatives', []):
                yield variant_id

    def check_causatives(self, case_obj):
        """Check if there are any variants that are previously marked causative

            Loop through all variants that are marked 'causative' for an
            institute and check if any of the variants are present in the
            current case.

            Args:
                case(Case): A Case object

            Returns:
                causatives(iterable(Variant))
        """
        #owner is a string
        variant_ids = list(self.get_causatives(case_obj['owner']))
        if len(variant_ids) == 0:
            return []

        return self.variant_collection.find({
            'case_id': case_obj['_id'],
            'variant_id': {'$in': variant_ids}
        })

    def update_variant(self, variant_obj):
        """Update one variant document in the database.

        Args:
            variant_obj(dict)

        Returns:
            new_variant(dict)
        """
        new_variant = self.variant_collection.find_one_and_replace(
            {'_id': variant_obj['_id']},
            variant_obj,
            return_document=pymongo.ReturnDocument.AFTER
        )
        return new_variant

    def update_variants(self, case_obj, variant_type='clinical', category='snv'):
        """Adds extra information on variants.

        Add a variant rank based on the rank score
        Add extra information on compounds

            Args:
                case_obj(Case)
                variant_type(str)
        """
        # Get all variants sorted by rank score
        variants = self.variant_collection.find({
            'case_id': case_obj['_id'],
            'category': category,
            'variant_type': variant_type,
        }).sort('rank_score', pymongo.DESCENDING)

        logger.info("Updating variant_rank for all variants")

        # Update the information on all compounds
        for index, variant in enumerate(variants):
            # This is a list with the updated compound documents
            # compound_objs = self.update_compounds(variant)
            self.variant_collection.find_one_and_update(
                {'_id': variant['_id']},
                {
                    '$set': {
                        'variant_rank': index + 1,
                        # 'compounds': compound_objs,
                    }
                }
            )

        logger.info("Updating variant_rank done")

    def update_compounds(self, variant):
        """Update compounds for a variant."""
        compound_objs = []
        for compound in variant.get('compounds', []):
            not_loaded = True
            gene_objs = []
            # Check if the compound variant exists
            variant_obj = self.variant_collection.find_one({'_id': compound['variant']})
            # If the variant exosts we try to collect as much info as possible
            if variant_obj:
                not_loaded = False
                compound['rank_score'] = variant_obj['rank_score']
                for gene in variant_obj['genes']:
                    gene_obj = {
                        'hgnc_id': gene['hgnc_id'],
                        'hgnc_symbol': gene.get('hgnc_symbol'),
                        'region_annotation': gene.get('region_annotation'),
                        'functional_annotation': gene.get('functional_annotation'),
                    }
                    gene_objs.append(gene_obj)

            compound['not_loaded'] = not_loaded
            compound['genes'] = gene_objs
            compound_objs.append(compound)
        return compound_objs

    def add_variant_rank(self, case_obj, variant_type='clinical', category='snv'):
        """Add the variant rank for all inserted variants.

            Args:
                case_obj(Case)
                variant_type(str)
        """
        variants = self.variant_collection.find(
            {
                'case_id': case_obj['case_id'],
                'category': category,
                'variant_type': variant_type,
            },
            {'_id':1}
        ).sort('rank_score', pymongo.DESCENDING)

        logger.info("Updating variant_rank for all variants")
        for index, variant in enumerate(variants):
            self.variant_collection.find_one_and_update(
                {'_id': variant['_id']},
                {'$set': {'variant_rank': index+1}}
            )
        logger.info("Updating variant_rank done")

    def other_causatives(self, case_obj, variant_obj):
        """Find the same variant in other cases marked causative."""
        # variant id without "*_[variant_type]"
        variant_id = variant_obj['display_name'].rsplit('_', 1)[0]

        causative_ids = self.get_causatives(variant_obj['institute'])
        for causative_id in causative_ids:
            other_variant = self.variant(causative_id)
            not_same_case = other_variant['case_id'] != case_obj['_id']
            same_variant = other_variant['display_name'].startswith(variant_id)
            if (not_same_case and same_variant):
                yield other_variant

    def delete_variants(self, case_id, variant_type):
        """Delete variants of one type for a case

            This is used when a case i reanalyzed

            Args:
                case_id(str): The case id
                variant_type(str): 'research' or 'clinical'
        """
        logger.info("Deleting old {0} variants for case {1}".format(
                    variant_type, case_id))

        result = self.variant_collection.delete_many(
            {
                'case_id': case_id,
                'variant_type': variant_type
            }
        )

        logger.info("{0} variants deleted".format(result.deleted_count))
        logger.debug("Variants deleted")

    def load_variant(self, variant_obj):
        """Load a variant object

        Args:
            variant_obj(dict)

        Returns:
            inserted_id
        """
        logger.debug("Loading variant %s", variant_obj['_id'])
        try:
            result = self.variant_collection.insert_one(variant_obj)
        except DuplicateKeyError as err:
            raise IntegrityError("Variant %s already exists in database", variant_obj['_id'])
        return result.inserted_id

    def load_variants(self, variants):
        """Load many variants

        Args:
            variants(iterable(dict))

        """
        logger.debug("Loading many variants")
        result = self.variant_collection.insert_many(variants)

    def overlapping(self, variant_obj):
        """Return ovelapping variants

            if variant_obj is sv it will return the overlapping snvs and oposite
        """
        category = 'snv' if variant_obj['category'] == 'sv' else 'sv'
        query = {
            'case_id': variant_obj['case_id'],
            'variant_type': variant_obj['variant_type'],
            'hgnc_symbols': variant_obj['hgnc_symbols'],
            'category': category,
        }
        sort_key = [('rank_score', pymongo.DESCENDING)]
        variants = self.variant_collection.find(query).sort(sort_key)

        return variants
