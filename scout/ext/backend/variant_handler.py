import logging

from datetime import datetime
from mongoengine import DoesNotExist, Q
from vcf_parser import VCFParser

from scout.models import Variant
from scout.ext.backend.utils import (get_mongo_variant, build_query)

logger = logging.getLogger(__name__)


class VariantHandler(object):
    """Methods to handle variants in the mongo adapter"""

    def variants(self, case_id, query=None, variant_ids=None,
                 nr_of_variants=10, skip=0):
        """Returns variants specified in question for a specific case.

        If skip not equal to 0 skip the first n variants.

        Arguments:
            case_id(str): A string that represents the case
            query(dict): A dictionary with querys for the database

        Yields:
            Variant objects
        """
        logger.info("Fetching variants from {0}".format(case_id))
        if variant_ids:
            nr_of_variants = len(variant_ids)
        else:
            nr_of_variants = skip + nr_of_variants

        mongo_query = build_query(case_id, query, variant_ids)

        result = Variant.objects(
            __raw__=mongo_query).order_by(
                'variant_rank').skip(
                    skip).limit(nr_of_variants)

        return result

    def variant(self, document_id=None, variant_id=None, case_id=None):
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


    def add_variants(self, vcf_file, variant_type, case, variant_number_treshold=5000,
                    rank_score_threshold = 0):
        """Add variants to the mongo database

            Args:
                variants(str): Path to a vcf file
                variant_type(str): 'research' or 'clinical'
                case(Case): The case for which the variants should be uploaded
                nr_of_variants(int): Treshold for number of variants
                rank_score_threshold(int): Treshold for rankscore
        """
        case_id = case.case_id

        logger.info("Setting up a variant parser")
        variant_parser = VCFParser(infile=vcf_file)
        nr_of_variants = 0

        self.delete_variants(case_id, variant_type)
        institute = self.institute(institute_id=case.owner)
        start_inserting_variants = datetime.now()

        # Check which individuals that exists in the vcf file.
        # Save the individuals in a dictionary with individual ids as keys
        # and display names as values
        individuals = {}
        # loop over keys (internal ids)
        logger.info("Checking which individuals in ped file exists in vcf")
        for individual in case.individuals:
            individual_id = individual.individual_id
            display_name = individual.display_name
            logger.debug("Checking individual {0}".format(individual_id))
            if individual_id in variant_parser.individuals:
                logger.debug("Individual {0} found".format(individual_id))
                individuals[individual_id] = display_name
            else:
                logger.warning("Individual {0} is present in ped file but"\
                                " not in vcf".format(individual_id))

        logger.info('Start parsing variants')

        # If a rank score threshold is used, check if below that threshold
        for variant in variant_parser:
            logger.debug("Parsing variant {0}".format(variant['variant_id']))
            if not float(variant['rank_scores'][case.display_name]) > rank_score_threshold:
                logger.info("Lower rank score threshold reached after {0}"\
                            " variants".format(nr_of_variants))
                break

            if variant_number_treshold:
                if nr_of_variants > variant_number_treshold:
                    logger.info("Variant number threshold reached. ({0})".format(
                                variant_number_treshold))
                    break

            nr_of_variants += 1

            mongo_variant = get_mongo_variant(
                variant=variant,
                variant_type=variant_type,
                individuals=individuals,
                case=case,
                institute=institute,
                variant_count=nr_of_variants,
            )
            logger.debug("Saving variant {0}".format(mongo_variant.display_name))
            mongo_variant.save()

            if nr_of_variants % 1000 == 0:
                logger.info('{0} variants parsed'.format(nr_of_variants))

        logger.info("Parsing variants done")
        logger.info("{0} variants inserted".format(nr_of_variants))
        logger.info("Time to insert variants: {0}".format(
          datetime.now() - start_inserting_variants))


