# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)


class VariantHandler(object):

    """Methods to handle variants in the mongo adapter"""

    def add_gene_info(self, variant_obj, gene_panels=None):
        """Add extra information about genes from gene panels"""
        return self.mongoengine_adapter.add_gene_info(
            variant_obj = variant_obj,
            gene_panels = gene_panels
        )

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
        return self.mongoengine_adapter.variants(
            case_id=case_id,
            query=query,
            variant_ids=variant_ids,
            category=category,
            nr_of_variants=nr_of_variants,
            skip=skip,
            sort_key=sort_key
        )


    def variant(self, document_id, gene_panels=None):
        """Returns the specified variant.

           Arguments:
               document_id : A md5 key that represents the variant
               gene_panels(List[GenePanel])

           Returns:
               variant_object(Variant): A odm variant object
        """
        return self.mongoengine_adapter.variant(document_id=document_id,
                                                gene_panels=gene_panels)

    def get_causatives(self, institute_id):
        """Return all causative variants for an institute

            Args:
                institute_id(str)

            Yields:
                causatives(iterable(Variant))
        """
        return self.mongoengine_adapter.get_causatives(
                    institute_id=institute_id
                )

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
        return self.mongoengine_adapter.check_causatives(
                    case_obj=case_obj
                )

    def add_variant_rank(self, case_obj, variant_type='clinical', category='snv'):
        """Add the variant rank for all inserted variants.

            Args:
                case_obj(Case)
                variant_type(str)
        """
        self.mongoengine_adapter.add_variant_rank(
                case_obj=case_obj,
                variant_type=variant_type,
                category=category
            )

    def other_causatives(self, case_obj, variant_obj):
        """Find the same variant in other cases marked causative."""
        return self.mongoengine_adapter.other_causatives(
                case_obj=case_obj,
                variant_obj=variant_obj,
            )

    def next_variant(self, document_id):
        """Returns the next variant from the rank order.

          Arguments:
              document_id : A md5 key that represents the variant

          Returns:
              variant_object: A odm variant object
        """
        return self.mongoengine_adapter.next_variant(
                document_id=document_id,
            )

    def previous_variant(self, document_id):
        """Returns the previus variant from the rank order

            Arguments:
                document_id : A md5 key that represents the variant

            Returns:
                variant_object: A odm variant object
        """
        return self.mongoengine_adapter.next_variant(
                document_id=document_id,
            )

    def delete_variants(self, case_id, variant_type):
        """Delete variants of one type for a case

            This is used when a case i reanalyzed

            Args:
                case_id(str): The case id
                variant_type(str): 'research' or 'clinical'
        """
        self.mongoengine_adapter.delete_variants(
                case_id=case_id,
                variant_type=variant_type
            )

    def load_variant(self, variant_obj):
        """Load a variant object"""
        self.mongoengine_adapter.load_variant(
                variant_obj=variant_obj,
            )

    def overlapping(self, variant_obj):
        """Return ovelapping variants

            if variant_obj is sv it will return the overlapping snvs and oposite
        """
        return self.mongoengine_adapter.overlapping(
                variant_obj=variant_obj,
                )
