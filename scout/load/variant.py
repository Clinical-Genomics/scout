import logging

from datetime import datetime

from vcf_parser import VCFParser

from scout.parse.variant import parse_variant
from scout.build import build_variant
from scout.exceptions import IntegrityError

logger = logging.getLogger(__name__)


def delete_variants(adapter, case_obj, variant_type='clinical'):
    """Delete all variants for a case of a certain variant type

        Args:
            case_obj(Case)
            variant_type(str)
    """
    adapter.delete_variants(
        case_id=case_obj['case_id'],
        variant_type=variant_type
    )


def check_coordinates(variant, coordinates):
    """Check if the variant is in the interval given by the coordinates

        Args:
            variant(dict)
            coordinates
    """
    if variant['chromosome'] == coordinates['chrom']:
        pos = variant['position']
        if (pos >= coordinates['start'] and pos <= coordinates['end']):
            return True
    return False


def load_variants(adapter, variant_file, case_obj, variant_type='clinical',
                  category='snv', rank_threshold=5, chrom=None, start=None,
                  end=None):
    """Load all variantt in variants

        Args:
            adapter(MongoAdapter)
            variant_file(str): Path to variant file
            case(Case)
            variant_type(str)
            category(str): 'snv' or 'sv'
            rank_threshold(int)
            chrom(str)
            start(int)
            end(int)
    """

    institute_obj = adapter.institute(institute_id=case_obj['owner'])

    if not institute_obj:
        raise IntegrityError("Institute {0} does not exist in"
                             " database.".format(case_obj['owner']))

    variants = VCFParser(infile=variant_file)

    rank_results_header = []
    for info_line in variants.metadata.info_lines:
        if info_line['ID'] == 'RankResult':
            rank_results_header = info_line['Description'].split('|')

    logger.info("Start inserting variants into database")
    start_insertion = datetime.now()
    start_five_thousand = datetime.now()
    nr_variants = 0
    nr_inserted = 0

    coordinates = False
    if chrom:
        coordinates = {
            'chrom': chrom,
            'start': start,
            'end': end
        }

    try:
        for nr_variants, variant in enumerate(variants):
            parsed_variant = parse_variant(
                variant_dict=variant,
                case=case_obj,
                variant_type=variant_type,
                rank_results_header=rank_results_header
            )
            variant_obj = None
            if coordinates:
                if check_coordinates(parsed_variant, coordinates):
                    variant_obj = build_variant(
                        variant=parsed_variant,
                        institute=institute_obj,
                    )

            elif parsed_variant.get('rank_score', 0) > rank_threshold:
                variant_obj = build_variant(
                    variant=parsed_variant,
                    institute=institute_obj,
                )

            if variant_obj:
                try:
                    load_variant(adapter, variant_obj)
                    nr_inserted += 1
                except IntegrityError as error:
                    pass

            if (nr_variants != 0 and nr_variants % 5000 == 0):
                logger.info("{} variants processed".format(nr_variants))
                logger.info("Time to parse variants: {0}".format(
                            datetime.now() - start_five_thousand))
                start_five_thousand = datetime.now()

    except Exception as error:
        logger.info("Deleting inserted variants")
        delete_variants(adapter, case_obj, variant_type)
        raise error

    logger.info("All variants inserted.")
    logger.info("Number of variants in file: {0}".format(nr_variants))
    logger.info("Number of variants inserted: {0}".format(nr_inserted))
    logger.info("Time to insert variants:{0}".format(
                datetime.now() - start_insertion))

    adapter.add_variant_rank(case_obj, variant_type, category=category)


def load_variant(adapter, variant_obj):
    """Load a variant into the database

        Parse the variant, create a mongoengine object and load it into
        the database.

        Args:
            adapter(MongoAdapter)
            variant_obj(scout.models.Variant)

    """
    adapter.load_variant(variant_obj)
