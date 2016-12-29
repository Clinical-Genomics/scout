# -*- coding: utf-8 -*-
import logging

from mongoengine import DoesNotExist, Q

from scout.models import Variant

from scout.exceptions.database import IntegrityError

logger = logging.getLogger(__name__)


class VariantHandler(object):

    """Methods to handle variants in the mongo adapter"""

    def add_gene_info(self, variant_obj, gene_panels=None):
        """Add extra information about genes"""
        gene_panels = gene_panels or []
        hgnc_symbols = set()
        for variant_gene in variant_obj.genes:
            hgnc_id = variant_gene.hgnc_id
            hgnc_gene = self.hgnc_gene(hgnc_id)
            hgnc_symbol = None
            variant_gene.common = hgnc_gene
            if hgnc_gene:
                hgnc_symbol = hgnc_gene.hgnc_symbol

            if hgnc_symbol:
                variant_gene.hgnc_symbol = hgnc_symbol
                hgnc_symbols.add(hgnc_symbol)

            disease_terms = self.disease_terms(hgnc_id)
            variant_gene.disease_terms = disease_terms

            if hgnc_gene is not None:
                vep_transcripts = {tx.transcript_id: tx for tx in
                                   variant_gene.transcripts}

                # fill in common information for transcripts
                for hgnc_transcript in hgnc_gene.transcripts:
                    hgnc_txid = hgnc_transcript.ensembl_transcript_id
                    if hgnc_txid in vep_transcripts:
                        vep_transcripts[hgnc_txid] = hgnc_transcript

                # fill in panel specific information for genes
                for panel_obj in gene_panels:
                    gene_obj = panel_obj.gene_objects.get(hgnc_symbol)
                    if gene_obj is not None:
                        variant_gene.panel_info = gene_obj
                        break

        variant_obj.hgnc_symbols = list(hgnc_symbols)
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
        else:
            nr_of_variants = skip + nr_of_variants

        mongo_query = self.build_query(case_id, query=query,
                                       variant_ids=variant_ids,
                                       category=category)

        if nr_of_variants == -1:
            result = Variant.objects(__raw__=mongo_query).order_by(sort_key)
        else:
            result = (Variant.objects(__raw__=mongo_query)
                             .order_by(sort_key)
                             .skip(skip)
                             .limit(nr_of_variants))

        all_variants = (self.add_gene_info(variant_obj) for variant_obj in
                        result)
        return all_variants, result.count()

    def variant(self, document_id, gene_panels=None):
        """Returns the specified variant.

           Arguments:
               document_id : A md5 key that represents the variant
               gene_panels(List[GenePanel])

           Returns:
               variant_object(Variant): A odm variant object
        """
        try:
            result = Variant.objects.get(document_id=document_id)
            variant_obj = self.add_gene_info(result, gene_panels)

        except DoesNotExist:
            variant_obj = None

        return variant_obj

    def get_causatives(self, institute_id):
        """Return all causative variants for an institute

            Args:
                institute_id(str)

            Yields:
                causatives(iterable(Variant))
        """
        for case in self.cases(collaborator=institute_id, has_causatives=True):
            for variant in case.causatives:
                yield variant

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
        causatives = self.get_causatives(case_obj.owner)

        fixed_ids = set([])
        for variant in causatives:
            variant_id = variant.display_name.split('_')[:-1]
            fixed_ids.add('_'.join(variant_id + ['research']))
            fixed_ids.add('_'.join(variant_id + ['clinical']))

        return Variant.objects((Q(case_id=case_obj.case_id) &
                                Q(display_name__in=list(fixed_ids))))

    def add_variant_rank(self, case_obj, variant_type='clinical', category='snv'):
        """Add the variant rank for all inserted variants.

            Args:
                case_obj(Case)
                variant_type(str)
        """
        variants, _ = self.variants(
            case_id=case_obj['case_id'],
            nr_of_variants=-1,
            category=category,
            query={'variant_type': variant_type},
            sort_key='-rank_score',
        )
        logger.info("Updating variant_rank for all variants")
        for index, variant in enumerate(variants):
            variant.variant_rank = index + 1
            variant.save()

    def other_causatives(self, case_obj, variant_obj):
        """Find the same variant in other cases marked causative."""
        # variant id without "*_[variant_type]"
        variant_id = variant_obj.display_name.rsplit('_', 1)[0]
        causatives = self.get_causatives(variant_obj.institute.id)
        for causative in causatives:
            not_same_case = causative.case_id != case_obj.id
            same_variant = causative.display_name.startswith(variant_id)
            if (not_same_case and same_variant):
                yield causative

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
            return Variant.objects.get(__raw__={
                'case_id': case_id,
                'variant_type': variant_type,
                'category': previous_variant.category,
                'variant_rank': rank + 1})
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
            return Variant.objects.get(__raw__={
                'case_id': case_id,
                'variant_type': variant_type,
                'category': previous_variant.category,
                'variant_rank': rank - 1})
        except DoesNotExist:
            return None

    def delete_variants(self, case_id, variant_type):
        """Delete variants of one type for a case

            This is used when a case i reanalyzed

            Args:
                case_id(str): The case id
                variant_type(str): 'research' or 'clinical'
        """
        logger.info("Deleting old {0} variants for case {1}".format(
                    variant_type, case_id))
        nr_deleted = Variant.objects(
            case_id=case_id,
            variant_type=variant_type).delete()

        logger.info("{0} variants deleted".format(nr_deleted))
        logger.debug("Variants deleted")

    def load_variant(self, variant_obj):
        """Load a variant object"""
        logger.debug("Loading variant %s into database", variant_obj['variant_id'])
        if Variant.objects(document_id=variant_obj.document_id):
            raise IntegrityError("Variant {} already exists in database".format(variant_obj.display_name))
        variant_obj.save()
        logger.debug("Variant saved")

    def overlapping(self, variant_obj):
        category = 'sv' if variant_obj.category == 'snv' else 'snv'
        query = {'variant_type': variant_obj.variant_type,
                 'chrom': variant_obj.chromosome,
                 'start': variant_obj.position,
                 'end': variant_obj.end}
        variants, _ = self.variants(variant_obj.case_id, category=category,
                                    nr_of_variants=-1, query=query)
        return variants
